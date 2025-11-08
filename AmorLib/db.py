from typing import Any, Union, Type
import sqlite3
from . import DB_PATH


class DataBase:
    def __init__(self, db: str = DB_PATH) -> None:
        self.db_path = db
        self.db: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def __enter__(self):
        try:
            self.db = sqlite3.connect(self.db_path)
            self.db.row_factory = sqlite3.Row
            self.cursor = self.db.cursor()
            return self
        except sqlite3.Error as e:
            print(f"数据库连接失败: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            try:
                if exc_type is not None:
                    # 执行失败，发动事务回滚
                    self.db.rollback()
                    print(f"数据库操作失败: {exc_val}")
                else:
                    self.db.commit()
            except Exception as e:
                print(f"数据库操作失败: {e}")
            finally:
                if self.cursor:
                    self.cursor.close()
                self.db.close()
        return False

    def execute(self, sql: str, *params: Any) -> list[sqlite3.Row] | None:
        if not self.db or not self.cursor:
            raise RuntimeError("数据库连接未建立，请在 'with' 语句块中使用。")
        try:
            self.cursor.execute(sql, params)
            if self.cursor.description:
                return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"数据库操作失败: {e}") from e

    def insert(self, table: str, data: dict[str, Any]) -> int | None:
        """插入数据并返回最后插入的rowid

        Args:
            table (str): 要插入数据的表名
            data (dict[str, Any]): 要插入的数据字典，键为列名，值为对应的数据

        Returns:
            int | None: 返回最后插入行的rowid

        Example:
            >>> with DataBase() as db:
            >>>     # 插入一条用户记录
            >>>     new_id = db.insert("users", {
            >>>         "username": "alice",
            >>>         "email": "alice@example.com",
            >>>         "age": 25,
            >>>         "created_at": "2023-01-01 10:00:00"
            >>>     })
            >>>     print(f"新用户的ID是: {new_id}")
        """
        assert self.cursor is not None
        sql = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['?'] * len(data))})"
        self.execute(sql, tuple(data.values()))
        return self.cursor.lastrowid

    def update(
        self,
        table: str,
        data: dict[str, Any],
        where: str,
        *where_params: Any,
    ) -> int:
        """更新数据

        Args:
            table (str): 表名
            data (dict[str, Any]): 要更新的数据字典，键为列名，值为对应的数据
            where (str): WHERE条件语句
            *where_params (Any): WHERE条件参数

        Returns:
            int: 影响的行数

        Example:
            >>> with DataBase() as db:
            >>>     # 更新用户名为Alice的记录的年龄
            >>>     count = db.update(
            >>>         "users",
            >>>         {"age": 25},
            >>>         "username = ?",
            >>>         "Alice"
            >>>     )
            >>>     print(f"更新了 {count} 条记录")
        """
        assert self.cursor is not None
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + where_params
        self.execute(sql, *params)
        return self.cursor.rowcount

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

        Example:
            >>> with DataBase() as db:
            >>>     # 删除所有age大于30的记录
            >>>     count = db.delete("users", "age > ?", 30)
            >>>     print(f"删除了 {count} 条记录")

            >>>     # 删除指定用户名的记录
            >>>     count = db.delete("users", "username = ?", "Alice")
            >>>     print(f"删除了 {count} 条记录")

            >>>     # 删除满足多个条件的记录
            >>>     count = db.delete("users", "age > ? AND status = ?", 30, "inactive")
            >>>     print(f"删除了 {count} 条记录")
        """
        assert self.cursor is not None
        sql = f"DELETE FROM {table} WHERE {where}"
        self.execute(sql, *where_params)
        return self.cursor.rowcount

    def truncate_table(self, table: str) -> bool:
        """清空表

        Args:
            table (str): 要清空的表名

        Returns:
            bool: 是否成功清空
        """
        assert self.cursor is not None
        try:
            sql = f"DELETE FROM {table}"
            self.execute(sql)
            return True
        except sqlite3.Error as e:
            print(f"数据库清空表失败: {e}")
            return False

    def drop_table(self, table: str) -> bool:
        """删除表

        Args:
            table (str): 要删除的表名

        Returns:
            bool: 是否成功删除
        """
        assert self.cursor is not None
        try:
            sql = f"DROP TABLE IF EXISTS {table}"
            self.execute(sql)
            return True
        except sqlite3.Error as e:
            print(f"数据库删除表失败: {e}")
            return False

    def create_table(
        self,
        table: str,
        columns: dict[str, Union[Type, str]],
        primary_key: str | list[str] | None = None,
        foreign_keys: dict[str, dict[str, str]] | None = None,
        unique_constraints: list[str] | list[list[str]] | None = None,
        auto_increment: bool = False,
    ) -> bool:
        """创建表

        Args:
            table (str): 表名
            columns (dict[str, Union[Type, str]]): 列定义字典，键为列名，值为数据类型或完整的列定义字符串
                    支持的数据类型: int, str, float, bool, 或直接使用SQL类型字符串
            primary_key (str | list[str] | None): 主键列名或列名列表. Defaults to None.
            foreign_keys (dict[str, dict[str, str]] | None): 外键定义字典，格式为 {列名: {参考表: 参考列}}. Defaults to None.
            unique_constraints (list[str] | list[list[str]] | None): 唯一约束，可以是单列列表或多列组合列表. Defaults to None.
            auto_increment (bool): 是否为主键启用自增（仅适用于单列整数主键）. Defaults to False.

        Returns:
            bool: 是否成功创建

        Example:
            >>> with DataBase() as db:
            >>>     # 简单创建表
            >>>     db.create_table("users", {
            >>>         "user_id": int,
            >>>         "name": str,
            >>>         "age": int,
            >>>         "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            >>>     }, primary_key="user_id")
            >>>
            >>>     # 创建带外键和唯一约束的表
            >>>     db.create_table("orders", {
            >>>         "order_id": int,
            >>>         "user_id": int,
            >>>         "product": str,
            >>>         "amount": float
            >>>     },
            >>>     primary_key="order_id",
            >>>     foreign_keys={
            >>>         "user_id": {"users": "user_id"}
            >>>     },
            >>>     unique_constraints=[["user_id", "product"]])
        """
        assert self.cursor is not None

        # 数据类型映射
        type_mapping = {int: "INTEGER", str: "TEXT", float: "REAL", bool: "INTEGER"}
        for column_name, column_type in columns.items():
            if column_type in type_mapping:
                # 使用映射的数据类型
                columns[column_name] = type_mapping[column_type]
            else:
                # 直接使用字符串定义
                columns[column_name] = column_type
        try:
            # 构建列定义
            column = []
            for column_name, column_type in columns.items():
                column_def = f"{column_name} {column_type}"
                # 如果是自增主键列，添加 AUTOINCREMENT
                if (
                    auto_increment
                    and primary_key
                    and isinstance(primary_key, str)
                    and column_name == primary_key
                    and column_type.upper() == "INTEGER"
                ):
                    column_def += " AUTOINCREMENT"
                column.append(column_def)

            # 添加主键约束
            if primary_key:
                if isinstance(primary_key, list):
                    pk_columns = ", ".join(primary_key)  # 复合主键
                else:
                    pk_columns = primary_key  # 单主键
                column.append(f"PRIMARY KEY ({pk_columns})")

            # 添加外键约束
            if foreign_keys:
                for column_name, ref in foreign_keys.items():
                    ref_table = list(ref.keys())[0]
                    column.append(
                        f"FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref[ref_table]})"
                    )

            # 添加唯一约束
            if unique_constraints:
                for constraint in unique_constraints:
                    if isinstance(constraint, list):
                        column.append(
                            f"UNIQUE ({", ".join(constraint)})"
                        )  # 复合唯一约束
                    else:
                        column.append(f"UNIQUE ({constraint})")  # 单列唯一约束

            # 构建完整的CREATE TABLE语句
            sql = (
                f"CREATE TABLE IF NOT EXISTS {table} (\n    {",\n    ".join(column)}\n)"
            )
            self.execute(sql)
            return True
        except sqlite3.Error as e:
            print(f"数据库创建表失败: {e}")
            return False
