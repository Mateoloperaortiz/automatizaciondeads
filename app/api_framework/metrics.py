"""
Metrics tracking for the API Integration Framework.

This module provides utilities for tracking and analyzing API usage metrics
such as request counts, latency, error rates, etc.
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta

from app.api_framework.base import APIRequest, APIResponse

# Configure logging
logger = logging.getLogger(__name__)


class APIMetrics:
    """
    API metrics collection and analysis.
    
    This class collects and analyzes metrics about API usage, providing
    insights into performance, reliability, and utilization.
    """
    
    def __init__(self, retention_period: int = 24 * 60 * 60):
        """
        Initialize the metrics collector.
        
        Args:
            retention_period: How long to retain metrics data in seconds (default: 24 hours)
        """
        self.retention_period = retention_period
        self.lock = threading.RLock()
        
        # Metrics storage
        self.requests = deque()  # [(timestamp, platform, operation, success, latency), ...]
        self.request_counts = defaultdict(int)  # {platform: count, ...}
        self.error_counts = defaultdict(int)  # {platform: count, ...}
        self.latency_data = defaultdict(list)  # {platform: [latency1, latency2, ...], ...}
        
        # Track when metrics were last aggregated
        self.last_aggregation = time.time()
        
        # Start background cleanup thread
        self._start_cleanup_thread()
        
    def record(self, request: APIRequest, response: APIResponse) -> None:
        """
        Record metrics for a request-response pair.
        
        Args:
            request: The API request
            response: The API response
        """
        platform = request.platform or 'unknown'
        operation = request.operation or request.endpoint
        success = response.success
        latency = response.timing or 0
        
        with self.lock:
            # Store detailed metrics for time-series analysis
            self.requests.append((
                time.time(),
                platform,
                operation,
                success,
                latency
            ))
            
            # Update aggregate counters
            self.request_counts[platform] += 1
            if not success:
                self.error_counts[platform] += 1
                
            # Update latency tracking
            self.latency_data[platform].append(latency)
            
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of metrics across all platforms.
        
        Returns:
            Dictionary containing metrics summary
        """
        with self.lock:
            # Clean up old data first
            self._cleanup_old_data()
            
            # Prepare response
            result = {
                'request_count': sum(self.request_counts.values()),
                'error_count': sum(self.error_counts.values()),
                'platforms': {}
            }
            
            # Calculate per-platform metrics
            for platform in self.request_counts.keys():
                requests = self.request_counts[platform]
                errors = self.error_counts[platform]
                
                platform_metrics = {
                    'requests': requests,
                    'errors': errors,
                    'error_rate': (errors / requests) if requests > 0 else 0,
                }
                
                # Calculate latency statistics if we have data
                latencies = self.latency_data.get(platform, [])
                if latencies:
                    platform_metrics['latency'] = {
                        'avg': sum(latencies) / len(latencies),
                        'min': min(latencies),
                        'max': max(latencies),
                        'p50': self._percentile(latencies, 50),
                        'p95': self._percentile(latencies, 95),
                        'p99': self._percentile(latencies, 99)
                    }
                    
                result['platforms'][platform] = platform_metrics
                
            return result
            
    def get_request_rate(self, platform: Optional[str] = None, 
                         window: int = 300) -> float:
        """
        Calculate requests per second over a time window.
        
        Args:
            platform: Platform to filter by (None for all platforms)
            window: Time window in seconds (default: 5 minutes)
            
        Returns:
            Requests per second
        """
        with self.lock:
            # Filter by timestamp and platform
            now = time.time()
            window_start = now - window
            
            if platform:
                filtered_requests = [r for r in self.requests
                                    if r[0] >= window_start and r[1] == platform]
            else:
                filtered_requests = [r for r in self.requests
                                    if r[0] >= window_start]
                
            # Calculate rate
            count = len(filtered_requests)
            if count == 0:
                return 0.0
                
            # Calculate actual duration (might be less than window)
            if count > 1:
                earliest = min(r[0] for r in filtered_requests)
                duration = now - earliest
            else:
                duration = window
                
            return count / max(duration, 1)  # Avoid division by zero
            
    def get_error_rate(self, platform: Optional[str] = None,
                      window: int = 3600) -> float:
        """
        Calculate error rate over a time window.
        
        Args:
            platform: Platform to filter by (None for all platforms)
            window: Time window in seconds (default: 1 hour)
            
        Returns:
            Error rate as a decimal (0.0 to 1.0)
        """
        with self.lock:
            # Filter by timestamp and platform
            now = time.time()
            window_start = now - window
            
            if platform:
                filtered_requests = [r for r in self.requests
                                    if r[0] >= window_start and r[1] == platform]
            else:
                filtered_requests = [r for r in self.requests
                                    if r[0] >= window_start]
                
            # Calculate error rate
            total = len(filtered_requests)
            if total == 0:
                return 0.0
                
            errors = sum(1 for r in filtered_requests if not r[3])  # r[3] is success
            return errors / total
            
    def get_latency_trends(self, platform: str, 
                         window: int = 24 * 60 * 60,
                         buckets: int = 24) -> List[Dict[str, Any]]:
        """
        Get latency trends over time.
        
        Args:
            platform: Platform to analyze
            window: Time window in seconds (default: 24 hours)
            buckets: Number of time buckets for the result (default: 24)
            
        Returns:
            List of dictionaries with timestamp and latency statistics
        """
        with self.lock:
            # Filter by timestamp and platform
            now = time.time()
            window_start = now - window
            
            filtered_requests = [r for r in self.requests
                               if r[0] >= window_start and r[1] == platform]
                
            # If no data, return empty result
            if not filtered_requests:
                return []
                
            # Calculate bucket size
            bucket_size = window / buckets
            result = []
            
            # Group by time buckets
            for i in range(buckets):
                bucket_start = window_start + (i * bucket_size)
                bucket_end = bucket_start + bucket_size
                
                bucket_requests = [r for r in filtered_requests
                                 if bucket_start <= r[0] < bucket_end]
                
                # Skip empty buckets
                if not bucket_requests:
                    continue
                    
                # Extract latencies
                latencies = [r[4] for r in bucket_requests]  # r[4] is latency
                
                # Calculate statistics
                result.append({
                    'timestamp': bucket_start,
                    'requests': len(bucket_requests),
                    'avg_latency': sum(latencies) / len(latencies),
                    'min_latency': min(latencies),
                    'max_latency': max(latencies),
                    'p95_latency': self._percentile(latencies, 95)
                })
                
            return result
            
    def _cleanup_old_data(self) -> None:
        """Remove data older than the retention period."""
        if not self.requests:
            return
            
        cutoff = time.time() - self.retention_period
        
        # Remove old detailed data
        while self.requests and self.requests[0][0] < cutoff:
            self.requests.popleft()
            
        # Re-aggregate counters if it's been more than an hour
        if time.time() - self.last_aggregation > 3600:
            self._reaggregate_metrics()
            
    def _reaggregate_metrics(self) -> None:
        """Recalculate aggregated metrics from raw data."""
        # Reset counters
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.latency_data = defaultdict(list)
        
        # Recalculate from raw data
        for timestamp, platform, operation, success, latency in self.requests:
            self.request_counts[platform] += 1
            if not success:
                self.error_counts[platform] += 1
            self.latency_data[platform].append(latency)
            
        self.last_aggregation = time.time()
        
    def _start_cleanup_thread(self) -> None:
        """Start a background thread to periodically clean up old data."""
        def cleanup_worker():
            while True:
                time.sleep(3600)  # Run once per hour
                try:
                    with self.lock:
                        self._cleanup_old_data()
                except Exception as e:
                    logger.error(f"Error in metrics cleanup: {str(e)}")
                    
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
        
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """
        Calculate percentile value from a list.
        
        Args:
            data: List of numeric values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not data:
            return 0.0
            
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        
        # Handle exact index
        if index.is_integer():
            return sorted_data[int(index)]
            
        # Interpolate between values
        lower_idx = int(index)
        upper_idx = lower_idx + 1
        weight = index - lower_idx
        
        return sorted_data[lower_idx] * (1 - weight) + sorted_data[upper_idx] * weight