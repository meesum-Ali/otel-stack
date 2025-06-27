#!/usr/bin/env python3
"""
Test script to send telemetry data to OpenTelemetry Collector
"""

import time
import random
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
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
    
    # Get tracer
    tracer = trace.get_tracer("test-tracer", "1.0.0")
    
    print("Sending test telemetry data to OpenTelemetry Collector...")
    
    # Create some test spans
    with tracer.start_as_current_span("main-operation") as main_span:
        main_span.set_attribute("operation.type", "test")
        main_span.set_attribute("user.id", "test-user-123")
        
        # Simulate some work
        time.sleep(0.1)
        
        # Create a child span
        with tracer.start_as_current_span("database-query") as db_span:
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "users")
            db_span.set_attribute("db.rows.affected", random.randint(1, 100))
            
            # Simulate database query time
            time.sleep(0.05)
        
        # Create another child span
        with tracer.start_as_current_span("external-api-call") as api_span:
            api_span.set_attribute("http.method", "POST")
            api_span.set_attribute("http.url", "https://api.example.com/data")
            api_span.set_attribute("http.status_code", 200)
            
            # Simulate API call time
            time.sleep(0.03)
    
    # Force flush to ensure all spans are sent
    trace.get_tracer_provider().force_flush(timeout_millis=5000)
    
    print("✅ Successfully sent test telemetry data!")
    print("Check Grafana at http://localhost:3000 to view the traces in Tempo")

if __name__ == "__main__":
    main()
