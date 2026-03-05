"""
Simple load/stress test runner for query endpoint.
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time

import httpx


async def _one_call(
    client: httpx.AsyncClient,
    url: str,
    payload: dict,
    api_key: str | None,
) -> tuple[int, float]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    start = time.perf_counter()
    response = await client.post(url, json=payload, headers=headers)
    latency_ms = (time.perf_counter() - start) * 1000
    return response.status_code, latency_ms


async def run_load_test(
    base_url: str,
    total_requests: int,
    concurrency: int,
    api_key: str | None,
    question: str,
    domain: str,
) -> None:
    endpoint = f"{base_url.rstrip('/')}/api/v1/query"
    payload = {"question": question, "domain": domain, "include_sources": False}

    semaphore = asyncio.Semaphore(concurrency)
    statuses: list[int] = []
    latencies: list[float] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        async def worker() -> None:
            async with semaphore:
                status, latency = await _one_call(client, endpoint, payload, api_key)
                statuses.append(status)
                latencies.append(latency)

        tasks = [asyncio.create_task(worker()) for _ in range(total_requests)]
        await asyncio.gather(*tasks)

    ok = len([s for s in statuses if 200 <= s < 300])
    errors = len([s for s in statuses if s >= 500])
    throttled = statuses.count(429)

    p95 = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 100 else max(latencies)
    p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

    print("Load test complete")
    print(f"Requests: {total_requests}")
    print(f"Concurrency: {concurrency}")
    print(f"2xx: {ok}, 5xx: {errors}, 429: {throttled}")
    print(f"Avg latency: {statistics.mean(latencies):.1f} ms")
    print(f"P95 latency: {p95:.1f} ms")
    print(f"P99 latency: {p99:.1f} ms")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run API load test")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--question", default="What are deductions under Section 80C?")
    parser.add_argument("--domain", choices=["tax", "finance", "legal", "all"], default="tax")
    args = parser.parse_args()

    asyncio.run(
        run_load_test(
            base_url=args.base_url,
            total_requests=args.requests,
            concurrency=args.concurrency,
            api_key=args.api_key,
            question=args.question,
            domain=args.domain,
        )
    )


if __name__ == "__main__":
    main()
