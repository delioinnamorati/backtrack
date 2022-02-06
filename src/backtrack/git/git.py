import subprocess
import time
from datetime import datetime
from logging import LoggerAdapter, getLogger
from pathlib import Path


class Git:
    def __init__(self):
        self.path = Path("/home/delio/backups")
        _logger = getLogger("backtrack.git")
        self.logger = LoggerAdapter(_logger, extra={"host": "-", "vendor": "-"})

    # verify that repository actually exists and git is setup!

    def update_repository(self) -> None:
        self.logger.info("Updating git repository")
        self._add()
        time.sleep(2)
        self._commit()
        time.sleep(2)
        self._push()

    def _add(self) -> None:
        self.logger.info("Adding to the local repository")
        subprocess.run(["git", "add", "."], cwd=self.path)

    def _commit(self) -> None:
        self.logger.info("Committing")
        today = datetime.utcnow()
        today = today.strftime("%Y:%m:%d %H:%M:%S")
        message = f"{today} - Routine repository update!"
        subprocess.run(["git", "commit", "-m", f"{message}"], cwd=self.path)

    def _push(self) -> None:
        self.logger.info("Pushing")
        subprocess.run(["git", "push"], cwd=self.path)
