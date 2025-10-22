#!/usr/bin/env python3
"""
GitOps Committer - Handles Git operations for AI recommendations
Creates branches, commits changes, and optionally creates merge requests
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from git import Repo, GitCommandError
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitOpsCommitter:
    """Handles GitOps operations for AI-driven infrastructure changes."""
    
    def __init__(self, repo_path: str, gitlab_url: Optional[str] = None, 
                 gitlab_token: Optional[str] = None):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        self.gitlab_url = gitlab_url or os.getenv('GITLAB_URL')
        self.gitlab_token = gitlab_token or os.getenv('GITLAB_TOKEN')
        self.project_id = os.getenv('CI_PROJECT_ID')
    
    def create_branch(self, branch_name: str, base_branch: str = 'main') -> bool:
        """Create a new branch from base branch."""
        try:
            # Fetch latest changes
            origin = self.repo.remote('origin')
            origin.fetch()
            
            # Checkout base branch
            self.repo.git.checkout(base_branch)
            self.repo.git.pull()
            
            # Create new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            logger.info(f"Created branch: {branch_name}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Failed to create branch: {e}")
            return False
    
    def commit_changes(self, files: list, commit_message: str, 
                      metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Commit changes to the current branch.
        
        Args:
            files: List of file paths to commit
            commit_message: Commit message
            metadata: Optional metadata to save alongside commit
            
        Returns:
            Commit SHA if successful, None otherwise
        """
        try:
            # Add files to staging
            self.repo.index.add(files)
            
            # Save metadata if provided
            if metadata:
                metadata_path = os.path.join(
                    self.repo_path, 
                    'infra/envs/prod/ai-metadata.json'
                )
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                self.repo.index.add([metadata_path])
            
            # Commit changes
            commit = self.repo.index.commit(commit_message)
            logger.info(f"Committed changes: {commit.hexsha[:8]}")
            
            return commit.hexsha
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return None
    
    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote."""
        try:
            origin = self.repo.remote('origin')
            origin.push(refspec=f'{branch_name}:{branch_name}')
            logger.info(f"Pushed branch: {branch_name}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Failed to push branch: {e}")
            return False
    
    def create_merge_request(self, source_branch: str, target_branch: str = 'main',
                            title: str = None, description: str = None) -> Optional[int]:
        """
        Create a GitLab merge request.
        
        Returns:
            Merge request IID if successful, None otherwise
        """
        if not self.gitlab_url or not self.gitlab_token or not self.project_id:
            logger.warning("GitLab credentials not configured, skipping MR creation")
            return None
        
        try:
            url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests"
            headers = {
                'PRIVATE-TOKEN': self.gitlab_token,
                'Content-Type': 'application/json'
            }
            
            data = {
                'source_branch': source_branch,
                'target_branch': target_branch,
                'title': title or f"AI Recommendation: {source_branch}",
                'description': description or "Automated infrastructure optimization by AI engine",
                'remove_source_branch': True,
                'labels': ['ai-generated', 'infrastructure', 'cost-optimization']
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            mr_data = response.json()
            mr_iid = mr_data['iid']
            logger.info(f"Created merge request: !{mr_iid}")
            
            return mr_iid
            
        except Exception as e:
            logger.error(f"Failed to create merge request: {e}")
            return None
    
    def execute_gitops_flow(self, service: str, changes: Dict, 
                           decision: Dict) -> bool:
        """
        Execute complete GitOps flow for an AI recommendation.
        
        Args:
            service: Service name
            changes: Dictionary of file changes {file_path: new_content}
            decision: AI decision metadata
            
        Returns:
            True if successful, False otherwise
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        branch_name = f"ai-recommendation/{service}-{timestamp}"
        
        try:
            # Create branch
            if not self.create_branch(branch_name):
                return False
            
            # Apply changes
            changed_files = []
            for file_path, content in changes.items():
                full_path = os.path.join(self.repo_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                
                changed_files.append(file_path)
            
            # Prepare metadata
            metadata = {
                'service': service,
                'timestamp': datetime.utcnow().isoformat(),
                'cost_delta': decision.get('cost_delta', 0.0),
                'confidence': decision.get('confidence', 0.0),
                'predicted_savings': decision.get('predicted_savings', 0.0),
                'change_type': decision.get('change_type', 'provider_change'),
                'affects_stateful': decision.get('affects_stateful', False),
                'traffic_impact_percent': decision.get('traffic_impact_percent', 0.0),
                'current_provider': decision.get('current_provider'),
                'recommended_provider': decision.get('recommended_provider'),
                'explanation': decision.get('explanation', '')
            }
            
            # Commit changes
            commit_msg = (
                f"AI Recommendation: Optimize {service}\n\n"
                f"Provider: {metadata['current_provider']} → {metadata['recommended_provider']}\n"
                f"Confidence: {metadata['confidence']:.2%}\n"
                f"Predicted Savings: ${metadata['predicted_savings']:.2f}/month\n"
                f"\n{metadata['explanation']}"
            )
            
            commit_sha = self.commit_changes(changed_files, commit_msg, metadata)
            if not commit_sha:
                return False
            
            # Push branch
            if not self.push_branch(branch_name):
                return False
            
            # Create merge request
            mr_title = f"🤖 AI Optimization: {service} → {metadata['recommended_provider']}"
            mr_description = f"""
## AI-Driven Infrastructure Optimization

**Service:** {service}  
**Current Provider:** {metadata['current_provider']}  
**Recommended Provider:** {metadata['recommended_provider']}  

### Metrics
- **Confidence:** {metadata['confidence']:.2%}
- **Predicted Monthly Savings:** ${metadata['predicted_savings']:.2f}
- **Cost Delta:** {metadata['cost_delta']:.2%}

### Explanation
{metadata['explanation']}

### Policy Evaluation
This change will be evaluated against auto-approval policies in the CI pipeline.

---
*Generated by SWEN AI Engine at {metadata['timestamp']}*
"""
            
            self.create_merge_request(branch_name, 'main', mr_title, mr_description)
            
            logger.info(f"GitOps flow completed successfully for {service}")
            return True
            
        except Exception as e:
            logger.error(f"GitOps flow failed: {e}")
            return False


def main():
    """Test the GitOps committer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitOps Committer Test")
    parser.add_argument('--repo', default='.', help='Repository path')
    parser.add_argument('--service', default='test-service', help='Service name')
    
    args = parser.parse_args()
    
    # Initialize committer
    committer = GitOpsCommitter(args.repo)
    
    # Test changes
    changes = {
        'infra/envs/prod/terraform.tfvars': 'service1_provider = "alibaba"\n'
    }
    
    decision = {
        'cost_delta': 0.03,
        'confidence': 0.92,
        'predicted_savings': 75.50,
        'change_type': 'provider_change',
        'affects_stateful': False,
        'traffic_impact_percent': 5.0,
        'current_provider': 'aws',
        'recommended_provider': 'alibaba',
        'explanation': 'Lower cost and better credits on Alibaba Cloud'
    }
    
    # Execute flow
    success = committer.execute_gitops_flow(args.service, changes, decision)
    
    if success:
        print("✓ GitOps flow completed successfully")
    else:
        print("✗ GitOps flow failed")


if __name__ == "__main__":
    main()
