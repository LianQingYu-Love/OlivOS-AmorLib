""">>>
命令路由器
通过路由装饰器实现命令识别与执行。
独立路由
    依次匹配直到匹配成功
    适合强独立性命令集
状态机路由
    依次匹配对应状态的命令
    适合不同状态或身份则不同触发的命令集
优先级路由
    按优先级依次匹配
    适合命令相同但有优先级的命令
"""

import re
from . import STRING_ROW


class UniqueRouter:
    """
    依次匹配直到匹配成功
    """

    def __init__(self) -> None:
        self._forward = []

    def route(self, pattern: str):
        def wrapper(handler):
            self._forward.append((re.compile(pattern), handler))
            return handler

        return wrapper

    def search(self, msg: str):
        for pattern, handler in self._forward:
            match = re.search(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None


class FsmRouter:
    """
    依次匹配对应状态的命令
    """

    def __init__(self, states: STRING_ROW) -> None:
        self._states = {}
        self._forward = []
        for state in states:
            self._states[state] = []

    def route(self, states: str | STRING_ROW, pattern: str):
        if type(states) == str:
            states = (states,)
        if any(state not in self._states.keys() for state in states):
            raise ValueError("状态路由器录入命令的状态非法。")

        def wrapper(handler):
            for state in states:
                self._states[state].append(len(self._forward))
            self._forward.append((re.compile(pattern), handler))
            return handler

        return wrapper

    def search(self, states: str | STRING_ROW, msg: str):
        if type(states) == str:
            states = (states,)
        cmd_unique_index = set()
        for state in states:
            if state in self._states.keys():
                cmd_unique_index.update(self._states[state])
        for cmd_index in cmd_unique_index:
            pattern, handler = self._forward[cmd_index]
            match = re.search(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None


class PriorityRouter:
    """
    按优先级依次匹配
    """

    def __init__(self) -> None:
        self._forward = []

    def route(self, priority: int, pattern: str):
        def wrapper(handler):
            self._forward.append((-priority, re.compile(pattern), handler))
            self._forward.sort()
            return handler

        return wrapper

    def search(self, msg: str):
        for _, pattern, handler in self._forward:
            match = re.search(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None
