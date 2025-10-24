#!/usr/bin/env python3
"""
Enhanced Self-Healing System with Branch Management
Integrates branch management into the self-healing capabilities
"""

import json
import time
import logging
import sys
import subprocess
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSelfHealingSystem:
    """Enhanced self-healing system with branch management integration."""
    
    def __init__(self, repo_path: str = ".", api_url: str = "http://localhost:8001"):
        self.repo_path = repo_path
        self.api_url = api_url
        self.event_log = []
        self.branch_manager = None
        self._init_branch_manager()
    
    def _init_branch_manager(self):
        """Initialize branch manager for self-healing."""
        try:
            sys.path.append(os.path.join(self.repo_path, 'ops'))
            from ai_branch_manager import AIBranchManager
            self.branch_manager = AIBranchManager(repo_path=self.repo_path, max_branches=5)
            logger.info("✅ Branch manager initialized for self-healing")
        except Exception as e:
            logger.error(f"Failed to initialize branch manager: {e}")
            self.branch_manager = None
    
    def log_event(self, event_type: str, message: str, data: Dict = None):
        """Log a self-healing event."""
        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': event_type,
            'message': message,
            'data': data or {}
        }
        self.event_log.append(event)
        logger.info(f"[{event_type}] {message}")
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health status."""
        health = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'api_status': self._check_api_health(),
            'branch_status': self._check_branch_health(),
            'telemetry_status': self._check_telemetry_health(),
            'ai_engine_status': self._check_ai_engine_health(),
            'overall_status': 'healthy'
        }
        
        # Determine overall status
        issues = []
        if not health['api_status']['healthy']:
            issues.append('API')
        if not health['branch_status']['healthy']:
            issues.append('Branch Management')
        if not health['telemetry_status']['healthy']:
            issues.append('Telemetry')
        if not health['ai_engine_status']['healthy']:
            issues.append('AI Engine')
        
        if issues:
            health['overall_status'] = 'degraded'
            health['issues'] = issues
        
        return health
    
    def _check_api_health(self) -> Dict:
        """Check API health status."""
        try:
            response = requests.get(f"{self.api_url}/healthz", timeout=5)
            if response.status_code == 200:
                return {'healthy': True, 'status_code': 200, 'data': response.json()}
            else:
                return {'healthy': False, 'status_code': response.status_code}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _check_branch_health(self) -> Dict:
        """Check branch management health."""
        if not self.branch_manager:
            return {'healthy': False, 'error': 'Branch manager not initialized'}
        
        try:
            status = self.branch_manager.get_status()
            branch_count = status['total_branches']
            max_branches = status['max_branches']
            
            health = {
                'healthy': True,
                'branch_count': branch_count,
                'max_branches': max_branches,
                'utilization': f"{branch_count}/{max_branches}",
                'status': status
            }
            
            # Check for branch health issues
            if branch_count >= max_branches:
                health['healthy'] = False
                health['issue'] = 'Branch limit reached'
            elif branch_count > max_branches * 0.8:  # 80% threshold
                health['warning'] = 'Approaching branch limit'
            
            return health
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _check_telemetry_health(self) -> Dict:
        """Check telemetry data health."""
        try:
            response = requests.get(f"{self.api_url}/api/telemetry", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'healthy': True,
                    'status_code': 200,
                    'services_count': len(data.get('services', {})),
                    'last_updated': data.get('timestamp')
                }
            else:
                return {'healthy': False, 'status_code': response.status_code}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def _check_ai_engine_health(self) -> Dict:
        """Check AI engine health."""
        try:
            # Check if AI engine process is running
            result = subprocess.run(
                ["pgrep", "-f", "engine.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pid = result.stdout.strip()
                return {
                    'healthy': True,
                    'pid': pid,
                    'status': 'running'
                }
            else:
                return {
                    'healthy': False,
                    'status': 'not_running',
                    'error': 'AI engine process not found'
                }
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def heal_branch_issues(self) -> bool:
        """Heal branch management issues."""
        if not self.branch_manager:
            self.log_event('HEAL_FAILED', 'Branch manager not available')
            return False
        
        try:
            status = self.branch_manager.get_status()
            branch_count = status['total_branches']
            max_branches = status['max_branches']
            
            if branch_count >= max_branches:
                self.log_event('HEAL_BRANCH', f'Branch limit reached ({branch_count}/{max_branches}), enforcing cleanup')
                
                # Enforce branch limit
                self.branch_manager.enforce_branch_limit()
                
                # Check if cleanup was successful
                new_status = self.branch_manager.get_status()
                new_count = new_status['total_branches']
                
                if new_count < max_branches:
                    self.log_event('HEAL_SUCCESS', f'Branch cleanup successful: {branch_count} → {new_count}')
                    return True
                else:
                    self.log_event('HEAL_FAILED', f'Branch cleanup failed: still {new_count} branches')
                    return False
            else:
                self.log_event('HEAL_SKIP', f'Branch count healthy: {branch_count}/{max_branches}')
                return True
                
        except Exception as e:
            self.log_event('HEAL_ERROR', f'Branch healing failed: {e}')
            return False
    
    def heal_api_issues(self) -> bool:
        """Heal API issues."""
        try:
            # Try to restart API if it's not responding
            health = self._check_api_health()
            if not health['healthy']:
                self.log_event('HEAL_API', 'API not responding, attempting restart')
                
                # Kill existing API process
                subprocess.run(["pkill", "-f", "main.py"], check=False)
                time.sleep(2)
                
                # Start API in background
                subprocess.Popen([
                    "python", "dashboard/api/main.py"
                ], cwd=self.repo_path)
                
                time.sleep(5)  # Wait for API to start
                
                # Check if API is now healthy
                new_health = self._check_api_health()
                if new_health['healthy']:
                    self.log_event('HEAL_SUCCESS', 'API restart successful')
                    return True
                else:
                    self.log_event('HEAL_FAILED', 'API restart failed')
                    return False
            else:
                self.log_event('HEAL_SKIP', 'API is healthy')
                return True
                
        except Exception as e:
            self.log_event('HEAL_ERROR', f'API healing failed: {e}')
            return False
    
    def heal_ai_engine_issues(self) -> bool:
        """Heal AI engine issues."""
        try:
            health = self._check_ai_engine_health()
            if not health['healthy']:
                self.log_event('HEAL_AI_ENGINE', 'AI engine not running, attempting restart')
                
                # Start AI engine in background
                subprocess.Popen([
                    "python", "ai-engine/engine.py"
                ], cwd=self.repo_path)
                
                time.sleep(5)  # Wait for AI engine to start
                
                # Check if AI engine is now healthy
                new_health = self._check_ai_engine_health()
                if new_health['healthy']:
                    self.log_event('HEAL_SUCCESS', 'AI engine restart successful')
                    return True
                else:
                    self.log_event('HEAL_FAILED', 'AI engine restart failed')
                    return False
            else:
                self.log_event('HEAL_SKIP', 'AI engine is healthy')
                return True
                
        except Exception as e:
            self.log_event('HEAL_ERROR', f'AI engine healing failed: {e}')
            return False
    
    def perform_self_healing(self) -> Dict:
        """Perform comprehensive self-healing."""
        self.log_event('HEAL_START', 'Starting self-healing process')
        
        health = self.get_system_health()
        healing_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'initial_health': health,
            'healing_actions': [],
            'final_health': None,
            'success': True
        }
        
        # Heal branch issues
        if not health['branch_status']['healthy']:
            result = self.heal_branch_issues()
            healing_results['healing_actions'].append({
                'action': 'branch_cleanup',
                'success': result
            })
            if not result:
                healing_results['success'] = False
        
        # Heal API issues
        if not health['api_status']['healthy']:
            result = self.heal_api_issues()
            healing_results['healing_actions'].append({
                'action': 'api_restart',
                'success': result
            })
            if not result:
                healing_results['success'] = False
        
        # Heal AI engine issues
        if not health['ai_engine_status']['healthy']:
            result = self.heal_ai_engine_issues()
            healing_results['healing_actions'].append({
                'action': 'ai_engine_restart',
                'success': result
            })
            if not result:
                healing_results['success'] = False
        
        # Get final health status
        healing_results['final_health'] = self.get_system_health()
        
        if healing_results['success']:
            self.log_event('HEAL_SUCCESS', 'Self-healing completed successfully')
        else:
            self.log_event('HEAL_PARTIAL', 'Self-healing completed with some failures')
        
        return healing_results
    
    def run_continuous_monitoring(self, interval: int = 60):
        """Run continuous monitoring and self-healing."""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                health = self.get_system_health()
                
                if health['overall_status'] != 'healthy':
                    logger.warning(f"System health degraded: {health.get('issues', [])}")
                    
                    # Perform self-healing
                    healing_results = self.perform_self_healing()
                    
                    if healing_results['success']:
                        logger.info("✅ Self-healing successful")
                    else:
                        logger.error("❌ Self-healing failed")
                else:
                    logger.info("✅ System health is good")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(interval)

def main():
    """Main function for self-healing system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Self-Healing System')
    parser.add_argument('--monitor', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run self-healing once')
    parser.add_argument('--health', action='store_true', help='Check system health only')
    
    args = parser.parse_args()
    
    healing_system = EnhancedSelfHealingSystem()
    
    if args.health:
        health = healing_system.get_system_health()
        print(json.dumps(health, indent=2))
    elif args.once:
        results = healing_system.perform_self_healing()
        print(json.dumps(results, indent=2))
    elif args.monitor:
        healing_system.run_continuous_monitoring(args.interval)
    else:
        # Default: check health and perform healing if needed
        health = healing_system.get_system_health()
        print("Current System Health:")
        print(json.dumps(health, indent=2))
        
        if health['overall_status'] != 'healthy':
            print("\nPerforming self-healing...")
            results = healing_system.perform_self_healing()
            print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
