"""
OpenTelemetry metrics setup for the channelization microservice.

Provides runtime metrics collection and custom business metrics using
asynchronous export to ensure telemetry never impacts request processing.
"""

import logging
import psutil
import os
from typing import Dict, Any, Optional
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
try:
    from opentelemetry.instrumentation.runtime import RuntimeInstrumentor
except ImportError:
    RuntimeInstrumentor = None
try:
    from opentelemetry.instrumentation.psutil import PsutilInstrumentor
except ImportError:
    PsutilInstrumentor = None

from .config import TelemetryConfig

logger = logging.getLogger(__name__)

# Global meter instance
_meter: Optional[metrics.Meter] = None


def setup_metrics(resource: Resource, config: TelemetryConfig) -> MeterProvider:
    """
    Set up OpenTelemetry metrics with async export.
    
    Features:
    - Runtime metrics (CPU, memory, threads, GC)
    - Custom business metrics
    - PeriodicExportingMetricReader for async, non-blocking export
    - Graceful degradation if collector unavailable
    
    Args:
        resource: OpenTelemetry resource with service info
        config: Telemetry configuration
    
    Returns:
        MeterProvider: Configured meter provider
    """
    global _meter
    
    # Create metric reader with async exporter
    if config.metrics_enabled and config.otlp_endpoint:
        try:
            metric_exporter = OTLPMetricExporter(
                endpoint=f"{config.otlp_endpoint}/v1/metrics",
                timeout=config.otlp_timeout,
                compression="gzip",
            )
            
            metric_reader = PeriodicExportingMetricReader(
                metric_exporter,
                export_interval_millis=config.metrics_export_interval,
                timeout_millis=config.otlp_timeout * 1000,
            )
            
            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader],
            )
            
            logger.info(f"Metrics configured with {config.metrics_export_interval}ms export interval, endpoint: {config.otlp_endpoint}")
            
        except Exception as e:
            logger.warning(f"Failed to configure metric exporter: {e}. Using default meter provider.")
            meter_provider = MeterProvider(resource=resource)
    else:
        meter_provider = MeterProvider(resource=resource)
    
    # Set as global provider
    metrics.set_meter_provider(meter_provider)
    
    # Get meter for custom metrics
    _meter = metrics.get_meter(config.service_name)
    
    # Auto-instrument runtime metrics
    if RuntimeInstrumentor is not None:
        try:
            RuntimeInstrumentor().instrument()
            logger.info("Runtime instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument runtime metrics: {e}")
    else:
        logger.info("Runtime instrumentation not available (opentelemetry-instrumentation-runtime not installed)")
    
    # Auto-instrument psutil for process metrics
    if PsutilInstrumentor is not None:
        try:
            PsutilInstrumentor().instrument()
            logger.info("Process instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument process metrics: {e}")
    else:
        logger.info("Process instrumentation not available (opentelemetry-instrumentation-psutil not installed)")
    
    return meter_provider


def get_meter() -> Optional[metrics.Meter]:
    """Get the global meter instance."""
    return _meter


def create_counter(name: str, description: str = "", unit: str = "1") -> Optional[metrics.Counter]:
    """
    Create a counter metric.
    
    Args:
        name: Metric name (e.g., "requests.total")
        description: Metric description
        unit: Metric unit
    
    Returns:
        Counter or None if meter not initialized
    """
    if _meter:
        return _meter.create_counter(name=name, description=description, unit=unit)
    return None


def create_histogram(name: str, description: str = "", unit: str = "ms") -> Optional[metrics.Histogram]:
    """
    Create a histogram metric.
    
    Args:
        name: Metric name (e.g., "request.duration")
        description: Metric description
        unit: Metric unit
    
    Returns:
        Histogram or None if meter not initialized
    """
    if _meter:
        return _meter.create_histogram(name=name, description=description, unit=unit)
    return None


def create_up_down_counter(name: str, description: str = "", unit: str = "1") -> Optional[metrics.UpDownCounter]:
    """
    Create an up-down counter metric.
    
    Args:
        name: Metric name (e.g., "active.requests")
        description: Metric description
        unit: Metric unit
    
    Returns:
        UpDownCounter or None if meter not initialized
    """
    if _meter:
        return _meter.create_up_down_counter(name=name, description=description, unit=unit)
    return None


# Pre-defined metrics for the channelization microservice
class ChannelServiceMetrics:
    """Pre-configured metrics for the channelization microservice."""
    
    def __init__(self):
        self._initialized = False
        self.requests_total = None
        self.request_duration = None
        self.active_requests = None
        self.messages_sent = None
        self.messages_failed = None
        self.delivery_duration = None
    
    def init(self):
        """Initialize all metrics."""
        if self._initialized:
            return
        
        self.requests_total = create_counter(
            "channelization.requests.total",
            "Total number of HTTP requests",
            "1"
        )
        
        self.request_duration = create_histogram(
            "channelization.request.duration",
            "HTTP request duration in milliseconds",
            "ms"
        )
        
        self.active_requests = create_up_down_counter(
            "channelization.active.requests",
            "Number of active HTTP requests",
            "1"
        )
        
        # Business metrics - messages sent
        self.messages_sent = create_counter(
            "channelization.messages.sent.total",
            "Total number of messages sent successfully",
            "1"
        )
        
        # Business metrics - messages failed
        self.messages_failed = create_counter(
            "channelization.messages.failed.total",
            "Total number of message send failures",
            "1"
        )
        
        # Delivery duration histogram
        self.delivery_duration = create_histogram(
            "channelization.delivery.duration",
            "Message delivery duration in milliseconds",
            "ms"
        )
        
        self._initialized = True
        logger.info("Channelization metrics initialized")
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration_ms: float):
        """Record a request metric."""
        if not self._initialized:
            self.init()
        
        attributes = {
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code),
        }
        
        if self.requests_total:
            self.requests_total.add(1, attributes)
        if self.request_duration:
            self.request_duration.record(duration_ms, attributes)
    
    def increment_active_requests(self):
        """Increment active request count."""
        if not self._initialized:
            self.init()
        if self.active_requests:
            self.active_requests.add(1)
    
    def decrement_active_requests(self):
        """Decrement active request count."""
        if not self._initialized:
            self.init()
        if self.active_requests:
            self.active_requests.add(-1)
    
    def record_message_sent(self, channel: str):
        """Record a successfully sent message."""
        if not self._initialized:
            self.init()
        if self.messages_sent:
            self.messages_sent.add(1, {"channel": channel})
    
    def record_message_failed(self, channel: str, error_type: str = "unknown"):
        """Record a failed message send."""
        if not self._initialized:
            self.init()
        if self.messages_failed:
            self.messages_failed.add(1, {"channel": channel, "error_type": error_type})
    
    def record_delivery_duration(self, channel: str, duration_ms: float):
        """Record message delivery duration."""
        if not self._initialized:
            self.init()
        if self.delivery_duration:
            self.delivery_duration.record(duration_ms, {"channel": channel})


# Global metrics instance
channel_metrics = ChannelServiceMetrics()