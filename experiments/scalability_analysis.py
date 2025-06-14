"""
experiments/scalability_analysis.py
===================================
Scalability analysis experiment for ethics-by-design architecture
"""

import numpy as np
import pandas as pd
import time
import logging
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt

from ethics_framework.core.constraints import create_constraint
from ethics_framework.simulation.workload_generator import (
    WorkloadGenerator, WorkloadConfig, UserDistribution, ContentDistribution
)
from ethics_framework.visualization.latency_plots import plot_scalability_analysis
from experiments.baseline_comparison import BaselineMLSystem, EthicsAwareMLSystem

logger = logging.getLogger(__name__)


class ScalabilityExperiment:
    """Test system scalability across different dimensions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.results = {}
        self.scaling_dimensions = ['users', 'content', 'constraints', 'requests']
        
    def run_user_scaling(self, user_scales: List[int]) -> Dict:
        """Test scalability with varying number of users"""
        logger.info("Running user scaling experiment...")
        
        results = {}
        base_config = self.config.copy()
        
        for num_users in user_scales:
            logger.info(f"Testing with {num_users} users")
            
            # Update configuration
            base_config['num_users'] = num_users
            
            # Run experiment
            exp_results = self._run_single_scale_test(
                base_config,
                num_requests=min(num_users * 10, 10000),
                test_name=f"users_{num_users}"
            )
            
            results[num_users] = exp_results
            
        return results
    
    def run_content_scaling(self, content_scales: List[int]) -> Dict:
        """Test scalability with varying content catalog sizes"""
        logger.info("Running content scaling experiment...")
        
        results = {}
        base_config = self.config.copy()
        
        for num_content in content_scales:
            logger.info(f"Testing with {num_content} content items")
            
            # Update configuration
            base_config['num_content'] = num_content
            
            # Run experiment
            exp_results = self._run_single_scale_test(
                base_config,
                num_requests=5000,
                test_name=f"content_{num_content}"
            )
            
            results[num_content] = exp_results
            
        return results
    
    def run_constraint_scaling(self, constraint_counts: List[int]) -> Dict:
        """Test scalability with varying number of constraints"""
        logger.info("Running constraint scaling experiment...")
        
        results = {}
        base_config = self.config.copy()
        
        # Base constraints
        base_constraints = [
            {
                'type': 'fairness',
                'name': 'fairness_demographic',
                'protected_attribute': 'demographic',
                'threshold': 0.1
            },
            {
                'type': 'privacy',
                'name': 'privacy_differential',
                'epsilon': 1.0,
                'delta': 1e-5
            },
            {
                'type': 'transparency',
                'name': 'transparency_explanation',
                'min_clarity_score': 0.8
            },
            {
                'type': 'consent',
                'name': 'consent_data',
                'consent_types': ['data_processing']
            },
            {
                'type': 'wellbeing',
                'name': 'wellbeing_engagement',
                'max_threshold': 120.0
            }
        ]
        
        for num_constraints in constraint_counts:
            logger.info(f"Testing with {num_constraints} constraints")
            
            # Select subset of constraints
            if num_constraints <= len(base_constraints):
                selected_constraints = base_constraints[:num_constraints]
            else:
                # Duplicate constraints with variations
                selected_constraints = base_constraints.copy()
                for i in range(num_constraints - len(base_constraints)):
                    base_idx = i % len(base_constraints)
                    new_constraint = base_constraints[base_idx].copy()
                    new_constraint['name'] = f"{new_constraint['name']}_{i+2}"
                    if 'threshold' in new_constraint:
                        new_constraint['threshold'] *= (1 + 0.1 * (i + 1))
                    selected_constraints.append(new_constraint)
            
            base_config['constraints'] = selected_constraints
            
            # Run experiment
            exp_results = self._run_single_scale_test(
                base_config,
                num_requests=5000,
                test_name=f"constraints_{num_constraints}"
            )
            
            results[num_constraints] = exp_results
            
        return results
    
    def run_request_scaling(self, request_scales: List[int]) -> Dict:
        """Test scalability with varying request volumes"""
        logger.info("Running request volume scaling experiment...")
        
        results = {}
        base_config = self.config.copy()
        
        for num_requests in request_scales:
            logger.info(f"Testing with {num_requests} requests")
            
            # Run experiment
            exp_results = self._run_single_scale_test(
                base_config,
                num_requests=num_requests,
                test_name=f"requests_{num_requests}"
            )
            
            results[num_requests] = exp_results
            
        return results
    
    def run_parallel_scaling(self, thread_counts: List[int]) -> Dict:
        """Test parallel processing scalability"""
        logger.info("Running parallel processing scaling experiment...")
        
        results = {}
        base_config = self.config.copy()
        
        # Generate fixed workload
        workload_config = WorkloadConfig(
            num_requests=10000,
            num_users=base_config['num_users'],
            num_content=base_config['num_content']
        )
        generator = WorkloadGenerator(workload_config)
        decisions = generator.generate()
        
        for num_threads in thread_counts:
            logger.info(f"Testing with {num_threads} threads")
            
            # Run with different thread counts
            start_time = time.time()
            
            if num_threads == 1:
                # Sequential processing
                latencies = self._process_sequential(decisions, base_config)
            else:
                # Parallel processing
                latencies = self._process_parallel(decisions, base_config, num_threads)
            
            total_time = time.time() - start_time
            
            results[num_threads] = {
                'latencies': latencies,
                'total_time': total_time,
                'throughput': len(decisions) / total_time,
                'mean_latency': np.mean(latencies),
                'p95_latency': np.percentile(latencies, 95)
            }
            
        return results
    
    def _run_single_scale_test(self, config: Dict, num_requests: int, 
                              test_name: str) -> Dict:
        """Run a single scalability test"""
        # Generate workload
        workload_config = WorkloadConfig(
            num_requests=num_requests,
            num_users=config.get('num_users', 100000),
            num_content=config.get('num_content', 1000000),
            user_distribution=UserDistribution.POWER_LAW,
            content_distribution=ContentDistribution.LONG_TAIL
        )
        
        generator = WorkloadGenerator(workload_config)
        decisions = generator.generate()
        
        # Initialize systems
        baseline_system = BaselineMLSystem(config)
        ethics_system = EthicsAwareMLSystem(config)
        
        # Process decisions
        baseline_latencies = []
        ethics_latencies = []
        
        for decision in tqdm(decisions, desc=test_name, leave=False):
            # Baseline
            baseline_result = baseline_system.process(decision)
            baseline_latencies.append(baseline_result['latency_ms'])
            
            # Ethics
            ethics_result = ethics_system.process(decision)
            ethics_latencies.append(ethics_result.get('total_latency_ms', 0))
        
        # Calculate statistics
        return {
            'baseline': {
                'latencies': baseline_latencies,
                'mean': np.mean(baseline_latencies),
                'median': np.median(baseline_latencies),
                'p95': np.percentile(baseline_latencies, 95),
                'p99': np.percentile(baseline_latencies, 99)
            },
            'ethics': {
                'latencies': ethics_latencies,
                'mean': np.mean(ethics_latencies),
                'median': np.median(ethics_latencies),
                'p95': np.percentile(ethics_latencies, 95),
                'p99': np.percentile(ethics_latencies, 99)
            },
            'overhead': {
                'mean_pct': ((np.mean(ethics_latencies) - np.mean(baseline_latencies)) / 
                            np.mean(baseline_latencies) * 100),
                'p95_pct': ((np.percentile(ethics_latencies, 95) - 
                           np.percentile(baseline_latencies, 95)) / 
                          np.percentile(baseline_latencies, 95) * 100)
            }
        }
    
    def _process_sequential(self, decisions: List, config: Dict) -> List[float]:
        """Process decisions sequentially"""
        system = EthicsAwareMLSystem(config)
        latencies = []
        
        for decision in decisions:
            result = system.process(decision)
            latencies.append(result.get('total_latency_ms', 0))
            
        return latencies
    
    def _process_parallel(self, decisions: List, config: Dict, 
                         num_threads: int) -> List[float]:
        """Process decisions in parallel"""
        # Split decisions into chunks
        chunk_size = len(decisions) // num_threads
        chunks = [decisions[i:i+chunk_size] for i in range(0, len(decisions), chunk_size)]
        
        latencies = []
        
        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            # Submit chunks to workers
            futures = {
                executor.submit(self._process_chunk, chunk, config): i
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results
            for future in as_completed(futures):
                chunk_latencies = future.result()
                latencies.extend(chunk_latencies)
        
        return latencies
    
    def _process_chunk(self, decisions: List, config: Dict) -> List[float]:
        """Process a chunk of decisions (for parallel processing)"""
        system = EthicsAwareMLSystem(config)
        latencies = []
        
        for decision in decisions:
            result = system.process(decision)
            latencies.append(result.get('total_latency_ms', 0))
            
        return latencies
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run all scalability tests"""
        logger.info("Running comprehensive scalability analysis...")
        
        # User scaling
        user_scales = [100, 1000, 10000, 100000]
        self.results['user_scaling'] = self.run_user_scaling(user_scales)
        
        # Content scaling
        content_scales = [1000, 10000, 100000, 1000000]
        self.results['content_scaling'] = self.run_content_scaling(content_scales)
        
        # Constraint scaling
        constraint_counts = [1, 3, 5, 10, 20]
        self.results['constraint_scaling'] = self.run_constraint_scaling(constraint_counts)
        
        # Request volume scaling
        request_scales = [100, 1000, 5000, 10000, 50000]
        self.results['request_scaling'] = self.run_request_scaling(request_scales)
        
        # Parallel processing scaling
        thread_counts = [1, 2, 4, 8, 16]
        self.results['parallel_scaling'] = self.run_parallel_scaling(thread_counts)
        
        # Generate visualizations
        self._generate_visualizations()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _generate_visualizations(self):
        """Generate scalability visualization plots"""
        output_dir = Path('results/figures')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive scalability plot
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # User scaling
        self._plot_scaling_dimension(
            axes[0], 
            self.results['user_scaling'],
            'Number of Users',
            'User Scalability'
        )
        
        # Content scaling
        self._plot_scaling_dimension(
            axes[1],
            self.results['content_scaling'],
            'Content Catalog Size',
            'Content Scalability'
        )
        
        # Constraint scaling
        self._plot_scaling_dimension(
            axes[2],
            self.results['constraint_scaling'],
            'Number of Constraints',
            'Constraint Scalability'
        )
        
        # Request scaling
        self._plot_scaling_dimension(
            axes[3],
            self.results['request_scaling'],
            'Number of Requests',
            'Request Volume Scalability'
        )
        
        # Parallel scaling
        if 'parallel_scaling' in self.results:
            scales = sorted(self.results['parallel_scaling'].keys())
            throughputs = [self.results['parallel_scaling'][s]['throughput'] 
                          for s in scales]
            
            axes[4].plot(scales, throughputs, 'o-', linewidth=2, markersize=8)
            axes[4].set_xlabel('Number of Threads')
            axes[4].set_ylabel('Throughput (req/s)')
            axes[4].set_title('Parallel Processing Scalability')
            axes[4].grid(True, alpha=0.3)
        
        # Overall overhead trends
        self._plot_overhead_trends(axes[5])
        
        plt.suptitle('Comprehensive Scalability Analysis', fontsize=16)
        plt.tight_layout()
        plt.savefig(output_dir / 'scalability_analysis.pdf', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Also use the plot_scalability_analysis function for interactive plot
        scalability_data = self._format_for_visualization()
        plot_scalability_analysis(
            scalability_data,
            save_path=str(output_dir / 'scalability_interactive.html')
        )
        
        logger.info(f"Visualizations saved to {output_dir}")
    
    def _plot_scaling_dimension(self, ax, data: Dict, xlabel: str, title: str):
        """Plot a single scaling dimension"""
        scales = sorted(data.keys())
        
        baseline_means = [data[s]['baseline']['mean'] for s in scales]
        ethics_means = [data[s]['ethics']['mean'] for s in scales]
        
        baseline_p95s = [data[s]['baseline']['p95'] for s in scales]
        ethics_p95s = [data[s]['ethics']['p95'] for s in scales]
        
        # Plot means
        ax.plot(scales, baseline_means, 'o-', label='Baseline Mean', 
                linewidth=2, markersize=8)
        ax.plot(scales, ethics_means, 's-', label='Ethics Mean', 
                linewidth=2, markersize=8)
        
        # Plot P95s with dashed lines
        ax.plot(scales, baseline_p95s, 'o--', label='Baseline P95', 
                linewidth=1.5, markersize=6, alpha=0.7)
        ax.plot(scales, ethics_p95s, 's--', label='Ethics P95', 
                linewidth=1.5, markersize=6, alpha=0.7)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Latency (ms)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Log scale for large ranges
        if max(scales) / min(scales) > 100:
            ax.set_xscale('log')
    
    def _plot_overhead_trends(self, ax):
        """Plot overhead trends across dimensions"""
        dimensions = ['Users', 'Content', 'Constraints', 'Requests']
        mean_overheads = []
        
        for dim_key in ['user_scaling', 'content_scaling', 'constraint_scaling', 
                       'request_scaling']:
            if dim_key in self.results:
                overheads = [v['overhead']['mean_pct'] 
                           for v in self.results[dim_key].values()]
                mean_overheads.append(np.mean(overheads))
            else:
                mean_overheads.append(0)
        
        bars = ax.bar(dimensions, mean_overheads, color=['#1f77b4', '#ff7f0e', 
                                                         '#2ca02c', '#d62728'])
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom')
        
        ax.set_ylabel('Average Overhead (%)')
        ax.set_title('Average Overhead by Scaling Dimension')
        ax.grid(True, axis='y', alpha=0.3)
    
    def _format_for_visualization(self) -> Dict:
        """Format results for visualization function"""
        formatted = {}
        
        # Convert each scaling dimension
        for dim_name, dim_data in self.results.items():
            if dim_name.endswith('_scaling') and dim_name != 'parallel_scaling':
                for scale, data in dim_data.items():
                    formatted[scale] = {
                        'baseline': data['baseline']['latencies'],
                        'ethics': data['ethics']['latencies']
                    }
        
        return formatted
    
    def _save_results(self):
        """Save scalability results"""
        output_dir = Path('results/data')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw results
        output_file = output_dir / 'scalability_results.json'
        
        # Convert to serializable format
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(v) for v in obj]
            return obj
        
        serializable_results = convert_to_serializable(self.results)
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        # Save summary
        self._save_summary()
        
        logger.info(f"Results saved to {output_dir}")
    
    def _save_summary(self):
        """Save scalability summary"""
        summary_path = Path('results/data/scalability_summary.txt')
        
        with open(summary_path, 'w') as f:
            f.write("SCALABILITY ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            # User scaling summary
            if 'user_scaling' in self.results:
                f.write("USER SCALING:\n")
                for scale, data in sorted(self.results['user_scaling'].items()):
                    f.write(f"  {scale:,} users: {data['overhead']['mean_pct']:.1f}% overhead\n")
                f.write("\n")
            
            # Content scaling summary
            if 'content_scaling' in self.results:
                f.write("CONTENT SCALING:\n")
                for scale, data in sorted(self.results['content_scaling'].items()):
                    f.write(f"  {scale:,} items: {data['overhead']['mean_pct']:.1f}% overhead\n")
                f.write("\n")
            
            # Constraint scaling summary
            if 'constraint_scaling' in self.results:
                f.write("CONSTRAINT SCALING:\n")
                for scale, data in sorted(self.results['constraint_scaling'].items()):
                    f.write(f"  {scale} constraints: {data['overhead']['mean_pct']:.1f}% overhead\n")
                f.write("\n")
            
            # Request scaling summary
            if 'request_scaling' in self.results:
                f.write("REQUEST VOLUME SCALING:\n")
                for scale, data in sorted(self.results['request_scaling'].items()):
                    f.write(f"  {scale:,} requests: {data['overhead']['mean_pct']:.1f}% overhead\n")
                f.write("\n")
            
            # Parallel scaling summary
            if 'parallel_scaling' in self.results:
                f.write("PARALLEL PROCESSING:\n")
                for threads, data in sorted(self.results['parallel_scaling'].items()):
                    f.write(f"  {threads} threads: {data['throughput']:.1f} req/s\n")


def main():
    """Main entry point for scalability experiment"""
    import argparse
    import yaml
    
    parser = argparse.ArgumentParser(description='Run scalability analysis experiment')
    parser.add_argument('--config', type=str, default='configs/experiment_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--dimension', type=str, default='all',
                       choices=['all', 'users', 'content', 'constraints', 'requests', 'parallel'],
                       help='Scaling dimension to test')
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run experiment
    experiment = ScalabilityExperiment(config)
    
    if args.dimension == 'all':
        results = experiment.run_comprehensive_analysis()
    elif args.dimension == 'users':
        results = experiment.run_user_scaling([100, 1000, 10000, 100000])
    elif args.dimension == 'content':
        results = experiment.run_content_scaling([1000, 10000, 100000, 1000000])
    elif args.dimension == 'constraints':
        results = experiment.run_constraint_scaling([1, 3, 5, 10, 20])
    elif args.dimension == 'requests':
        results = experiment.run_request_scaling([100, 1000, 5000, 10000])
    elif args.dimension == 'parallel':
        results = experiment.run_parallel_scaling([1, 2, 4, 8, 16])
    
    print("\nScalability analysis complete!")
    print("Results saved to: results/data/scalability_results.json")
    print("Visualizations saved to: results/figures/")


if __name__ == "__main__":
    main()