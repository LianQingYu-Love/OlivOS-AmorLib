from typing import List, Union, Literal, Annotated
from pydantic import BaseModel, ValidationError, Field, Tag

# region 消息类型定义


# 文本
class TextData(BaseModel):
    text: str
class TextMsg(BaseModel):
    type: Literal["text"] = "text"
    data: TextData

    @staticmethod
    def create(text: str) -> dict:
        return {"type": "text", "data": {"text": text}}

# 表情
class FaceData(BaseModel):
    id: int
class FaceMsg(BaseModel):
    type: Literal["face"] = "face"
    data: FaceData

    @staticmethod
    def create(id: int) -> dict:
        return {"type": "face", "data": {"id": id}}

# 图片
class ImageData(BaseModel):
    file: str
    summary: str | None = None
class ImageMsg(BaseModel):
    type: Literal["image"] = "image"
    data: ImageData

    @staticmethod
    def create(file: str, summary: str | None = None) -> dict:
        data = {"type": "image", "data": {"file": file}}
        if summary:
            data["data"]["summary"] = summary
        return data

# 回复
class ReplyData(BaseModel):
    id: str
class ReplyMsg(BaseModel):
    type: Literal["reply"] = "reply"
    data: ReplyData

    @staticmethod
    def create(id: str) -> dict:
        return {"type": "reply", "data": {"id": id}}

# json
class JsonData(BaseModel):
    data: str
class JsonMsg(BaseModel):
    type: Literal["json"] = "json"
    data: JsonData

    @staticmethod
    def create(data: str) -> dict:
        return {"type": "json", "data": {"data": data}}

# 视频
class VideoData(BaseModel):
    file: str
class VideoMsg(BaseModel):
    type: Literal["video"] = "video"
    data: VideoData

    @staticmethod
    def create(file: str) -> dict:
        return {"type": "video", "data": {"file": file}}

# 文件
class FileData(BaseModel):
    file: str
    name: str | None = None
class FileMsg(BaseModel):
    type: Literal["file"] = "file"
    data: FileData

    @staticmethod
    def create(file: str, name: str | None = None) -> dict:
        data = {"type": "file", "data": {"file": file}}
        if name:
            data["data"]["name"] = name
        return data

#  markdown
class RecordData(BaseModel):
    content: str
class RecordMsg(BaseModel):
    type: Literal["record"] = "record"
    data: RecordData

    @staticmethod
    def create(content: str) -> dict:
        return {"type": "record", "data": {"content": content}}

# 合并转发
# region 合并消息支持的类型
MsgNodeUnion = Annotated[
    Union[
        Annotated[TextMsg, Tag("text")],
        Annotated[FaceMsg, Tag("face")],
        Annotated[ImageMsg, Tag("image")],
        Annotated[ReplyMsg, Tag("reply")],
        Annotated[JsonMsg, Tag("json")],
        Annotated[VideoMsg, Tag("video")],
        Annotated[FileMsg, Tag("file")],
        Annotated[RecordMsg, Tag("record")],
        Annotated["NodeMsg", Tag("node")],
    ],
    Field(discriminator="type"),
]
# endregion
class NewsItem(BaseModel):
    text: str
class NodeData(BaseModel):
    user_id: Union[str, int]
    nickname: str
    content: List[MsgNodeUnion]
    news: List[NewsItem] | None = None
    prompt: str | None = None
    summary: str | None = None
    source: str | None = None
class NodeMsg(BaseModel):
    type: Literal["node"] = "node"
    data: NodeData

    @staticmethod
    def create(user_id: str | int, nickname: str, *content: dict) -> dict:
        data = {
            "type": "node",
            "data": {
                "user_id": user_id,
                "nickname": nickname,
                "content": list(content),
            },
        }
        return valMsg(data, type="node")

# 艾特
class AtData(BaseModel):
    qq: str
class AtMsg(BaseModel):
    type: Literal["at"] = "at"
    data: AtData

    @staticmethod
    def create(user_id: str | int) -> dict:
        data = {
            "type": "at",
            "data": {
                "qq": str(user_id),
            },
        }
        return valMsg(data, type="at")

# endregion

# region main
msgType = Literal[
    "text", "face", "image", "reply", "json", "video", "file", "record", "node", "at"
]
# ----------


# 消息构建集合
class Message:
    text = TextMsg
    face = FaceMsg
    image = ImageMsg
    reply = ReplyMsg
    json = JsonMsg
    video = VideoMsg
    file = FileMsg
    record = RecordMsg
    node = NodeMsg
    at = AtMsg


def valMsg(
    msg: dict,
    type: msgType | None = None,
) -> dict:
    """消息结构验证
    Args:
        msg (dict): 消息
        type (MsgType, optional): 指定要验证的类型. Defaults to None.

    Raises:
        ValueError: 缺少type字段
        ValueError: 不是允许的消息类型
        ValueError: 不是指定的消息类型
        ValueError: 消息结构错误
        ValueError: 其他异常

    Returns:
        dict: 验证过后的消息
    """
    # 消息类型验证
    if not (msg_type := msg.get("type")):
        raise ValueError("消息缺少 'type' 字段")
    elif type is not None and msg_type != type:
        raise ValueError(f"消息类型指定为：{type}, 但结果是{msg_type}")
    # 消息结构验证
    try:
        return getattr(Message, msg_type)(**msg).model_dump(exclude_none=True)
    # 消息结构错误
    except ValidationError as e:
        err_details = [
            f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()
        ]
        raise ValueError(
            f"消息结构错误 - {msg_type}:\n  " + "\n  ".join(err_details)
        ) from None
    # 其他异常
    except Exception as e:
        raise ValueError(f"消息验证错误: {str(e)}") from e


def valMessages(*messages: dict, type: msgType | None = None):
    """消息结构验证
    Args:
        *messages (dict): 消息
        type (MsgType, optional): 指定要验证的类型. Defaults to None.

    Raises:
        ValueError: 缺少type字段
        ValueError: 不是允许的消息类型
        ValueError: 不是指定的消息类型
        ValueError: 消息结构错误
        ValueError: 其他异常

    Returns:
        dict: 验证过后的消息
    """
    err_list = []
    for index, msg in enumerate(messages):
        try:
            valMsg(msg, type)
        except Exception as e:
            err_list.append(f"第{index+1}条消息验证错误：\n  {e}")
    if err_list:
        raise ValueError(
            f"共发现{len(err_list)}条消息验证错误：\n{"\n\n".join(err_list)}"
        ) from None

# endregion