import OlivOS  # type: ignore
import OlivaDiceCore  # type: ignore

try:
    import OlivaDiceNativeGUI  # type: ignore

    has_NativeGUI = True
except ImportError:
    has_NativeGUI = False


def init_msgCustom(Plugin, Proc):
    bot_info_dict = Proc.Proc_data["bot_info_dict"]
    for bot_id in bot_info_dict:
        if bot_id not in OlivaDiceCore.msgCustom.dictStrCustomDict:
            OlivaDiceCore.msgCustom.dictStrCustomDict[bot_id] = {}
        for key in Plugin.msgCustom.dictStrCustom:
            if key not in OlivaDiceCore.msgCustom.dictStrCustomDict[bot_id]:
                OlivaDiceCore.msgCustom.dictStrCustomDict[bot_id][key] = (
                    Plugin.msgCustom.dictStrCustom[key]
                )
        for key in Plugin.msgCustom.dictHelpDocTemp:
            if key not in OlivaDiceCore.helpDocData.dictHelpDoc[bot_id]:
                OlivaDiceCore.helpDocData.dictHelpDoc[bot_id][key] = (
                    Plugin.msgCustom.dictHelpDocTemp[key]
                )
        if has_NativeGUI:
            for key in Plugin.msgCustom.dictStrCustomNote:
                if key not in OlivaDiceNativeGUI.msgCustom.dictStrCustomNote:
                    OlivaDiceNativeGUI.msgCustom.dictStrCustomNote[key] = (
                        Plugin.msgCustom.dictStrCustomNote[key]
                    )
    OlivaDiceCore.msgCustom.dictStrConst.update(Plugin.msgCustom.dictStrConst)
    OlivaDiceCore.msgCustom.dictGValue.update(Plugin.msgCustom.dictGValue)
    OlivaDiceCore.msgCustom.dictTValue.update(Plugin.msgCustom.dictTValue)
    if has_NativeGUI:
        OlivaDiceNativeGUI.msgCustom.dictStrCustomNote.update(
            Plugin.msgCustom.dictStrCustomNote
        )


class MsgManager:
    def __init__(self, plugin_event):
        force_reply = False  # 是否强制回复
        # region 基本参数
        self.val = {}
        self.flags = {  # 存储各类状态标识
            "is_command": False,  # 是否为命令消息
            "is_host": False,  # 是否来自主机账号
            "is_master": False,  # 是否来自机器人主人
            "is_group": False,  # 是否来自群聊
            "is_group_admin": False,  # 是否来自群管理员
            "is_group_sub_admin": False,  # 是否来自群副管理员
            "is_group_have_admin": False,  # 是否拥有群管理权限
        }
        self.msg = plugin_event.data.message  # 消息
        self.sender = plugin_event.data.sender  # 发送者信息
        self.bot_hash = plugin_event.bot_info.hash  # 机器人哈希
        self.bot_id = str(plugin_event.base_info["self_id"])  # 机器人ID
        self.bot_id_sub = None  # 子账号ID（如果存在）
        if (
            "sub_self_id" in (extend := plugin_event.data.extend)
            and extend["sub_self_id"] is not None
        ):
            self.bot_id_sub = str(extend["sub_self_id"])
        self.at_list = []  # 被艾特的用户ID列表
        self.user_id = plugin_event.data.user_id  # 发送者ID
        self.platform = plugin_event.platform["platform"]  # 平台
        self.group_id = None
        # endregion 基本参数
        # region 初始化模板变量
        dictTValue = OlivaDiceCore.msgCustom.dictTValue.copy()
        dictTValue["tUserName"] = self.sender["name"]
        dictTValue["tName"] = self.sender["name"]
        dictTValue.update(OlivaDiceCore.msgCustom.dictGValue)
        dictTValue = OlivaDiceCore.msgCustomManager.dictTValueInit(
            plugin_event, dictTValue
        )
        self.dictTValue = dictTValue  # 模板变量
        self.dictStrCustom = OlivaDiceCore.msgCustom.dictStrCustomDict[
            self.bot_hash
        ]  # 自定义回复
        # endregion 初始化模板变量
        # region 处理回复
        """处理强制回复标识（@机器人触发）"""
        msg_templet = OlivOS.messageAPI.Message_templet("old_string", self.msg)
        if not msg_templet.data:
            msg_para = msg_templet.data[0]
            if msg_para.type == "at":
                at_id = msg_para.data["id"]
                if at_id in (self.bot_id, self.bot_id_sub):
                    force_reply = True
        """处理at和空文本"""
        for msg_para in msg_templet.data:
            msg_para_cq = msg_para.CQ()
            if msg_para.type == "at":
                self.at_list.append(msg_para_cq)
                self.msg = self.msg.lstrip(msg_para_cq)
            elif msg_para.type == "text" and msg_para_cq.strip(" ") == "":
                self.msg = self.msg.lstrip(msg_para_cq)
            else:
                break
        """检查消息是否为命令"""
        self.msg, self.flags["is_command"] = OlivaDiceCore.msgReply.msgIsCommand(
            self.msg, OlivaDiceCore.crossHook.dictHookList["prefix"]
        )
        # endregion 处理回复
        # region 初始化用户身份相关标识
        self.flags["is_master"] = OlivaDiceCore.ordinaryInviteManager.isInMasterList(
            plugin_event.bot_info.hash,
            OlivaDiceCore.userConfig.getUserHash(
                self.user_id, "user", plugin_event.platform["platform"]
            ),
        )
        """判断消息类型（群/私聊）"""
        func_type = plugin_event.plugin_info["func_type"]
        if func_type == "group_message":
            self.group_id = plugin_event.data.group_id
            self.flags["is_host"] = plugin_event.data.host_id is not None
            self.flags["is_group"] = True
            # 检查群管理员身份
            if "role" in plugin_event.data.sender:
                self.flags["is_group_have_admin"] = True
                role = plugin_event.data.sender["role"]
                if role in ("owner", "admin"):
                    self.flags["is_group_admin"] = True
                elif role == "sub_admin":
                    self.flags["is_group_admin"] = True
                    self.flags["is_group_sub_admin"] = True
        elif func_type == "private_message":
            self.flags["is_group"] = False
        # endregion 初始化用户身份相关标识
        # region 检查权限配置
        if self.flags["is_host"] and self.flags["is_group"]:
            hag_id = (
                f"{str(plugin_event.data.host_id)}|{str(plugin_event.data.group_id)}"
            )
        elif self.flags["is_group"]:
            hag_id = str(plugin_event.data.group_id)
        flags_host_enable = True
        flags_host_local_enable = True
        flags_group_enable = True
        if self.flags["is_host"]:
            """获取频道启用状态"""
            flags_host_enable = OlivaDiceCore.userConfig.getUserConfigByKey(
                userId=plugin_event.data.host_id,
                userType="host",
                platform=self.platform,
                userConfigKey="hostEnable",
                botHash=self.bot_hash,
            )
            """获取频道本地启用状态"""
            flags_host_local_enable = OlivaDiceCore.userConfig.getUserConfigByKey(
                userId=plugin_event.data.host_id,
                userType="host",
                platform=self.platform,
                userConfigKey="hostLocalEnable",
                botHash=self.bot_hash,
            )
        """获取群启用状态"""
        if self.flags["is_group"]:
            if self.flags["is_host"]:
                if flags_host_enable:
                    flags_group_enable = OlivaDiceCore.userConfig.getUserConfigByKey(
                        userId=hag_id,
                        userType="group",
                        platform=plugin_event.platform["platform"],
                        userConfigKey="groupEnable",
                        botHash=plugin_event.bot_info.hash,
                    )
                else:
                    flags_group_enable = OlivaDiceCore.userConfig.getUserConfigByKey(
                        userId=hag_id,
                        userType="group",
                        platform=plugin_event.platform["platform"],
                        userConfigKey="groupWithHostEnable",
                        botHash=plugin_event.bot_info.hash,
                    )
            else:
                flags_group_enable = OlivaDiceCore.userConfig.getUserConfigByKey(
                    userId=hag_id,
                    userType="group",
                    platform=plugin_event.platform["platform"],
                    userConfigKey="groupEnable",
                    botHash=plugin_event.bot_info.hash,
                )
        """判断是否回复"""
        if not flags_host_local_enable and not force_reply:
            self.allow_reply = False
        elif not flags_group_enable and not force_reply:
            self.allow_reply = False
        else:
            self.allow_reply = True

    # endregion

    def msg_format(self, custom: str, t_value: dict[str, str] = {}):
        """格式化"""
        if custom in self.dictStrCustom:
            dictTValue = self.dictTValue
            dictTValue.update(t_value)
            return OlivaDiceCore.msgCustomManager.formatReplySTR(
                self.dictStrCustom[custom], dictTValue
            )
        return
