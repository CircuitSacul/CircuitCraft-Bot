from sqlite3.dbapi2 import Row
from typing import Any, Iterable, Tuple
import aiosqlite
import asyncio


class Database:
    def __init__(self):
        self.con: aiosqlite.Connection = None
        self.lock = asyncio.Lock()

    async def init(self):
        self.con = await aiosqlite.connect("db.sqlite3")
        self.con.row_factory = aiosqlite.Row
        await self._create_tables()

    async def close(self):
        async with self.lock:
            await self.con.close()

    async def _create_tables(self):
        users_table = """CREATE TABLE IF NOT EXISTS users (
            id NUMERIC PRIMARY KEY,
            mc_username TEXT DEFAULT NULL
        )"""

        await self.execute(users_table)

    async def fetch(self, sql: str, args: Tuple[Any] = ()) -> Iterable[Row]:
        async with self.lock:
            cur = await self.con.execute(sql, args)
            rows = await cur.fetchall()
        return rows

    async def execute(self, sql: str, args: Tuple[Any] = ()):
        async with self.lock:
            await self.con.execute(sql, args)
            await self.con.commit()
