"""
experiments/baseline_comparison.py
==================================
Baseline comparison experiment: Traditional ML vs Ethics-Aware System
"""

import numpy as np
import pandas as pd
import time
import logging
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import json
from pathlib import Path

from src.ethics_framework.core.constraints import (
    FairnessConstraint, PrivacyConstraint, TransparencyConstraint,
    ConsentConstraint, WellbeingConstraint
)
from src.ethics_framework.core.layers import (
    Layer1_EthicalAIServices, Layer2_PrivacyPreserving,
    Layer3_ExplainabilityTransparency, Layer4_BiasDetectionMitigation,
    Layer5_AdaptiveGovernance
)
from src.ethics_framework.core.interfaces import Decision, SystemOrchestrator
from src.ethics_framework.simulation.workload_generator import WorkloadGenerator, WorkloadConfig
from src.ethics_framework.analysis.statistical_analysis import StatisticalAnalyzer
from src.ethics_framework.visualization.latency_plots import plot_latency_distributions

logger = logging.getLogger(__name__)


class BaselineMLSystem:
    """Traditional ML system without ethical constraints"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.matrix_size = config.get('matrix_size', 80)
        self.cache = {}
        self.metrics = []
        self.cache_hits = 0
        self.total_requests = 0
        
    def process(self, decision: Decision) -> Dict:
        """Process decision with traditional ML inference"""
        start_time = time.perf_counter()
        self.total_requests += 1
        
        # Check cache
        cache_key = f"{decision.user_id}_{decision.content_id}_{decision.algorithm}"
        if cache_key in self.cache and self.config.get('enable_cache', True):
            self.cache_hits += 1
            cached_result = self.cache[cache_key].copy()
            cached_result['cache_hit'] = True
            cached_result['latency_ms'] = 0.1  # Cache hit latency
            self.metrics.append(0.1)
            return cached_result
        
        # Simulate realistic ML inference
        result = self._simulate_ml_inference(decision)
        
        # Update cache
        if len(self.cache) < self.config.get('cache_size', 10000):
            self.cache[cache_key] = result.copy()
        
        latency = (time.perf_counter() - start_time) * 1000
        result['latency_ms'] = latency
        self.metrics.append(latency)
        
        return result
    
    def _simulate_ml_inference(self, decision: Decision) -> Dict:
        """Simulate ML inference workload"""
        np.random.seed(hash(str(decision)) % 10000)
        
        # Feature extraction
        features = np.random.randn(self.matrix_size // 2, self.matrix_size // 2)
        
        # Neural network layers
        layer_sizes = [self.matrix_size, self.matrix_size // 2, self.matrix_size // 4]
        activations = features.flatten()
        
        for size in layer_sizes:
            weights = np.random.randn(len(activations), size) * 0.01
            activations = np.tanh(activations @ weights)
        
        # Final prediction
        score = float(np.mean(activations))
        confidence = float(np.std(activations))
        
        # Post-processing
        for _ in range(200):
            score = np.sin(score * 2.1) * 0.99 + 0.01
        
        return {
            'score': score,
            'confidence': confidence,
            'algorithm': decision.algorithm,
            'features_used': ['user_history', 'content_features', 'context'],
            'model_version': 'baseline_v1.0'
        }
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        if not self.metrics:
            return {}
        
        return {
            'mean_latency': np.mean(self.metrics),
            'median_latency': np.median(self.metrics),
            'p50_latency': np.percentile(self.metrics, 50),
            'p75_latency': np.percentile(self.metrics, 75),
            'p90_latency': np.percentile(self.metrics, 90),
            'p95_latency': np.percentile(self.metrics, 95),
            'p99_latency': np.percentile(self.metrics, 99),
            'std_latency': np.std(self.metrics),
            'min_latency': np.min(self.metrics),
            'max_latency': np.max(self.metrics),
            'total_requests': self.total_requests,
            'cache_hit_rate': self.cache_hits / max(1, self.total_requests)
        }


class EthicsAwareMLSystem:
    """ML system with full ethics-by-design architecture"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics = []
        self.constraint_violations = []
        self.layer_metrics = {i: [] for i in range(1, 6)}
        
        # Initialize the full system
        self._setup_system()
        
    def _setup_system(self):
        """Initialize all layers and components"""
        # Create constraints
        self.constraints = self._create_constraints()
        
        # Initialize layers
        self.layer1 = Layer1_EthicalAIServices(self.constraints)
        self.layer2 = Layer2_PrivacyPreserving(
            epsilon=self.config.get('privacy_epsilon', 1.0),
            delta=self.config.get('privacy_delta', 1e-5)
        )
        self.layer3 = Layer3_ExplainabilityTransparency()
        self.layer4 = Layer4_BiasDetectionMitigation(
            monitoring_window=self.config.get('monitoring_window', 1000)
        )
        self.layer5 = Layer5_AdaptiveGovernance(
            policy_config=self.config.get('policy_config', {
                'policies': [],
                'enforcement_mode': 'balanced'
            })
        )
        
        # Register ML algorithms
        self._register_algorithms()
        
        # Setup orchestrator
        self.orchestrator = SystemOrchestrator()
        for i, layer in enumerate([self.layer1, self.layer2, self.layer3, 
                                  self.layer4, self.layer5], 1):
            self.orchestrator.register_layer(i, layer)
        
        self.orchestrator.start()
    
    def _create_constraints(self) -> List:
        """Create ethical constraints from configuration"""
        constraints = []
        
        for c_config in self.config.get('constraints', []):
            if c_config['type'] == 'fairness':
                constraints.append(FairnessConstraint(
                    name=c_config['name'],
                    protected_attribute=c_config['protected_attribute'],
                    fairness_metric=c_config.get('fairness_metric', 'demographic_parity'),
                    threshold=c_config.get('threshold', 0.1)
                ))
            elif c_config['type'] == 'privacy':
                constraints.append(PrivacyConstraint(
                    name=c_config['name'],
                    epsilon=c_config.get('epsilon', 1.0),
                    delta=c_config.get('delta', 1e-5),
                    mechanism=c_config.get('mechanism', 'laplace')
                ))
            elif c_config['type'] == 'transparency':
                constraints.append(TransparencyConstraint(
                    name=c_config['name'],
                    explanation_type=c_config.get('explanation_type', 'feature_importance'),
                    min_clarity_score=c_config.get('min_clarity_score', 0.8)
                ))
            elif c_config['type'] == 'consent':
                constraints.append(ConsentConstraint(
                    name=c_config['name'],
                    consent_types=c_config.get('consent_types', ['data_processing']),
                    enforcement_mode=c_config.get('enforcement_mode', 'strict')
                ))
            elif c_config['type'] == 'wellbeing':
                constraints.append(WellbeingConstraint(
                    name=c_config['name'],
                    metric=c_config.get('metric', 'engagement_time'),
                    max_threshold=c_config.get('max_threshold', 120.0)
                ))
        
        return constraints
    
    def _register_algorithms(self):
        """Register ML algorithms with ethical properties"""
        # Recommendation algorithm
        def recommendation_algorithm(decision: Decision, context: Dict) -> Dict:
            np.random.seed(hash(str(decision)) % 10000)
            
            # Collaborative filtering simulation
            user_factors = np.random.randn(64)
            item_factors = np.random.randn(64)
            
            score = float(np.dot(user_factors, item_factors) / 
                         (np.linalg.norm(user_factors) * np.linalg.norm(item_factors)))
            
            return {
                'score': score,
                'confidence': np.random.beta(5, 2),
                'algorithm': 'collaborative_filtering',
                'explanation': 'Based on similar users and content'
            }
        
        self.layer1.register_algorithm(
            'recommendation',
            recommendation_algorithm,
            {'type': 'collaborative', 'version': '2.0', 'ethical_review': 'approved'}
        )
        
        # Ranking algorithm
        def ranking_algorithm(decision: Decision, context: Dict) -> Dict:
            np.random.seed(hash(str(decision)) % 10000)
            
            # Learning to rank simulation
            features = np.random.randn(50)
            weights = np.random.randn(50) * 0.1
            
            score = float(np.dot(features, weights))
            rank = int(np.random.zipf(1.5, 1)[0])
            
            return {
                'score': score,
                'rank_position': min(rank, 100),
                'algorithm': 'learning_to_rank',
                'features_used': 50
            }
        
        self.layer1.register_algorithm(
            'ranking',
            ranking_algorithm,
            {'type': 'pointwise', 'version': '1.5', 'bias_tested': True}
        )
    
    def process(self, decision: Decision) -> Dict:
        """Process decision through full ethics pipeline"""
        start_time = time.perf_counter()
        
        try:
            # Process through full pipeline
            result = self.orchestrator.process_decision(decision)
            
            # Extract total latency
            total_latency = (time.perf_counter() - start_time) * 1000
            self.metrics.append(total_latency)
            
            # Extract layer-specific metrics
            self._extract_layer_metrics(result)
            
            # Track violations
            if 'validation_results' in result:
                for violation in result['validation_results'].get('violations', []):
                    self.constraint_violations.append(violation)
            
            result['total_latency_ms'] = total_latency
            return result
            
        except Exception as e:
            logger.error(f"Error processing decision: {str(e)}")
            total_latency = (time.perf_counter() - start_time) * 1000
            self.metrics.append(total_latency)
            raise
    
    def _extract_layer_metrics(self, result: Dict):
        """Extract timing for each layer"""
        current = result
        
        while current and 'layer' in current:
            layer_id = current['layer']
            if 'processing_times' in current:
                total_time = current['processing_times'].get('total_ms', 0)
                self.layer_metrics[layer_id].append(total_time)
            
            current = current.get('previous_layer_data')
    
    def get_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        if not self.metrics:
            return {}
        
        stats = {
            'mean_latency': np.mean(self.metrics),
            'median_latency': np.median(self.metrics),
            'p50_latency': np.percentile(self.metrics, 50),
            'p75_latency': np.percentile(self.metrics, 75),
            'p90_latency': np.percentile(self.metrics, 90),
            'p95_latency': np.percentile(self.metrics, 95),
            'p99_latency': np.percentile(self.metrics, 99),
            'std_latency': np.std(self.metrics),
            'min_latency': np.min(self.metrics),
            'max_latency': np.max(self.metrics),
            'total_requests': len(self.metrics),
            'total_violations': len(self.constraint_violations)
        }
        
        # Add per-layer statistics
        for layer_id, timings in self.layer_metrics.items():
            if timings:
                stats[f'layer_{layer_id}_mean_ms'] = np.mean(timings)
                stats[f'layer_{layer_id}_median_ms'] = np.median(timings)
                stats[f'layer_{layer_id}_p95_ms'] = np.percentile(timings, 95)
        
        # Add constraint satisfaction rates
        for constraint in self.constraints:
            stats[f'{constraint.name}_satisfaction_rate'] = constraint.satisfaction_rate
        
        # Violation breakdown
        violation_types = {}
        for v in self.constraint_violations:
            v_type = v.get('constraint_type', 'unknown')
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
        stats['violations_by_type'] = violation_types
        
        return stats


class BaselineComparisonExperiment:
    """Main baseline comparison experiment"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.results = {}
        
    def run(self, num_requests: int = 10000, warmup_requests: int = 100) -> Dict:
        """Run the baseline comparison experiment"""
        logger.info(f"Starting baseline comparison experiment with {num_requests} requests")
        
        # Generate workload
        workload_config = WorkloadConfig(
            num_requests=num_requests + warmup_requests,
            num_users=self.config.get('num_users', 100000),
            num_content=self.config.get('num_content', 1000000),
            seed=self.config.get('random_seed', 42)
        )
        
        generator = WorkloadGenerator(workload_config)
        decisions = generator.generate()
        
        # Split into warmup and test
        warmup_decisions = decisions[:warmup_requests]
        test_decisions = decisions[warmup_requests:]
        
        # Initialize systems
        baseline_system = BaselineMLSystem(self.config)
        ethics_system = EthicsAwareMLSystem(self.config)
        
        # Warmup phase
        logger.info("Running warmup phase...")
        for decision in tqdm(warmup_decisions, desc="Warmup"):
            baseline_system.process(decision)
            ethics_system.process(decision)
        
        # Clear metrics after warmup
        baseline_system.metrics = []
        ethics_system.metrics = []
        
        # Main experiment
        logger.info("Running main experiment...")
        baseline_results = []
        ethics_results = []
        
        for i, decision in enumerate(tqdm(test_decisions, desc="Processing")):
            # Process with baseline
            baseline_result = baseline_system.process(decision)
            baseline_results.append({
                'decision_id': i,
                'latency_ms': baseline_result['latency_ms'],
                'cache_hit': baseline_result.get('cache_hit', False),
                'score': baseline_result.get('score', 0)
            })
            
            # Process with ethics system
            ethics_result = ethics_system.process(decision)
            ethics_results.append({
                'decision_id': i,
                'latency_ms': ethics_result.get('total_latency_ms', 0),
                'approved': ethics_result.get('governance_decision', {}).get('approved', True),
                'violations': len(ethics_result.get('validation_results', {}).get('violations', []))
            })
        
        # Get statistics
        baseline_stats = baseline_system.get_statistics()
        ethics_stats = ethics_system.get_statistics()
        
        # Calculate overhead
        overhead_pct = ((ethics_stats['mean_latency'] - baseline_stats['mean_latency']) / 
                       baseline_stats['mean_latency'] * 100)
        
        # Prepare results
        self.results = {
            'config': self.config,
            'num_requests': num_requests,
            'baseline': {
                'latencies': [r['latency_ms'] for r in baseline_results],
                'statistics': baseline_stats,
                'raw_results': baseline_results
            },
            'ethics': {
                'latencies': [r['latency_ms'] for r in ethics_results],
                'statistics': ethics_stats,
                'raw_results': ethics_results
            },
            'comparison': {
                'mean_overhead_ms': ethics_stats['mean_latency'] - baseline_stats['mean_latency'],
                'mean_overhead_pct': overhead_pct,
                'p95_overhead_ms': ethics_stats['p95_latency'] - baseline_stats['p95_latency'],
                'p95_overhead_pct': ((ethics_stats['p95_latency'] - baseline_stats['p95_latency']) / 
                                    baseline_stats['p95_latency'] * 100),
                'p99_overhead_ms': ethics_stats['p99_latency'] - baseline_stats['p99_latency'],
                'p99_overhead_pct': ((ethics_stats['p99_latency'] - baseline_stats['p99_latency']) / 
                                    baseline_stats['p99_latency'] * 100)
            },
            'workload_stats': generator.get_workload_statistics(test_decisions)
        }
        
        # Statistical analysis
        self._perform_statistical_analysis()
        
        # Generate visualizations
        self._generate_visualizations()
        
        logger.info(f"Experiment complete. Mean overhead: {overhead_pct:.1f}%")
        
        return self.results
    
    def _perform_statistical_analysis(self):
        """Perform statistical analysis on results"""
        analyzer = StatisticalAnalyzer()
        
        analysis = analyzer.analyze_performance_comparison(
            self.results['baseline']['latencies'],
            self.results['ethics']['latencies']
        )
        
        self.results['statistical_analysis'] = analysis
        
        # Generate statistical report
        report = analyzer.generate_report(analysis)
        self.results['statistical_report'] = report
    
    def _generate_visualizations(self):
        """Generate visualization plots"""
        output_dir = Path('results/figures')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Latency distribution plot
        fig = plot_latency_distributions(
            self.results['baseline']['latencies'],
            self.results['ethics']['latencies'],
            save_path=str(output_dir / 'baseline_comparison_latencies.pdf')
        )
        
        logger.info(f"Visualizations saved to {output_dir}")
    
    def save_results(self, output_path: Optional[str] = None):
        """Save experiment results"""
        if output_path is None:
            output_path = 'results/data/baseline_comparison_results.json'
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy arrays to lists for JSON serialization
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
        
        logger.info(f"Results saved to {output_file}")
        
        # Also save summary
        summary_path = output_file.parent / 'baseline_comparison_summary.txt'
        with open(summary_path, 'w') as f:
            f.write("BASELINE COMPARISON EXPERIMENT SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Requests: {self.results['num_requests']}\n")
            f.write(f"Baseline Mean Latency: {self.results['baseline']['statistics']['mean_latency']:.2f} ms\n")
            f.write(f"Ethics Mean Latency: {self.results['ethics']['statistics']['mean_latency']:.2f} ms\n")
            f.write(f"Mean Overhead: {self.results['comparison']['mean_overhead_pct']:.1f}%\n")
            f.write(f"P95 Overhead: {self.results['comparison']['p95_overhead_pct']:.1f}%\n")
            f.write(f"P99 Overhead: {self.results['comparison']['p99_overhead_pct']:.1f}%\n")
            f.write("\n" + self.results.get('statistical_report', ''))


def main():
    """Main entry point for baseline comparison experiment"""
    import argparse
    import yaml
    
    parser = argparse.ArgumentParser(description='Run baseline comparison experiment')
    parser.add_argument('--config', type=str, default='configs/experiment_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--requests', type=int, default=10000,
                       help='Number of requests to process')
    parser.add_argument('--warmup', type=int, default=100,
                       help='Number of warmup requests')
    parser.add_argument('--output', type=str, default=None,
                       help='Output path for results')
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run experiment
    experiment = BaselineComparisonExperiment(config)
    results = experiment.run(num_requests=args.requests, warmup_requests=args.warmup)
    
    # Save results
    experiment.save_results(args.output)
    
    print(f"\nExperiment complete!")
    print(f"Mean overhead: {results['comparison']['mean_overhead_pct']:.1f}%")
    print(f"Results saved to: results/data/")


if __name__ == "__main__":
    main()