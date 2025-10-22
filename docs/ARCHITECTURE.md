# SWEN AIOps Platform - Architecture Documentation

## System Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                         SWEN AIOps Platform Architecture                      │
└───────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Streamlit Dashboard (UI)                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────┐ │  │
│  │  │ Overview │  │AI Decisions│ │   Cost   │  │Telemetry │  │ Live  │ │  │
│  │  │   Tab    │  │    Tab     │ │ Analysis │  │   Tab    │  │ Feed  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └───────┘ │  │
│  │                         http://localhost:8501                        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     │ HTTP/WebSocket                         │
│                                     ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              API & SERVICES LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Backend (API)                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │  /healthz  │  │/telemetry  │  │ /decisions │  │  /metrics  │    │  │
│  │  │            │  │            │  │            │  │(Prometheus)│    │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │  │
│  │                                                                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                    │  │
│  │  │/cost-analysis│ │    /ws     │  │/deployments│                    │  │
│  │  │            │  │ (WebSocket)│  │  (webhook) │                    │  │
│  │  └────────────┘  └────────────┘  └────────────┘                    │  │
│  │                         http://localhost:8000                        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     │ File I/O                               │
│                                     ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI & DECISION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────┐        ┌─────────────────────────────────┐   │
│  │  Telemetry Simulator    │        │      AI Engine                  │   │
│  │  ┌──────────────────┐   │        │  ┌──────────────────────────┐  │   │
│  │  │ Generate Metrics │   │        │  │  Cost Scoring Algorithm  │  │   │
│  │  │ - Cost           │   │        │  │  - Cost: 40%             │  │   │
│  │  │ - Latency        │───┼────────┼─▶│  - Latency: 25%          │  │   │
│  │  │ - Credits        │   │        │  │  - Credits: 20%          │  │   │
│  │  │ - GPU Avail.     │   │        │  │  - Availability: 15%     │  │   │
│  │  └──────────────────┘   │        │  └──────────────────────────┘  │   │
│  │         │                │        │              │                  │   │
│  │         ▼                │        │              ▼                  │   │
│  │  latest_telemetry.json  │        │  ┌──────────────────────────┐  │   │
│  └─────────────────────────┘        │  │  Decision Making         │  │   │
│                                      │  │  - Confidence > 70%      │  │   │
│                                      │  │  - Provider Selection    │  │   │
│                                      │  │  - Explanation Gen.      │  │   │
│                                      │  └──────────────────────────┘  │   │
│                                      │              │                  │   │
│                                      │              ▼                  │   │
│                                      │     ai_decisions.json           │   │
│                                      └─────────────────────────────────┘   │
│                                                     │                       │
│                                                     │ If change needed      │
│                                                     ▼                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            GITOPS & AUTOMATION LAYER                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GitOps Committer                                │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │Create Branch│ │Update TF   │  │   Commit   │  │Push & Create│   │  │
│  │  │ai-rec/...  │─▶│ Variables  │─▶│  Changes   │─▶│   MR        │   │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     │ Git Push                               │
│                                     ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GitLab CI/CD Pipeline                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐  │  │
│  │  │ Validate │─▶│  Policy  │─▶│   Plan   │─▶│  Apply   │─▶│Notify│  │  │
│  │  │          │  │  Check   │  │          │  │          │  │      │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────┘  │  │
│  │                      │                                                │  │
│  │                      ▼                                                │  │
│  │              ┌──────────────┐                                        │  │
│  │              │ Policy Gate  │                                        │  │
│  │              │ - Cost < 5%  │                                        │  │
│  │              │ - Conf > 85% │                                        │  │
│  │              │ - No Stateful│                                        │  │
│  │              └──────────────┘                                        │  │
│  │                      │                                                │  │
│  │         ┌────────────┴────────────┐                                  │  │
│  │         ▼                         ▼                                  │  │
│  │  ┌──────────────┐        ┌──────────────┐                          │  │
│  │  │ Auto-Approve │        │Manual Review │                          │  │
│  │  │   (70-80%)   │        │   (20-30%)   │                          │  │
│  │  └──────────────┘        └──────────────┘                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     │ Terraform Apply                        │
│                                     ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Terraform (IaC)                                 │  │
│  │  ┌────────────────┐              ┌────────────────┐                 │  │
│  │  │ Cluster Module │              │   App Module   │                 │  │
│  │  │ - VPC          │              │ - EC2/Compute  │                 │  │
│  │  │ - Networking   │              │ - Monitoring   │                 │  │
│  │  │ - Security     │              │ - Auto-scaling │                 │  │
│  │  └────────────────┘              └────────────────┘                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                    ┌────────────────┴────────────────┐                      │
│                    ▼                                 ▼                      │
│  ┌─────────────────────────────┐   ┌─────────────────────────────┐        │
│  │      AWS Infrastructure     │   │  Alibaba Infrastructure     │        │
│  │  ┌─────────────────────┐    │   │  ┌─────────────────────┐    │        │
│  │  │  Cluster: swen-aws  │    │   │  │Cluster: swen-alibaba│    │        │
│  │  │  Region: us-east-1  │    │   │  │Region: ap-southeast │    │        │
│  │  └─────────────────────┘    │   │  └─────────────────────┘    │        │
│  │  ┌─────────────────────┐    │   │  ┌─────────────────────┐    │        │
│  │  │    Service 1        │    │   │  │    Service 3        │    │        │
│  │  │    Service 2        │    │   │  │  (AI-optimized)     │    │        │
│  │  │  (AI-optimized)     │    │   │  └─────────────────────┘    │        │
│  │  └─────────────────────┘    │   │                              │        │
│  └─────────────────────────────┘   └─────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐                      │
│  │    Prometheus        │    │   Alert Manager      │                      │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │                      │
│  │  │ Scrape Metrics │◀─┼────┼──│  Cost Alerts   │  │                      │
│  │  │ - Cost         │  │    │  │  - High Cost   │  │                      │
│  │  │ - Latency      │  │    │  │  - Cost Spike  │  │                      │
│  │  │ - Availability │  │    │  │  - High Latency│  │                      │
│  │  └────────────────┘  │    │  └────────────────┘  │                      │
│  │         │             │    │         │            │                      │
│  │         ▼             │    │         ▼            │                      │
│  │  ┌────────────────┐  │    │  ┌────────────────┐  │                      │
│  │  │ Alert Rules    │──┼────┼─▶│ Self-Healing   │  │                      │
│  │  │ - Thresholds   │  │    │  │   Triggers     │  │                      │
│  │  └────────────────┘  │    │  └────────────────┘  │                      │
│  └──────────────────────┘    └──────────────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### Normal Operation Flow

```
1. Telemetry Generation
   Simulator → latest_telemetry.json
   (Every 5 seconds)

2. AI Analysis
   AI Engine reads telemetry
   → Calculates scores
   → Makes decision
   → Logs to ai_decisions.json

3. Dashboard Display
   API reads JSON files
   → Serves via REST/WebSocket
   → UI displays real-time data

4. User Monitoring
   User views dashboard
   → Sees current state
   → Reviews AI decisions
```

### AI-Driven Change Flow

```
1. Decision Made
   AI Engine detects optimization opportunity
   → Confidence > 70%
   → Cost savings > $50/month

2. GitOps Initiated
   GitOps Committer creates branch
   → Updates terraform.tfvars
   → Commits changes
   → Pushes to remote
   → Creates Merge Request

3. CI/CD Pipeline
   GitLab CI triggered
   → Validates Terraform
   → Runs policy check
   → Generates plan

4. Policy Evaluation
   Policy Gate evaluates
   → Cost delta < 5%?
   → Confidence > 85%?
   → No stateful services?
   
   YES → Auto-approve → Apply
   NO  → Manual review required

5. Infrastructure Update
   Terraform applies changes
   → Service migrates to new provider
   → Monitoring confirms success
   → Dashboard shows new state
```

### Self-Healing Flow

```
1. Issue Detection
   Prometheus alert fires
   OR
   AI Engine detects anomaly
   (High latency, cost spike, outage)

2. Immediate Analysis
   AI Engine evaluates alternatives
   → Calculates best option
   → High confidence (emergency)

3. Emergency Response
   GitOps workflow accelerated
   → Emergency branch created
   → Policy gate: emergency override
   → Immediate apply

4. Recovery
   Service migrated to healthy provider
   → Monitoring confirms recovery
   → Event logged
   → Dashboard updated

5. Post-Incident
   Review decision accuracy
   → Update thresholds if needed
   → Document in runbook
```

---

## Component Interactions

### AI Engine ↔ Dashboard

```
AI Engine                    Dashboard API
    │                             │
    ├─ Writes ─────────────────▶ │
    │  ai_decisions.json          │
    │                             │
    │                             ├─ Reads ─────────────▶ Dashboard UI
    │                             │  /api/decisions       │
    │                             │                       │
    │                             │◀───── HTTP Request ───┤
    │                             │                       │
    │                             ├─ Returns JSON ───────▶│
```

### Telemetry Flow

```
Simulator                    AI Engine                Dashboard
    │                             │                        │
    ├─ Writes ──────────────────▶│                        │
    │  latest_telemetry.json      │                        │
    │                             │                        │
    │                             ├─ Reads                 │
    │                             ├─ Analyzes              │
    │                             ├─ Decides               │
    │                             │                        │
    │                             │                        │
    │◀──────── Also Read ─────────┼────────────────────────┤
    │                             │                        │
    │                             │                        │
    └─ Updates every 5s           └─ Checks every 30s     └─ Displays real-time
```

### GitOps Workflow

```
AI Engine          Git Repo          GitLab CI          Terraform
    │                  │                  │                  │
    ├─ Create Branch ─▶│                  │                  │
    ├─ Commit ────────▶│                  │                  │
    ├─ Push ──────────▶│                  │                  │
    │                  │                  │                  │
    │                  ├─ Webhook ───────▶│                  │
    │                  │                  │                  │
    │                  │                  ├─ Validate        │
    │                  │                  ├─ Policy Check    │
    │                  │                  ├─ Plan ──────────▶│
    │                  │                  │                  │
    │                  │                  │◀─ Plan Output ───┤
    │                  │                  │                  │
    │                  │                  ├─ Apply ─────────▶│
    │                  │                  │                  │
    │                  │                  │◀─ Success ───────┤
    │                  │                  │                  │
    │                  │◀─ Update State ──┤                  │
```

---

## Technology Stack

### Frontend
- **Streamlit** - Interactive dashboard UI
- **Plotly** - Data visualization
- **Pandas** - Data manipulation

### Backend
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time communication

### AI/ML
- **NumPy** - Numerical computations
- **Scikit-learn** - ML algorithms (future)
- **Custom Algorithm** - Multi-factor scoring

### Infrastructure
- **Terraform** - Infrastructure as Code
- **AWS** - Primary cloud provider
- **Alibaba Cloud** - Secondary provider (simulated)

### DevOps
- **GitLab CI/CD** - Continuous deployment
- **Git** - Version control
- **ArgoCD** - GitOps (optional)

### Monitoring
- **Prometheus** - Metrics collection
- **Alertmanager** - Alert management
- **Custom Exporters** - Metrics export

### Languages
- **Python 3.8+** - Primary language
- **HCL** - Terraform configuration
- **YAML** - CI/CD and config files
- **Markdown** - Documentation

---

## Scalability Considerations

### Horizontal Scaling
- Dashboard API: Multiple instances behind load balancer
- AI Engine: Distributed decision making
- Telemetry: Partitioned by service

### Vertical Scaling
- Increase AI Engine compute for complex decisions
- Scale database for decision history
- Larger instances for high-traffic dashboard

### Performance Optimization
- Caching: Redis for frequently accessed data
- Async: Non-blocking I/O throughout
- Batching: Bulk decision processing
- CDN: Static assets for dashboard

---

## Security Architecture

```
┌─────────────────────────────────────────┐
│         Security Layers                 │
├─────────────────────────────────────────┤
│                                         │
│  1. Authentication & Authorization      │
│     - API keys for services             │
│     - OAuth for users (future)          │
│     - RBAC for GitLab                   │
│                                         │
│  2. Network Security                    │
│     - VPC isolation                     │
│     - Security groups                   │
│     - Private subnets                   │
│                                         │
│  3. Data Security                       │
│     - Encrypted state files             │
│     - Secrets in env vars               │
│     - No hardcoded credentials          │
│                                         │
│  4. Audit & Compliance                  │
│     - All decisions logged              │
│     - Git history preserved             │
│     - Immutable audit trail             │
│                                         │
│  5. Policy Enforcement                  │
│     - Automated policy gates            │
│     - Manual approval for high-risk     │
│     - Rollback capabilities             │
│                                         │
└─────────────────────────────────────────┘
```

---

## Deployment Topology

### Local Development
```
Single Machine
├── Python processes (4)
│   ├── Simulator
│   ├── AI Engine
│   ├── API
│   └── Dashboard UI
└── File system
    ├── Telemetry JSON
    └── Decision logs
```

### Production (Recommended)
```
Cloud Infrastructure
├── Kubernetes Cluster
│   ├── Dashboard Pod (replicas: 3)
│   ├── API Pod (replicas: 3)
│   ├── AI Engine Pod (replicas: 2)
│   └── Simulator Pod (replicas: 1)
├── Load Balancer
│   └── Routes traffic to services
├── Database (PostgreSQL)
│   └── Stores decision history
├── Object Storage (S3)
│   └── Stores telemetry archives
└── Monitoring Stack
    ├── Prometheus
    ├── Grafana
    └── Alertmanager
```

---

## Future Enhancements

1. **Machine Learning**
   - Train models on historical data
   - Reinforcement learning for optimization
   - Predictive cost forecasting

2. **Advanced Observability**
   - Distributed tracing (Jaeger)
   - Log aggregation (ELK stack)
   - APM integration

3. **Multi-Region**
   - Global load balancing
   - Regional failover
   - Data replication

4. **Advanced Automation**
   - Chaos engineering integration
   - Automated capacity planning
   - Predictive scaling

5. **Enhanced Security**
   - Zero-trust architecture
   - Automated compliance checks
   - Security scanning in CI/CD

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-22  
**Maintained By:** Platform Engineering Team
