"""TickrakeClient — facade over all dataset sub-clients."""

from __future__ import annotations

from tickrake_client.candles import CandlesClient
from tickrake_client.config import TickrakeConfig
from tickrake_client.level_one import LevelOneClient
from tickrake_client.options.archive import ArchiveClient
from tickrake_client.options.filesystem import FilesystemClient
from tickrake_client.options.intraday import IntradayClient
from tickrake_client.order_book import OrderBookClient


class TickrakeClient:
    def __init__(self, cfg: TickrakeConfig | None = None) -> None:
        _cfg = cfg or TickrakeConfig.from_env()
        self.options_intraday = IntradayClient(_cfg)
        self.options_archive = ArchiveClient(_cfg)
        self.options_filesystem = FilesystemClient(_cfg)
        self.candles = CandlesClient(_cfg)
        self.level_one = LevelOneClient(_cfg)
        self.order_book = OrderBookClient(_cfg)
