import uasyncio as asyncio

class Queue:
    def __init__(self):
        self._queue = []
        self._ev = asyncio.Event()

    async def put(self, val):
        if len(self._queue) >= 6:
            print("[IPC]: Can't write in channel.")
            return 0
        self._queue.append(val)
        self._ev.set()

    async def get(self):
        while not self._queue:
            await self._ev.wait()
            self._ev.clear()
        return self._queue.pop(0)

class Pipe:
    def __init__(self):
        self.channels = [Queue(), Queue()]

    async def write(self, side, data):
        await self.channels[1 - side].put(data)

    async def read(self, side):
        return await self.channels[side].get()

