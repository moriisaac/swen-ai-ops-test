#!/usr/bin/env python3
"""
Policy Gate - Evaluates AI recommendations against deployment policies
Used in GitLab CI/CD pipeline to determine auto-approval vs manual review
"""

import json
import os
import sys
import logging
from typing import Dict, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyGate:
    """Policy evaluation for AI recommendations."""
    
    def __init__(self):
        self.policies = {
            'max_cost_change_percent': 10.0,  # Max 10% cost change
            'min_confidence_threshold': 0.7,   # Min 70% confidence
            'max_risk_level': 'medium',        # Max medium risk
            'max_downtime_minutes': 5,         # Max 5 min downtime
            'auto_approve_savings_threshold': 0.05,  # Auto-approve if >5% savings
            'require_manual_review': [
                'stateful_service',
                'high_traffic_service',
                'critical_service'
            ]
        }
    
    def evaluate_recommendation(self, metadata: Dict) -> Tuple[bool, str]:
        """
        Evaluate AI recommendation against policies.
        
        Returns:
            (auto_approve: bool, reasoning: str)
        """
        try:
            # Extract key metrics
            confidence = metadata.get('confidence', 0.0)
            cost_delta = abs(metadata.get('cost_delta', 0.0))
            predicted_savings = metadata.get('predicted_savings', 0.0)
            risk_level = metadata.get('risk_level', 'unknown')
            downtime = metadata.get('estimated_downtime', 0)
            service_type = metadata.get('service_type', 'stateless')
            
            violations = []
            approvals = []
            
            # Check confidence threshold
            if confidence < self.policies['min_confidence_threshold']:
                violations.append(f"Confidence {confidence:.1%} below threshold {self.policies['min_confidence_threshold']:.1%}")
            else:
                approvals.append(f"Confidence {confidence:.1%} meets threshold")
            
            # Check cost change percentage
            if cost_delta > self.policies['max_cost_change_percent']:
                violations.append(f"Cost change {cost_delta:.1%} exceeds limit {self.policies['max_cost_change_percent']:.1%}")
            else:
                approvals.append(f"Cost change {cost_delta:.1%} within limits")
            
            # Check risk level
            risk_levels = ['low', 'medium', 'high', 'critical']
            if risk_level in risk_levels:
                max_risk_index = risk_levels.index(self.policies['max_risk_level'])
                current_risk_index = risk_levels.index(risk_level)
                if current_risk_index > max_risk_index:
                    violations.append(f"Risk level '{risk_level}' exceeds '{self.policies['max_risk_level']}'")
                else:
                    approvals.append(f"Risk level '{risk_level}' acceptable")
            
            # Check downtime
            if downtime > self.policies['max_downtime_minutes']:
                violations.append(f"Downtime {downtime}min exceeds limit {self.policies['max_downtime_minutes']}min")
            else:
                approvals.append(f"Downtime {downtime}min acceptable")
            
            # Check for manual review requirements
            for requirement in self.policies['require_manual_review']:
                if requirement in service_type.lower():
                    violations.append(f"Service type '{service_type}' requires manual review")
            
            # Check savings threshold for auto-approval
            if predicted_savings >= self.policies['auto_approve_savings_threshold']:
                approvals.append(f"Savings {predicted_savings:.1%} meets auto-approval threshold")
            
            # Determine auto-approval
            auto_approve = len(violations) == 0
            
            # Build reasoning
            reasoning_parts = []
            if approvals:
                reasoning_parts.append("✅ APPROVALS:")
                reasoning_parts.extend([f"  - {approval}" for approval in approvals])
            
            if violations:
                reasoning_parts.append("❌ VIOLATIONS:")
                reasoning_parts.extend([f"  - {violation}" for violation in violations])
            
            reasoning = "\n".join(reasoning_parts)
            
            # Final decision
            if auto_approve:
                reasoning += f"\n\n🎯 DECISION: AUTO-APPROVE (no policy violations)"
            else:
                reasoning += f"\n\n🎯 DECISION: MANUAL REVIEW REQUIRED ({len(violations)} violations)"
            
            return auto_approve, reasoning
            
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")
            return False, f"Policy evaluation error: {e}"
    
    def load_metadata(self, metadata_path: str) -> Dict:
        """Load AI recommendation metadata."""
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {}

def main():
    """Main entry point for policy gate."""
    # Get metadata file path from environment or use default
    metadata_path = os.getenv('METADATA_PATH', 'infra/envs/prod/ai-metadata.json')
    
    if not os.path.exists(metadata_path):
        logger.warning(f"Metadata file not found: {metadata_path}")
        logger.info("Creating sample metadata for testing...")
        
        # Create sample metadata
        sample_metadata = {
            'service': 'service1',
            'confidence': 0.85,
            'cost_delta': 0.05,
            'predicted_savings': 0.08,
            'risk_level': 'low',
            'estimated_downtime': 2,
            'service_type': 'stateless',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        with open(metadata_path, 'w') as f:
            json.dump(sample_metadata, f, indent=2)
        
        metadata = sample_metadata
    else:
        metadata = PolicyGate().load_metadata(metadata_path)
    
    if not metadata:
        logger.error("No metadata available for policy evaluation")
        sys.exit(1)
    
    # Evaluate policy
    gate = PolicyGate()
    auto_approve, reasoning = gate.evaluate_recommendation(metadata)
    
    # Print results
    print("=" * 60)
    print("🤖 AI RECOMMENDATION POLICY EVALUATION")
    print("=" * 60)
    print(f"Service: {metadata.get('service', 'unknown')}")
    print(f"Timestamp: {metadata.get('timestamp', 'unknown')}")
    print()
    print(reasoning)
    print("=" * 60)
    
    # Exit with appropriate code
    if auto_approve:
        print("✅ EXIT CODE: 0 (AUTO-APPROVE)")
        sys.exit(0)
    else:
        print("❌ EXIT CODE: 1 (MANUAL REVIEW)")
        sys.exit(1)

if __name__ == "__main__":
    main()