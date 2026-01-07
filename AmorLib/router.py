"""
命令路由器
通过路由装饰器实现命令识别与执行。
    - 独立路由
        依次匹配直到匹配成功
        适合强独立性命令集
    - 状态机路由
        只匹配对应状态的命令
        适合不同状态或身份则不同触发的命令集
    - 优先级路由
        按优先级依次匹配
        适合命令相同但有优先级的命令
"""

import re


class UniqueRouter:
    def __init__(self) -> None:
        self._commands = []

    def route(self, pattern: str):
        def decorator(handler):
            self._commands.append((re.compile(pattern), handler))
            return handler

        return decorator

    def match(self, msg: str):
        for pattern, handler in self._commands:
            match = re.match(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None


class FsmRouter:
    def __init__(self) -> None:
        self._commands = {}

    def route(self, state: str, pattern: str):
        if state not in self._commands.keys():
            self._commands[state] = []

        def decorator(handler):
            self._commands[state].append((re.compile(pattern), handler))
            return handler

        return decorator

    def match(self, state: str, msg: str):
        if state not in self._commands.keys():
            return None, None
        for pattern, handler in self._commands[state]:
            match = re.match(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None


class PriorityRouter:
    def __init__(self) -> None:
        self._commands = []

    def route(self, priority: int, pattern: str):
        def decorator(handler):
            self._commands.append((-priority, re.compile(pattern), handler))
            self._commands.sort()
            return handler

        return decorator

    def match(self, msg: str):
        for _, pattern, handler in self._commands:
            match = re.match(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None
