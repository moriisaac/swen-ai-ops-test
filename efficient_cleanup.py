#!/usr/bin/env python3
"""
Efficient Branch Cleanup - Batch delete remote branches
Uses git commands to efficiently clean up remote branches
"""

import subprocess
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_remote_branches():
    """Get all remote AI branches."""
    try:
        result = subprocess.run(
            ["git", "branch", "-r"],
            capture_output=True,
            text=True,
            check=True
        )
        
        branches = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('origin/ai-recommendation/'):
                branch_name = line.replace('origin/', '')
                branches.append(branch_name)
        
        return branches
        
    except Exception as e:
        logger.error(f"Error getting remote branches: {e}")
        return []

def batch_delete_remote_branches(branches, keep_count=5):
    """Efficiently delete remote branches in batches."""
    if len(branches) <= keep_count:
        logger.info(f"Remote branches within limit: {len(branches)}")
        return []
    
    logger.info(f"Cleaning up {len(branches)} remote branches, keeping {keep_count}")
    
    # Get branch info and sort by creation date
    branch_info = []
    for branch in branches:
        try:
            result = subprocess.run(
                ["git", "log", "--format=%ci", f"origin/{branch}", "-1"],
                capture_output=True,
                text=True,
                check=True
            )
            created_date = result.stdout.strip()
            branch_info.append({"name": branch, "date": created_date})
        except:
            branch_info.append({"name": branch, "date": "1970-01-01"})
    
    # Sort by creation date (newest first)
    branch_info.sort(key=lambda x: x['date'], reverse=True)
    
    # Keep only the most recent
    branches_to_keep = branch_info[:keep_count]
    branches_to_delete = branch_info[keep_count:]
    
    logger.info(f"Will delete {len(branches_to_delete)} branches, keep {len(branches_to_keep)}")
    
    # Delete in batches of 50 to avoid overwhelming the server
    batch_size = 50
    deleted_count = 0
    
    for i in range(0, len(branches_to_delete), batch_size):
        batch = branches_to_delete[i:i + batch_size]
        
        # Create batch delete command
        delete_commands = []
        for branch in batch:
            delete_commands.append(f"git push origin --delete {branch['name']}")
        
        # Execute batch
        logger.info(f"Deleting batch {i//batch_size + 1}: {len(batch)} branches")
        
        for branch in batch:
            try:
                subprocess.run(
                    ["git", "push", "origin", "--delete", branch['name']],
                    check=True,
                    timeout=30
                )
                deleted_count += 1
                if deleted_count % 10 == 0:
                    logger.info(f"Deleted {deleted_count} branches so far...")
            except Exception as e:
                logger.warning(f"Failed to delete {branch['name']}: {e}")
    
    logger.info(f"✅ Deleted {deleted_count} remote branches")
    return deleted_count

def create_consolidated_branch():
    """Create a consolidated branch with all AI recommendations."""
    try:
        # Switch to main
        subprocess.run(["git", "checkout", "main"], check=True)
        
        # Create consolidated branch
        branch_name = f"ai-recommendations-consolidated-{int(datetime.now().timestamp())}"
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        
        # Get all AI decisions
        try:
            with open("ai-engine/ai_decisions.json", "r") as f:
                decisions = json.load(f)
            
            # Create a comprehensive summary
            summary_content = f"""# AI Recommendations Consolidated Summary

Generated: {datetime.now().isoformat()}
Total Recommendations: {len(decisions)}

## Executive Summary
This branch contains a consolidated view of all AI-generated infrastructure recommendations.
The AI engine has analyzed telemetry data and made {len(decisions)} recommendations for cost optimization.

## Recent High-Confidence Recommendations
"""
            
            # Filter high-confidence recommendations
            high_confidence = [d for d in decisions if d.get('confidence', 0) > 0.8]
            summary_content += f"\nHigh-confidence recommendations (>80%): {len(high_confidence)}\n"
            
            for i, decision in enumerate(high_confidence[-10:]):  # Last 10 high-confidence
                summary_content += f"""
### Recommendation {i+1}
- **Service**: {decision.get('service', 'Unknown')}
- **Current Provider**: {decision.get('current_provider', 'Unknown')}
- **Recommended Provider**: {decision.get('recommended_provider', 'Unknown')}
- **Confidence**: {decision.get('confidence', 0):.2f}
- **Predicted Savings**: ${decision.get('predicted_savings', 0):.2f}/hour
- **Timestamp**: {decision.get('timestamp', 'Unknown')}
- **Branch**: {decision.get('git_branch', 'N/A')}
- **Reasoning**: {decision.get('reasoning', 'N/A')}
"""
            
            summary_content += f"""

## All Recommendations Summary
Total recommendations: {len(decisions)}
High confidence (>80%): {len(high_confidence)}
Medium confidence (60-80%): {len([d for d in decisions if 0.6 <= d.get('confidence', 0) <= 0.8])}
Low confidence (<60%): {len([d for d in decisions if d.get('confidence', 0) < 0.6])}

## Cost Impact Analysis
Total predicted savings: ${sum(d.get('predicted_savings', 0) for d in decisions):.2f}/hour
Monthly projected savings: ${sum(d.get('predicted_savings', 0) for d in decisions) * 24 * 30:.2f}

## Next Steps
1. Review high-confidence recommendations for auto-application
2. Evaluate medium-confidence recommendations for manual review
3. Investigate low-confidence recommendations for data quality issues
4. Implement automated merge process for approved recommendations

---
*This consolidated branch preserves all AI recommendations while cleaning up the repository.*
"""
            
            with open("AI_RECOMMENDATIONS_CONSOLIDATED.md", "w") as f:
                f.write(summary_content)
            
            # Also save the raw decisions data
            with open("ai_decisions_consolidated.json", "w") as f:
                json.dump(decisions, f, indent=2)
            
            # Commit the consolidated data
            subprocess.run(["git", "add", "AI_RECOMMENDATIONS_CONSOLIDATED.md", "ai_decisions_consolidated.json"], check=True)
            subprocess.run(["git", "commit", "-m", f"Consolidated AI recommendations summary ({len(decisions)} total)"], check=True)
            
            logger.info(f"✅ Created consolidated branch: {branch_name}")
            return branch_name
            
        except Exception as e:
            logger.error(f"Failed to create consolidated branch: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating consolidated branch: {e}")
        return None

def main():
    """Main cleanup function."""
    print("🧹 Efficient AI Branch Cleanup")
    print("=" * 50)
    
    # Get remote branches
    remote_branches = get_remote_branches()
    print(f"📊 Found {len(remote_branches)} remote AI branches")
    
    if len(remote_branches) > 5:
        print(f"🗑️ Will delete {len(remote_branches) - 5} branches, keeping 5 most recent")
        
        # Delete remote branches
        deleted_count = batch_delete_remote_branches(remote_branches, keep_count=5)
        print(f"✅ Deleted {deleted_count} remote branches")
    
    # Create consolidated branch
    print("📋 Creating consolidated branch with all recommendations...")
    consolidated_branch = create_consolidated_branch()
    if consolidated_branch:
        print(f"✅ Created consolidated branch: {consolidated_branch}")
    
    print("🎯 Cleanup complete!")
    
    # Final count
    final_branches = get_remote_branches()
    print(f"📊 Final remote branch count: {len(final_branches)}")

if __name__ == "__main__":
    main()

