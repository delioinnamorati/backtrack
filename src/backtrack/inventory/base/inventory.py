"""backtrack.inventory.base.inventory"""
from abc import ABC, abstractmethod
from logging import LoggerAdapter, getLogger

WORKDIR = "/home/delio/backtrack/backtrack/devs.json"


class Inventory(ABC):
    def __init__(self, destination):
        _logger = getLogger("backtrack.inventory")
        self.logger = LoggerAdapter(_logger, extra={"host": "-", "vendor": "-"})
        self.destination = destination

    @abstractmethod
    async def update_cache():
        pass

    @abstractmethod
    async def get_inventory():
        pass

    @abstractmethod
    async def trigger_backup():
        pass
