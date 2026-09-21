"""TickrakeClient — facade over all dataset sub-clients."""

from __future__ import annotations

import warnings

import duckdb

from tractatus.tickrake.candles import CandlesClient
from tractatus.tickrake.config import TickrakeConfig
from tractatus.tickrake.level_one import LevelOneClient
from tractatus.tickrake.options.archive import ArchiveClient
from tractatus.tickrake.options.filesystem import FilesystemClient
from tractatus.tickrake.options.intraday import IntradayClient
from tractatus.tickrake.options.queries import OptionsQueryClient
from tractatus.tickrake.order_book import OrderBookClient


class TickrakeClient:
    def __init__(
        self,
        cfg: TickrakeConfig | None = None,
        query_conn: duckdb.DuckDBPyConnection | None = None,
    ) -> None:
        _cfg = cfg or TickrakeConfig.from_env()
        self._options_intraday = IntradayClient(_cfg)
        self.options_archive = ArchiveClient(_cfg)
        self.options_filesystem = FilesystemClient(_cfg)
        self.options_query = OptionsQueryClient(query_conn)
        self.candles = CandlesClient(_cfg)
        self.level_one = LevelOneClient(_cfg)
        self.order_book = OrderBookClient(_cfg)

    @property
    def options_intraday(self) -> IntradayClient:
        warnings.warn(
            "TickrakeClient.options_intraday is deprecated and will be removed in a future release. "
            "Move MinIO/intraday access into your application layer.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._options_intraday
