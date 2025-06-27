# OpenTelemetry Stack Example

This project demonstrates how to set up and test an OpenTelemetry (OTel) stack locally using Docker Compose. It includes a Python script to generate and send telemetry data to an OpenTelemetry Collector, with traces viewable in Grafana via Tempo.

## Project Structure

- `test_otel.py` — Python script to generate and send test telemetry data (traces) to the OTel Collector.
- `docker-compose.yml` — Docker Compose file to spin up the OTel Collector, Tempo, Loki, Prometheus, and Grafana.
- `otelcol/otelcol.yaml` — Configuration for the OpenTelemetry Collector.
- `tempo/tempo.yaml` — Configuration for Tempo (distributed tracing backend).
- `prometheus/prometheus.yml` — Configuration for Prometheus (metrics backend).
- `loki/loki-local.yaml` — Configuration for Loki (logs backend).
- `otel_test_env/` — Python virtual environment for dependencies.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)
- Python 3.8+

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd otel-stack
```

### 2. Start the Observability Stack

This will start the OTel Collector, Tempo, Loki, Prometheus, and Grafana:

```bash
docker-compose up -d
```

- Grafana: [http://localhost:3000](http://localhost:3000)
- OTel Collector: [http://localhost:4317](http://localhost:4317)
- Tempo: [http://localhost:3200](http://localhost:3200)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Loki: [http://localhost:3100](http://localhost:3100)

### 3. Set Up Python Environment

It is recommended to use the provided virtual environment (`otel_test_env/`). If you need to recreate it:

```bash
python3 -m venv otel_test_env
source otel_test_env/bin/activate
pip install -r requirements.txt  # If requirements.txt is present
```

Or manually install dependencies:

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```

### 4. Run the Test Telemetry Script

With the stack running and your Python environment activated:

```bash
python test_otel.py
```

You should see output indicating that telemetry data was sent.

### 5. View Traces in Grafana

1. Open Grafana at [http://localhost:3000](http://localhost:3000)
2. Log in (default: `admin` / `admin`)
3. Navigate to **Explore** > **Tempo**
4. Search for traces from the `test-service`.

## Customization

- **Change Service Name:** Edit `test_otel.py` and modify the `service.name` in the `Resource.create` call.
- **Collector Endpoint:** Ensure the `endpoint` in `OTLPSpanExporter` matches your OTel Collector address.
- **Add More Spans:** Extend `test_otel.py` to generate more complex traces.

## Troubleshooting

- **No Traces in Grafana:**
  - Ensure all containers are running: `docker-compose ps`
  - Check logs for the OTel Collector: `docker-compose logs otelcol`
  - Ensure the Python script is using the correct endpoint and port.
- **Port Conflicts:**
  - Make sure the required ports (3000, 4317, 3200, 9090, 3100) are free.

## References

- [OpenTelemetry Python Docs](https://opentelemetry.io/docs/instrumentation/python/)
- [Grafana Tempo](https://grafana.com/oss/tempo/)
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [Prometheus](https://prometheus.io/)

---

**Author:** Your Name

**License:** MIT (or specify your license)
