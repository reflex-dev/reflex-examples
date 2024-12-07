from __future__ import annotations

import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes
from reflex.config import get_config

from hackathon_project_tracker.helper_logging.helper_otel import (
    OtelConfig,
    get_otel_config,
)
from hackathon_project_tracker.tokens import TOKENS

otel_config: OtelConfig = get_otel_config(
    tokens=TOKENS,
)
resource_attributes: dict[str, str] = {
    ResourceAttributes.SERVICE_NAME: get_config().app_name,
}
resource = Resource(
    attributes=resource_attributes, # trunk-ignore(pyright/reportArgumentType)
)

TRACE_PROVIDER = TracerProvider(
    resource=resource,
)
otel_config: OtelConfig = get_otel_config(
    tokens=TOKENS,
)
if otel_config.headers is not None:
    os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = otel_config.headers

if otel_config.endpoint is not None:
    TRACE_PROVIDER.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=otel_config.endpoint,
            ),
        ),
    )
else:
    TRACE_PROVIDER.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

trace.set_tracer_provider(TRACE_PROVIDER)
tracer = trace.get_tracer(resource_attributes[ResourceAttributes.SERVICE_NAME])

reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
METER_PROVIDER = MeterProvider(
    resource=resource,
    metric_readers=[reader],
)
metrics.set_meter_provider(
    METER_PROVIDER,
)
