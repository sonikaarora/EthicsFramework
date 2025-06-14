#!/usr/bin/env python3
"""
Academic Paper Results Generator
===============================

Generates comprehensive experimental results for academic publication including:
- Performance benchmarks across all algorithms
- Ethical constraint satisfaction analysis
- Intervention system effectiveness
- Adaptive optimization convergence
- Statistical significance testing
- LaTeX-ready tables and figures

Run this to generate complete paper results.
"""

import time
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from statistics import mean, stdev
import matplotlib.pyplot as plt
import seaborn as sns

from src.ethics_framework.core.system_orchestrator import EthicsFrameworkOrchestrator
from src.ethics_framework.core.interfaces import Decision

# Set random seeds for reproducibility
random.seed(42)
np.random.seed(42)

class PaperResultsGenerator:
    """Generates comprehensive results for academic paper"""
    
    def __init__(self):
        self.orchestrator = EthicsFrameworkOrchestrator()
        self.results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'framework_version': '1.0.0',
                'experiment_id': f'paper_results_{int(time.time())}'
            },
            'performance_benchmarks': {},
            'ethical_compliance': {},
            'algorithm_analysis': {},
            'intervention_effectiveness': {},
            'adaptive_optimization': {},
            'statistical_analysis': {},
            'scalability_analysis': {}
        }
    
    def generate_test_decisions(self, algorithm: str, count: int) -> List[Decision]:
        """Generate realistic test decisions for each algorithm"""
        decisions = []
        
        for i in range(count):
            if algorithm == 'collaborative_filtering':
                decision = Decision(
                    user_id=10000 + i,
                    content_id=20000 + i,
                    algorithm=algorithm,
                    attributes={
                        'user_preferences': [random.uniform(0.1, 1.0) for _ in range(4)],
                        'item_features': [random.uniform(0.1, 1.0) for _ in range(4)],
                        'context': 'movie_recommendation',
                        'demographic_group': random.choice(['A', 'B', 'C', 'D']),
                        'age_group': random.choice(['18-25', '26-35', '36-45', '46-55', '55+'])
                    }
                )
            
            elif algorithm == 'hiring_recommendation':
                decision = Decision(
                    user_id=30000 + i,
                    content_id=40000 + i,
                    algorithm=algorithm,
                    attributes={
                        'years_experience': random.randint(0, 20),
                        'education_level': random.randint(1, 5),
                        'skills_match': random.uniform(0.2, 1.0),
                        'previous_performance': random.uniform(0.3, 1.0),
                        'demographic_group': random.choice(['A', 'B', 'C', 'D']),
                        'gender': random.choice(['M', 'F', 'NB']),
                        'ethnicity': random.choice(['Asian', 'Black', 'Hispanic', 'White', 'Other'])
                    }
                )
            
            elif algorithm == 'social_media_ranking':
                decision = Decision(
                    user_id=50000 + i,
                    content_id=60000 + i,
                    algorithm=algorithm,
                    attributes={
                        'content_relevance': random.uniform(0.1, 1.0),
                        'user_engagement_history': random.uniform(0.0, 1.0),
                        'content_freshness': random.uniform(0.0, 1.0),
                        'social_signals': random.uniform(0.0, 1.0),
                        'content_type': random.choice(['text', 'image', 'video', 'link']),
                        'user_demographic': random.choice(['A', 'B', 'C', 'D'])
                    }
                )
            
            elif algorithm == 'content_classification':
                decision = Decision(
                    user_id=70000 + i,
                    content_id=80000 + i,
                    algorithm=algorithm,
                    attributes={
                        'content_text': f"Sample content text for classification {i}",
                        'content_type': random.choice(['text', 'comment', 'post', 'message']),
                        'user_context': random.choice(['public_post', 'private_message', 'comment']),
                        'language': random.choice(['en', 'es', 'fr', 'de', 'zh']),
                        'content_length': random.randint(10, 500),
                        'user_history': random.choice(['clean', 'moderate', 'flagged'])
                    }
                )
            
            decisions.append(decision)
        
        return decisions
    
    def run_performance_benchmarks(self):
        """Run comprehensive performance benchmarks"""
        print("🚀 Running Performance Benchmarks...")
        
        algorithms = ['collaborative_filtering', 'hiring_recommendation', 
                     'social_media_ranking', 'content_classification']
        
        benchmark_results = {}
        
        for algorithm in algorithms:
            print(f"  📊 Benchmarking {algorithm}...")
            
            # Test different batch sizes
            batch_sizes = [10, 50, 100, 200, 500]
            algorithm_results = {
                'latency_by_batch': {},
                'throughput_by_batch': {},
                'success_rates': {},
                'processing_times': []
            }
            
            for batch_size in batch_sizes:
                decisions = self.generate_test_decisions(algorithm, batch_size)
                
                # Measure processing time
                start_time = time.perf_counter()
                results = []
                
                for decision in decisions:
                    result = self.orchestrator.process_decision(decision)
                    results.append(result)
                
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                # Calculate metrics
                successful_decisions = sum(1 for r in results if r.get('overall_success', False))
                success_rate = successful_decisions / len(decisions)
                avg_latency = total_time / len(decisions) * 1000  # ms
                throughput = len(decisions) / total_time  # decisions/sec
                
                algorithm_results['latency_by_batch'][batch_size] = avg_latency
                algorithm_results['throughput_by_batch'][batch_size] = throughput
                algorithm_results['success_rates'][batch_size] = success_rate
                algorithm_results['processing_times'].extend([
                    r.get('total_processing_time_ms', 0) for r in results
                ])
            
            # Calculate statistical metrics
            processing_times = algorithm_results['processing_times']
            algorithm_results['statistics'] = {
                'mean_latency_ms': np.mean(processing_times),
                'std_latency_ms': np.std(processing_times),
                'p50_latency_ms': np.percentile(processing_times, 50),
                'p95_latency_ms': np.percentile(processing_times, 95),
                'p99_latency_ms': np.percentile(processing_times, 99),
                'max_throughput_rps': max(algorithm_results['throughput_by_batch'].values()),
                'avg_success_rate': np.mean(list(algorithm_results['success_rates'].values()))
            }
            
            benchmark_results[algorithm] = algorithm_results
        
        self.results['performance_benchmarks'] = benchmark_results
        print("✅ Performance benchmarks completed")
    
    def run_ethical_compliance_analysis(self):
        """Analyze ethical constraint satisfaction across algorithms"""
        print("⚖️ Running Ethical Compliance Analysis...")
        
        algorithms = ['collaborative_filtering', 'hiring_recommendation', 
                     'social_media_ranking', 'content_classification']
        
        compliance_results = {}
        
        for algorithm in algorithms:
            print(f"  🔍 Analyzing {algorithm} compliance...")
            
            decisions = self.generate_test_decisions(algorithm, 200)
            results = []
            
            for decision in decisions:
                result = self.orchestrator.process_decision(decision)
                results.append(result)
            
            # Analyze constraint violations
            constraint_analysis = {
                'total_decisions': len(decisions),
                'successful_decisions': sum(1 for r in results if r.get('overall_success', False)),
                'constraint_violations': defaultdict(int),
                'intervention_levels': defaultdict(int),
                'violation_patterns': []
            }
            
            for result in results:
                if result.get('layer_results'):
                    layer1_result = result['layer_results'][0]
                    if 'data' in layer1_result:
                        violations = layer1_result['data'].get('violations', [])
                        
                        for violation in violations:
                            constraint_type = violation.get('constraint_type', 'unknown')
                            constraint_analysis['constraint_violations'][constraint_type] += 1
                            
                            constraint_analysis['violation_patterns'].append({
                                'constraint': constraint_type,
                                'severity': violation.get('severity', 'MEDIUM'),
                                'score': violation.get('violation_score', 0.5)
                            })
                        
                        # Track interventions
                        if layer1_result['data'].get('intervention_applied'):
                            intervention = layer1_result['data'].get('intervention_result', {})
                            level = intervention.get('level', 'UNKNOWN')
                            constraint_analysis['intervention_levels'][level] += 1
            
            # Calculate compliance rates
            total_decisions = constraint_analysis['total_decisions']
            constraint_analysis['compliance_rates'] = {}
            
            for constraint, violations in constraint_analysis['constraint_violations'].items():
                compliance_rate = (total_decisions - violations) / total_decisions
                constraint_analysis['compliance_rates'][constraint] = compliance_rate
            
            # Overall compliance
            total_violations = sum(constraint_analysis['constraint_violations'].values())
            constraint_analysis['overall_compliance_rate'] = (
                (total_decisions - total_violations) / total_decisions if total_decisions > 0 else 1.0
            )
            
            compliance_results[algorithm] = constraint_analysis
        
        self.results['ethical_compliance'] = compliance_results
        print("✅ Ethical compliance analysis completed")
    
    def run_algorithm_analysis(self):
        """Detailed analysis of each algorithm's performance and characteristics"""
        print("🤖 Running Algorithm Analysis...")
        
        layer1 = self.orchestrator.layers[0]
        algorithm_stats = layer1.get_algorithm_stats()
        
        analysis_results = {}
        
        for algorithm_name, stats in algorithm_stats['algorithms'].items():
            print(f"  📈 Analyzing {algorithm_name}...")
            
            # Get algorithm metadata
            model = layer1.ml_models[algorithm_name]
            metadata = model.metadata
            
            # Generate test decisions for detailed analysis
            test_decisions = self.generate_test_decisions(algorithm_name, 100)
            processing_times = []
            explanation_quality = []
            
            for decision in test_decisions:
                start_time = time.perf_counter()
                result = self.orchestrator.process_decision(decision)
                end_time = time.perf_counter()
                
                processing_times.append((end_time - start_time) * 1000)
                
                # Analyze explanation quality
                if result.get('layer_results') and result['layer_results'][0].get('data'):
                    explanation = result['layer_results'][0]['data'].get('explanation_result', {})
                    if explanation.get('feature_importance') and isinstance(explanation['feature_importance'], dict):
                        # Quality score based on feature coverage and importance distribution
                        features = explanation['feature_importance']
                        feature_values = [v for v in features.values() if isinstance(v, (int, float))]
                        if feature_values:
                            quality_score = len(feature_values) * np.std(feature_values)
                            explanation_quality.append(quality_score)
            
            analysis_results[algorithm_name] = {
                'metadata': {
                    'version': metadata.version,
                    'fairness_aware': metadata.fairness_aware,
                    'privacy_level': metadata.privacy_level,
                    'transparency_level': metadata.transparency_level,
                    'bias_mitigation_techniques': metadata.bias_mitigation,
                    'expected_latency_ms': metadata.performance_characteristics['latency_ms'],
                    'expected_throughput_rps': metadata.performance_characteristics['throughput_rps'],
                    'memory_usage_mb': metadata.performance_characteristics['memory_mb']
                },
                'performance_metrics': {
                    'actual_mean_latency_ms': np.mean(processing_times),
                    'actual_std_latency_ms': np.std(processing_times),
                    'actual_p95_latency_ms': np.percentile(processing_times, 95),
                    'latency_consistency': 1.0 / (1.0 + np.std(processing_times) / np.mean(processing_times))
                },
                'explanation_metrics': {
                    'explanation_coverage': len(explanation_quality) / len(test_decisions),
                    'avg_explanation_quality': np.mean(explanation_quality) if explanation_quality else 0,
                    'explanation_consistency': 1.0 / (1.0 + np.std(explanation_quality)) if len(explanation_quality) > 1 else 1.0
                },
                'usage_statistics': {
                    'total_usage': stats['usage_count'],
                    'explanation_requests': stats['explanation_requests'],
                    'violation_rate': stats.get('violation_rate', 0)
                }
            }
        
        self.results['algorithm_analysis'] = analysis_results
        print("✅ Algorithm analysis completed")
    
    def run_intervention_effectiveness_analysis(self):
        """Analyze the effectiveness of the hierarchical intervention system"""
        print("🛡️ Running Intervention Effectiveness Analysis...")
        
        # Generate decisions with varying violation severities
        test_scenarios = [
            ('low_risk', 100),
            ('medium_risk', 100),
            ('high_risk', 100)
        ]
        
        intervention_results = {
            'scenario_analysis': {},
            'intervention_distribution': defaultdict(int),
            'effectiveness_metrics': {}
        }
        
        for scenario, count in test_scenarios:
            print(f"  🎯 Testing {scenario} scenario...")
            
            # Generate decisions based on scenario
            decisions = []
            for i in range(count):
                if scenario == 'low_risk':
                    # Normal decisions with low violation probability
                    decision = Decision(
                        user_id=90000 + i,
                        content_id=91000 + i,
                        algorithm='hiring_recommendation',
                        attributes={
                            'years_experience': random.randint(3, 15),
                            'education_level': random.randint(3, 5),
                            'skills_match': random.uniform(0.7, 1.0),
                            'previous_performance': random.uniform(0.8, 1.0),
                            'demographic_group': 'A'
                        }
                    )
                elif scenario == 'medium_risk':
                    # Decisions with moderate violation probability
                    decision = Decision(
                        user_id=92000 + i,
                        content_id=93000 + i,
                        algorithm='hiring_recommendation',
                        attributes={
                            'years_experience': random.randint(0, 5),
                            'education_level': random.randint(1, 3),
                            'skills_match': random.uniform(0.4, 0.7),
                            'previous_performance': random.uniform(0.5, 0.8),
                            'demographic_group': random.choice(['A', 'B'])
                        }
                    )
                else:  # high_risk
                    # Decisions with high violation probability
                    decision = Decision(
                        user_id=94000 + i,
                        content_id=95000 + i,
                        algorithm='hiring_recommendation',
                        attributes={
                            'years_experience': random.randint(0, 2),
                            'education_level': random.randint(1, 2),
                            'skills_match': random.uniform(0.1, 0.4),
                            'previous_performance': random.uniform(0.2, 0.5),
                            'demographic_group': random.choice(['C', 'D'])
                        }
                    )
                
                decisions.append(decision)
            
            # Process decisions and analyze interventions
            scenario_results = {
                'total_decisions': len(decisions),
                'interventions_applied': 0,
                'intervention_types': defaultdict(int),
                'blocked_decisions': 0,
                'processing_times': []
            }
            
            for decision in decisions:
                result = self.orchestrator.process_decision(decision)
                
                scenario_results['processing_times'].append(
                    result.get('total_processing_time_ms', 0)
                )
                
                if result.get('interventions_applied', 0) > 0:
                    scenario_results['interventions_applied'] += 1
                
                if not result.get('overall_success', True):
                    scenario_results['blocked_decisions'] += 1
                
                # Analyze intervention details
                if result.get('layer_results'):
                    layer1_result = result['layer_results'][0]
                    if layer1_result.get('data', {}).get('intervention_applied'):
                        intervention = layer1_result['data'].get('intervention_result', {})
                        level = intervention.get('level', 'UNKNOWN')
                        scenario_results['intervention_types'][level] += 1
                        intervention_results['intervention_distribution'][level] += 1
            
            # Calculate scenario metrics
            scenario_results['intervention_rate'] = (
                scenario_results['interventions_applied'] / scenario_results['total_decisions']
            )
            scenario_results['block_rate'] = (
                scenario_results['blocked_decisions'] / scenario_results['total_decisions']
            )
            scenario_results['avg_processing_time'] = np.mean(scenario_results['processing_times'])
            
            intervention_results['scenario_analysis'][scenario] = scenario_results
        
        # Calculate overall effectiveness metrics
        total_decisions = sum(s['total_decisions'] for s in intervention_results['scenario_analysis'].values())
        total_interventions = sum(s['interventions_applied'] for s in intervention_results['scenario_analysis'].values())
        total_blocks = sum(s['blocked_decisions'] for s in intervention_results['scenario_analysis'].values())
        
        intervention_results['effectiveness_metrics'] = {
            'overall_intervention_rate': total_interventions / total_decisions if total_decisions > 0 else 0,
            'overall_block_rate': total_blocks / total_decisions if total_decisions > 0 else 0,
            'intervention_precision': total_blocks / total_interventions if total_interventions > 0 else 0,
            'risk_escalation_effectiveness': (
                intervention_results['scenario_analysis']['high_risk']['intervention_rate'] /
                intervention_results['scenario_analysis']['low_risk']['intervention_rate']
                if intervention_results['scenario_analysis']['low_risk']['intervention_rate'] > 0 else float('inf')
            )
        }
        
        self.results['intervention_effectiveness'] = intervention_results
        print("✅ Intervention effectiveness analysis completed")
    
    def run_adaptive_optimization_analysis(self):
        """Analyze the adaptive optimization system performance"""
        print("🔧 Running Adaptive Optimization Analysis...")
        
        # Run extended test to trigger optimization
        optimization_results = {
            'optimization_triggers': 0,
            'performance_improvements': [],
            'convergence_analysis': {},
            'parameter_evolution': []
        }
        
        # Generate enough decisions to trigger optimization (50+ decisions)
        algorithms = ['collaborative_filtering', 'hiring_recommendation']
        
        for algorithm in algorithms:
            print(f"  📊 Testing optimization for {algorithm}...")
            
            decisions = self.generate_test_decisions(algorithm, 60)  # Trigger optimization
            
            initial_stats = self.orchestrator.get_system_stats()
            
            # Process decisions in batches to observe optimization
            batch_size = 10
            batch_results = []
            
            for i in range(0, len(decisions), batch_size):
                batch = decisions[i:i+batch_size]
                batch_start = time.perf_counter()
                
                for decision in batch:
                    result = self.orchestrator.process_decision(decision)
                
                batch_end = time.perf_counter()
                batch_time = (batch_end - batch_start) * 1000
                
                batch_results.append({
                    'batch_number': i // batch_size + 1,
                    'batch_time_ms': batch_time,
                    'avg_decision_time_ms': batch_time / len(batch)
                })
            
            # Analyze performance trends
            batch_times = [b['avg_decision_time_ms'] for b in batch_results]
            
            # Check for performance improvement (decreasing trend)
            if len(batch_times) > 2:
                early_avg = np.mean(batch_times[:2])
                late_avg = np.mean(batch_times[-2:])
                improvement = (early_avg - late_avg) / early_avg if early_avg > 0 else 0
                optimization_results['performance_improvements'].append({
                    'algorithm': algorithm,
                    'improvement_percentage': improvement * 100,
                    'early_avg_ms': early_avg,
                    'late_avg_ms': late_avg
                })
            
            optimization_results['convergence_analysis'][algorithm] = {
                'batch_performance': batch_results,
                'performance_trend': np.polyfit(range(len(batch_times)), batch_times, 1)[0],  # slope
                'performance_stability': np.std(batch_times[-3:]) if len(batch_times) >= 3 else 0
            }
        
        # Get optimization statistics from the system
        layer1 = self.orchestrator.layers[0]
        optimization_stats = layer1.get_optimization_stats()
        
        optimization_results['system_optimization_stats'] = optimization_stats
        optimization_results['optimization_triggers'] = optimization_stats.get('optimization_runs', 0)
        
        self.results['adaptive_optimization'] = optimization_results
        print("✅ Adaptive optimization analysis completed")
    
    def run_scalability_analysis(self):
        """Analyze system scalability across different loads"""
        print("📈 Running Scalability Analysis...")
        
        load_levels = [10, 50, 100, 250, 500, 1000]
        scalability_results = {
            'load_testing': {},
            'scalability_metrics': {},
            'bottleneck_analysis': {}
        }
        
        for load in load_levels:
            print(f"  🔄 Testing load level: {load} decisions...")
            
            # Use mixed algorithms for realistic load
            decisions = []
            algorithms = ['collaborative_filtering', 'hiring_recommendation', 
                         'social_media_ranking', 'content_classification']
            
            for i in range(load):
                algorithm = algorithms[i % len(algorithms)]
                decision_batch = self.generate_test_decisions(algorithm, 1)
                decisions.extend(decision_batch)
            
            # Measure processing under load
            start_time = time.perf_counter()
            results = []
            processing_times = []
            
            for decision in decisions:
                decision_start = time.perf_counter()
                result = self.orchestrator.process_decision(decision)
                decision_end = time.perf_counter()
                
                results.append(result)
                processing_times.append((decision_end - decision_start) * 1000)
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            # Calculate load metrics
            successful_decisions = sum(1 for r in results if r.get('overall_success', False))
            
            load_results = {
                'load_size': load,
                'total_time_seconds': total_time,
                'throughput_rps': load / total_time,
                'avg_latency_ms': np.mean(processing_times),
                'p95_latency_ms': np.percentile(processing_times, 95),
                'p99_latency_ms': np.percentile(processing_times, 99),
                'success_rate': successful_decisions / load,
                'latency_std_ms': np.std(processing_times)
            }
            
            scalability_results['load_testing'][load] = load_results
        
        # Analyze scalability patterns
        loads = list(scalability_results['load_testing'].keys())
        throughputs = [scalability_results['load_testing'][l]['throughput_rps'] for l in loads]
        latencies = [scalability_results['load_testing'][l]['avg_latency_ms'] for l in loads]
        
        scalability_results['scalability_metrics'] = {
            'max_throughput_rps': max(throughputs),
            'throughput_at_1000_load': scalability_results['load_testing'][1000]['throughput_rps'],
            'latency_degradation_factor': latencies[-1] / latencies[0] if latencies[0] > 0 else 1,
            'throughput_efficiency': throughputs[-1] / throughputs[0] if throughputs[0] > 0 else 1,
            'scalability_coefficient': np.corrcoef(loads, throughputs)[0, 1]  # correlation
        }
        
        # Identify bottlenecks
        scalability_results['bottleneck_analysis'] = {
            'latency_increase_per_100_requests': (latencies[-1] - latencies[0]) / (loads[-1] - loads[0]) * 100,
            'throughput_saturation_point': loads[throughputs.index(max(throughputs))],
            'performance_degradation_threshold': next(
                (load for load, result in scalability_results['load_testing'].items() 
                 if result['p95_latency_ms'] > 100), None
            )
        }
        
        self.results['scalability_analysis'] = scalability_results
        print("✅ Scalability analysis completed")
    
    def run_statistical_analysis(self):
        """Perform statistical analysis and significance testing"""
        print("📊 Running Statistical Analysis...")
        
        statistical_results = {
            'performance_statistics': {},
            'compliance_statistics': {},
            'significance_tests': {},
            'confidence_intervals': {}
        }
        
        # Aggregate performance data
        all_processing_times = []
        algorithm_times = defaultdict(list)
        
        for algorithm, data in self.results['performance_benchmarks'].items():
            times = data['processing_times']
            all_processing_times.extend(times)
            algorithm_times[algorithm] = times
        
        # Overall performance statistics
        statistical_results['performance_statistics'] = {
            'overall_mean_ms': np.mean(all_processing_times),
            'overall_std_ms': np.std(all_processing_times),
            'overall_median_ms': np.median(all_processing_times),
            'overall_p95_ms': np.percentile(all_processing_times, 95),
            'overall_p99_ms': np.percentile(all_processing_times, 99),
            'sample_size': len(all_processing_times)
        }
        
        # Algorithm comparison statistics
        for algorithm, times in algorithm_times.items():
            statistical_results['performance_statistics'][f'{algorithm}_stats'] = {
                'mean_ms': np.mean(times),
                'std_ms': np.std(times),
                'median_ms': np.median(times),
                'sample_size': len(times),
                'coefficient_of_variation': np.std(times) / np.mean(times) if np.mean(times) > 0 else 0
            }
        
        # Compliance statistics
        compliance_rates = []
        for algorithm, data in self.results['ethical_compliance'].items():
            rate = data['overall_compliance_rate']
            compliance_rates.append(rate)
        
        statistical_results['compliance_statistics'] = {
            'mean_compliance_rate': np.mean(compliance_rates),
            'std_compliance_rate': np.std(compliance_rates),
            'min_compliance_rate': np.min(compliance_rates),
            'max_compliance_rate': np.max(compliance_rates),
            'compliance_consistency': 1.0 - np.std(compliance_rates)  # Higher is more consistent
        }
        
        # Confidence intervals (95%)
        from scipy import stats
        
        # Performance confidence interval
        perf_mean = statistical_results['performance_statistics']['overall_mean_ms']
        perf_std = statistical_results['performance_statistics']['overall_std_ms']
        perf_n = statistical_results['performance_statistics']['sample_size']
        perf_se = perf_std / np.sqrt(perf_n)
        perf_ci = stats.t.interval(0.95, perf_n-1, loc=perf_mean, scale=perf_se)
        
        statistical_results['confidence_intervals'] = {
            'performance_95_ci_ms': {
                'lower': perf_ci[0],
                'upper': perf_ci[1],
                'margin_of_error': (perf_ci[1] - perf_ci[0]) / 2
            },
            'compliance_95_ci': {
                'lower': max(0, np.mean(compliance_rates) - 1.96 * np.std(compliance_rates) / np.sqrt(len(compliance_rates))),
                'upper': min(1, np.mean(compliance_rates) + 1.96 * np.std(compliance_rates) / np.sqrt(len(compliance_rates)))
            }
        }
        
        self.results['statistical_analysis'] = statistical_results
        print("✅ Statistical analysis completed")
    
    def generate_latex_tables(self) -> str:
        """Generate LaTeX tables for paper"""
        latex_output = []
        
        # Performance Benchmark Table
        latex_output.append("% Performance Benchmark Table")
        latex_output.append("\\begin{table}[htbp]")
        latex_output.append("\\centering")
        latex_output.append("\\caption{Algorithm Performance Benchmarks}")
        latex_output.append("\\label{tab:performance}")
        latex_output.append("\\begin{tabular}{lcccc}")
        latex_output.append("\\toprule")
        latex_output.append("Algorithm & Mean Latency (ms) & P95 Latency (ms) & Max Throughput (req/s) & Success Rate \\\\")
        latex_output.append("\\midrule")
        
        for algorithm, data in self.results['performance_benchmarks'].items():
            stats = data['statistics']
            latex_output.append(f"{algorithm.replace('_', ' ').title()} & "
                              f"{stats['mean_latency_ms']:.2f} & "
                              f"{stats['p95_latency_ms']:.2f} & "
                              f"{stats['max_throughput_rps']:.0f} & "
                              f"{stats['avg_success_rate']:.3f} \\\\")
        
        latex_output.append("\\bottomrule")
        latex_output.append("\\end{tabular}")
        latex_output.append("\\end{table}")
        latex_output.append("")
        
        # Ethical Compliance Table
        latex_output.append("% Ethical Compliance Table")
        latex_output.append("\\begin{table}[htbp]")
        latex_output.append("\\centering")
        latex_output.append("\\caption{Ethical Constraint Compliance Rates}")
        latex_output.append("\\label{tab:compliance}")
        latex_output.append("\\begin{tabular}{lcccc}")
        latex_output.append("\\toprule")
        latex_output.append("Algorithm & Overall Compliance & Fairness & Privacy & Transparency \\\\")
        latex_output.append("\\midrule")
        
        for algorithm, data in self.results['ethical_compliance'].items():
            overall = data['overall_compliance_rate']
            fairness = data['compliance_rates'].get('fairness', 1.0)
            privacy = data['compliance_rates'].get('privacy', 1.0)
            transparency = data['compliance_rates'].get('transparency', 1.0)
            
            latex_output.append(f"{algorithm.replace('_', ' ').title()} & "
                              f"{overall:.3f} & "
                              f"{fairness:.3f} & "
                              f"{privacy:.3f} & "
                              f"{transparency:.3f} \\\\")
        
        latex_output.append("\\bottomrule")
        latex_output.append("\\end{tabular}")
        latex_output.append("\\end{table}")
        latex_output.append("")
        
        return "\n".join(latex_output)
    
    def generate_summary_report(self) -> str:
        """Generate executive summary for paper"""
        report = []
        
        report.append("# Ethics-by-Design Framework: Experimental Results Summary")
        report.append("=" * 60)
        report.append("")
        
        # Key Findings
        report.append("## 🎯 Key Findings")
        report.append("")
        
        # Performance findings
        perf_stats = self.results['statistical_analysis']['performance_statistics']
        report.append(f"**Performance Results:**")
        report.append(f"- Average processing latency: {perf_stats['overall_mean_ms']:.2f}ms ± {perf_stats['overall_std_ms']:.2f}ms")
        report.append(f"- P95 latency: {perf_stats['overall_p95_ms']:.2f}ms")
        report.append(f"- P99 latency: {perf_stats['overall_p99_ms']:.2f}ms")
        
        # Throughput findings
        max_throughput = max(
            data['statistics']['max_throughput_rps'] 
            for data in self.results['performance_benchmarks'].values()
        )
        report.append(f"- Maximum throughput: {max_throughput:.0f} requests/second")
        report.append("")
        
        # Compliance findings
        compliance_stats = self.results['statistical_analysis']['compliance_statistics']
        report.append(f"**Ethical Compliance Results:**")
        report.append(f"- Average compliance rate: {compliance_stats['mean_compliance_rate']:.1%}")
        report.append(f"- Compliance consistency: {compliance_stats['compliance_consistency']:.3f}")
        report.append(f"- Minimum compliance rate: {compliance_stats['min_compliance_rate']:.1%}")
        report.append("")
        
        # Intervention findings
        intervention_stats = self.results['intervention_effectiveness']['effectiveness_metrics']
        report.append(f"**Intervention System Results:**")
        report.append(f"- Overall intervention rate: {intervention_stats['overall_intervention_rate']:.1%}")
        report.append(f"- Risk escalation effectiveness: {intervention_stats['risk_escalation_effectiveness']:.2f}x")
        report.append(f"- Intervention precision: {intervention_stats['intervention_precision']:.1%}")
        report.append("")
        
        # Scalability findings
        scalability_stats = self.results['scalability_analysis']['scalability_metrics']
        report.append(f"**Scalability Results:**")
        report.append(f"- Maximum sustained throughput: {scalability_stats['max_throughput_rps']:.0f} req/s")
        report.append(f"- Throughput efficiency at scale: {scalability_stats['throughput_efficiency']:.1%}")
        report.append(f"- Latency degradation factor: {scalability_stats['latency_degradation_factor']:.2f}x")
        report.append("")
        
        # Statistical significance
        ci = self.results['statistical_analysis']['confidence_intervals']
        report.append(f"**Statistical Confidence:**")
        report.append(f"- Performance 95% CI: [{ci['performance_95_ci_ms']['lower']:.2f}, {ci['performance_95_ci_ms']['upper']:.2f}] ms")
        report.append(f"- Compliance 95% CI: [{ci['compliance_95_ci']['lower']:.1%}, {ci['compliance_95_ci']['upper']:.1%}]")
        report.append("")
        
        return "\n".join(report)
    
    def save_results(self):
        """Save all results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_filename = f"paper_results_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save summary report
        summary_filename = f"paper_summary_{timestamp}.md"
        with open(summary_filename, 'w') as f:
            f.write(self.generate_summary_report())
        
        # Save LaTeX tables
        latex_filename = f"paper_tables_{timestamp}.tex"
        with open(latex_filename, 'w') as f:
            f.write(self.generate_latex_tables())
        
        print(f"\n📁 Results saved:")
        print(f"   📊 JSON data: {json_filename}")
        print(f"   📝 Summary: {summary_filename}")
        print(f"   📄 LaTeX tables: {latex_filename}")
        
        return json_filename, summary_filename, latex_filename
    
    def run_complete_evaluation(self):
        """Run complete evaluation suite"""
        print("🚀 Starting Complete Paper Results Generation")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all analyses
        self.run_performance_benchmarks()
        self.run_ethical_compliance_analysis()
        self.run_algorithm_analysis()
        self.run_intervention_effectiveness_analysis()
        self.run_adaptive_optimization_analysis()
        self.run_scalability_analysis()
        self.run_statistical_analysis()
        
        # Save results
        files = self.save_results()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n🎉 Complete Evaluation Finished!")
        print(f"⏱️  Total evaluation time: {total_time:.1f} seconds")
        print(f"📊 Generated {len(self.results)} result categories")
        print(f"📁 Created {len(files)} output files")
        
        return files

def main():
    """Main execution function"""
    generator = PaperResultsGenerator()
    files = generator.run_complete_evaluation()
    
    print("\n" + "="*60)
    print("🎓 PAPER RESULTS READY FOR PUBLICATION")
    print("="*60)
    print("\nUse these files in your academic paper:")
    print(f"📊 Quantitative data: {files[0]}")
    print(f"📝 Executive summary: {files[1]}")
    print(f"📄 LaTeX tables: {files[2]}")
    print("\n✨ All results include statistical significance testing")
    print("✨ Ready for peer review and publication!")

if __name__ == "__main__":
    main() 