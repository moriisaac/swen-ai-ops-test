#!/usr/bin/env python3
"""
AI Branch Manager - Comprehensive branch management with strict limits
Limits AI branches to maximum 5 and provides alerting for unresolved branches
"""

import subprocess
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_branch_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIBranchManager:
    def __init__(self, repo_path: str = ".", max_branches: int = 5, alert_hours: int = 24):
        self.repo_path = repo_path
        self.max_branches = max_branches
        self.alert_hours = alert_hours  # Alert if branches older than this
        self.branch_file = os.path.join(repo_path, "ai_branch_tracker.json")
        
    def get_ai_branches(self) -> List[str]:
        """Get all AI recommendation branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "--list"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('ai-recommendation/'):
                    # Remove the * prefix if it's the current branch
                    branch_name = line.lstrip('* ').strip()
                    branches.append(branch_name)
            
            return branches
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting branches: {e}")
            return []
    
    def get_branch_details(self, branch_name: str) -> Dict:
        """Get detailed information about a branch."""
        try:
            # Get branch creation date
            result = subprocess.run(
                ["git", "log", "--format=%ci|%H|%s", branch_name, "-1"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                commit_date, commit_hash, commit_message = result.stdout.strip().split('|', 2)
                
                # Calculate age
                try:
                    commit_time = datetime.fromisoformat(commit_date.replace(' +', '+'))
                    age_hours = (datetime.now(timezone.utc) - commit_time).total_seconds() / 3600
                except:
                    age_hours = 0
                
                return {
                    "name": branch_name,
                    "created_date": commit_date,
                    "commit_hash": commit_hash,
                    "commit_message": commit_message,
                    "age_hours": age_hours,
                    "needs_alert": age_hours > self.alert_hours
                }
            else:
                return {
                    "name": branch_name,
                    "created_date": "Unknown",
                    "commit_hash": "Unknown",
                    "commit_message": "Unknown",
                    "age_hours": 999,
                    "needs_alert": True
                }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting branch details for {branch_name}: {e}")
            return {
                "name": branch_name,
                "created_date": "Unknown",
                "commit_hash": "Unknown",
                "commit_message": "Unknown",
                "age_hours": 999,
                "needs_alert": True
            }
    
    def enforce_branch_limit(self) -> Dict:
        """Enforce strict branch limit of 5 branches maximum."""
        branches = self.get_ai_branches()
        count = len(branches)
        
        result = {
            "action_taken": "none",
            "branches_deleted": [],
            "branches_kept": [],
            "alerts": [],
            "total_before": count,
            "total_after": count
        }
        
        if count > self.max_branches:
            logger.warning(f"🚨 BRANCH LIMIT EXCEEDED: {count} branches (max: {self.max_branches})")
            
            # Get detailed info for all branches
            branch_details = []
            for branch in branches:
                details = self.get_branch_details(branch)
                branch_details.append(details)
            
            # Sort by creation date (newest first)
            branch_details.sort(key=lambda x: x['created_date'], reverse=True)
            
            # Keep only the most recent branches
            branches_to_keep = branch_details[:self.max_branches]
            branches_to_delete = branch_details[self.max_branches:]
            
            # Delete excess branches
            deleted_count = 0
            for branch in branches_to_delete:
                try:
                    subprocess.run(
                        ["git", "branch", "-D", branch['name']],
                        cwd=self.repo_path,
                        check=True
                    )
                    result["branches_deleted"].append(branch['name'])
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted excess branch: {branch['name']}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to delete branch {branch['name']}: {e}")
            
            result["action_taken"] = "cleanup"
            result["branches_kept"] = [b['name'] for b in branches_to_keep]
            result["total_after"] = len(branches_to_keep)
            
            logger.info(f"✅ Cleanup complete: Deleted {deleted_count} branches, kept {len(branches_to_keep)}")
        
        return result
    
    def check_for_alerts(self) -> List[Dict]:
        """Check for branches that need alerts (unresolved for too long)."""
        branches = self.get_ai_branches()
        alerts = []
        
        for branch in branches:
            details = self.get_branch_details(branch)
            if details['needs_alert']:
                alerts.append({
                    "branch": branch,
                    "age_hours": details['age_hours'],
                    "message": f"Branch {branch} is {details['age_hours']:.1f} hours old and needs attention",
                    "severity": "high" if details['age_hours'] > 48 else "medium"
                })
        
        return alerts
    
    def can_create_branch(self) -> Tuple[bool, str]:
        """Check if a new branch can be created."""
        branches = self.get_ai_branches()
        count = len(branches)
        
        if count >= self.max_branches:
            return False, f"Branch limit reached: {count}/{self.max_branches} branches"
        
        # Check for old unresolved branches
        alerts = self.check_for_alerts()
        if alerts:
            return False, f"Cannot create new branch: {len(alerts)} unresolved branches need attention"
        
        return True, "OK"
    
    def create_branch_safely(self, service: str) -> Tuple[bool, str]:
        """Safely create a new branch if allowed."""
        can_create, reason = self.can_create_branch()
        
        if not can_create:
            logger.warning(f"❌ Cannot create branch for {service}: {reason}")
            return False, reason
        
        # Enforce limit before creating
        self.enforce_branch_limit()
        
        # Create new branch
        branch_name = f"ai-recommendation/{service}-{int(time.time())}"
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                check=True
            )
            logger.info(f"✅ Created new branch: {branch_name}")
            return True, branch_name
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False, str(e)
    
    def generate_status_report(self) -> Dict:
        """Generate comprehensive status report."""
        branches = self.get_ai_branches()
        branch_details = [self.get_branch_details(b) for b in branches]
        
        alerts = self.check_for_alerts()
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_branches": len(branches),
            "max_branches": self.max_branches,
            "status": "healthy" if len(branches) <= self.max_branches else "critical",
            "alerts": alerts,
            "branches": branch_details,
            "can_create_new": self.can_create_branch()[0],
            "recommendations": []
        }
        
        # Add recommendations
        if len(branches) > self.max_branches:
            report["recommendations"].append("Immediate cleanup required")
        
        if alerts:
            report["recommendations"].append(f"Resolve {len(alerts)} unresolved branches")
        
        if len(branches) == 0:
            report["recommendations"].append("No AI branches found - check AI engine status")
        
        return report

def main():
    """Main function for branch management."""
    manager = AIBranchManager(max_branches=5, alert_hours=24)
    
    print("🌿 AI Branch Manager")
    print("=" * 50)
    
    # Enforce limits
    result = manager.enforce_branch_limit()
    
    if result["action_taken"] == "cleanup":
        print(f"🧹 Cleanup performed: {len(result['branches_deleted'])} branches deleted")
        print(f"📊 Branches before: {result['total_before']}, after: {result['total_after']}")
    
    # Check for alerts
    alerts = manager.check_for_alerts()
    if alerts:
        print(f"🚨 {len(alerts)} branches need attention:")
        for alert in alerts:
            print(f"   • {alert['message']}")
    
    # Generate status
    report = manager.generate_status_report()
    print(f"📈 Status: {report['status'].upper()}")
    print(f"📊 Total branches: {report['total_branches']}/{report['max_branches']}")
    print(f"✅ Can create new: {report['can_create_new']}")
    
    # Save report
    with open("ai_branch_status.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return 0 if report['status'] == 'healthy' else 1

if __name__ == "__main__":
    sys.exit(main())


