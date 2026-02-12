import OlivOS  # type: ignore
import OlivaDiceCore  # type: ignore

try:
    import OlivaDiceNativeGUI  # type: ignore

    has_NativeGUI = True
except ImportError:
    has_NativeGUI = False



def init_msgCustom(Plugin, Proc):
    bot_info_dict = Proc.Proc_data['bot_info_dict']
    for bot in bot_info_dict:
        if bot not in OlivaDiceCore.msgCustom.dictStrCustomDict:
            OlivaDiceCore.msgCustom.dictStrCustomDict[bot] = {}
        for key in Plugin.msgCustom.dictStrCustom:
            if key not in OlivaDiceCore.msgCustom.dictStrCustomDict[bot]:
                OlivaDiceCore.msgCustom.dictStrCustomDict[bot][key] = Plugin.msgCustom.dictStrCustom[key]
        for key in Plugin.msgCustom.dictHelpDocTemp:
            if key not in OlivaDiceCore.helpDocData.dictHelpDoc[bot]:
                OlivaDiceCore.helpDocData.dictHelpDoc[bot][key] = Plugin.msgCustom.dictHelpDocTemp[key]
        if has_NativeGUI:
            for key in Plugin.msgCustom.dictStrCustomNote:
                if key not in OlivaDiceNativeGUI.msgCustom.dictStrCustomNote:
                    OlivaDiceNativeGUI.msgCustom.dictStrCustomNote[key] = Plugin.msgCustom.dictStrCustomNote[key]   
    OlivaDiceCore.msgCustom.dictStrConst.update(Plugin.msgCustom.dictStrConst)
    OlivaDiceCore.msgCustom.dictGValue.update(Plugin.msgCustom.dictGValue)
    OlivaDiceCore.msgCustom.dictTValue.update(Plugin.msgCustom.dictTValue)
    if has_NativeGUI:
        OlivaDiceNativeGUI.msgCustom.dictStrCustomNote.update(Plugin.msgCustom.dictStrCustomNote)

