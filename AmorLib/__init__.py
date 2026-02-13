__author__ = "星瑚"
__version__ = "0.2.0"
__description__ = "提供简易的插件函数"

STRING_ROW = list[str] | tuple[str, ...]


from .db import DataBase, execute
from .router import UniqueRouter, FsmRouter, PriorityRouter

from .user import is_master, get_group_role
from .msgCustom import init_msgCustom, has_NativeGUI
from .msgrReply import format_reply
