"""backtrack.storage.base.storage"""

from abc import ABC, abstractmethod


class Storage(ABC):
    def __init__(self, hostname):
        self.hostname = hostname

    @abstractmethod
    async def create_storage():
        """Create storage for backup"""
        pass

    @abstractmethod
    def verify_storage():
        """Verify if storage is created"""
        pass

    @abstractmethod
    def validate_storage():
        """Validate the name of the storage"""
        pass
