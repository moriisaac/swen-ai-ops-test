import json
import os
import time
import logging
import subprocess
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Optional
import numpy as np
from git import Repo, GitCommandError
import hcl2

# Import policy engine
try:
    from .policy_engine import PolicyEngine, ApprovalStatus
except ImportError:
    from policy_engine import PolicyEngine, ApprovalStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_engine.log'
)
logger = logging.getLogger(__name__)

class CostOptimizationEngine:
    """Core AI engine for cost-optimized workload placement."""
    
    def __init__(self, repo_path: str = None):
        # Auto-detect repository path if not provided
        if repo_path is None:
            # Get the directory containing this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to get the project root
            repo_path = os.path.dirname(script_dir)
        
        self.repo_path = repo_path
        self.terraform_vars_path = os.path.join(repo_path, "infra/envs/prod/terraform.tfvars")
        self.telemetry_path = os.path.join(repo_path, "ai-engine/latest_telemetry.json")
        self.decisions_log = os.path.join(repo_path, "ai-engine/ai_decisions.json")
        self.git_repo = self._init_git_repo()
        
        # Initialize decision history
        self.decision_history: List[dict] = []
        self._load_decision_history()
        
        # Initialize branch manager
        self.branch_manager = self._init_branch_manager()
        
        # Initialize policy engine
        self.policy_engine = PolicyEngine()
    
    def _init_git_repo(self):
        """Initialize git repository handler."""
        try:
            return Repo(self.repo_path)
        except Exception as e:
            logger.error(f"Failed to initialize git repository: {e}")
            raise
    
    def _init_branch_manager(self):
        """Initialize branch manager for strict branch control."""
        try:
            # Import the branch manager
            import sys
            sys.path.append(os.path.join(self.repo_path, 'ops'))
            from ai_branch_manager import AIBranchManager
            
            return AIBranchManager(repo_path=self.repo_path, max_branches=5, alert_hours=24)
        except Exception as e:
            logger.error(f"Failed to initialize branch manager: {e}")
            return None
    
    def _load_decision_history(self):
        """Load previous decisions from log file."""
        try:
            if os.path.exists(self.decisions_log):
                with open(self.decisions_log, 'r') as f:
                    self.decision_history = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load decision history: {e}")
    
    def _save_decision(self, decision: dict):
        """Save decision to history and log file."""
        self.decision_history.append(decision)
        try:
            with open(self.decisions_log, 'w') as f:
                json.dump(self.decision_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save decision: {e}")
    
    def _read_telemetry(self) -> dict:
        """Read latest telemetry data."""
        try:
            with open(self.telemetry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read telemetry: {e}")
            raise
    
    def _read_current_config(self) -> dict:
        """Read current Terraform configuration."""
        try:
            with open(self.terraform_vars_path, 'r') as f:
                return hcl2.load(f)
        except Exception as e:
            logger.error(f"Failed to read Terraform config: {e}")
            raise
    
    def calculate_scores(self, metrics: dict) -> Dict[str, float]:
        """Calculate optimization scores for each provider."""
        scores = {}
        
        for provider, data in metrics.items():
            if provider == 'current_provider':
                continue
                
            # Normalize metrics (0-1 scale, lower is better for cost/latency)
            cost_score = 1 - min(data.get('cost', 0) / 2.0, 1.0)  # Assume max cost of 2.0 for normalization
            latency_score = 1 - min(data.get('latency', 0) / 500, 1.0)  # Max 500ms latency
            
            # Higher credits/availability is better
            credits_score = min(data.get('credits', 0) / 1.0, 1.0)
            gpu_score = min(data.get('available_gpus', 0) / 4.0, 1.0)  # Max 4 GPUs
            
            # Weighted sum of factors
            total_score = (
                0.4 * cost_score + 
                0.3 * latency_score + 
                0.2 * credits_score + 
                0.1 * gpu_score
            )
            
            scores[provider] = {
                'total': total_score,
                'cost': cost_score,
                'latency': latency_score,
                'credits': credits_score,
                'gpu': gpu_score
            }
        
        return scores
    
    def make_decision(self, service: str, metrics: dict) -> Tuple[Optional[str], dict]:
        """Make a placement decision for a service."""
        current_provider = metrics.get('current_provider')
        
        # Calculate scores for each provider
        scores = self.calculate_scores(metrics)
        
        # Find best provider (highest score)
        best_provider = max(scores.items(), key=lambda x: x[1]['total'])[0]
        
        # If no change needed, return None
        if best_provider == current_provider:
            return None, {}
        
        # Calculate predicted savings
        current_cost = metrics.get(current_provider, {}).get('cost', 0)
        recommended_cost = metrics.get(best_provider, {}).get('cost', 0)
        predicted_savings = current_cost - recommended_cost
        
        # Prepare decision record
        decision = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': service,
            'current_provider': current_provider,
            'recommended_provider': best_provider,
            'scores': scores,
            'metrics': metrics,
            'confidence': scores[best_provider]['total'],
            'predicted_savings': predicted_savings,
            'reasoning': (
                f"Recommended moving {service} from {current_provider} to {best_provider} "
                f"due to better cost/performance (score: {scores[best_provider]['total']:.2f})"
            )
        }
        
        # Evaluate policy
        policy_decision = self.policy_engine.evaluate_policy(service, decision, metrics)
        
        # Add policy information to decision
        decision.update({
            'policy_status': policy_decision.status.value,
            'policy_reasoning': policy_decision.reasoning,
            'policy_violations': policy_decision.policy_violations,
            'cost_delta_percent': policy_decision.cost_delta_percent,
            'budget_impact': policy_decision.budget_impact,
            'credit_utilization': policy_decision.credit_utilization
        })
        
        return best_provider, decision
    
    def update_infrastructure(self, service: str, provider: str, decision: dict) -> bool:
        """Update infrastructure configuration via GitOps with policy-based approval."""
        try:
            # Check policy status
            policy_status = decision.get('policy_status', 'pending')
            
            # Only proceed with auto-approved decisions
            if policy_status != 'auto_approved':
                logger.info(f"Skipping infrastructure update for {service}: {policy_status}")
                logger.info(f"Policy reasoning: {decision.get('policy_reasoning', 'No reasoning')}")
                return False
            
            # Check if we can create a new branch using branch manager
            if self.branch_manager:
                can_create, reason = self.branch_manager.can_create_branch()
                if not can_create:
                    logger.warning(f"Cannot create branch for {service}: {reason}")
                    
                    # Enforce cleanup and try again
                    self.branch_manager.enforce_branch_limit()
                    can_create, reason = self.branch_manager.can_create_branch()
                    
                    if not can_create:
                        logger.error(f"Still cannot create branch after cleanup: {reason}")
                        return False
                
                # Create branch safely
                success, branch_name = self.branch_manager.create_branch_safely(service)
                if not success:
                    logger.error(f"Failed to create branch: {branch_name}")
                    return False
            else:
                # Fallback to old method if branch manager not available
                branch_name = f"ai-recommendation/{service}-{int(time.time())}"
                try:
                    subprocess.run(
                        ["git", "checkout", "-b", branch_name],
                        cwd=self.repo_path,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to create branch {branch_name}: {e}")
                    return False
            
            # Update Terraform variables
            with open(self.terraform_vars_path, 'r') as f:
                content = f.read()
            
            # Update the provider for the service
            pattern = f'{service}_provider = "[a-z]+"'
            import re
            new_content = re.sub(
                pattern, 
                f'{service}_provider = "{provider}"',
                content
            )
            
            # Write changes
            with open(self.terraform_vars_path, 'w') as f:
                f.write(new_content)
            
            # Commit changes
            self.git_repo.index.add([self.terraform_vars_path])
            self.git_repo.index.commit(f"AI Recommendation: Move {service} to {provider}")
            
            # Try to push to remote (graceful failure)
            try:
                origin = self.git_repo.remote(name='origin')
                origin.push(branch_name)
                logger.info(f"✅ Pushed branch {branch_name} to remote")
            except Exception as e:
                logger.warning(f"⚠️ Could not push to remote: {e}. Branch saved locally.")
            
            # Log the decision
            decision['git_branch'] = branch_name
            decision['commit_sha'] = self.git_repo.head.commit.hexsha
            self._save_decision(decision)
            
            logger.info(f"✅ Successfully created branch {branch_name} for {service}")
            
            # Update budget with cost change
            budget_impact = decision.get('budget_impact', 0)
            if budget_impact != 0:
                self.policy_engine.update_budget(budget_impact)
            
            # Apply credits if available
            credit_utilization = decision.get('credit_utilization', 0)
            if credit_utilization > 0:
                self.policy_engine.apply_credits(credit_utilization)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update infrastructure: {e}")
            return False
    
    def run(self):
        """Main execution loop."""
        logger.info("Starting AI Engine...")
        
        while True:
            try:
                # Read latest telemetry
                telemetry = self._read_telemetry()
                
                # Process each service
                for service, metrics in telemetry.items():
                    # Make decision
                    best_provider, decision = self.make_decision(service, metrics)
                    
                    # If a change is recommended, update infrastructure
                    if best_provider and decision:
                        logger.info(decision['explanation'])
                        
                        # Only proceed if confidence is high enough
                        if decision['confidence'] > 0.7:  # 70% confidence threshold
                            success = self.update_infrastructure(service, best_provider, decision)
                            if success:
                                logger.info(f"Successfully updated infrastructure for {service}")
                            else:
                                logger.warning(f"Failed to update infrastructure for {service}")
                
                # Wait before next iteration
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error


if __name__ == "__main__":
    # Initialize and run the engine
    engine = CostOptimizationEngine()
    engine.run()
