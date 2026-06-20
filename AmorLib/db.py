# -*- encoding: utf-8 -*-
"""
@File      :    AmorLib/db.py
@Author    :    LianQingYu-Love恋倾雨
@Contact   :    xinghu2408@foxmail.com
@License   :    AGPLv3
@Copyright :    (C) 2026 AmorLib
@Desc      :    sqlite3 数据库操作工具包，该模块提供了一些简易使用 SQLite 数据库的方法。
"""

import sqlite3
from typing import Any, Union, Type
from . import STRING_ROW

DB_PATH = "plugin/data/AmorLib.db"


class DataBase:
    # region with
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self.db: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def __enter__(self):
        try:
            self.db = sqlite3.connect(self.db_path)
            self.db.row_factory = sqlite3.Row
            self.cursor = self.db.cursor()
            return self
        except sqlite3.Error as e:
            raise ConnectionError(f"数据库连接失败：{str(e)}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            try:
                if exc_type is not None:
                    # 执行失败，发动事务回滚
                    self.db.rollback()
                    print(f"数据库操作回滚: \n{str(exc_val)}")
                else:
                    self.db.commit()
            except Exception as e:
                print(f"数据库事务处理失败：{str(e)}")
            finally:
                if self.cursor:
                    self.cursor.close()
                if self.db:
                    self.db.close()
        return False

    # endregion
    def execute(self, sql: str, *params: Any) -> list[sqlite3.Row]:
        if not self.db or not self.cursor:
            raise RuntimeError("数据库连接未建立，请在 'with' 语句块中使用。")
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall() if self.cursor.description else []
        except sqlite3.Error as e:
            raise RuntimeError(f"SQL语句执行失败|{sql}\n {str(e)}") from e

    # region execute
    def select(
        self,
        table: str,
        rows: str | STRING_ROW | None = None,
        where: str | None = None,
        *where_params: Any,
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[sqlite3.Row]:
        """查询数据
        Args:
            table (str): 表名
            rows (str | list | tuple | None, optional): 要查询的列. Defaults to None.
            where (str | None, optional): WHERE条件语句. Defaults to None.
            *where_params (Any): WHERE条件参数
            order (str | None, optional): 排序模式. Defaults to None.
            limit (int | None, optional): 界限. Defaults to None.
            offset (int | None, optional): 偏差. Defaults to None.
        Returns:
            list[sqlite3.Row] | None: 查询到的数据
        """
        assert self.cursor is not None
        sql = f"SELECT {rows if type(rows)== str else ', '.join(rows) if rows else '*'} FROM {table}"
        if where:
            sql += f" WHERE {where}"
        if order and isinstance(order, str) and order.strip():
            sql += f" ORDER BY {order.strip()}"
        if limit:
            sql += f" LIMIT {limit}"
            if offset:
                sql += f" OFFSET {offset}"
        try:
            return self.execute(sql, *where_params)
        except RuntimeError as e:
            raise RuntimeError(f"[SELECT]数据查询失败| {str(e)}") from None

    def insert(self, table: str, data: dict[str, Any]) -> int | None:
        """插入数据
        Args:
            table (str): 表名
            data (dict[str, Any]): 插入的数据，键为列名，值为数据
        Returns:
            int | None: 最后插入行的rowid
        """
        assert self.cursor is not None
        sql = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['?'] * len(data))})"
        params = tuple(data.values())
        try:
            self.execute(sql, *params)
            return self.cursor.lastrowid
        except RuntimeError as e:
            raise RuntimeError(f"[INSERT]数据插入失败| {str(e)}") from None

    def update(
        self,
        table: str,
        data: dict[str, Any],
        where: str,
        *where_params: Any,
        increment: STRING_ROW | None = None,
    ) -> int:
        """更新数据
        Args:
            table (str): 表名
            data (dict[str, Any]): 更新的数据字，键为列名，值为数据
            where (str): WHERE条件语句
            *where_params (Any): WHERE条件参数
            increment (str | list | tuple | None, optional): 需要累加更新的列名 Defaults to None.
        Returns:
            int: 影响行数
        """
        assert self.cursor is not None
        inc_cols = set(increment) if increment else set()
        set_clause_parts = []
        for col_name in data.keys():
            if col_name in inc_cols:
                set_clause_parts.append(f"{col_name} = {col_name} + ?")
            else:
                set_clause_parts.append(f"{col_name} = ?")
        set_clause = ", ".join(set_clause_parts)
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + where_params
        try:
            self.execute(sql, *params)
            return self.cursor.rowcount
        except RuntimeError as e:
            raise RuntimeError(f"[UPDATE]数据更新失败| {str(e)}") from None

    def delete(
        self,
        table: str,
        where: str,
        *where_params: Any,
    ) -> int:
        """删除数据
        Args:
            table (str): 表名
            where (str): WHERE条件语句
            *where_params (Any): WHERE条件参数
        Returns:
            int: 删除的行数
        """
        assert self.cursor is not None
        sql = f"DELETE FROM {table} WHERE {where}"
        try:
            self.execute(sql, *where_params)
            return self.cursor.rowcount
        except RuntimeError as e:
            raise RuntimeError(f"[DELETE]数据删除失败| {str(e)}") from None

    def truncate(self, table: str) -> None:
        """清空表
        Args:
            table (str): 表名
        """
        assert self.cursor is not None
        sql = f"DELETE FROM {table}"
        try:
            self.execute(sql)
        except RuntimeError as e:
            raise RuntimeError(f"[DELETE]清空表失败| {str(e)}") from None

    def drop(self, table: str) -> None:
        """删除表
        Args:
            table (str): 表名
        """
        assert self.cursor is not None
        sql = f"DROP TABLE IF EXISTS {table}"
        try:
            self.execute(sql)
        except RuntimeError as e:
            raise RuntimeError(f"[DROP]删除表失败| {str(e)}") from None

    def create(
        self,
        table: str,
        columns: dict[str, Union[Type[int], Type[float], Type[str], Type[dict], str]],
        primary_key: str | STRING_ROW | None = None,
        foreign_keys: dict[str, dict[str, str]] | None = None,
        unique_constraints: (
            STRING_ROW | list[STRING_ROW] | tuple[STRING_ROW, ...] | None
        ) = None,
        auto_increment: bool = False,
    ) -> None:
        """创建表
        Args:
            table (str): 表名
            columns (dict[str, Union[Type[int], Type[float], Type[str], Type[dict], str]]): 列定义，键为列名，值为数据类型或完整的列定义
                - int: "INTEGER",
                - float: "REAL",
                - str: "TEXT",
                - dict: "JSON",
                - "NOW": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                - 直接使用SQL类型字符串
            primary_key (str | list[str] | tuple[str, ...] | None): 主键列名. Defaults to None.
            foreign_keys (dict[str, dict[str, str]] | None): 外键定义，格式为 {列名: {参考表: 参考列}}. Defaults to None.
            unique_constraints (list[str] | tuple[str, ...] | list[list[str] | tuple[str, ...]] | tuple[list[str] | tuple[str, ...], ...] | None): 唯一约束，可以是单列列表或多列组合列表. Defaults to None.
            auto_increment (bool): 主键是否自增（仅适用于单列整数主键）. Defaults to False.
        """
        assert self.cursor is not None
        # region create
        # 构建列定义
        type_mapping = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            dict: "JSON",
            "NOW": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }
        column_defs = []
        for column_name, column_type in columns.items():
            if column_type not in type_mapping.keys() and type(column_type) != str:
                raise RuntimeError(
                    f"[CREATE]创建表失败: columns类型定义错误, 仅允许<class 'int'>、<class 'float'>、 <class 'str'>、 <class 'dict'>、 str类型| key: '{column_name}' is {column_type}"
                ) from None
            if column_type in type_mapping:
                # 使用映射的数据类型
                column_type = type_mapping[column_type]
            column_def = f"{column_name} {column_type}"

            # 如果是自增主键列，添加 AUTOINCREMENT
            if (
                auto_increment
                and primary_key
                and type(primary_key) == str
                and column_name == primary_key
                and column_type.upper() == "INTEGER"
            ):
                column_def += " PRIMARY KEY AUTOINCREMENT"
                primary_key = None

            column_defs.append(column_def)

        # 添加主键约束
        if primary_key:
            if type(primary_key) != str:
                pk_columns = ", ".join(primary_key)  # 复合主键
            else:
                pk_columns = primary_key  # 单主键
            column_defs.append(f"PRIMARY KEY ({pk_columns})")

        # 添加外键约束
        if foreign_keys:
            for column_name, ref in foreign_keys.items():
                ref_table = list(ref.keys())[0]
                column_defs.append(
                    f"FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref[ref_table]})"
                )

        # 添加唯一约束
        if unique_constraints:
            for constraint in unique_constraints:
                if type(constraint) != str:
                    column_defs.append(
                        f"UNIQUE ({', '.join(constraint)})"
                    )  # 复合唯一约束
                else:
                    column_defs.append(f"UNIQUE ({constraint})")  # 单列唯一约束
        # endregion
        # 构建完整的CREATE TABLE语句
        sql = f"CREATE TABLE IF NOT EXISTS {table} (\n    {', '.join(column_defs)}\n)"
        try:
            self.execute(sql)
        except RuntimeError as e:
            raise RuntimeError(f"[CREATE]创建表失败| {str(e)}") from None

    def get_schema(self, table: str) -> dict[str, Any] | None:
        """获取表的结构
        Args:
            table (str): 表名
        Returns:
            dict[str, Any] | None: 表的结构
        """
        assert self.cursor is not None
        try:
            # region get schema
            # 检查表是否存在
            self.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
            )
            if not self.cursor.fetchone():
                return None

            schema = {
                "table_name": table,
                "columns": [],
                "primary_key": [],
                "foreign_keys": [],
                "unique_constraints": [],
            }

            # 获取列信息
            self.execute(f"PRAGMA table_info({table})")
            columns = self.cursor.fetchall()
            for col in columns:
                column_info = {
                    "name": col["name"],
                    "type": col["type"],
                    "not_null": bool(col["notnull"]),
                    "default_value": col["dflt_value"],
                    "pk": bool(col["pk"]),
                    "constraints": "",
                }

                # 构建约束字符串
                constraints = []
                if col["notnull"]:
                    constraints.append("NOT NULL")
                if col["pk"]:
                    constraints.append("PRIMARY KEY")
                if col["dflt_value"] is not None:
                    constraints.append(f"DEFAULT {col['dflt_value']}")

                column_info["constraints"] = " ".join(constraints)
                schema["columns"].append(column_info)

                # 记录主键列
                if col["pk"]:
                    schema["primary_key"].append(col["name"])

            # 获取外键信息
            self.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = self.cursor.fetchall()
            for fk in foreign_keys:
                fk_info = {
                    "from_column": fk["from"],
                    "to_table": fk["table"],
                    "to_column": fk["to"],
                    "on_update": fk["on_update"],
                    "on_delete": fk["on_delete"],
                }
                schema["foreign_keys"].append(fk_info)

            # 获取索引信息（用于识别唯一约束）
            self.execute(f"PRAGMA index_list({table})")
            indexes = self.cursor.fetchall()
            for idx in indexes:
                if idx["unique"]:
                    # 获取索引列
                    self.execute(f"PRAGMA index_info({idx['name']})")
                    index_cols = self.cursor.fetchall()
                    unique_cols = [col["name"] for col in index_cols]

                    # 排除主键的唯一约束
                    if set(unique_cols) != set(schema["primary_key"]):
                        schema["unique_constraints"].append(unique_cols)
            # endregion
            return schema
        except RuntimeError as e:
            raise RuntimeError(f"[PRAGMA]获取表结构失败| {str(e)}") from None

    # endregion


def execute(db_path: str, sql: str, *params: Any) -> list[sqlite3.Row] | None:
    with DataBase(db_path) as db:
        return db.execute(sql, *params)
