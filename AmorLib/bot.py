""">>>
napcat api接口集成包
该模块提供了一些简易使用napcat api的方法。
"""

# region 数据结构
from typing import Generic, TypeVar, Any, Callable, Literal

T = TypeVar("T")
# ----------

# Work的基类
class BaseWork:
    def __init__(self, work) -> None:
        self.work = work


# 延迟加载描述符
class LazyLoad(Generic[T]):
    def __init__(self, work):
        self.work = work
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner) -> T:
        if instance is None:
            return self  # type: ignore
        storage_name = f"_{self.name}"
        if not hasattr(instance, storage_name):
            setattr(instance, storage_name, self.work(instance))
        return getattr(instance, storage_name)
def Lazy(method: Callable[[Any], T]) -> LazyLoad[T]:
    return LazyLoad(method)

# endregion

# region 功能实现
import os, re
from . import Message, val_msg, val_msgs

sendType = Literal["group", "private"]
botResult = tuple[bool, dict]
# ----------


# 信息
class msgWork(BaseWork):
    # 发送基本消息
    def send_msg(
        self, send_type: sendType, target_id: int | str, *messages: dict
    ) -> botResult:
        """
        发送基本消息
        Args:
            send_type ("group","private"): 发送的窗口 group=群聊 private=私聊
            target_id (int | str): 发送对象的id
            *messages (dict): 消息的具体内容
        """
        # 消息验证
        val_msgs(*messages)
        # 处理发送载荷
        url = f"/send_{send_type}_msg"
        payload = {
            "group_id" if send_type == "group" else "user_id": target_id,
            "message": list(messages),
        }
        return self.work.post(url, payload)

    # 发送合并消息
    def send_forward(
        self,
        send_type: sendType,
        target_id: int | str,
        *messages: dict,
        **options,
    ) -> botResult:
        """
        发送合并消息
        Args:
            send_type ("group","private"): 发送的窗口 group=群聊 private=私聊
            target_id (int | str): 发送对象的id
            *messages (dict): 消息的具体内容
            **options :
                - news (List[str]): 打开前显示的内容,留空则显示原内容.
                - prompt (str): 外显
                - summary (str): 底下文本
                - source (sre): 顶部文本
        """
        # 消息验证
        val_msgs(*messages, type="node")
        # 处理发送载荷
        url = "/send_forward_msg"
        payload = {
            "group_id" if send_type == "group" else "user_id": target_id,
            "messages": list(messages),
        }
        if "news" in options:
            payload["news"] = [{"text": value} for value in options["news"]]
        payload.update(
            {key: options.get(key, "") for key in ("prompt", "summary", "source")}
        )
        return self.work.post(url, payload)

    # 戳一戳
    def poke(self, target_id: int | str, group_id: int | str = "") -> botResult:
        """
        戳一戳
        Args:
            target_id (int | str): 对象id
            group_id (int | str, option): 群聊id,留空则发送至私聊. Defaults to "".
        """
        url = "/send_poke"
        payload = {"user_id": target_id, "group_id": group_id}
        return self.work.post(url, payload)


# 文件
class fileWork(BaseWork):
    # 上传文件
    def upload(
        self, send_type: sendType, target_id: int | str, **file: str
    ) -> botResult:
        """
        上传文件到好友或群聊
        Args:
            send_type (str): 发送的窗口 group=群聊 private=私聊
            target_id (int | str): 发送对象的id
            **file :
                - path (str): 文件路径
                - name (str, option): 文件名字,留空则发送原文件名
                - folder (str, option, send_type=group): 文件夹id,留空则保存到根目录.
        """
        if "path" not in file or not os.path.exists(path := file["path"]):
            raise FileNotFoundError("文件路径不存在。")
        # 处理发送载荷
        url = f"/upload_{send_type}_file"
        payload = {
            "group_id" if send_type == "group" else "user_id": target_id,
            "file": os.path.abspath(path),
            "name": name if (name := file.get("name")) else os.path.basename(path),
        }
        if send_type == "group" and "folder" in file:
            payload["folder"] = file["folder"]
        return self.work.post(url, payload)


# 群聊
class groupWork(BaseWork):
    # 发送群公告
    def send_notice(
        self, group_id: int | str, content: str, image: str = "", **options: int | str
    ) -> botResult:
        """
        发送群公告
        Args:
            group_id (int | str): 群聊id
            content (str): 公告内容
            image (str, option): 配图的URL或Base64. Defaults to "".
            **options:
                - pinned (int | str): 是否置顶
                - type (int | str): 公告类型
                - confirm_required (int | str): 是否需要成员确认阅读
                - is_show_edit_card (int | str): 是否显示 “编辑卡片” 入口（供管理员修改公告）
                - tip_window_type (int | str): 提示窗口
        """
        # 处理发送载荷
        url = "/_send_group_notice"
        payload = {
            "group_id": group_id,
            "content": content,
            "image": image,
        }
        payload.update(
            {
                key: options.get(key, 0)
                for key in (
                    "pinned",
                    "type",
                    "confirm_required",
                    "is_show_edit_card",
                    "tip_window_type",
                )
            }
        )
        return self.work.post(url, payload)

    # 设置群头衔
    def set_special_title(
        self, group_id: int | str, user_id: int | str, special_title: str = ""
    ) -> botResult:
        """
        设置群头衔
        Args:
            group_id (int | str): 群聊id
            user_id (int | str): 用户id
            special (str, option): 设置的头衔,留空则取消头衔
        """
        # 处理发送载荷
        url = "/set_group_special_title"
        payload = {
            "group_id": group_id,
            "user_id": user_id,
            "special_title": special_title,
        }
        return self.work.post(url, payload)


# 账号
class accountWork(BaseWork):
    # 获取账号信息
    def get_stranger_info(self, user_id: int | str) -> botResult:
        """获取账号信息
        Args:
            user_id (int | str): 用户id
        """
        # 处理发送载荷
        url = "/get_stranger_info"
        payload = {"user_id": user_id}
        return self.work.post(url, payload)

# endregion

# region main
import requests, json
ACCOUNT_PATH = "conf/account.json"
# ----------

class BotClient:
    def __init__(self, bot_id: int, bot_nick: str | None = None) -> None:
        self.url = None
        with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
            account = json.load(f)["account"]
            for bot in account:
                if bot["id"] == bot_id:
                    server = bot["server"]
                    self.url = f"{server['host']}:{server['port']}"
                    self.headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {server['access_token']}",
                    }
                    self.id = bot_id
                    if bot_nick:
                        self.nick = bot_nick
                    else:
                        _, bot_info = self.accountWork.get_stranger_info(bot_id)
                        self.nick = bot_info['data']['nick']
                    break
        if self.url is None:
            raise ValueError(f"未找到匹配的bot账号。")

    # 访问服务
    def post(self, url: str, payload: dict) -> botResult:
        assert self.url is not None, "URL should be set in __init__"
        try:
            response = requests.request(
                "POST", self.url + url, headers=self.headers, data=json.dumps(payload)
            )
            data = response.json()
            return data.get("status") == "ok", data
        except requests.exceptions.RequestException as e:
            return False, {"err": f"请求失败: {e}"}
        except json.JSONDecodeError as e:
            return False, {"err": f"响应解析失败: {e}"}
        except Exception as e:
            return False, {"err": f"未知错误: {e}"}

    # bot可调用功能
    msgWork = Lazy(msgWork)
    fileWork = Lazy(fileWork)
    groupWork = Lazy(groupWork)
    accountWork = Lazy(accountWork)

    # 简易使用
    def send(
        self, send_type: sendType, target_id: int | str, messages: str
    ) -> botResult:
        """
        {SPLIT} 分割消息
        {NODE} 合并消息节点
        {AT:int} 艾特
        """
        # 分割消息
        msg_segments = messages.split("{SPLIT}")
        result = []
        # 处理结构
        for msg in msg_segments:
            # 如果msg为空，跳过
            if not msg.strip():
                continue
            # 当前msg的处理结果列表
            msg_result = []

            # 处理AT
            matches = list(re.finditer(r"\{AT-(\d+)\}", msg))
            if not matches:
                msg_result.append(Message.text.create(msg))
            else:
                current_pos = 0
                for match in matches:
                    # 处理AT前面的文本部分
                    if text_before := msg[current_pos : match.start()]:
                        msg_result.append(Message.text.create(text_before))
                    # 处理AT部分
                    msg_result.append(Message.at.create(match.group(1)))

                    current_pos = match.end()

                # 处理最后一个AT后面的文本部分
                text_after = msg[current_pos:]
                if text_after:
                    msg_result.append(Message.text.create(text_after))

            # 将当前msg的处理结果添加到最终结果中
            result.append(msg_result)
        # 发送消息
        if len(result) == 1:
            msg = result[0]
            return self.msgWork.send_msg(send_type, target_id, *msg)
        else:
            msg_node = []
            for msg_list in result:
                msg_node.append(Message.node.create(self.id, self.nick, *msg_list))
            return self.msgWork.send_forward(send_type, target_id, *msg_node)

# endregion