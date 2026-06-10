"""OTLP HTTP receiver — accepts protobuf pushes from backend / channel services.

Render free tier exposes only one HTTP port per service, so we cannot run the
standalone otel-collector binary on 4317/4318. Instead, FastAPI itself handles
the OTLP HTTP spec endpoints (/v1/traces, /v1/metrics, /v1/logs) and writes
decoded payloads into the in-memory storage used by the dashboard API.
"""

import gzip
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Request, Response
from opentelemetry.proto.collector.logs.v1 import logs_service_pb2
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from .telemetry import log_storage, metric_storage

logger = logging.getLogger(__name__)
router = APIRouter()

OTLP_CONTENT_TYPE = "application/x-protobuf"


async def _read_body(request: Request) -> bytes:
    body = await request.body()
    if request.headers.get("content-encoding", "").lower() == "gzip":
        try:
            body = gzip.decompress(body)
        except OSError as exc:
            logger.warning("Failed to decompress OTLP gzip body: %s", exc)
    return body


def _attrs_to_dict(attributes) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for attr in attributes:
        v = attr.value
        if v.HasField("string_value"):
            out[attr.key] = v.string_value
        elif v.HasField("int_value"):
            out[attr.key] = v.int_value
        elif v.HasField("double_value"):
            out[attr.key] = v.double_value
        elif v.HasField("bool_value"):
            out[attr.key] = v.bool_value
        else:
            out[attr.key] = str(v)
    return out


def _resource_service_name(resource_attrs: Dict[str, Any]) -> str:
    return str(resource_attrs.get("service.name", "unknown"))


def _data_point_value(dp) -> float:
    if dp.HasField("as_double"):
        return float(dp.as_double)
    if dp.HasField("as_int"):
        return float(dp.as_int)
    return 0.0


@router.post("/v1/metrics")
async def receive_metrics(request: Request) -> Response:
    body = await _read_body(request)
    req = metrics_service_pb2.ExportMetricsServiceRequest()
    try:
        req.ParseFromString(body)
    except Exception as exc:
        logger.warning("OTLP metrics parse failed: %s", exc)
        return Response(content=b"", media_type=OTLP_CONTENT_TYPE, status_code=400)

    recorded = 0
    for rm in req.resource_metrics:
        resource_attrs = _attrs_to_dict(rm.resource.attributes)
        service = _resource_service_name(resource_attrs)
        for sm in rm.scope_metrics:
            for metric in sm.metrics:
                points: List = []
                if metric.HasField("sum"):
                    points = list(metric.sum.data_points)
                elif metric.HasField("gauge"):
                    points = list(metric.gauge.data_points)
                elif metric.HasField("histogram"):
                    for dp in metric.histogram.data_points:
                        labels = _attrs_to_dict(dp.attributes)
                        labels["service"] = service
                        await metric_storage.record_metric(
                            f"{metric.name}.sum", float(dp.sum), labels
                        )
                        await metric_storage.record_metric(
                            f"{metric.name}.count", float(dp.count), labels
                        )
                        recorded += 2
                    continue
                for dp in points:
                    labels = _attrs_to_dict(dp.attributes)
                    labels["service"] = service
                    await metric_storage.record_metric(
                        metric.name, _data_point_value(dp), labels
                    )
                    recorded += 1

    logger.debug("Received OTLP metrics: %d data points", recorded)
    resp = metrics_service_pb2.ExportMetricsServiceResponse().SerializeToString()
    return Response(content=resp, media_type=OTLP_CONTENT_TYPE)


_SEVERITY_TO_LEVEL = {
    1: "trace", 2: "trace", 3: "trace", 4: "trace",
    5: "debug", 6: "debug", 7: "debug", 8: "debug",
    9: "info", 10: "info", 11: "info", 12: "info",
    13: "warning", 14: "warning", 15: "warning", 16: "warning",
    17: "error", 18: "error", 19: "error", 20: "error",
    21: "fatal", 22: "fatal", 23: "fatal", 24: "fatal",
}


@router.post("/v1/logs")
async def receive_logs(request: Request) -> Response:
    body = await _read_body(request)
    req = logs_service_pb2.ExportLogsServiceRequest()
    try:
        req.ParseFromString(body)
    except Exception as exc:
        logger.warning("OTLP logs parse failed: %s", exc)
        return Response(content=b"", media_type=OTLP_CONTENT_TYPE, status_code=400)

    received = 0
    for rl in req.resource_logs:
        service = _resource_service_name(_attrs_to_dict(rl.resource.attributes))
        for sl in rl.scope_logs:
            for record in sl.log_records:
                level = _SEVERITY_TO_LEVEL.get(int(record.severity_number), "info")
                message = record.body.string_value if record.body.HasField("string_value") else str(record.body)
                await log_storage.add_log({
                    "level": level,
                    "message": message,
                    "service": service,
                    "metadata": _attrs_to_dict(record.attributes),
                })
                received += 1

    logger.debug("Received OTLP logs: %d records", received)
    resp = logs_service_pb2.ExportLogsServiceResponse().SerializeToString()
    return Response(content=resp, media_type=OTLP_CONTENT_TYPE)


@router.post("/v1/traces")
async def receive_traces(request: Request) -> Response:
    body = await _read_body(request)
    req = trace_service_pb2.ExportTraceServiceRequest()
    try:
        req.ParseFromString(body)
    except Exception as exc:
        logger.warning("OTLP traces parse failed: %s", exc)
        return Response(content=b"", media_type=OTLP_CONTENT_TYPE, status_code=400)

    spans = 0
    for rs in req.resource_spans:
        service = _resource_service_name(_attrs_to_dict(rs.resource.attributes))
        for ss in rs.scope_spans:
            for span in ss.spans:
                duration_ns = span.end_time_unix_nano - span.start_time_unix_nano
                await metric_storage.record_metric(
                    "trace.span.duration_ms",
                    duration_ns / 1_000_000.0,
                    {"service": service, "span": span.name},
                )
                spans += 1

    logger.debug("Received OTLP traces: %d spans", spans)
    resp = trace_service_pb2.ExportTraceServiceResponse().SerializeToString()
    return Response(content=resp, media_type=OTLP_CONTENT_TYPE)
