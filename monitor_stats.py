#!/usr/bin/env python3
import asyncio
import json

from grainfather.grainfather import Grainfather


def print_stats(stats):
    print(json.dumps(stats.to_dict(), indent=4))


async def main():
    grain = Grainfather()

    await grain.connect()

    await grain.run(callback=print_stats)

    while True:
        await asyncio.sleep(0.001)

if __name__ == '__main__':
    asyncio.run(main())
