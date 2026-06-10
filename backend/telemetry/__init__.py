"""
OpenTelemetry instrumentation for the backend service.

This module provides centralized telemetry configuration that is
isolated from business logic. Telemetry failures will never impact
application functionality.

Usage:
    from telemetry import init_telemetry
    init_telemetry(app)
"""

import logging
from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.logging import LoggingHandler
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Meter

from .config import TelemetryConfig
from .tracing import setup_tracing
from .metrics import setup_metrics
from .logging import setup_logging

logger = logging.getLogger(__name__)

# Global tracer and meter instances
_tracer: Optional[Tracer] = None
_meter: Optional[Meter] = None


def init_telemetry(app=None, config: Optional[TelemetryConfig] = None) -> dict:
    """
    Initialize OpenTelemetry instrumentation for the application.
    
    This function sets up tracing, metrics, and structured logging.
    It is designed to fail silently - telemetry errors will not impact
    the application.
    
    Args:
        app: Optional FastAPI application instance for auto-instrumentation
        config: Optional telemetry configuration (reads from env if not provided)
    
    Returns:
        dict: Initialization status and configuration
    """
    if config is None:
        config = TelemetryConfig()
    
    result = {
        "status": "initializing",
        "service_name": config.service_name,
        "endpoint": config.otlp_endpoint,
    }
    
    try:
        # Create resource with service information
        resource = Resource.create({
            "service.name": config.service_name,
            "service.version": config.service_version,
            "deployment.environment": config.environment,
        })
        
        # Setup tracing with async exporter
        tracer_provider = setup_tracing(resource, config)
        result["tracing"] = "configured"
        
        # Setup metrics with async exporter
        meter_provider = setup_metrics(resource, config)
        result["metrics"] = "configured"
        
        # Setup structured JSON logging
        setup_logging(config)
        result["logging"] = "configured"
        
        # Auto-instrument FastAPI if app provided
        if app is not None:
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=tracer_provider,
                meter_provider=meter_provider,
                excluded_urls="health,metrics,docs,openapi.json",
            )
            result["instrumentation"] = "fastapi"
        
        # Get global tracer and meter
        global _tracer, _meter
        _tracer = trace.get_tracer(config.service_name)
        _meter = metrics.get_meter(config.service_name)
        
        result["status"] = "initialized"
        logger.info(f"Telemetry initialized for {config.service_name}")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.warning(f"Telemetry initialization failed: {e}. Application will continue without telemetry.")
    
    return result


def get_tracer() -> Optional[Tracer]:
    """Get the global tracer instance."""
    return _tracer


def get_meter() -> Optional[Meter]:
    """Get the global meter instance."""
    return _meter