"""backtrack.device.base.device"""
from abc import ABC, abstractmethod
from logging import LoggerAdapter, getLogger
from typing import Any, Coroutine, List

from scrapli import AsyncScrapli
from scrapli.exceptions import ScrapliAuthenticationFailed
from scrapli_netconf import AsyncNetconfDriver

from backtrack.results import OperationResult, OperationStatus
from backtrack.storage.base.storage import Storage
from backtrack.storage.fs.storage import FileSystemStorage


class Device(ABC):
    def __init__(
        self,
        host: str,
        vendor: str,
        auth_username: str,
        auth_password: str,
        auth_strict_key: bool,
        platform: str,
    ):
        self.hostname = host
        self.auth_username = auth_username
        self.vendor = vendor
        self.auth_password = auth_password
        self.auth_strict_key = auth_strict_key
        self.platform = platform
        self.ssh_conn = AsyncScrapli(
            host=self.hostname,
            port=22,
            auth_strict_key=self.auth_strict_key,
            ssh_config_file=True,
            auth_username=self.auth_username,
            auth_password=self.auth_password,
            platform=self.platform,
            transport="asyncssh",
        )
        self.netconf_conn = AsyncNetconfDriver(
            host=self.hostname,
            port=830,
            auth_strict_key=self.auth_strict_key,
            auth_username=self.auth_username,
            auth_password=self.auth_password,
            strip_namespaces=True,
            transport="asyncssh",
        )
        self.repository: Storage = FileSystemStorage(hostname=self.hostname)
        self.backup: str = ""
        self.results: List = [OperationResult]
        _logger = getLogger("backtrack.device")
        self.logger = LoggerAdapter(_logger, extra={"host": self.hostname, "vendor": self.vendor})

    def __repr__(self) -> str:
        return f"<{self.ssh_conn}>"

    def __hash__(self) -> int:
        return hash(self.hostname)

    def __eq__(self, other) -> bool:
        return self.hostname == other.hostname

    async def operation_handler(self) -> List[OperationResult]:
        self.coros: List[Coroutine[Any, Any, Any]] = [
            self.connect(),
            self.get_backup(),
            self.repository.setup_storage(),
            self.repository.write_storage(self),
        ]
        for index, coro in enumerate(self.coros):
            result = await coro
            self.results.append(result)
            if result.status == OperationStatus.FAILED:
                self.logger.warning(
                    f"Operation {coro} failed for {self.hostname}, proceeding to gracefully shut subsequent coroutines."
                )
                for _coro in self.coros[index:]:
                    self.logger.debug(f"Closing {_coro}")
                    _coro.close()
                break

        return self.results

    async def connect(self) -> OperationResult:
        operation = OperationResult(name="connect()")
        try:
            self.logger.info(f"Connecting to {self.hostname}")
            await self.ssh_conn.open()
            operation.record(
                status=OperationStatus.COMPLETE, status_reason="Connected successfully"
            )
            self.logger.info(f"Successfully connected to {self.hostname}")
        except ScrapliAuthenticationFailed as exc:
            operation.record(
                status=OperationStatus.FAILED,
                status_reason=f"Authentication to {self.hostname} failed!",
                exc=exc,
            )
            self.logger.warning(f"Authentication failed for {self.hostname}")
        except OSError as exc:
            operation.record(
                status=OperationStatus.FAILED,
                status_reason=f"Could not establish a connection",
                exc=exc,
            )
            self.logger.warning(f"Could not establish a connection to {self.hostname}")
        finally:
            return operation

    @abstractmethod
    async def get_backup(self) -> str:
        """Get the backup configuration of target device"""
        pass

    @abstractmethod
    async def update_backup(self) -> None:
        """Update backup configuration of a target device"""
        pass
