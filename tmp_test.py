
import asyncio
from fastapi.concurrency import run_in_threadpool

def sync_fn(x):
    return {"result": x}

async def _run_with_timeout(fn, *args, timeout_seconds: int, **kwargs):
    return await asyncio.wait_for(
        run_in_threadpool(fn, *args, **kwargs),
        timeout=float(timeout_seconds),
    )

async def main():
    res = await _run_with_timeout(sync_fn, 42, timeout_seconds=5)
    print(f"Type of res: {type(res)}")
    print(f"Value of res: {res}")

if __name__ == "__main__":
    asyncio.run(main())
