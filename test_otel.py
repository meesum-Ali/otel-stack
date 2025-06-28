#!/usr/bin/env python3
"""
Test script to send telemetry data to OpenTelemetry Collector
"""

import time
import random
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource

def main():
    # Set up the tracer provider with resource information
    resource = Resource.create({
        "service.name": "test-service",
        "service.version": "1.0.0",
        "deployment.environment": "testing"
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # Configure OTLP exporter to send to our collector
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    # Add batch span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # --- METRICS SETUP ---
    metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
    metric_reader = PeriodicExportingMetricReader(metric_exporter)
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
    meter = metrics.get_meter("test-meter", "1.0.0")
    request_counter = meter.create_counter(
        name="requests_total",
        description="Total number of requests",
        unit="1"
    )
    latency_histogram = meter.create_histogram(
        name="request_latency_ms",
        description="Request latency in milliseconds",
        unit="ms"
    )

    # --- LOGS SETUP ---
    log_exporter = OTLPLogExporter(endpoint="http://localhost:4317", insecure=True)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    logging.setLoggerClass(logging.getLoggerClass())
    logging.basicConfig(level=logging.INFO)
    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(otel_handler)
    logger = logging.getLogger("otel-logger")
    
    # Get tracer
    tracer = trace.get_tracer("test-tracer", "1.0.0")
    
    print("Sending test telemetry data to OpenTelemetry Collector...")
    
    # Create some test spans
    with tracer.start_as_current_span("main-operation") as main_span:
        main_span.set_attribute("operation.type", "test")
        main_span.set_attribute("user.id", "test-user-123")
        # METRICS: Record a request and latency
        request_counter.add(1, {"endpoint": "/main-operation"})
        latency_histogram.record(100, {"endpoint": "/main-operation"})
        # LOGS: Emit a log
        logger.info("Started main operation", extra={"user.id": "test-user-123"})
        
        # Simulate some work
        time.sleep(0.1)
        
        # Create a child span
        with tracer.start_as_current_span("database-query") as db_span:
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "users")
            rows = random.randint(1, 100)
            db_span.set_attribute("db.rows.affected", rows)
            # METRICS: Record DB query
            request_counter.add(1, {"endpoint": "/database-query"})
            latency_histogram.record(50, {"endpoint": "/database-query"})
            # LOGS: Emit a log
            logger.info(f"Database query affected {rows} rows", extra={"db.table": "users"})
            
            # Simulate database query time
            time.sleep(0.05)
        
        # Create another child span
        with tracer.start_as_current_span("external-api-call") as api_span:
            api_span.set_attribute("http.method", "POST")
            api_span.set_attribute("http.url", "https://api.example.com/data")
            api_span.set_attribute("http.status_code", 200)
            # METRICS: Record API call
            request_counter.add(1, {"endpoint": "/external-api-call"})
            latency_histogram.record(30, {"endpoint": "/external-api-call"})
            # LOGS: Emit a log
            logger.info("External API call completed", extra={"http.url": "https://api.example.com/data"})
            
            # Simulate API call time
            time.sleep(0.03)
    
    # Force flush to ensure all spans are sent
    trace.get_tracer_provider().force_flush(timeout_millis=5000)
    
    print("✅ Successfully sent test telemetry data!")
    print("Check Grafana at http://localhost:3000 to view the traces, metrics, and logs.")

if __name__ == "__main__":
    main()
