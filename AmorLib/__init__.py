__author__ = "星瑚"
__version__ = "1.2.1"

STRING_ROW = list[str] | tuple[str, ...]

from .db import DataBase, execute
from .router import UniqueRouter, FsmRouter, PriorityRouter
from .msgCustom import MsgManager, init_msgCustom, has_NativeGUI
