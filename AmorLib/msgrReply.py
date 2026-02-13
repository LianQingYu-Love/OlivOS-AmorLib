import OlivaDiceCore  # type: ignore


def format_reply(plugin_event, msg_custom: str, tValue: dict[str, str] = {}):
    dictTValue = OlivaDiceCore.msgCustom.dictTValue.copy()
    dictTValue.update(OlivaDiceCore.msgCustom.dictGValue)
    dictTValue = OlivaDiceCore.msgCustomManager.dictTValueInit(plugin_event, dictTValue)
    dictTValue.update(tValue)

    dictStrCustom = OlivaDiceCore.msgCustom.dictStrCustomDict[
        plugin_event.bot_info.hash
    ]
    custom = dictStrCustom.get(msg_custom)
    if custom:
        return OlivaDiceCore.msgCustomManager.formatReplySTR(custom, dictTValue)
    return msg_custom
