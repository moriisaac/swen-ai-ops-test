# SWEN AIOps Platform - Complete Index

**Quick navigation to all project resources**

---

## 📖 Documentation

### Getting Started
- **[README.md](README.md)** - Main project overview and introduction
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[COMMANDS.md](COMMANDS.md)** - Quick command reference

### Operations
- **[docs/RUNBOOK.md](docs/RUNBOOK.md)** - Complete operations guide (600+ lines)
- **[TESTING.md](TESTING.md)** - Comprehensive testing checklist
- **[DELIVERABLES.md](DELIVERABLES.md)** - Submission checklist

### Architecture & Design
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture documentation
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project summary

### Governance & Strategy
- **[ops/POLICY.md](ops/POLICY.md)** - Governance and approval policies (500+ lines)
- **[docs/COST_STRATEGY.md](docs/COST_STRATEGY.md)** - FinOps and cost optimization (600+ lines)
- **[docs/AI_LOG.md](docs/AI_LOG.md)** - AI collaboration transparency (400+ lines)

### Technical Documentation
- **[dashboard/TELEMETRY_README.md](dashboard/TELEMETRY_README.md)** - Dashboard documentation
- **[infra/README.md](infra/README.md)** - Infrastructure documentation

---

## 💻 Source Code

### AI Engine
- **[ai-engine/engine.py](ai-engine/engine.py)** - Core cost optimization logic
- **[ai-engine/simulator.py](ai-engine/simulator.py)** - Telemetry data generator
- **[ai-engine/gitops_committer.py](ai-engine/gitops_committer.py)** - Git automation
- **[ai-engine/requirements.txt](ai-engine/requirements.txt)** - Python dependencies

### Dashboard
- **[dashboard/api/main.py](dashboard/api/main.py)** - FastAPI backend (REST + WebSocket)
- **[dashboard/api/requirements.txt](dashboard/api/requirements.txt)** - API dependencies
- **[dashboard/ui/app.py](dashboard/ui/app.py)** - Streamlit frontend
- **[dashboard/ui/requirements.txt](dashboard/ui/requirements.txt)** - UI dependencies

### Infrastructure (Terraform)
- **[infra/modules/cluster/main.tf](infra/modules/cluster/main.tf)** - Cluster module
- **[infra/modules/app/main.tf](infra/modules/app/main.tf)** - Application module
- **[infra/envs/prod/main.tf](infra/envs/prod/main.tf)** - Production configuration
- **[infra/envs/prod/variables.tf](infra/envs/prod/variables.tf)** - Variable definitions
- **[infra/envs/prod/terraform.tfvars](infra/envs/prod/terraform.tfvars)** - Variable values (AI-managed)
- **[infra/envs/prod/outputs.tf](infra/envs/prod/outputs.tf)** - Output definitions

### Operations
- **[ops/policy_gate.py](ops/policy_gate.py)** - Policy evaluation engine
- **[ops/self_healing_demo.py](ops/self_healing_demo.py)** - Self-healing demonstration
- **[ops/prometheus.yml](ops/prometheus.yml)** - Prometheus configuration
- **[ops/alerts/cost-alerts.yml](ops/alerts/cost-alerts.yml)** - Alert rules
- **[ops/argocd-apps/swen-aiops.yaml](ops/argocd-apps/swen-aiops.yaml)** - ArgoCD manifest

### CI/CD
- **[.gitlab-ci.yml](.gitlab-ci.yml)** - GitLab CI/CD pipeline

---

## 🛠️ Scripts & Utilities

### Automation
- **[start-all.sh](start-all.sh)** - Start all services automatically
- **[stop-all.sh](stop-all.sh)** - Stop all services automatically

### Configuration
- **[.gitignore](.gitignore)** - Git ignore patterns
- **[LICENSE](LICENSE)** - MIT License

### Examples
- **[infra/envs/prod/ai-metadata.json.example](infra/envs/prod/ai-metadata.json.example)** - Sample AI metadata

---

## 📊 Key Features by File

### AI-Driven Optimization
- `ai-engine/engine.py` - Multi-factor scoring algorithm
- `ai-engine/simulator.py` - Real-time telemetry generation
- `ops/policy_gate.py` - Automated policy evaluation

### Real-Time Dashboard
- `dashboard/api/main.py` - REST API + WebSocket streaming
- `dashboard/ui/app.py` - Interactive 5-tab dashboard
- `dashboard/TELEMETRY_README.md` - Dashboard documentation

### GitOps Automation
- `.gitlab-ci.yml` - 5-stage CI/CD pipeline
- `ai-engine/gitops_committer.py` - Git automation
- `ops/argocd-apps/swen-aiops.yaml` - ArgoCD integration

### Self-Healing
- `ops/self_healing_demo.py` - 3 demonstration scenarios
- `ops/alerts/cost-alerts.yml` - Automated alert rules
- `docs/RUNBOOK.md` - Emergency procedures

### Infrastructure
- `infra/modules/` - Reusable Terraform modules
- `infra/envs/prod/` - Production environment
- `infra/README.md` - Infrastructure guide

---

## 🎯 Quick Access by Task

### I want to...

#### Start the Platform
→ Run `./start-all.sh`  
→ See [QUICKSTART.md](QUICKSTART.md)

#### View the Dashboard
→ Open http://localhost:8501  
→ See [dashboard/TELEMETRY_README.md](dashboard/TELEMETRY_README.md)

#### Understand the Architecture
→ Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

#### Run a Demo
→ Execute `python ops/self_healing_demo.py`  
→ See [ops/self_healing_demo.py](ops/self_healing_demo.py)

#### Deploy Infrastructure
→ Follow [infra/README.md](infra/README.md)  
→ Use [infra/envs/prod/](infra/envs/prod/)

#### Troubleshoot Issues
→ Check [docs/RUNBOOK.md](docs/RUNBOOK.md) (Troubleshooting section)  
→ Review [TESTING.md](TESTING.md)

#### Understand Policies
→ Read [ops/POLICY.md](ops/POLICY.md)  
→ Read [docs/COST_STRATEGY.md](docs/COST_STRATEGY.md)

#### Learn About AI Usage
→ Read [docs/AI_LOG.md](docs/AI_LOG.md)  
→ Review `ai-engine/engine.py`

#### Find Commands
→ See [COMMANDS.md](COMMANDS.md)  
→ Check [QUICKSTART.md](QUICKSTART.md)

#### Submit the Project
→ Review [DELIVERABLES.md](DELIVERABLES.md)  
→ Run tests from [TESTING.md](TESTING.md)

---

## 📁 Directory Structure

```
swen-aio-test/
│
├── 📄 Documentation (Root)
│   ├── README.md                    # Main overview
│   ├── QUICKSTART.md                # 5-minute guide
│   ├── COMMANDS.md                  # Command reference
│   ├── TESTING.md                   # Testing checklist
│   ├── DELIVERABLES.md              # Submission checklist
│   ├── PROJECT_SUMMARY.md           # Complete summary
│   ├── INDEX.md                     # This file
│   ├── LICENSE                      # MIT License
│   └── .gitignore                   # Git ignore patterns
│
├── 📂 ai-engine/                    # AI optimization engine
│   ├── engine.py                    # Core logic
│   ├── simulator.py                 # Telemetry generator
│   ├── gitops_committer.py          # Git automation
│   └── requirements.txt             # Dependencies
│
├── 📂 dashboard/                    # Real-time dashboard
│   ├── api/                         # Backend
│   │   ├── main.py                  # FastAPI app
│   │   └── requirements.txt         # Dependencies
│   ├── ui/                          # Frontend
│   │   ├── app.py                   # Streamlit app
│   │   └── requirements.txt         # Dependencies
│   └── TELEMETRY_README.md          # Documentation
│
├── 📂 infra/                        # Infrastructure as Code
│   ├── modules/                     # Terraform modules
│   │   ├── cluster/                 # Cluster module
│   │   └── app/                     # App module
│   ├── envs/prod/                   # Production env
│   │   ├── main.tf                  # Main config
│   │   ├── variables.tf             # Variables
│   │   ├── terraform.tfvars         # Values
│   │   ├── outputs.tf               # Outputs
│   │   └── ai-metadata.json.example # Sample metadata
│   └── README.md                    # Documentation
│
├── 📂 ops/                          # Operations
│   ├── policy_gate.py               # Policy engine
│   ├── self_healing_demo.py         # Demo script
│   ├── prometheus.yml               # Prometheus config
│   ├── alerts/                      # Alert rules
│   │   └── cost-alerts.yml          # Cost alerts
│   ├── argocd-apps/                 # ArgoCD manifests
│   │   └── swen-aiops.yaml          # App manifest
│   └── POLICY.md                    # Governance docs
│
├── 📂 docs/                         # Documentation
│   ├── RUNBOOK.md                   # Operations guide
│   ├── ARCHITECTURE.md              # Architecture docs
│   ├── COST_STRATEGY.md             # FinOps strategy
│   └── AI_LOG.md                    # AI collaboration
│
├── 🔧 Scripts
│   ├── start-all.sh                 # Start services
│   └── stop-all.sh                  # Stop services
│
└── ⚙️ CI/CD
    └── .gitlab-ci.yml               # GitLab pipeline
```

---

## 📈 Project Statistics

- **Total Files:** 35+
- **Lines of Code:** ~8,000+
- **Documentation:** ~4,000+ lines
- **Python Modules:** 6
- **Terraform Files:** 8
- **Markdown Docs:** 12
- **Shell Scripts:** 2

---

## 🔗 External Resources

### Technologies Used
- [Python](https://www.python.org/) - Primary language
- [Terraform](https://www.terraform.io/) - Infrastructure as Code
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Prometheus](https://prometheus.io/) - Monitoring
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/) - Continuous deployment

### Useful Links
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)

---

## 🎓 Learning Path

### For Beginners
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Run `./start-all.sh` and explore the dashboard
3. Read [README.md](README.md) for overview
4. Try [ops/self_healing_demo.py](ops/self_healing_demo.py)

### For Operators
1. Read [docs/RUNBOOK.md](docs/RUNBOOK.md)
2. Review [COMMANDS.md](COMMANDS.md)
3. Study [ops/POLICY.md](ops/POLICY.md)
4. Practice with [TESTING.md](TESTING.md)

### For Developers
1. Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. Study [ai-engine/engine.py](ai-engine/engine.py)
3. Explore [dashboard/api/main.py](dashboard/api/main.py)
4. Read [docs/AI_LOG.md](docs/AI_LOG.md)

### For Architects
1. Study [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. Read [docs/COST_STRATEGY.md](docs/COST_STRATEGY.md)
4. Analyze [infra/](infra/) structure

---

## ✅ Checklist for Reviewers

- [ ] Read [README.md](README.md) for project overview
- [ ] Follow [QUICKSTART.md](QUICKSTART.md) to run locally
- [ ] Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design
- [ ] Check [DELIVERABLES.md](DELIVERABLES.md) for completeness
- [ ] Run [ops/self_healing_demo.py](ops/self_healing_demo.py)
- [ ] Explore dashboard at http://localhost:8501
- [ ] Review [docs/AI_LOG.md](docs/AI_LOG.md) for transparency
- [ ] Check [TESTING.md](TESTING.md) for quality assurance

---

## 📞 Support

For questions or issues:
- Check [docs/RUNBOOK.md](docs/RUNBOOK.md) for troubleshooting
- Review [TESTING.md](TESTING.md) for common problems
- See [COMMANDS.md](COMMANDS.md) for quick reference

---

**Last Updated:** 2025-10-23  
**Version:** 1.0  
**Status:** ✅ Complete and Ready

---

**Navigate efficiently with this index!** 🗺️
