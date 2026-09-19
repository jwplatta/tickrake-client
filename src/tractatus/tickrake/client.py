"""TickrakeClient — facade over all dataset sub-clients."""

from __future__ import annotations

from tractatus.tickrake.candles import CandlesClient
from tractatus.tickrake.config import TickrakeConfig
from tractatus.tickrake.level_one import LevelOneClient
from tractatus.tickrake.options.archive import ArchiveClient
from tractatus.tickrake.options.filesystem import FilesystemClient
from tractatus.tickrake.options.intraday import IntradayClient
from tractatus.tickrake.order_book import OrderBookClient


class TickrakeClient:
    def __init__(self, cfg: TickrakeConfig | None = None) -> None:
        _cfg = cfg or TickrakeConfig.from_env()
        self.options_intraday = IntradayClient(_cfg)
        self.options_archive = ArchiveClient(_cfg)
        self.options_filesystem = FilesystemClient(_cfg)
        self.candles = CandlesClient(_cfg)
        self.level_one = LevelOneClient(_cfg)
        self.order_book = OrderBookClient(_cfg)
