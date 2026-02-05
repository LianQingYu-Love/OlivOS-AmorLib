"""
对于user的一些功能实现
"""

import OlivaDiceCore  # type: ignore


def isInMasterList(plugin_event):  # type: ignore
    return OlivaDiceCore.ordinaryInviteManager.isInMasterList(
        plugin_event.bot_info.hash,
        OlivaDiceCore.userConfig.getUserHash(
            plugin_event.data.user_id, "user", plugin_event.platform["platform"]
        ),
    )


def getGroupRole(plugin_event):
    if hasattr(plugin_event.data, "group_id"):
        user_info = plugin_event.get_group_member_info(
            plugin_event.data.group_id, plugin_event.data.user_id
        )
        return user_info["data"]["role"]
    return
