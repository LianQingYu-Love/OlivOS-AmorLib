# -*- encoding: utf-8 -*-
"""
@File      :    AmorLib/__init__.py
@Author    :    LianQingYu-Love恋倾雨
@Contact   :    None
@License   :    AGPLv3
@Copyright :    (C) 2026 AmorLib
@Desc      :    None
"""

STRING_ROW = list[str] | tuple[str, ...]

from .db import DataBase, execute
from .router import UniqueRouter, FsmRouter, PriorityRouter
from .custom import MsgManager, init_msgCustom, has_NativeGUI
