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
from enum import Enum

from . import STRING_ROW


class UniqueRouter:
    def __init__(self) -> None:
        self._forward = {}

    def route(self, route_id: str, pattern: str):
        def decorator(handler):
            rule = {
                "pattern": re.compile(pattern),
                "handler": handler,
            }
            self._forward[route_id] = rule
            return handler

        return decorator

    def search(self, msg: str):
        forward = []
        for route_id, rule in self._forward.items():
            match = re.search(rule["pattern"], msg)
            if match:
                forward.append((route_id, rule["handler"], match.groups()))
        return forward

    def remove(self, route_id: str):
        if route_id in self._forward:
            del self._forward[route_id]
            return True
        return False


class SearchMode(Enum):
    ANY = "any"  # 任一满足
    EXACT = "exact"  # 一致性
    ALL = "all"  # 全部满足


class FsmRouter:
    def __init__(self, states: STRING_ROW):
        self._forward = []
        self._states = {state: [] for state in states}

    SearchMode = SearchMode

    def route(self, states: str | STRING_ROW, pattern: str):
        if type(states) == str:
            states = (states,)
        if any(state not in self._states for state in states):
            raise ValueError("状态路由器录入命令的状态非法。")

        def decorator(handler):
            rule = {
                "states": set(states),
                "pattern": pattern,
                "handler": handler,
            }
            self._forward.append(rule)
            forward_id = len(self._forward) - 1
            for state in states:
                self._states[state].append(forward_id)
            return handler

        return decorator

    def search(
        self,
        states: str | STRING_ROW,
        msg: str,
        search_mode: SearchMode = SearchMode.ANY,
    ):
        if type(states) == str:
            states = (states,)
        states = set(states)
        forward = []
        target_rules = set()
        for state in states:
            if state in self._states:
                target_rules.update(self._states[state])
        for rule_id in target_rules:
            rule = self._forward[rule_id]
            match_state = False
            if search_mode == SearchMode.ANY:
                # 任一状态匹配：规则状态与当前状态有交集
                match_state = bool(rule["states"] & states)
            elif search_mode == SearchMode.EXACT:
                # 完全匹配：规则状态与当前状态完全一致
                match_state = rule["states"] == states
            elif search_mode == SearchMode.ALL:
                # 全部匹配：规则包含所有当前状态
                match_state = states.issubset(rule["states"])
            if match_state:
                result = re.search(rule["pattern"], msg)
                if result:
                    forward.append((rule["handler"], result.groups()))
        return forward


class PriorityRouter:
    """
    按优先级依次匹配
    """

    def __init__(self) -> None:
        self._forward = []

    def route(self, priority: int, pattern: str):
        def decorator(handler):
            self._forward.append((-priority, re.compile(pattern), handler))
            self._forward.sort()
            return handler

        return decorator

    def search(self, msg: str):
        for _, pattern, handler in self._forward:
            match = re.search(pattern, msg)
            if match:
                return handler, match.groups()
        return None, None
