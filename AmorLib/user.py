'''
    对于user的一些功能实现
'''
try:
    import OlivaDiceCore # type: ignore
    def isInMasterList(plugin_event): # type: ignore
        return OlivaDiceCore.ordinaryInviteManager.isInMasterList(
                plugin_event.bot_info.hash,
                OlivaDiceCore.userConfig.getUserHash(
                    plugin_event.data.user_id, 'user',
                    plugin_event.platform['platform']))
except:
    def isInMasterList(plugin_event):
        return False