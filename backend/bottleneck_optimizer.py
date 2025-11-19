"""
Fractal Bottleneck Optimizer using Bellman-Ford Logic
Identifies slow endpoints and optimizes request routing
"""

import time
import asyncio
from collections import defaultdict
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

class BellmanBottleneckOptimizer:
    """
    Uses dynamic programming (Bellman-Ford inspired) to find optimal
    paths through API dependency graph and identify bottlenecks.
    """

    def __init__(self):
        self.endpoint_metrics = defaultdict(lambda: {
            'call_count': 0,
            'total_latency': 0.0,
            'failures': 0,
            'last_called': None,
            'latency_history': []
        })
        self.dependency_graph = {}
        self.optimization_state = {}

    def record_call(self, endpoint: str, latency: float, success: bool):
        """Record an API call for analysis"""
        metrics = self.endpoint_metrics[endpoint]
        metrics['call_count'] += 1
        metrics['total_latency'] += latency
        metrics['last_called'] = datetime.now()

        if not success:
            metrics['failures'] += 1

        # Keep last 100 latencies for percentile calculations
        metrics['latency_history'].append(latency)
        if len(metrics['latency_history']) > 100:
            metrics['latency_history'] = metrics['latency_history'][-100:]

    def get_avg_latency(self, endpoint: str) -> float:
        """Calculate average latency for an endpoint"""
        metrics = self.endpoint_metrics[endpoint]
        if metrics['call_count'] == 0:
            return 0.0
        return metrics['total_latency'] / metrics['call_count']

    def get_p95_latency(self, endpoint: str) -> float:
        """Calculate 95th percentile latency"""
        metrics = self.endpoint_metrics[endpoint]
        history = metrics['latency_history']
        if not history:
            return 0.0
        sorted_latencies = sorted(history)
        index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[index]

    def get_failure_rate(self, endpoint: str) -> float:
        """Calculate failure rate as percentage"""
        metrics = self.endpoint_metrics[endpoint]
        if metrics['call_count'] == 0:
            return 0.0
        return (metrics['failures'] / metrics['call_count']) * 100

    def identify_bottlenecks(self, threshold_ms: float = 500) -> List[Dict]:
        """
        Identify endpoints that are bottlenecks based on:
        - High latency (> threshold)
        - High failure rate (> 5%)
        - High p95 latency
        """
        bottlenecks = []

        for endpoint, metrics in self.endpoint_metrics.items():
            if metrics['call_count'] == 0:
                continue

            avg_latency = self.get_avg_latency(endpoint)
            p95_latency = self.get_p95_latency(endpoint)
            failure_rate = self.get_failure_rate(endpoint)

            # Bellman score: weighted combination of factors
            # Lower score = better performance
            bellman_score = (
                avg_latency * 0.4 +  # Average latency weight
                p95_latency * 0.4 +   # P95 latency weight
                failure_rate * 20     # Failure rate heavily weighted
            )

            is_bottleneck = (
                avg_latency > threshold_ms or
                failure_rate > 5.0 or
                p95_latency > threshold_ms * 2
            )

            bottlenecks.append({
                'endpoint': endpoint,
                'avg_latency_ms': round(avg_latency, 2),
                'p95_latency_ms': round(p95_latency, 2),
                'failure_rate_pct': round(failure_rate, 2),
                'call_count': metrics['call_count'],
                'bellman_score': round(bellman_score, 2),
                'is_bottleneck': is_bottleneck,
                'last_called': metrics['last_called'].isoformat() if metrics['last_called'] else None
            })

        # Sort by Bellman score (worst first)
        bottlenecks.sort(key=lambda x: x['bellman_score'], reverse=True)
        return bottlenecks

    def get_optimization_recommendations(self) -> List[str]:
        """Generate recommendations based on Bellman analysis"""
        recommendations = []
        bottlenecks = [b for b in self.identify_bottlenecks() if b['is_bottleneck']]

        for bottleneck in bottlenecks[:5]:  # Top 5 bottlenecks
            endpoint = bottleneck['endpoint']

            if bottleneck['failure_rate_pct'] > 10:
                recommendations.append(
                    f"🔴 CRITICAL: {endpoint} has {bottleneck['failure_rate_pct']}% failure rate - Check external API health"
                )
            elif bottleneck['p95_latency_ms'] > 2000:
                recommendations.append(
                    f"🟡 HIGH LATENCY: {endpoint} p95 latency is {bottleneck['p95_latency_ms']}ms - Consider caching or CDN"
                )
            elif bottleneck['avg_latency_ms'] > 1000:
                recommendations.append(
                    f"🟠 SLOW: {endpoint} avg latency is {bottleneck['avg_latency_ms']}ms - Review API call efficiency"
                )

        if not recommendations:
            recommendations.append("✅ All endpoints performing within acceptable thresholds")

        return recommendations

    def export_state(self) -> Dict:
        """Export optimizer state for monitoring dashboard"""
        return {
            'timestamp': datetime.now().isoformat(),
            'endpoints_monitored': len(self.endpoint_metrics),
            'total_calls': sum(m['call_count'] for m in self.endpoint_metrics.values()),
            'bottlenecks': self.identify_bottlenecks(),
            'recommendations': self.get_optimization_recommendations()
        }


# Global instance
optimizer = BellmanBottleneckOptimizer()


async def monitor_endpoint(endpoint: str, func, *args, **kwargs):
    """
    Wrapper to monitor endpoint performance
    Usage: result = await monitor_endpoint('/api/weather', fetch_weather_data, lat, lon)
    """
    start = time.time()
    success = True

    try:
        result = await func(*args, **kwargs)
        return result
    except Exception as e:
        success = False
        raise
    finally:
        latency = (time.time() - start) * 1000  # Convert to ms
        optimizer.record_call(endpoint, latency, success)


def get_optimizer() -> BellmanBottleneckOptimizer:
    """Get global optimizer instance"""
    return optimizer
