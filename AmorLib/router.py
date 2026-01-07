"""
    命令路由器
    通过路由装饰器实现命令识别与执行。

    更新计划：
        对路由器进行分类：
            - 独立路由
                依次匹配直到返回匹配成功的第一个命令
                适合强独立性命令集
            - 状态机路由
                确定匹配的命令类型，再从对应区间进行依次匹配
                适合不同状态或身份则不同触发的命令集
            - 优先级路由
                按优先级依次匹配，同优先级且均匹配成功的命令同时返回
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

    def match(self, msg):
        for pattern, handler in self._commands:
            match = re.match(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None

class FsmRouter:
    pass

class PriorityRouter:
    pass
