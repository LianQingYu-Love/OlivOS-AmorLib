"""
对于user的一些功能实现
"""

import OlivaDiceCore  # type: ignore


def is_master(plugin_event):  # type: ignore
    return OlivaDiceCore.ordinaryInviteManager.isInMasterList(
        plugin_event.bot_info.hash,
        OlivaDiceCore.userConfig.getUserHash(
            plugin_event.data.user_id, "user", plugin_event.platform["platform"]
        ),
    )


def get_group_role(plugin_event):
    if "role" in plugin_event.data.sender:
        return plugin_event.data.sender["role"]
    return
