#!/usr/bin/env python3
"""
Self-Healing Demonstration Script

This script demonstrates the self-healing capabilities of the SWEN AIOps platform
by simulating failures and showing automated recovery.
"""

import json
import time
import logging
import sys
from datetime import datetime
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SelfHealingDemo:
    """Demonstrates self-healing scenarios."""
    
    def __init__(self, telemetry_path: str = "ai-engine/latest_telemetry.json"):
        self.telemetry_path = telemetry_path
        self.event_log = []
    
    def log_event(self, event_type: str, message: str, data: Dict = None):
        """Log a self-healing event."""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'message': message,
            'data': data or {}
        }
        self.event_log.append(event)
        logger.info(f"[{event_type}] {message}")
    
    def save_event_log(self, output_path: str = "ops/self_heal_event.log"):
        """Save event log to file."""
        with open(output_path, 'w') as f:
            for event in self.event_log:
                f.write(json.dumps(event) + '\n')
        logger.info(f"Event log saved to {output_path}")
    
    def read_telemetry(self) -> dict:
        """Read current telemetry data."""
        try:
            with open(self.telemetry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read telemetry: {e}")
            return {}
    
    def write_telemetry(self, data: dict):
        """Write telemetry data."""
        try:
            with open(self.telemetry_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write telemetry: {e}")
    
    def scenario_1_region_outage(self):
        """
        Scenario 1: Simulate region outage
        
        Steps:
        1. Show normal operation
        2. Simulate AWS region failure (high latency, no GPUs)
        3. AI engine detects issue
        4. AI recommends migration to Alibaba
        5. GitOps applies change
        6. Service restored on Alibaba
        """
        print("\n" + "="*70)
        print("SCENARIO 1: Region Outage Self-Healing")
        print("="*70)
        
        # Step 1: Normal operation
        self.log_event("NORMAL", "System operating normally")
        telemetry = self.read_telemetry()
        
        if not telemetry:
            logger.error("No telemetry data available")
            return
        
        service = "service1"
        if service not in telemetry:
            logger.error(f"Service {service} not found in telemetry")
            return
        
        current_provider = telemetry[service].get('current_provider', 'aws')
        
        print(f"\n✓ Service '{service}' running on {current_provider.upper()}")
        print(f"  Cost: ${telemetry[service][current_provider]['cost']:.2f}/hr")
        print(f"  Latency: {telemetry[service][current_provider]['latency']:.1f}ms")
        print(f"  GPUs: {telemetry[service][current_provider]['available_gpus']}")
        
        time.sleep(2)
        
        # Step 2: Simulate outage
        print(f"\n⚠️  SIMULATING {current_provider.upper()} REGION OUTAGE...")
        self.log_event("OUTAGE_DETECTED", f"{current_provider} region experiencing issues", {
            'service': service,
            'provider': current_provider
        })
        
        # Modify telemetry to simulate outage
        telemetry[service][current_provider]['latency'] = 9999
        telemetry[service][current_provider]['available_gpus'] = 0
        telemetry[service][current_provider]['cost'] = 5.0  # Spike in cost
        
        self.write_telemetry(telemetry)
        
        print(f"  Latency: 9999ms (CRITICAL)")
        print(f"  GPUs: 0 (UNAVAILABLE)")
        print(f"  Cost: $5.00/hr (SPIKE)")
        
        time.sleep(2)
        
        # Step 3: AI detection
        print("\n🤖 AI ENGINE ANALYZING...")
        self.log_event("AI_ANALYSIS", "AI engine evaluating alternative providers")
        
        # Calculate scores for alternative provider
        alt_provider = 'alibaba' if current_provider == 'aws' else 'aws'
        alt_data = telemetry[service][alt_provider]
        
        print(f"\n  Alternative: {alt_provider.upper()}")
        print(f"  Cost: ${alt_data['cost']:.2f}/hr")
        print(f"  Latency: {alt_data['latency']:.1f}ms")
        print(f"  GPUs: {alt_data['available_gpus']}")
        
        time.sleep(2)
        
        # Step 4: AI recommendation
        predicted_savings = (5.0 - alt_data['cost']) * 730  # Monthly
        confidence = 0.98  # High confidence due to clear failure
        
        print(f"\n✅ AI RECOMMENDATION:")
        print(f"  Action: Migrate {service} to {alt_provider.upper()}")
        print(f"  Confidence: {confidence:.1%}")
        print(f"  Predicted Savings: ${predicted_savings:.2f}/month")
        print(f"  Reason: Current provider experiencing critical issues")
        
        self.log_event("AI_RECOMMENDATION", f"Recommend migration to {alt_provider}", {
            'service': service,
            'from_provider': current_provider,
            'to_provider': alt_provider,
            'confidence': confidence,
            'predicted_savings': predicted_savings
        })
        
        time.sleep(2)
        
        # Step 5: GitOps (simulated)
        print(f"\n🔄 GITOPS WORKFLOW:")
        print(f"  1. Creating branch: ai-recommendation/{service}-emergency")
        print(f"  2. Updating terraform.tfvars: {service}_provider = \"{alt_provider}\"")
        print(f"  3. Committing changes...")
        print(f"  4. Triggering CI/CD pipeline...")
        print(f"  5. Running terraform plan...")
        print(f"  6. Auto-approving (emergency override)...")
        print(f"  7. Applying infrastructure changes...")
        
        self.log_event("GITOPS_INITIATED", "GitOps workflow started", {
            'branch': f'ai-recommendation/{service}-emergency',
            'auto_approved': True,
            'reason': 'emergency_override'
        })
        
        time.sleep(3)
        
        # Step 6: Recovery
        print(f"\n✅ SELF-HEALING COMPLETE:")
        
        # Update telemetry to show recovery
        telemetry[service]['current_provider'] = alt_provider
        self.write_telemetry(telemetry)
        
        print(f"  Service '{service}' migrated to {alt_provider.upper()}")
        print(f"  Cost: ${alt_data['cost']:.2f}/hr (NORMAL)")
        print(f"  Latency: {alt_data['latency']:.1f}ms (NORMAL)")
        print(f"  GPUs: {alt_data['available_gpus']} (AVAILABLE)")
        print(f"  Status: HEALTHY ✓")
        
        self.log_event("RECOVERY_COMPLETE", f"Service restored on {alt_provider}", {
            'service': service,
            'provider': alt_provider,
            'recovery_time_seconds': 10  # Simulated
        })
        
        print(f"\n📊 RECOVERY METRICS:")
        print(f"  Detection Time: 2 seconds")
        print(f"  Decision Time: 3 seconds")
        print(f"  Execution Time: 5 seconds")
        print(f"  Total Recovery Time: 10 seconds")
        print(f"  Downtime: Minimal (rolling deployment)")
    
    def scenario_2_cost_spike(self):
        """
        Scenario 2: Sudden cost spike detection and mitigation
        """
        print("\n" + "="*70)
        print("SCENARIO 2: Cost Spike Self-Healing")
        print("="*70)
        
        self.log_event("NORMAL", "Monitoring costs")
        telemetry = self.read_telemetry()
        
        service = "service2"
        if service not in telemetry:
            logger.error(f"Service {service} not found")
            return
        
        current_provider = telemetry[service].get('current_provider', 'aws')
        original_cost = telemetry[service][current_provider]['cost']
        
        print(f"\n✓ Service '{service}' on {current_provider.upper()}")
        print(f"  Normal Cost: ${original_cost:.2f}/hr")
        
        time.sleep(2)
        
        # Simulate cost spike
        print(f"\n⚠️  COST SPIKE DETECTED!")
        spike_cost = original_cost * 2.5
        telemetry[service][current_provider]['cost'] = spike_cost
        self.write_telemetry(telemetry)
        
        print(f"  New Cost: ${spike_cost:.2f}/hr (+150%)")
        print(f"  Trigger: Prometheus alert 'HighServiceCost'")
        
        self.log_event("COST_SPIKE", f"Cost increased by 150%", {
            'service': service,
            'provider': current_provider,
            'original_cost': original_cost,
            'new_cost': spike_cost
        })
        
        time.sleep(2)
        
        # AI response
        print(f"\n🤖 AI ENGINE RESPONDING...")
        alt_provider = 'alibaba' if current_provider == 'aws' else 'aws'
        alt_cost = telemetry[service][alt_provider]['cost']
        
        savings = (spike_cost - alt_cost) * 730
        
        print(f"  Evaluating alternatives...")
        print(f"  {alt_provider.upper()} Cost: ${alt_cost:.2f}/hr")
        print(f"  Potential Savings: ${savings:.2f}/month")
        
        self.log_event("AI_RECOMMENDATION", f"Migrate to {alt_provider} to reduce costs", {
            'service': service,
            'savings': savings,
            'confidence': 0.92
        })
        
        print(f"\n✅ MIGRATION INITIATED")
        print(f"  Moving {service} to {alt_provider.upper()}...")
        
        time.sleep(2)
        
        telemetry[service]['current_provider'] = alt_provider
        self.write_telemetry(telemetry)
        
        print(f"\n✅ COST OPTIMIZATION COMPLETE:")
        print(f"  Service: {service}")
        print(f"  Provider: {alt_provider.upper()}")
        print(f"  New Cost: ${alt_cost:.2f}/hr")
        print(f"  Savings: ${savings:.2f}/month")
        
        self.log_event("OPTIMIZATION_COMPLETE", "Cost normalized", {
            'service': service,
            'provider': alt_provider,
            'cost': alt_cost
        })
    
    def scenario_3_performance_degradation(self):
        """
        Scenario 3: Performance degradation and automatic optimization
        """
        print("\n" + "="*70)
        print("SCENARIO 3: Performance Degradation Self-Healing")
        print("="*70)
        
        telemetry = self.read_telemetry()
        service = "service3"
        
        if service not in telemetry:
            logger.error(f"Service {service} not found")
            return
        
        current_provider = telemetry[service].get('current_provider', 'alibaba')
        original_latency = telemetry[service][current_provider]['latency']
        
        print(f"\n✓ Service '{service}' on {current_provider.upper()}")
        print(f"  Latency: {original_latency:.1f}ms")
        
        time.sleep(2)
        
        # Simulate degradation
        print(f"\n⚠️  PERFORMANCE DEGRADATION DETECTED!")
        degraded_latency = original_latency * 3
        telemetry[service][current_provider]['latency'] = degraded_latency
        self.write_telemetry(telemetry)
        
        print(f"  New Latency: {degraded_latency:.1f}ms (+200%)")
        print(f"  Trigger: Prometheus alert 'HighLatency'")
        
        self.log_event("PERFORMANCE_DEGRADATION", "Latency increased significantly", {
            'service': service,
            'provider': current_provider,
            'original_latency': original_latency,
            'new_latency': degraded_latency
        })
        
        time.sleep(2)
        
        # AI analysis
        print(f"\n🤖 AI ENGINE ANALYZING...")
        alt_provider = 'aws' if current_provider == 'alibaba' else 'alibaba'
        alt_latency = telemetry[service][alt_provider]['latency']
        
        print(f"  Alternative {alt_provider.upper()} latency: {alt_latency:.1f}ms")
        print(f"  Improvement: {degraded_latency - alt_latency:.1f}ms")
        
        self.log_event("AI_RECOMMENDATION", f"Switch to {alt_provider} for better performance", {
            'service': service,
            'latency_improvement': degraded_latency - alt_latency,
            'confidence': 0.89
        })
        
        print(f"\n✅ REROUTING TRAFFIC...")
        time.sleep(2)
        
        telemetry[service]['current_provider'] = alt_provider
        self.write_telemetry(telemetry)
        
        print(f"\n✅ PERFORMANCE RESTORED:")
        print(f"  Service: {service}")
        print(f"  Provider: {alt_provider.upper()}")
        print(f"  Latency: {alt_latency:.1f}ms (NORMAL)")
        
        self.log_event("PERFORMANCE_RESTORED", "Latency normalized", {
            'service': service,
            'provider': alt_provider,
            'latency': alt_latency
        })
    
    def run_all_scenarios(self):
        """Run all self-healing scenarios."""
        print("\n" + "="*70)
        print("SWEN AIOPS SELF-HEALING DEMONSTRATION")
        print("="*70)
        print("\nThis demo will showcase three self-healing scenarios:")
        print("1. Region Outage Recovery")
        print("2. Cost Spike Mitigation")
        print("3. Performance Degradation Response")
        print("\nPress Enter to continue...")
        input()
        
        try:
            # Run scenarios
            self.scenario_1_region_outage()
            time.sleep(3)
            
            self.scenario_2_cost_spike()
            time.sleep(3)
            
            self.scenario_3_performance_degradation()
            
            # Summary
            print("\n" + "="*70)
            print("DEMONSTRATION COMPLETE")
            print("="*70)
            print(f"\nTotal Events: {len(self.event_log)}")
            print(f"Recovery Time: < 15 seconds per incident")
            print(f"Success Rate: 100%")
            print(f"\nEvent log saved to: ops/self_heal_event.log")
            
            # Save event log
            self.save_event_log()
            
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
            self.save_event_log()
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            self.save_event_log()


def main():
    """Main entry point."""
    demo = SelfHealingDemo()
    demo.run_all_scenarios()


if __name__ == "__main__":
    main()
