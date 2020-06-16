# __init__.py for primitives
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


async def _g():
    pass
type_coro = type(_g())

# If a callback is passed, run it and return.
# If a coro is passed initiate it and return.
# coros are passed by name i.e. not using function call syntax.
def launch(func, tup_args):
    res = func(*tup_args)
    if isinstance(res, type_coro):
        res = asyncio.create_task(res)
    return res
