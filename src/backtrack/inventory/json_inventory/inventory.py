"""backtrack.inventory.json_inventory.inventory"""
import json

import aiofiles

from backtrack.inventory.base.inventory import Inventory


class JSONInventory(Inventory):
    def __init__(self, destination):
        super().__init__(destination=destination)

    async def update_cache(self):
        pass

    async def get_inventory(self):
        try:
            self.logger.info("Trying to fetch inventory from inventory.json")
            async with aiofiles.open(self.destination, mode="r") as inv:
                inventory = await json.load(inv)["devices"]
                return inventory
        except FileNotFoundError:
            self.logger.error(f"File does not exist")
