#!/usr/bin/env python3
"""
Policy Gate for AI Recommendations
Evaluates AI-generated infrastructure changes against policy rules
"""

import json
import sys
import os
from typing import Dict, Tuple

class PolicyGate:
    """Policy evaluation engine for AI recommendations."""
    
    # Policy thresholds
    AUTO_APPROVE_COST_DELTA = 0.05  # 5% cost change threshold
    AUTO_APPROVE_CONFIDENCE = 0.85  # 85% confidence threshold
    AUTO_APPROVE_SAVINGS = 50.0     # $50/month minimum savings
    
    def __init__(self, metadata_path: str = "infra/envs/prod/ai-metadata.json"):
        self.metadata_path = metadata_path
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load AI recommendation metadata."""
        try:
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Metadata file not found: {self.metadata_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in metadata file: {e}")
            sys.exit(1)
    
    def evaluate(self) -> Tuple[bool, str]:
        """
        Evaluate the AI recommendation against policy rules.
        
        Returns:
            Tuple of (should_auto_approve, reason)
        """
        service = self.metadata.get('service', 'unknown')
        cost_delta = self.metadata.get('cost_delta', 1.0)
        confidence = self.metadata.get('confidence', 0.0)
        predicted_savings = self.metadata.get('predicted_savings', 0.0)
        change_type = self.metadata.get('change_type', 'unknown')
        affects_stateful = self.metadata.get('affects_stateful', False)
        traffic_impact = self.metadata.get('traffic_impact_percent', 0.0)
        
        print(f"\n=== Policy Evaluation for {service} ===")
        print(f"Cost Delta: {cost_delta:.2%}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Predicted Savings: ${predicted_savings:.2f}/month")
        print(f"Change Type: {change_type}")
        print(f"Affects Stateful: {affects_stateful}")
        print(f"Traffic Impact: {traffic_impact:.1f}%")
        
        # Rule 1: Never auto-approve stateful service changes
        if affects_stateful:
            return False, "Change affects stateful services (requires manual approval)"
        
        # Rule 2: Never auto-approve high traffic impact changes
        if traffic_impact > 10.0:
            return False, f"High traffic impact ({traffic_impact:.1f}% > 10%)"
        
        # Rule 3: Check confidence threshold
        if confidence < self.AUTO_APPROVE_CONFIDENCE:
            return False, f"Low confidence ({confidence:.2%} < {self.AUTO_APPROVE_CONFIDENCE:.2%})"
        
        # Rule 4: Check cost delta threshold
        if cost_delta > self.AUTO_APPROVE_COST_DELTA:
            return False, f"Cost delta too high ({cost_delta:.2%} > {self.AUTO_APPROVE_COST_DELTA:.2%})"
        
        # Rule 5: Check minimum savings threshold
        if predicted_savings < self.AUTO_APPROVE_SAVINGS:
            return False, f"Savings below threshold (${predicted_savings:.2f} < ${self.AUTO_APPROVE_SAVINGS})"
        
        # Rule 6: Only auto-approve provider/region changes for stateless services
        if change_type not in ['provider_change', 'region_change', 'instance_type_change']:
            return False, f"Change type '{change_type}' requires manual review"
        
        # All checks passed
        return True, f"Auto-approved: High confidence ({confidence:.2%}), low risk, savings ${predicted_savings:.2f}/month"
    
    def generate_report(self) -> Dict:
        """Generate a detailed policy evaluation report."""
        auto_approve, reason = self.evaluate()
        
        return {
            'auto_approve': auto_approve,
            'reason': reason,
            'metadata': self.metadata,
            'policy_version': '1.0',
            'evaluated_at': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


def main():
    """Main entry point for policy gate."""
    print("SWEN AIOps Policy Gate v1.0")
    print("=" * 50)
    
    # Initialize policy gate
    gate = PolicyGate()
    
    # Evaluate policy
    auto_approve, reason = gate.evaluate()
    
    # Generate report
    report = gate.generate_report()
    
    # Save report
    report_path = "infra/envs/prod/policy-report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n=== Policy Decision ===")
    print(f"Auto-Approve: {auto_approve}")
    print(f"Reason: {reason}")
    print(f"\nReport saved to: {report_path}")
    
    # Exit with appropriate code
    if auto_approve:
        print("\n✓ APPROVED: Change meets auto-approval criteria")
        sys.exit(0)
    else:
        print("\n⚠ MANUAL REVIEW REQUIRED")
        sys.exit(1)


if __name__ == "__main__":
    main()
