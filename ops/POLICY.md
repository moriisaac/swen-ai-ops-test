# SWEN AIOps Policy Framework

This document defines the governance policies for AI-driven infrastructure decisions.

## Policy Version

**Version:** 1.0  
**Last Updated:** 2025-10-22  
**Owner:** DevOps/Platform Team

---

## 1. Auto-Approval Policy

### 1.1 Criteria for Automatic Approval

An AI recommendation will be **automatically approved and applied** if ALL of the following conditions are met:

#### Cost Criteria
- **Cost Delta** ≤ 5% of current cost
- **Predicted Monthly Savings** ≥ $50
- **Budget Impact** does not exceed allocated variance

#### Confidence Criteria
- **AI Confidence Score** ≥ 85%
- **Historical Accuracy** of similar decisions ≥ 80%

#### Risk Criteria
- **Change Type** is one of:
  - Provider change (AWS ↔ Alibaba)
  - Region change within same provider
  - Instance type change (same family)
- **Affects Stateful Services** = NO
- **Traffic Impact** ≤ 10% of total traffic
- **No Database Changes** involved

#### Operational Criteria
- **Business Hours** (optional): Changes during maintenance windows
- **No Active Incidents** in the target environment
- **Rollback Plan** is available and tested

### 1.2 Auto-Approval Workflow

```
AI Decision → Policy Gate → Auto-Approve Check
                ↓
            [PASS] → Terraform Plan → Auto-Apply → Notify
                ↓
            [FAIL] → Create MR → Manual Review Required
```

---

## 2. Manual Approval Policy

### 2.1 Scenarios Requiring Human Review

The following changes **ALWAYS require manual approval**:

#### High-Impact Changes
- Cost delta > 5%
- Traffic impact > 10%
- Changes affecting > 3 services simultaneously
- Predicted savings < $50/month

#### Stateful Services
- Database migrations
- Storage tier changes
- Persistent volume modifications
- State management changes

#### Security-Sensitive Changes
- Network topology changes
- Security group modifications
- IAM role changes
- Encryption configuration changes

#### Low Confidence
- AI confidence < 85%
- Insufficient historical data
- Conflicting metrics
- Anomalous patterns detected

### 2.2 Manual Review Process

1. **AI creates Merge Request** with detailed explanation
2. **Policy Gate** labels MR with risk level
3. **Platform Team** reviews within 4 business hours
4. **Approval requires** 2 reviewers for critical changes
5. **Apply** is executed manually after approval

---

## 3. Rollback Policy

### 3.1 Automatic Rollback Triggers

Automatic rollback is initiated if:

- **Health Check Failures** > 3 consecutive checks (30 seconds)
- **Error Rate** increases by > 50% within 5 minutes
- **Latency** increases by > 100% within 5 minutes
- **Cost** increases by > 20% within 1 hour (unexpected)

### 3.2 Manual Rollback

- Available via GitLab CI/CD manual job
- Reverts to last known good state
- Preserves logs and metrics for analysis
- Requires incident report within 24 hours

### 3.3 Rollback SLA

- **Detection:** < 2 minutes
- **Decision:** < 3 minutes
- **Execution:** < 5 minutes
- **Total:** < 10 minutes from issue to rollback completion

---

## 4. Change Windows

### 4.1 Standard Change Windows

- **Low-Risk Changes:** Anytime (auto-approved)
- **Medium-Risk Changes:** Business hours (manual approval)
- **High-Risk Changes:** Maintenance windows only

### 4.2 Maintenance Windows

- **Weekly:** Saturday 02:00-06:00 UTC
- **Emergency:** As needed with incident commander approval

---

## 5. Cost Governance

### 5.1 Budget Thresholds

| Environment | Monthly Budget | Alert Threshold | Hard Limit |
|-------------|----------------|-----------------|------------|
| Production  | $10,000        | $8,000 (80%)    | $12,000    |
| Staging     | $2,000         | $1,600 (80%)    | $2,500     |
| Development | $500           | $400 (80%)      | $600       |

### 5.2 Cost Optimization Targets

- **Minimum Savings per Decision:** $50/month
- **Target Annual Savings:** 15% of infrastructure budget
- **ROI Threshold:** 3x (savings vs. operational cost)

### 5.3 Provider Credits Management

- Track available credits per provider
- Prioritize providers with expiring credits
- Factor credits into cost calculations (negative cost)
- Alert when credits < 10% of monthly spend

---

## 6. Service Classification

### 6.1 Service Tiers

#### Tier 1: Critical (Stateful)
- **Examples:** Databases, message queues, storage
- **Policy:** Manual approval required
- **SLA:** 99.9% uptime
- **Backup:** Automated, tested monthly

#### Tier 2: Important (Stateless)
- **Examples:** API services, web servers
- **Policy:** Auto-approval with constraints
- **SLA:** 99.5% uptime
- **Backup:** Configuration only

#### Tier 3: Non-Critical (Batch/Jobs)
- **Examples:** Analytics, reporting, ML training
- **Policy:** Full auto-approval
- **SLA:** Best effort
- **Backup:** Not required

### 6.2 Service Tagging

All services must be tagged:
```hcl
tags = {
  Tier           = "1|2|3"
  Stateful       = "true|false"
  AIManaged      = "true|false"
  CostCenter     = "engineering|product|..."
  Owner          = "team-name"
}
```

---

## 7. Compliance & Audit

### 7.1 Audit Trail Requirements

Every AI decision must log:
- Timestamp (UTC)
- Service affected
- Current vs. recommended state
- Metrics snapshot
- Confidence score
- Approval method (auto/manual)
- Approver (if manual)
- Outcome (success/failure/rollback)

### 7.2 Retention Policy

- **Decision Logs:** 2 years
- **Telemetry Data:** 90 days
- **Terraform State:** Indefinite (versioned)
- **Audit Reports:** 7 years

### 7.3 Compliance Checks

- **Weekly:** Cost variance analysis
- **Monthly:** Policy effectiveness review
- **Quarterly:** Security audit of AI decisions
- **Annually:** Full policy review and update

---

## 8. Escalation Procedures

### 8.1 Escalation Levels

#### Level 1: Automated Alert
- Slack/Email notification
- Dashboard warning
- No action required if within thresholds

#### Level 2: Team Notification
- On-call engineer notified
- Review required within 1 hour
- Can approve or reject AI recommendation

#### Level 3: Manager Approval
- Cost impact > $1,000/month
- Multiple service impact
- Security implications
- Approval required within 4 hours

#### Level 4: Executive Approval
- Cost impact > $10,000/month
- Architecture changes
- Vendor changes
- Approval required within 24 hours

### 8.2 Emergency Override

- **Who:** On-call incident commander
- **When:** Active P0/P1 incident
- **Process:** Override policy, apply change, document in incident report
- **Follow-up:** Post-incident review within 48 hours

---

## 9. AI Model Governance

### 9.1 Model Validation

- **Training Data:** Minimum 30 days of telemetry
- **Validation:** 80% accuracy on test set
- **Monitoring:** Track prediction accuracy weekly
- **Retraining:** When accuracy drops below 75%

### 9.2 Explainability Requirements

Every decision must include:
- Human-readable explanation
- Top 3 factors influencing decision
- Confidence score breakdown
- Alternative options considered

### 9.3 Bias Prevention

- Monitor for provider bias
- Ensure balanced training data
- Regular fairness audits
- Override mechanism for suspected bias

---

## 10. Exception Handling

### 10.1 Policy Exceptions

Exceptions to this policy require:
- Written justification
- Risk assessment
- Approval from Platform Lead
- Documentation in exception log
- Expiration date (max 90 days)

### 10.2 Emergency Procedures

In case of:
- **Provider Outage:** Immediate manual override allowed
- **Security Incident:** Disable AI automation until resolved
- **Data Quality Issues:** Pause AI decisions, investigate

---

## 11. Policy Review & Updates

### 11.1 Review Schedule

- **Monthly:** Metrics review, threshold adjustments
- **Quarterly:** Policy effectiveness assessment
- **Annually:** Full policy rewrite if needed

### 11.2 Stakeholders

- Platform Engineering Team
- FinOps Team
- Security Team
- Engineering Leadership

### 11.3 Change Process

1. Propose change with rationale
2. Review with stakeholders
3. Test in staging environment
4. Document and communicate
5. Implement with monitoring
6. Review after 30 days

---

## 12. Metrics & KPIs

### 12.1 Policy Effectiveness Metrics

- **Auto-Approval Rate:** Target 70-80%
- **Rollback Rate:** Target < 5%
- **Cost Savings:** Track actual vs. predicted
- **Decision Accuracy:** Target > 85%
- **Time to Apply:** Target < 15 minutes

### 12.2 Reporting

- **Daily:** Cost dashboard
- **Weekly:** Decision summary
- **Monthly:** Policy compliance report
- **Quarterly:** Executive summary

---

## Appendix A: Decision Matrix

| Criteria | Auto-Approve | Manual Review | Reject |
|----------|--------------|---------------|--------|
| Cost Delta | ≤ 5% | 5-20% | > 20% |
| Confidence | ≥ 85% | 70-85% | < 70% |
| Stateful | No | - | Yes |
| Traffic Impact | ≤ 10% | 10-50% | > 50% |
| Savings | ≥ $50 | $10-$50 | < $10 |

---

## Appendix B: Contact Information

- **Platform Team:** platform@swen.ai
- **On-Call:** +1-XXX-XXX-XXXX
- **Slack:** #swen-aiops
- **Incident Management:** incidents@swen.ai

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-22 | Platform Team | Initial release |
