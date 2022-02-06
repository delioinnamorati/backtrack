"""backtrack.device.arista.device"""
from scrapli.exceptions import ScrapliCommandFailure, ScrapliConnectionNotOpened, ScrapliTimeout

from backtrack.device.base.device import Device
from backtrack.exceptions import BacktrackInvalidInput
from backtrack.results import OperationResult, OperationStatus


class AristaDevice(Device):
    def __init__(
        self,
        host: str,
        auth_username: str,
        auth_password: str,
        auth_strict_key: bool,
        platform: str,
        vendor: str = "Arista",
    ):
        super().__init__(
            host=host,
            auth_username=auth_username,
            vendor=vendor,
            auth_password=auth_password,
            auth_strict_key=auth_strict_key,
            platform=platform,
        )

    async def get_backup(self) -> OperationResult:
        operation = OperationResult(name="get_backup()")
        try:
            self.logger.info(f"Fetching running configuration from {self.hostname}")
            result = await self.ssh_conn.send_command("show running-config")
            """
            result = await self.netconf_conn.get_config(source="running")
            """
            if "% Invalid input" in result.result:
                self.logger.warning(
                    f"Tried fetching running configuration but the command provided is wrong!"
                )
                raise BacktrackInvalidInput()
            self.backup = result.result
            operation.record(
                status=OperationStatus.COMPLETE,
                status_reason="Bacup fetched successfully",
            )
            self.logger.info(f"Successfully fetched running configuration from {self.hostname}")
        except BacktrackInvalidInput as exc:
            operation.record(
                status=OperationStatus.FAILED,
                status_reason="Invalid input received from device",
                exc=exc,
            )
        except ScrapliCommandFailure as exc:
            operation.record(status=OperationStatus.FAILED, status_reason="Bad command", exc=exc)
        except ScrapliConnectionNotOpened as exc:
            self.logger.warning(
                f"Trying to operate on a transport when connection was not opened for {self.hostname}"
            )
            operation.record(
                status=OperationStatus.FAILED,
                status_reason="Trying to operate on transport when not openned connection",
                exc=exc,
            )
        except ScrapliTimeout as exc:
            self.logger.warning(
                f"Timeout encountered when fetching running configuration for {self.hostname}"
            )
            operation.record(
                status=OperationStatus.FAILED,
                status_reason="Session timed out",
                exc=exc,
            )
        finally:
            await self.ssh_conn.close()
            return operation

    async def update_backup():
        pass
