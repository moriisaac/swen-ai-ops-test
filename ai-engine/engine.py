import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, Tuple, List, Optional
import numpy as np
from git import Repo, GitCommandError
import hcl2

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
    
    def _init_git_repo(self):
        """Initialize git repository handler."""
        try:
            return Repo(self.repo_path)
        except Exception as e:
            logger.error(f"Failed to initialize git repository: {e}")
            raise
    
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
        
        # Prepare decision record
        decision = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': service,
            'current_provider': current_provider,
            'recommended_provider': best_provider,
            'scores': scores,
            'metrics': metrics,
            'confidence': scores[best_provider]['total'],
            'explanation': (
                f"Recommended moving {service} from {current_provider} to {best_provider} "
                f"due to better cost/performance (score: {scores[best_provider]['total']:.2f})"
            )
        }
        
        return best_provider, decision
    
    def update_infrastructure(self, service: str, provider: str, decision: dict) -> bool:
        """Update infrastructure configuration via GitOps."""
        try:
            # Create a new branch
            branch_name = f"ai-recommendation/{service}-{int(time.time())}"
            
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
            self.git_repo.git.checkout('HEAD', b=branch_name)
            self.git_repo.index.add([self.terraform_vars_path])
            self.git_repo.index.commit(f"AI Recommendation: Move {service} to {provider}")
            
            # Push to remote
            origin = self.git_repo.remote(name='origin')
            origin.push(branch_name)
            
            # Log the decision
            decision['git_branch'] = branch_name
            decision['commit_sha'] = self.git_repo.head.commit.hexsha
            self._save_decision(decision)
            
            return True
            
        except GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            return False
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
