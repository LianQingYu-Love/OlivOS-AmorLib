from typing import Tuple, List, Dict, Any
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

    def execute(self, sql: str, params: Tuple[Any, ...] | None = None) -> List[sqlite3.Row] | None:
        if not self.db or not self.cursor:
            raise RuntimeError("数据库连接未建立，请在 'with' 语句块中使用。")
        try:
            self.cursor.execute(sql, params or ())
            if self.cursor.description:
                return self.cursor.fetchall()
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"数据库操作失败: {e}") from e

    def fetch(
        self, sql: str, params: Tuple[Any, ...] | None = None
    ) -> List[sqlite3.Row]:
        """执行查询并返回所有结果"""
        return self.execute(sql, params) or []

    def insert(self, table: str, data: dict) -> int | None:
        """插入数据并返回最后插入的rowid"""
        assert self.cursor is not None
        sql = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['?'] * len(data))})"
        self.execute(sql, tuple(data.values()))
        return self.cursor.lastrowid

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Tuple[Any, ...] = (),
    ) -> int:
        """更新数据并返回影响的行数"""
        assert self.cursor is not None
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + where_params
        self.execute(sql, params)
        return self.cursor.rowcount
