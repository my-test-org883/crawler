"""Database related fixtures."""

from asyncio import iscoroutine
from collections.abc import Awaitable
from typing import Any

import sqlalchemy as sqla
from boostsec.common.testing.docker import (
    DockerService,
)
from boostsec.database.target import MysqlTarget
from sqlalchemy import Connection, CursorResult, Engine
from sqlalchemy.database.engine import (
    AsyncEngine,
    create_engine,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class Database(DockerService):
    """Running Database representation."""

    target: MysqlTarget
    internal_target: MysqlTarget

    async def drop_database(self) -> None:
        """Drop existing database."""
        async with create_engine(self.target.sqlalchemy_url) as engine:
            async with engine.begin() as conn:
                result = self._drop_db(engine, conn)
                assert iscoroutine(result)  # noqa: S101 use of assert # Typeguard
                await result

    def _drop_db(
        self,
        engine: AsyncEngine | Engine,
        connection: AsyncConnection | Connection,
    ) -> Awaitable[CursorResult[Any]] | CursorResult[Any]:
        quoted_database = engine.dialect.identifier_preparer.quote(self.target.database)
        return connection.execute(
            sqla.text(f"DROP DATABASE IF EXISTS {quoted_database}")
        )
