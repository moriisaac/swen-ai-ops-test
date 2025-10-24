#!/usr/bin/env python3
"""
Quick Branch Cleanup - Clean up excessive AI branches to 5 maximum
"""

import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_branches():
    """Clean up AI branches to maximum 5."""
    try:
        # Get all AI branches
        result = subprocess.run(
            ["git", "branch", "--list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        branches = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('ai-recommendation/'):
                branch_name = line.lstrip('* ').strip()
                branches.append(branch_name)
        
        logger.info(f"Found {len(branches)} AI branches")
        
        if len(branches) <= 5:
            logger.info("Branch count is within limit")
            return
        
        # Get branch info and sort by creation date
        branch_info = []
        for branch in branches:
            try:
                result = subprocess.run(
                    ["git", "log", "--format=%ci", branch, "-1"],
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
        
        # Keep only the 5 most recent
        branches_to_keep = branch_info[:5]
        branches_to_delete = branch_info[5:]
        
        logger.info(f"Keeping {len(branches_to_keep)} branches, deleting {len(branches_to_delete)}")
        
        # Delete old branches
        for branch in branches_to_delete:
            try:
                subprocess.run(
                    ["git", "branch", "-D", branch['name']],
                    check=True
                )
                logger.info(f"Deleted: {branch['name']}")
            except Exception as e:
                logger.error(f"Failed to delete {branch['name']}: {e}")
        
        logger.info("✅ Cleanup complete!")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    cleanup_branches()


