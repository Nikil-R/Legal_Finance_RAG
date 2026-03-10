"""
Load testing suite for the RAG API using Locust.

Run with:
    locust -f tests/load/locustfile.py --host http://localhost:8000

For headless mode:
    locust -f tests/load/locustfile.py --headless --users 50 --spawn-rate 5 --run-time 5m --host http://localhost:8000
"""

from locust import HttpUser, between, events, task
import random
from faker import Faker

fake = Faker()


class LegalRAGUser(HttpUser):
    """Simulated user behavior for load testing."""

    wait_time = between(1, 5)  # Wait 1-5 seconds between requests

    def on_start(self):
        """Initialize user session."""
        self.api_key = "query_key_67890"
        self.queries = [
            "What is the revenue recognition policy?",
            "Explain lease accounting standards",
            "Summary of SEC filing requirements",
            "Details on stock-based compensation",
            "Goodwill impairment testing procedures",
            "Fair value measurement guidelines",
            "Pension liability calculations",
            "Derivative financial instruments",
            "Related party transactions disclosure",
            "Contingent liabilities reporting",
            "Income tax provision calculation",
            "Segment reporting requirements",
            "Earnings per share computation",
            "Business combination accounting",
            "Impairment of long-lived assets",
        ]
        self.domains = ["tax", "finance", "legal"]

    @task(10)
    def query_documents(self):
        """Most common operation: querying documents."""
        query = random.choice(self.queries)
        domain = random.choice(self.domains)

        self.client.post(
            "/api/v1/query",
            json={
                "question": query,
                "domain": domain,
                "top_k": 5
            },
            headers={"X-API-Key": self.api_key},
            name="/api/v1/query"
        )

    @task(2)
    def query_with_filters(self):
        """Query with metadata filters."""
        self.client.post(
            "/api/v1/query",
            json={
                "question": random.choice(self.queries),
                "domain": random.choice(self.domains),
                "filters": {
                    "year": random.choice([2021, 2022, 2023]),
                    "document_type": random.choice(["10-K", "10-Q", "8-K"])
                },
                "top_k": 10
            },
            headers={"X-API-Key": self.api_key},
            name="/api/v1/query [filtered]"
        )

    @task(1)
    def query_retrieval_only(self):
        """Test retrieval-only endpoint."""
        self.client.post(
            "/api/v1/query/retrieve",
            json={
                "question": random.choice(self.queries),
                "domain": random.choice(self.domains),
                "top_k": 5
            },
            headers={"X-API-Key": self.api_key},
            name="/api/v1/query/retrieve"
        )

    @task(1)
    def list_documents(self):
        """Occasionally list documents."""
        self.client.get(
            "/api/v1/documents",
            headers={"X-API-Key": self.api_key},
            name="/api/v1/documents"
        )

    @task(1)
    def get_document_stats(self):
        """Get document statistics."""
        self.client.get(
            "/api/v1/documents/stats",
            headers={"X-API-Key": self.api_key},
            name="/api/v1/documents/stats"
        )

    @task(1)
    def list_domains(self):
        """List available domains."""
        self.client.get(
            "/api/v1/documents/domains",
            headers={"X-API-Key": self.api_key},
            name="/api/v1/documents/domains"
        )

    @task(3)
    def health_check(self):
        """Simulate monitoring/health checks."""
        self.client.get("/health/liveness", name="/health/liveness")

    @task(1)
    def get_metrics(self):
        """Check Prometheus metrics."""
        self.client.get("/metrics", name="/metrics")


class AdminUser(HttpUser):
    """Simulated admin performing uploads and management."""

    wait_time = between(10, 30)  # Admins act less frequently

    def on_start(self):
        self.api_key = "admin_key_12345"

    @task(3)
    def query_as_admin(self):
        """Admins also query documents."""
        self.client.post(
            "/api/v1/query",
            json={
                "question": "administrative query",
                "domain": random.choice(["tax", "finance", "legal"])
            },
            headers={"X-API-Key": self.api_key},
            name="/api/v1/query [admin]"
        )

    @task(1)
    def get_stats(self):
        """Get system statistics."""
        self.client.get(
            "/api/v1/documents/stats",
            headers={"X-API-Key": self.api_key},
            name="/api/v1/documents/stats [admin]"
        )

    @task(1)
    def list_domains(self):
        """List domains as admin."""
        self.client.get(
            "/api/v1/documents/domains",
            headers={"X-API-Key": self.api_key},
            name="/api/v1/documents/domains [admin]"
        )


class PowerUser(HttpUser):
    """Power users with higher request rates."""

    wait_time = between(0.5, 2)

    def on_start(self):
        self.api_key = "admin_key_12345"
        self.queries = [
            "tax deduction under section 80C",
            "RBI guidelines for NBFC",
            "SEBI disclosure requirements",
            "GST input tax credit",
            "deferred tax asset",
            "lease liability measurement",
        ]

    @task(5)
    def rapid_query(self):
        """Rapid-fire queries for stress testing."""
        self.client.post(
            "/api/v1/query",
            json={
                "question": random.choice(self.queries),
                "domain": "tax",
                "top_k": 3
            },
            headers={"X-API-Key": self.api_key},
            name="/api/v1/query [rapid]"
        )

    @task(1)
    def health_check(self):
        """Rapid health checks."""
        self.client.get("/health/readiness", name="/health/readiness")


@events.quitting.add_listener
def on_quit(environment, **kwargs):
    """Print summary when test completes."""
    stats = environment.stats

    print("\n" + "=" * 60)
    print("LOAD TEST SUMMARY")
    print("=" * 60)

    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Failed Requests: {stats.total.num_failures}")
    if stats.total.num_requests > 0:
        print(f"Failure Rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"Avg Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Median Response Time: {stats.total.median_response_time:.2f}ms")
    print(f"P95 Response Time: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"P99 Response Time: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")

    # Per-endpoint breakdown
    print("\nPer-Endpoint Statistics:")
    print("-" * 60)
    for endpoint_name, endpoint_stats in stats.entries.items():
        print(f"\n{endpoint_name}:")
        print(f"  Requests: {endpoint_stats.num_requests}")
        print(f"  Failures: {endpoint_stats.num_failures}")
        print(f"  Avg: {endpoint_stats.avg_response_time:.2f}ms")
        print(f"  P95: {endpoint_stats.get_response_time_percentile(0.95):.2f}ms")

    print("\n" + "=" * 60)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print info when test starts."""
    print("\n" + "=" * 60)
    print("LEGAL FINANCE RAG LOAD TEST")
    print("=" * 60)
    print(f"Target Host: {environment.host}")
    print(f"Test Start Time: {kwargs.get('start_time', 'N/A')}")
    print("=" * 60 + "\n")
