"""
OpenTelemetry tracing setup for the channelization microservice.

Provides asynchronous trace export using BatchSpanProcessor to ensure
telemetry failures never block request processing.
"""

import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, Sampler
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import TracerProvider

from .config import TelemetryConfig

logger = logging.getLogger(__name__)


def create_sampler(config: TelemetryConfig) -> Sampler:
    """
    Create a trace sampler based on configuration.
    
    Uses TraceIdRatioBased sampling to sample a percentage of traces.
    This is configurable via OTEL_TRACE_SAMPLING_RATE environment variable.
    """
    return TraceIdRatioBased(config.trace_sampling_rate)


def setup_tracing(resource: Resource, config: TelemetryConfig) -> TracerProvider:
    """
    Set up OpenTelemetry tracing with async export.
    
    Features:
    - Configurable sampling rate (default 10%)
    - BatchSpanProcessor for async export (non-blocking)
    - OTLP HTTP exporter for trace export
    - Graceful degradation if collector unavailable
    
    Args:
        resource: OpenTelemetry resource with service info
        config: Telemetry configuration
    
    Returns:
        TracerProvider: Configured tracer provider
    """
    # Create sampler based on configuration
    sampler = create_sampler(config)
    
    # Create tracer provider with sampling
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=sampler,
    )
    
    # Set as global provider
    trace.set_tracer_provider(tracer_provider)
    
    # Only set up exporter if endpoint is configured and sampling > 0
    if config.tracing_enabled and config.otlp_endpoint:
        try:
            # Create OTLP span exporter with async HTTP protocol
            span_exporter = OTLPSpanExporter(
                endpoint=f"{config.otlp_endpoint}/v1/traces",
                timeout=config.otlp_timeout,
                compression="gzip",
            )
            
            # Use BatchSpanProcessor for async, non-blocking export
            # This ensures trace export never blocks request processing
            span_processor = BatchSpanProcessor(
                span_exporter,
                max_queue_size=2048,
                max_export_batch_size=512,
                export_timeout_millis=config.trace_export_interval,
                schedule_delay_millis=5000,
            )
            
            tracer_provider.add_span_processor(span_processor)
            logger.info(f"Tracing configured with {config.trace_sampling_rate*100}% sampling, endpoint: {config.otlp_endpoint}")
            
        except Exception as e:
            logger.warning(f"Failed to configure trace exporter: {e}. Tracing will be local only.")
    
    return tracer_provider


def get_current_trace_id() -> Optional[str]:
    """
    Get the current trace ID from the active span.
    
    Returns:
        str: Current trace ID as hex string, or None if no active span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return None


def get_current_span_id() -> Optional[str]:
    """
    Get the current span ID from the active span.
    
    Returns:
        str: Current span ID as hex string, or None if no active span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, '016x')
    return None