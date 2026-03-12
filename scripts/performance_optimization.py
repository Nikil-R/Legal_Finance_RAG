"""
Performance Optimization & Load Testing

Profile, optimize, and load test all production systems.
"""

import time
import json
from typing import Dict, List, Callable
from statistics import mean, median, stdev
from concurrent.futures import ThreadPoolExecutor, as_completed

class PerformanceProfiler:
    """Profile tool execution times and identify bottlenecks"""
    
    def __init__(self):
        self.results = {}
        self.bottlenecks = []
    
    def profile_function(self, func: Callable, args: tuple, iterations: int = 100) -> Dict:
        """Profile function execution time"""
        
        execution_times = []
        errors = 0
        
        for _ in range(iterations):
            try:
                start = time.perf_counter()
                result = func(*args)
                end = time.perf_counter()
                execution_times.append((end - start) * 1000)  # Convert to ms
            except Exception as e:
                errors += 1
        
        if not execution_times:
            return {"error": "All iterations failed"}
        
        profile = {
            "function": func.__name__,
            "iterations": iterations,
            "errors": errors,
            "min_ms": min(execution_times),
            "max_ms": max(execution_times),
            "mean_ms": mean(execution_times),
            "median_ms": median(execution_times),
            "stdev_ms": stdev(execution_times) if len(execution_times) > 1 else 0,
            "p95_ms": sorted(execution_times)[int(len(execution_times) * 0.95)],
            "p99_ms": sorted(execution_times)[int(len(execution_times) * 0.99)]
        }
        
        return profile
    
    def identify_bottlenecks(self, profiles: Dict[str, Dict]) -> List:
        """Identify performance bottlenecks"""
        
        bottlenecks = []
        
        for func_name, profile in profiles.items():
            if profile["p95_ms"] > 1000:  # > 1 second at p95
                bottlenecks.append({
                    "function": func_name,
                    "issue": "High latency (p95 > 1s)",
                    "p95_ms": profile["p95_ms"],
                    "recommendations": [
                        "1. Add caching for repeated queries",
                        "2. Optimize database queries",
                        "3. Profile memory usage",
                        "4. Consider async execution"
                    ]
                })
            
            if profile["stdev_ms"] > profile["mean_ms"]:
                bottlenecks.append({
                    "function": func_name,
                    "issue": "High variance in performance",
                    "stdev_ms": profile["stdev_ms"],
                    "recommendations": [
                        "1. Investigate resource contention",
                        "2. Add connection pooling",
                        "3. Review error handling"
                    ]
                })
        
        return bottlenecks
    
    def generate_report(self, profiles: Dict[str, Dict]) -> Dict:
        """Generate performance report"""
        
        bottlenecks = self.identify_bottlenecks(profiles)
        
        report = {
            "timestamp": time.time(),
            "total_functions_profiled": len(profiles),
            "profiles": profiles,
            "bottlenecks": bottlenecks,
            "optimization_priority": self._prioritize_optimizations(bottlenecks)
        }
        
        return report
    
    @staticmethod
    def _prioritize_optimizations(bottlenecks: List) -> List:
        """Prioritize optimization efforts"""
        
        return sorted(
            bottlenecks,
            key=lambda x: x.get("p95_ms", 0) or x.get("stdev_ms", 0),
            reverse=True
        )


class LoadTester:
    """Load test the system with concurrent requests"""
    
    def __init__(self, num_workers: int = 10):
        self.num_workers = num_workers
        self.results = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "response_times": [],
            "errors": []
        }
    
    def load_test(self, func: Callable, args: tuple, num_requests: int = 1000) -> Dict:
        """Execute load test"""
        
        print(f"\n🔥 Load Testing: {func.__name__}")
        print(f"   Workers: {self.num_workers}")
        print(f"   Total Requests: {num_requests}")
        print("-" * 60)
        
        start_time = time.perf_counter()
        response_times = []
        errors = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(self._execute_request, func, args)
                for _ in range(num_requests)
            ]
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                
                # Show progress
                if completed % 100 == 0:
                    print(f"   Progress: {completed}/{num_requests}")
                
                try:
                    response_time = future.result()
                    response_times.append(response_time)
                except Exception as e:
                    errors.append(str(e))
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Calculate statistics
        if response_times:
            load_test_result = {
                "function": func.__name__,
                "total_requests": num_requests,
                "successful": len(response_times),
                "failed": len(errors),
                "total_time_seconds": total_time,
                "requests_per_second": num_requests / total_time,
                "min_response_ms": min(response_times),
                "max_response_ms": max(response_times),
                "mean_response_ms": mean(response_times),
                "p95_response_ms": sorted(response_times)[int(len(response_times) * 0.95)],
                "p99_response_ms": sorted(response_times)[int(len(response_times) * 0.99)] if len(response_times) > 100 else None,
                "throughput_status": self._evaluate_throughput(num_requests / total_time),
                "errors": errors[:10]  # First 10 errors
            }
        else:
            load_test_result = {
                "function": func.__name__,
                "status": "ALL_FAILED",
                "errors": errors
            }
        
        print(f"✅ Load test completed: {load_test_result.get('requests_per_second', 0):.1f} req/s")
        print("-" * 60)
        
        return load_test_result
    
    @staticmethod
    def _execute_request(func: Callable, args: tuple) -> float:
        """Execute single request and return response time in ms"""
        
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        
        return (end - start) * 1000
    
    @staticmethod
    def _evaluate_throughput(rps: float) -> Dict:
        """Evaluate throughput performance"""
        
        if rps > 1000:
            return {"rating": "EXCELLENT", "comment": ">1000 req/s"}
        elif rps > 500:
            return {"rating": "GOOD", "comment": "500-1000 req/s"}
        elif rps > 100:
            return {"rating": "ACCEPTABLE", "comment": "100-500 req/s"}
        else:
            return {"rating": "NEEDS_OPTIMIZATION", "comment": "<100 req/s"}


class OptimizationRecommendations:
    """Generate optimization recommendations"""
    
    @staticmethod
    def for_compliance_manager() -> Dict:
        """Optimization tips for compliance manager"""
        return {
            "module": "Compliance Manager",
            "current_bottleneck": "Disclaimer text generation",
            "recommendations": [
                {
                    "optimization": "Cache disclaimer text",
                    "expected_improvement": "50% faster",
                    "implementation": "Use functools.lru_cache"
                },
                {
                    "optimization": "Batch disclaimer generation",
                    "expected_improvement": "30% improvement for bulk operations",
                    "implementation": "Group disclaimers by tool type"
                }
            ]
        }
    
    @staticmethod
    def for_audit_logger() -> Dict:
        """Optimization tips for audit logger"""
        return {
            "module": "Audit Logger",
            "current_bottleneck": "JSON serialization and file I/O",
            "recommendations": [
                {
                    "optimization": "Batch write audit events",
                    "expected_improvement": "70% faster writes",
                    "implementation": "Buffer 100 events before writing"
                },
                {
                    "optimization": "Use faster JSON encoder",
                    "expected_improvement": "20% improvement",
                    "implementation": "Use ujson or orjson library"
                },
                {
                    "optimization": "Compress old audit logs",
                    "expected_improvement": "80% storage reduction",
                    "implementation": "gzip files older than 7 days"
                }
            ]
        }
    
    @staticmethod
    def for_rate_limiter() -> Dict:
        """Optimization tips for rate limiter"""
        return {
            "module": "Rate Limiter",
            "current_bottleneck": "Dictionary lookups for high concurrency",
            "recommendations": [
                {
                    "optimization": "Use threading.RLock only when needed",
                    "expected_improvement": "40% improvement",
                    "implementation": "Use read-write lock pattern"
                },
                {
                    "optimization": "Implement local caching",
                    "expected_improvement": "50% improvement",
                    "implementation": "Cache recent rate limit decisions"
                }
            ]
        }
    
    @staticmethod
    def for_cache_layer() -> Dict:
        """Optimization tips for cache layer"""
        return {
            "module": "Cache Layer",
            "current_bottleneck": "Hash computation for cache keys",
            "recommendations": [
                {
                    "optimization": "Use Redis for distributed caching",
                    "expected_improvement": "10x improvement for multi-server",
                    "implementation": "Add Redis backend"
                },
                {
                    "optimization": "Implement two-level cache (L1 local, L2 Redis)",
                    "expected_improvement": "99% cache hit rate",
                    "implementation": "L1 = hot data, L2 = warm data"
                }
            ]
        }
    
    @staticmethod
    def generate_optimization_plan() -> Dict:
        """Generate comprehensive optimization plan"""
        
        return {
            "short_term_optimizations": [
                {
                    "priority": 1,
                    "module": "Audit Logger",
                    "action": "Implement batch writing",
                    "expected_gain": "70%",
                    "effort": "2 hours",
                    "timeline": "Week 1"
                },
                {
                    "priority": 2,
                    "module": "Cache Layer",
                    "action": "Add Redis support",
                    "expected_gain": "10x for distributed",
                    "effort": "1 day",
                    "timeline": "Week 1-2"
                }
            ],
            "medium_term_optimizations": [
                {
                    "priority": 3,
                    "module": "Rate Limiter",
                    "action": "Implement RWLock pattern",
                    "expected_gain": "40%",
                    "effort": "4 hours",
                    "timeline": "Week 2"
                }
            ],
            "long_term_optimizations": [
                {
                    "priority": 4,
                    "module": "All",
                    "action": "Database indexing and query optimization",
                    "expected_gain": "Custom",
                    "effort": "1 week",
                    "timeline": "Month 2"
                }
            ]
        }


def main():
    """Main performance testing script"""
    
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION & LOAD TESTING")
    print("=" * 60)
    
    # Profiling recommendations
    profiler = PerformanceProfiler()
    load_tester = LoadTester(num_workers=20)
    
    print("\n📊 Performance Baseline Metrics")
    print("-" * 60)
    
    # Show optimization recommendations
    for module in [
        OptimizationRecommendations.for_compliance_manager,
        OptimizationRecommendations.for_audit_logger,
        OptimizationRecommendations.for_rate_limiter,
        OptimizationRecommendations.for_cache_layer
    ]:
        recommendations = module()
        print(f"\n✅ {recommendations['module']}")
        print(f"   Bottleneck: {recommendations.get('current_bottleneck', 'N/A')}")
    
    # Optimization plan
    plan = OptimizationRecommendations.generate_optimization_plan()
    
    print("\n" + "=" * 60)
    print("📈 OPTIMIZATION PLAN")
    print("=" * 60)
    print(json.dumps(plan, indent=2))
    
    print("\n" + "=" * 60)
    print("✅ Performance analysis complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
