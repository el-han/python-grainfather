#!/usr/bin/env python3
import asyncio
import sys

from grainfather.grainfather import Grainfather


async def main():
    grain = Grainfather()

    await grain.connect()

    await grain.send_recipe_beerxml(sys.argv[1])

if __name__ == '__main__':
    asyncio.run(main())
