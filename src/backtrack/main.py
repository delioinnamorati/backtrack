"""backtrack.main"""
import asyncio
import signal
from datetime import datetime
from logging import FileHandler, LoggerAdapter, getLogger

import aionotify
from git.git import Git

from backtrack.backtrack_logging import BacktrackFormatter
from backtrack.device.arista.device import AristaDevice


class Producer:
    def __init__(self, queue: asyncio.Queue, periodic: int = 0):
        self.periodic = periodic
        self.queue = queue

    async def producer(self, periodic: int = None) -> None:
        if periodic:
            print("Identified periodic run")
            while True:
                await asyncio.gather(*[self.add_to_queue(dev) for dev in devs])
                print("Sleeping until the next run...")
                await self.queue.put(None)
                await asyncio.sleep(25)
        else:
            print("Identified non periodic run")
            # added new device in file.. trigger backup!
            await asyncio.gather(*[self.add_to_queue(dev) for dev in devs])
            await queue.put(None)

    async def add_to_queue(self, dev):
        logger.debug(f"Adding {dev} to queue")
        devi = AristaDevice(**dev)
        await self.queue.put(devi)


class Scheduler:
    def __init__(self, periodic: int, queue: asyncio.Queue, loop: asyncio.BaseEventLoop = None):
        self.periodic = periodic
        self.producer = Producer(periodic=self.periodic, queue=queue)
        self.consumer = Consumer(queue=queue)
        self._next_run = 0

    @classmethod
    async def shutdown(self, loop, signal=None):
        """Cleanup tasks tied to the service's shutdown"""
        # logger.info(f"Rec exit signal {signal.name}")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError as error:
            logger.info(f"Normal cancelled error {error}")
        except Exception as exc:
            logger.error(f"Cancelling a task produced unexpected error {exc}")
        logger.info("Flushing metrics")
        loop.stop()


async def run(dev):
    # Here you would have some inventory discovery logic
    logger.info(f"Fetched the following inventory of devices: {dev}")
    # res = await asyncio.gather(*[dev.operation_handler() for dev in devices])
    await dev.operation_handler()
    # g = Git()
    # g.update_repository()


class Consumer:
    def __init__(self, queue):
        self.queue = queue

    async def consumer(self) -> None:
        while True:
            dev = await self.fetch_from_queue()
            if dev is None:
                print("Queue is empty")
                break
            logger.info(f"Consuming {dev}")
            asyncio.create_task(run(dev))

    async def fetch_from_queue(self):
        return await self.queue.get()


def handle_exception(loop, context):
    exc = context.get("exception", context["message"])
    logger.error(f"Caught exception: {exc}")
    logger.info("Shutting down...")
    asyncio.create_task(Scheduler.shutdown(loop=loop))


async def monitor_devs(loop, scheduler):
    await watcher.setup(loop)
    while True:
        event = await watcher.get_event()
        print(f"Received event... {event}")
        print("Triggering backup")
        await scheduler.producer.producer()


if __name__ == "__main__":
    backtrack_handler = FileHandler(filename="backtrack.log", mode="w")
    backtrack_handler.setFormatter(BacktrackFormatter(log_header=True, caller_info=True))
    _logger = getLogger("backtrack")
    _logger.setLevel(level="DEBUG")
    _logger.addHandler(backtrack_handler)
    logger = LoggerAdapter(_logger, extra={"host": "-", "vendor": "-"})

    queue = asyncio.Queue()

    watcher = aionotify.Watcher()
    watcher.watch(
        alias="devs",
        path="/home/delio/backtrack/backtrack/devs.json",
        flags=aionotify.Flags.MODIFY,
    )

    loop = asyncio.get_event_loop()
    """signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s =s: asyncio.create_task(shutdown(s, loop)))"""
    loop.set_exception_handler(handle_exception)
    scheduler = Scheduler(periodic=15, loop=loop, queue=queue)
    try:
        loop.create_task(monitor_devs(loop, scheduler))
        loop.create_task(scheduler.consumer.consumer())
        loop.create_task(scheduler.producer.producer(scheduler.periodic))
        loop.run_forever()
    except KeyboardInterrupt as kb:
        logger.info("Interrupting process")
    finally:
        loop.close()
        logger.info("Shutting down loop")
