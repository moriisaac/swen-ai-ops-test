#!/usr/bin/env python3
"""
SWEN Policy Engine - FinOps + Policy Intelligence
Implements budget management, credit tracking, and approval workflows
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    AUTO_APPROVED = "auto_approved"
    ESCALATED = "escalated"
    PENDING = "pending"
    REJECTED = "rejected"

class ServiceTier(Enum):
    TIER_1_CRITICAL = "tier_1_critical"  # Stateful services
    TIER_2_IMPORTANT = "tier_2_important"  # Stateless services
    TIER_3_NON_CRITICAL = "tier_3_non_critical"  # Batch/Jobs

@dataclass
class BudgetConfig:
    """Budget configuration for cost management."""
    monthly_budget: float
    variance_threshold: float = 0.1  # 10% variance allowed
    alert_threshold: float = 0.8  # Alert at 80% of budget
    current_spend: float = 0.0
    credits_available: float = 0.0
    regional_discounts: Dict[str, float] = None
    
    def __post_init__(self):
        if self.regional_discounts is None:
            self.regional_discounts = {
                "us-east-1": 0.05,  # 5% discount
                "us-west-2": 0.03,  # 3% discount
                "eu-west-1": 0.04,  # 4% discount
                "ap-southeast-1": 0.06,  # 6% discount
            }

@dataclass
class PolicyDecision:
    """Policy evaluation result."""
    status: ApprovalStatus
    reasoning: str
    cost_delta_percent: float
    predicted_savings: float
    confidence: float
    requires_manual_approval: bool
    policy_violations: List[str]
    budget_impact: float
    credit_utilization: float

class PolicyEngine:
    """Core policy evaluation engine for FinOps and governance."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "ai-engine/policy_config.json"
        self.budget_config = self._load_budget_config()
        self.service_tiers = self._load_service_tiers()
        self.policy_history = []
        
    def _load_budget_config(self) -> BudgetConfig:
        """Load budget configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    return BudgetConfig(**config_data)
        except Exception as e:
            logger.warning(f"Failed to load budget config: {e}")
        
        # Default configuration
        return BudgetConfig(
            monthly_budget=10000.0,  # $10,000/month
            current_spend=0.0,
            credits_available=2000.0,  # $2,000 in credits
        )
    
    def _load_service_tiers(self) -> Dict[str, ServiceTier]:
        """Load service tier classifications."""
        return {
            "service1": ServiceTier.TIER_2_IMPORTANT,  # API service
            "service2": ServiceTier.TIER_1_CRITICAL,   # Database
            "service3": ServiceTier.TIER_3_NON_CRITICAL,  # Analytics
        }
    
    def _save_budget_config(self):
        """Save budget configuration."""
        try:
            config_data = {
                "monthly_budget": self.budget_config.monthly_budget,
                "variance_threshold": self.budget_config.variance_threshold,
                "alert_threshold": self.budget_config.alert_threshold,
                "current_spend": self.budget_config.current_spend,
                "credits_available": self.budget_config.credits_available,
                "regional_discounts": self.budget_config.regional_discounts
            }
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save budget config: {e}")
    
    def evaluate_policy(self, service: str, decision: Dict, metrics: Dict) -> PolicyDecision:
        """
        Evaluate AI decision against policies and determine approval status.
        
        Args:
            service: Service name
            decision: AI decision data
            metrics: Current service metrics
            
        Returns:
            PolicyDecision with approval status and reasoning
        """
        violations = []
        requires_manual = False
        
        # Extract decision details
        current_provider = decision.get('current_provider')
        recommended_provider = decision.get('recommended_provider')
        confidence = decision.get('confidence', 0.0)
        
        # Calculate cost impact
        current_cost = metrics.get(current_provider, {}).get('cost', 0)
        recommended_cost = metrics.get(recommended_provider, {}).get('cost', 0)
        cost_delta = abs(recommended_cost - current_cost)
        cost_delta_percent = (cost_delta / current_cost * 100) if current_cost > 0 else 0
        
        # Calculate predicted savings (negative cost delta = savings)
        predicted_savings = current_cost - recommended_cost
        
        # Apply regional discounts
        region = metrics.get(recommended_provider, {}).get('region', '')
        discount = self.budget_config.regional_discounts.get(region, 0.0)
        discounted_cost = recommended_cost * (1 - discount)
        actual_savings = current_cost - discounted_cost
        
        # Budget impact calculation
        budget_impact = discounted_cost - current_cost
        
        # Credit utilization
        credit_utilization = min(self.budget_config.credits_available, discounted_cost)
        
        # Policy evaluation
        
        # 1. Cost Delta Policy (≤ 5% for auto-approval)
        if cost_delta_percent > 5:
            violations.append(f"Cost delta {cost_delta_percent:.1f}% exceeds 5% threshold")
            requires_manual = True
        
        # 2. Confidence Policy (≥ 85% for auto-approval)
        if confidence < 0.85:
            violations.append(f"Confidence {confidence:.1%} below 85% threshold")
            requires_manual = True
        
        # 3. Predicted Savings Policy (≥ $50/month for auto-approval)
        if predicted_savings < 50:
            violations.append(f"Predicted savings ${predicted_savings:.2f} below $50 threshold")
            requires_manual = True
        
        # 4. Service Tier Policy
        service_tier = self.service_tiers.get(service, ServiceTier.TIER_2_IMPORTANT)
        if service_tier == ServiceTier.TIER_1_CRITICAL:
            violations.append("Tier 1 critical service requires manual approval")
            requires_manual = True
        
        # 5. Budget Impact Policy
        projected_monthly_impact = budget_impact * 24 * 30
        if abs(projected_monthly_impact) > self.budget_config.monthly_budget * 0.1:
            violations.append(f"Monthly budget impact ${projected_monthly_impact:.2f} exceeds 10% of budget")
            requires_manual = True
        
        # 6. Credit Availability Policy
        if discounted_cost > self.budget_config.credits_available:
            violations.append(f"Cost ${discounted_cost:.2f} exceeds available credits ${self.budget_config.credits_available:.2f}")
            requires_manual = True
        
        # Determine approval status
        if not violations:
            status = ApprovalStatus.AUTO_APPROVED
            reasoning = f"Auto-approved: All policy criteria met (confidence: {confidence:.1%}, savings: ${actual_savings:.2f}/month)"
        elif requires_manual:
            status = ApprovalStatus.ESCALATED
            reasoning = f"Escalated for manual review: {len(violations)} policy violations"
        else:
            status = ApprovalStatus.PENDING
            reasoning = "Pending policy evaluation"
        
        # Create policy decision
        policy_decision = PolicyDecision(
            status=status,
            reasoning=reasoning,
            cost_delta_percent=cost_delta_percent,
            predicted_savings=actual_savings,
            confidence=confidence,
            requires_manual_approval=requires_manual,
            policy_violations=violations,
            budget_impact=budget_impact,
            credit_utilization=credit_utilization
        )
        
        # Log policy decision
        self._log_policy_decision(service, decision, policy_decision)
        
        return policy_decision
    
    def _log_policy_decision(self, service: str, decision: Dict, policy_decision: PolicyDecision):
        """Log policy decision for audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": service,
            "decision_id": decision.get('timestamp'),
            "policy_status": policy_decision.status.value,
            "reasoning": policy_decision.reasoning,
            "cost_delta_percent": policy_decision.cost_delta_percent,
            "predicted_savings": policy_decision.predicted_savings,
            "confidence": policy_decision.confidence,
            "policy_violations": policy_decision.policy_violations,
            "budget_impact": policy_decision.budget_impact,
            "credit_utilization": policy_decision.credit_utilization
        }
        
        self.policy_history.append(log_entry)
        
        # Keep only last 1000 decisions
        if len(self.policy_history) > 1000:
            self.policy_history = self.policy_history[-1000:]
    
    def update_budget(self, cost_change: float):
        """Update current spend in budget."""
        self.budget_config.current_spend += cost_change
        self._save_budget_config()
    
    def apply_credits(self, amount: float) -> float:
        """Apply credits to cost and return remaining cost."""
        applied = min(amount, self.budget_config.credits_available)
        self.budget_config.credits_available -= applied
        self._save_budget_config()
        return amount - applied
    
    def get_budget_status(self) -> Dict:
        """Get current budget status."""
        utilization_percent = (self.budget_config.current_spend / self.budget_config.monthly_budget) * 100
        
        return {
            "monthly_budget": self.budget_config.monthly_budget,
            "current_spend": self.budget_config.current_spend,
            "utilization_percent": utilization_percent,
            "credits_available": self.budget_config.credits_available,
            "budget_remaining": self.budget_config.monthly_budget - self.budget_config.current_spend,
            "alert_threshold": self.budget_config.alert_threshold,
            "is_over_budget": utilization_percent > 100,
            "needs_alert": utilization_percent > (self.budget_config.alert_threshold * 100),
            "regional_discounts": self.budget_config.regional_discounts
        }
    
    def get_policy_stats(self) -> Dict:
        """Get policy statistics."""
        if not self.policy_history:
            return {
                "total_decisions": 0,
                "auto_approved": 0,
                "escalated": 0,
                "pending": 0,
                "rejected": 0
            }
        
        stats = {
            "total_decisions": len(self.policy_history),
            "auto_approved": 0,
            "escalated": 0,
            "pending": 0,
            "rejected": 0
        }
        
        for decision in self.policy_history:
            status = decision.get('policy_status')
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def get_recent_policy_decisions(self, limit: int = 20) -> List[Dict]:
        """Get recent policy decisions."""
        return self.policy_history[-limit:] if self.policy_history else []


def main():
    """Test the policy engine."""
    engine = PolicyEngine()
    
    # Test policy evaluation
    test_decision = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "service1",
        "current_provider": "aws",
        "recommended_provider": "alibaba",
        "confidence": 0.9
    }
    
    test_metrics = {
        "aws": {"cost": 10.0, "region": "us-east-1"},
        "alibaba": {"cost": 8.0, "region": "ap-southeast-1"}
    }
    
    result = engine.evaluate_policy("service1", test_decision, test_metrics)
    print(f"Policy Decision: {result.status.value}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Violations: {result.policy_violations}")
    
    # Test budget status
    budget_status = engine.get_budget_status()
    print(f"\nBudget Status: {budget_status}")


if __name__ == "__main__":
    main()
