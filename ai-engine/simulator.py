import json
import random
import time
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('telemetry_simulator')

class TelemetrySimulator:
    """Simulates telemetry data for cloud providers."""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.output_file = os.path.join(output_dir, "latest_telemetry.json")
        self.services = ["service1", "service2", "service3"]
        self.providers = ["aws", "alibaba"]
        self.regions = {
            "aws": ["us-east-1", "us-west-2", "eu-west-1"],
            "alibaba": ["ap-southeast-1", "us-west-1", "eu-central-1"]
        }
        self.instance_types = {
            "aws": ["t3.medium", "m5.large", "c5.xlarge", "p3.2xlarge"],
            "alibaba": ["ecs.g6.large", "ecs.c6.xlarge", "ecs.gn7.large"]
        }
        
        # Initialize state
        self.state = {}
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize the initial state of all services."""
        for service in self.services:
            # Randomly assign initial provider
            current_provider = random.choice(self.providers)
            
            self.state[service] = {
                'current_provider': current_provider,
            }
            
            # Initialize metrics for each provider
            for provider in self.providers:
                self.state[service][provider] = self._generate_provider_metrics(provider)
    
    def _generate_provider_metrics(self, provider: str) -> dict:
        """Generate realistic metrics for a provider."""
        # Base values with some randomness
        if provider == "aws":
            cost = random.uniform(0.8, 1.5)  # $/hour
            latency = random.uniform(40, 120)  # ms
            credits = random.uniform(0, 0.3)  # Available credits (0-1)
            gpus = random.choices([0, 1, 2, 4], weights=[0.4, 0.3, 0.2, 0.1])[0]
        else:  # alibaba
            cost = random.uniform(0.6, 1.8)  # $/hour
            latency = random.uniform(60, 200)  # ms
            credits = random.uniform(0.2, 0.8)  # More credits on Alibaba
            gpus = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        
        return {
            'cost': round(cost, 2),
            'latency': round(latency, 1),
            'credits': round(credits, 2),
            'available_gpus': gpus,
            'region': random.choice(self.regions[provider]),
            'instance': random.choice(self.instance_types[provider]),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _simulate_market_changes(self):
        """Simulate market changes and random fluctuations."""
        for service in self.services:
            # Occasionally introduce a significant change (10% chance)
            if random.random() < 0.1:
                # Simulate a price spike or drop (up to 30% change)
                for provider in self.providers:
                    change = 1 + (random.random() * 0.6 - 0.3)  # ±30%
                    self.state[service][provider]['cost'] = max(0.1, 
                        self.state[service][provider]['cost'] * change)
                    
                    # Also adjust latency slightly
                    latency_change = 1 + (random.random() * 0.4 - 0.2)  # ±20%
                    self.state[service][provider]['latency'] = max(10, 
                        self.state[service][provider]['latency'] * latency_change)
            
            # Update all metrics with small fluctuations
            for provider in self.providers:
                metrics = self.state[service][provider]
                
                # Small random walk for cost (±5%)
                metrics['cost'] = max(0.1, metrics['cost'] * (1 + (random.random() * 0.1 - 0.05)))
                
                # Small random walk for latency (±10%)
                metrics['latency'] = max(5, metrics['latency'] * (1 + (random.random() * 0.2 - 0.1)))
                
                # Update credits (slight increase or decrease)
                metrics['credits'] = max(0, min(1, 
                    metrics['credits'] + (random.random() * 0.1 - 0.05)))
                
                # Update GPU availability (occasionally)
                if random.random() < 0.2:  # 20% chance to change GPU count
                    if provider == "aws":
                        metrics['available_gpus'] = random.choices(
                            [0, 1, 2, 4], 
                            weights=[0.4, 0.3, 0.2, 0.1]
                        )[0]
                    else:  # alibaba
                        metrics['available_gpus'] = random.choices(
                            [0, 1, 2], 
                            weights=[0.6, 0.3, 0.1]
                        )[0]
                
                # Update timestamp
                metrics['timestamp'] = datetime.now(timezone.utc).isoformat()
    
    def save_telemetry(self):
        """Save current telemetry to file."""
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.debug(f"Telemetry saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save telemetry: {e}")
    
    def run(self, interval: int = 5):
        """Run the telemetry simulator."""
        logger.info("Starting telemetry simulator...")
        
        try:
            while True:
                # Update metrics with random fluctuations
                self._simulate_market_changes()
                
                # Save to file
                self.save_telemetry()
                
                # Log current state
                current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"[{current_time}] Telemetry updated")
                
                # Wait for next interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping telemetry simulator...")
        except Exception as e:
            logger.error(f"Error in simulator: {e}")


def generate_sample_telemetry(output_file: str):
    """Generate a sample telemetry file for testing."""
    sim = TelemetrySimulator()
    sim._initialize_state()
    
    # Save initial state
    with open(output_file, 'w') as f:
        json.dump(sim.state, f, indent=2)
    
    print(f"Sample telemetry generated at: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud Telemetry Simulator")
    parser.add_argument("--sample", action="store_true", help="Generate a sample telemetry file and exit")
    parser.add_argument("--output", default="latest_telemetry.json", help="Output file for telemetry")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")
    
    args = parser.parse_args()
    
    if args.sample:
        generate_sample_telemetry(args.output)
    else:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        
        # Run the simulator
        sim = TelemetrySimulator(os.path.dirname(os.path.abspath(args.output)) or "./")
        sim.run(interval=args.interval)
