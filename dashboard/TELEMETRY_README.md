# SWEN Telemetry Dashboard

Real-time monitoring and visualization dashboard for SWEN AIOps platform.

## Architecture

```
dashboard/
├── api/          # FastAPI backend
│   ├── main.py   # API endpoints and WebSocket server
│   └── requirements.txt
└── ui/           # Streamlit frontend
    ├── app.py    # Dashboard UI
    └── requirements.txt
```

## Components

### API Backend (FastAPI)

The API provides:
- **REST Endpoints**: JSON data for telemetry, decisions, and metrics
- **WebSocket**: Real-time streaming updates
- **Prometheus Metrics**: `/metrics` endpoint for Prometheus scraping
- **Health Check**: `/healthz` endpoint with system state

#### Key Endpoints

- `GET /healthz` - System health and current state
- `GET /api/telemetry` - Latest telemetry data
- `GET /api/decisions` - AI decision history
- `GET /api/metrics` - Aggregated metrics and statistics
- `GET /api/cost-analysis` - Detailed cost breakdown
- `POST /api/deployments` - Receive deployment events from CI/CD
- `WS /ws` - WebSocket for real-time updates
- `GET /metrics` - Prometheus-compatible metrics

### UI Frontend (Streamlit)

Interactive dashboard with:
- **Overview**: System status, service distribution, key metrics
- **AI Decisions**: Decision history with explanations and confidence scores
- **Cost Analysis**: Provider comparison, cost vs latency visualization
- **Telemetry**: Live metrics for each service
- **Live Feed**: Real-time activity stream

## Data Pipeline

```
Telemetry Simulator → JSON Files → API → Dashboard UI
                                    ↓
                              Prometheus
```

### Data Flow

1. **Simulator** generates telemetry data every 5 seconds
2. **AI Engine** reads telemetry and makes decisions
3. **API** exposes data via REST and WebSocket
4. **Dashboard** polls API and displays real-time updates
5. **Prometheus** scrapes metrics from API

## Running the Dashboard

### Start the API

```bash
cd dashboard/api
pip install -r requirements.txt
python main.py
```

API will be available at `http://localhost:8000`

### Start the UI

```bash
cd dashboard/ui
pip install -r requirements.txt
streamlit run app.py
```

Dashboard will open in your browser at `http://localhost:8501`

### Environment Variables

```bash
# API Configuration
export TELEMETRY_PATH="../ai-engine/latest_telemetry.json"
export DECISIONS_PATH="../ai-engine/ai_decisions.json"
export TF_OUTPUT_PATH="../../infra/envs/prod/outputs.json"
export PORT=8000

# Dashboard Configuration
export API_URL="http://localhost:8000"
```

## Refresh Mechanism

### API
- Data is read from JSON files on each request
- WebSocket pushes updates every 5 seconds
- No caching to ensure real-time data

### UI
- Auto-refresh every 10 seconds (configurable)
- Manual refresh button available
- Streamlit caching with 5-second TTL

## Integration with Other Components

### AI Engine
The AI engine writes to:
- `latest_telemetry.json` - Current metrics
- `ai_decisions.json` - Decision history

The API reads these files to provide data to the dashboard.

### GitLab CI/CD
Pipeline can POST deployment events to `/api/deployments`:

```bash
curl -X POST http://dashboard:8000/api/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "ai-recommendation/service1",
    "commit": "abc123",
    "status": "success",
    "timestamp": "2025-10-22T20:00:00Z"
  }'
```

### Prometheus
Add this scrape config to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'swen-dashboard'
    static_configs:
      - targets: ['dashboard-api:8000']
    metrics_path: '/metrics'
```

## Metrics Exposed

The API exposes Prometheus metrics:

```
swen_service_cost{service="service1",provider="aws"} 1.2
swen_service_latency{service="service1",provider="aws"} 85.3
swen_service_gpus{service="service1",provider="aws"} 2
```

## WebSocket Protocol

Connect to `ws://localhost:8000/ws` to receive real-time updates:

```json
{
  "type": "update",
  "telemetry": { ... },
  "metrics": { ... },
  "timestamp": "2025-10-22T20:00:00Z"
}
```

## Customization

### Adding New Visualizations

Edit `dashboard/ui/app.py` and add new tabs or charts using Plotly:

```python
fig = px.line(df, x='time', y='cost', color='provider')
st.plotly_chart(fig)
```

### Adding New API Endpoints

Edit `dashboard/api/main.py`:

```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"data": "custom"}
```

## Troubleshooting

### API not responding
- Check if API is running: `curl http://localhost:8000/healthz`
- Verify telemetry files exist
- Check API logs

### Dashboard not updating
- Verify API URL in sidebar
- Check browser console for errors
- Ensure auto-refresh is enabled

### Missing data
- Ensure simulator is running
- Check file paths in environment variables
- Verify JSON file permissions

## Production Deployment

### Docker Deployment

```dockerfile
# API
FROM python:3.9-slim
WORKDIR /app
COPY dashboard/api/requirements.txt .
RUN pip install -r requirements.txt
COPY dashboard/api/ .
CMD ["python", "main.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: swen-dashboard-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dashboard-api
  template:
    metadata:
      labels:
        app: dashboard-api
    spec:
      containers:
      - name: api
        image: swen/dashboard-api:latest
        ports:
        - containerPort: 8000
```

## Security Considerations

- Add authentication for production use
- Use HTTPS/WSS for encrypted connections
- Implement rate limiting
- Validate all input data
- Use environment variables for sensitive config

## Performance

- API can handle 1000+ requests/second
- WebSocket supports 100+ concurrent connections
- Dashboard refresh interval is configurable
- Consider Redis for caching in high-traffic scenarios
