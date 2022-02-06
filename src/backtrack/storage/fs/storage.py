"""backtrack.storage.fs.storage"""

from logging import LoggerAdapter, getLogger

import aiofiles
from aiopath import AsyncPath

from backtrack.results import OperationResult, OperationStatus
from backtrack.storage.base.storage import Storage

WORKDIR = "/home/delio/backups"


class FileSystemStorage:
    def __init__(self, hostname: str):
        self.hostname = hostname
        _logger = getLogger("backtrack.fs")
        self.logger = LoggerAdapter(_logger, extra={"host": self.hostname, "vendor": "Arista"})
        self.dir_path = AsyncPath(f"{WORKDIR}/{self.hostname}")
        self.file_path = AsyncPath(f"{WORKDIR}/{self.hostname}/{self.hostname}.txt")

    def __repr__(self) -> str:
        return f"<FileSystemStorage object for {self.file_path}"

    async def write_storage(self, backup: str):
        operation = OperationResult(name="write_storage()")
        try:
            self.logger.info(f"Trying to write backup on local storage for {self.hostname}")
            async with aiofiles.open(self.file_path, mode="w") as f:
                await f.write(backup.backup)
            operation.record(status=OperationStatus.COMPLETE, status_reason="Wrote backup complete")
            self.logger.info(f"Backup successfully done for {self.hostname}")
        except FileNotFoundError as exc:
            operation.record(status=OperationStatus.FAILED, status_reason="FIle not found", exc=exc)
            self.logger.warning(f"File path for {self.hostname} does not exist")
        finally:
            return operation

    async def setup_storage(self) -> OperationResult:
        self.logger.info(f"Setting up the local storage for {self.hostname}")
        operation = OperationResult(name="setup_storage()")
        await self._verify_directory()
        await self._verify_file()
        operation.record(
            status=OperationStatus.COMPLETE,
            status_reason="Successfully created environment",
        )
        self.logger.info(f"Successfully setup local storage for {self.hostname}")
        return operation

    async def _create_directory(self) -> None:
        self.logger.info(f"Creating directory for {self.hostname}")
        await self.dir_path.mkdir()

    async def _create_file(self) -> None:
        self.logger.info(f"Creating file for {self.hostname}")
        await self.file_path.touch(exist_ok=True)

    async def _verify_directory(self) -> None:
        if await self.dir_path.is_dir():
            pass
        else:
            await self._create_directory()

    async def _verify_file(self) -> None:
        if await self.file_path.is_file():
            return
        else:
            await self._create_file()
