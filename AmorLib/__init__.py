__author__ = "星瑚"
__version__ = "0.1.0"
__description__ = "提供简易的插件函数"

STRING_ROW = list[str] | tuple[str, ...]


from .db import DataBase, execute
from .router import UniqueRouter, FsmRouter, PriorityRouter

from .user import isInMasterList, getGroupRole

# from .msg import Message, val_msg, val_msgs
# from .bot import BotClient
