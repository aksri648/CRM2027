"""
OpenTelemetry structured logging setup for the channelization microservice.

Provides JSON-formatted logs with trace context injection for
correlation between logs, metrics, and traces.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.logging import LoggingHandler, SDKLoggerProvider
from opentelemetry.sdk.logging.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.log_exporter import OTLPLogExporter

from .config import TelemetryConfig
from .tracing import get_current_trace_id, get_current_span_id

logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Every log entry includes:
    - service: Service name
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (INFO, ERROR, etc.)
    - message: Log message
    - trace_id: OpenTelemetry trace ID (if available)
    - span_id: OpenTelemetry span ID (if available)
    """
    
    def __init__(self, service_name: str = "channelization-microservice"):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "service": self.service_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add trace context if available
        trace_id = get_current_trace_id()
        span_id = get_current_span_id()
        
        if trace_id:
            log_entry["trace_id"] = trace_id
        if span_id:
            log_entry["span_id"] = span_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class PlainTextFormatter(logging.Formatter):
    """
    Fallback plain text formatter that still includes trace context.
    Used when JSON parsing is not available or for local development.
    """
    
    def __init__(self, service_name: str = "channelization-microservice"):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with trace context."""
        trace_id = get_current_trace_id()
        span_id = get_current_span_id()
        
        trace_context = ""
        if trace_id:
            trace_context = f" [trace_id={trace_id}"
            if span_id:
                trace_context += f" span_id={span_id}"
            trace_context += "]"
        
        return f"{datetime.now(timezone.utc).isoformat()} {record.levelname} {self.service_name} {record.name} {record.getMessage()}{trace_context}"


def setup_logging(config: TelemetryConfig) -> None:
    """
    Set up OpenTelemetry-compatible structured logging.
    
    Features:
    - JSON formatted logs for production
    - Trace context injection (trace_id, span_id)
    - Async log export using BatchLogRecordProcessor
    - Fallback to console if collector unavailable
    
    Args:
        config: Telemetry configuration
    """
    # Create resource for logging
    resource = Resource.create({
        "service.name": config.service_name,
        "service.version": config.service_version,
        "deployment.environment": config.environment,
    })
    
    # Set up log exporter (async OTLP if endpoint available)
    log_exporter = None
    if config.otlp_endpoint:
        try:
            log_exporter = OTLPLogExporter(
                endpoint=f"{config.otlp_endpoint}/v1/logs",
                timeout=config.otlp_timeout,
                compression="gzip",
            )
        except Exception as e:
            logger.warning(f"Failed to create OTLP log exporter: {e}")
    
    # Use console exporter as fallback or primary
    if log_exporter is None:
        log_exporter = ConsoleLogExporter()
    
    # Create log processor with batch export for async operation
    log_processor = BatchLogRecordProcessor(
        log_exporter,
        max_queue_size=2048,
        max_export_batch_size=512,
        export_timeout_millis=5000,
        schedule_delay_millis=1000,
    )
    
    # Create and set logger provider
    logger_provider = SDKLoggerProvider(
        resource=resource,
    )
    logger_provider.add_log_record_processor(log_processor)
    
    # Set as global provider
    logging.setLoggerClass(SDKLoggerProvider)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    
    # Use JSON formatter in production, plain text in development
    if config.is_production:
        handler.setFormatter(JSONFormatter(config.service_name))
    else:
        handler.setFormatter(PlainTextFormatter(config.service_name))
    
    root_logger.addHandler(handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logger.info(f"Logging configured for {config.service_name} in {config.environment} mode")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with trace context support.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance with trace context injection
    """
    return logging.getLogger(name)