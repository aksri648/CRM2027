"""
Telemetry configuration for the backend service.

All configuration is driven by environment variables with sensible defaults.
No hardcoded values - all settings can be overridden via environment.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class TelemetryConfig:
    """
    Configuration for OpenTelemetry instrumentation.
    
    All values are read from environment variables with fallback defaults.
    This ensures the application can run without telemetry infrastructure.
    """
    
    # Service identification
    service_name: str = None
    service_version: str = None
    environment: str = None
    
    # OpenTelemetry exporter configuration
    otlp_endpoint: str = None
    otlp_protocol: str = None
    otlp_timeout: int = None
    
    # Tracing configuration
    trace_sampling_rate: float = None
    trace_export_interval: int = None
    
    # Metrics configuration
    metrics_export_interval: int = None
    
    # Logging configuration
    log_level: str = None
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        # Service identification
        self.service_name = self.service_name or os.getenv("OTEL_SERVICE_NAME", "backend")
        self.service_version = self.service_version or os.getenv("OTEL_SERVICE_VERSION", "1.0.0")
        self.environment = self.environment or os.getenv("DEPLOYMENT_ENVIRONMENT", "development")
        
        # OpenTelemetry exporter
        self.otlp_endpoint = self.otlp_endpoint or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", 
            "http://telemetry-dashboard:4318"
        )
        self.otlp_protocol = self.otlp_protocol or os.getenv(
            "OTEL_EXPORTER_OTLP_PROTOCOL",
            "http/protobuf"
        )
        self.otlp_timeout = self.otlp_timeout or int(os.getenv("OTEL_EXPORTER_TIMEOUT", "10"))
        
        # Tracing
        self.trace_sampling_rate = self.trace_sampling_rate or float(os.getenv("OTEL_TRACE_SAMPLING_RATE", "0.1"))
        self.trace_export_interval = self.trace_export_interval or int(os.getenv("OTEL_TRACE_EXPORT_INTERVAL", "5000"))
        
        # Metrics
        self.metrics_export_interval = self.metrics_export_interval or int(os.getenv("OTEL_METRICS_EXPORT_INTERVAL", "30000"))
        
        # Logging
        self.log_level = self.log_level or os.getenv("OTEL_LOG_LEVEL", "INFO")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ("production", "prod")
    
    @property
    def tracing_enabled(self) -> bool:
        """Check if tracing is enabled based on sampling rate."""
        return self.trace_sampling_rate > 0
    
    @property
    def metrics_enabled(self) -> bool:
        """Check if metrics export is enabled."""
        return self.metrics_export_interval > 0