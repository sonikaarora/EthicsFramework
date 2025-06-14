"""
experiments/constraint_composition_study.py
==========================================
Study different constraint composition strategies and their effects
"""

import numpy as np
import pandas as pd
import time
import logging
from typing import Dict, List, Tuple, Optional, Set
from itertools import combinations, product
from tqdm import tqdm
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

from src.ethics_framework.core.constraints import (
    EthicalConstraint, ConstraintType, ConstraintComposer,
    FairnessConstraint, PrivacyConstraint, TransparencyConstraint,
    ConsentConstraint, WellbeingConstraint
)
from src.ethics_framework.algorithms.constraint_composition import (
    ConstraintGraph, OptimalCompositionFinder, ConflictResolver,
    DynamicCompositionManager
)
from src.ethics_framework.simulation.workload_generator import WorkloadGenerator, WorkloadConfig
from experiments.baseline_comparison import EthicsAwareMLSystem

logger = logging.getLogger(__name__)


class ConstraintCompositionStudy:
    """Study constraint composition strategies and conflicts"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.results = {}
        self.all_constraints = self._create_all_constraints()
        
    def _create_all_constraints(self) -> List[EthicalConstraint]:
        """Create a comprehensive set of constraints for testing"""
        constraints = []
        
        # Multiple fairness constraints
        constraints.extend([
            FairnessConstraint(
                name="fairness_demographic",
                protected_attribute="demographic",
                fairness_metric="demographic_parity",
                threshold=0.1,
                weight=1.0
            ),
            FairnessConstraint(
                name="fairness_gender",
                protected_attribute="gender",
                fairness_metric="equalized_odds",
                threshold=0.15,
                weight=0.8
            ),
            FairnessConstraint(
                name="fairness_age",
                protected_attribute="age_group",
                fairness_metric="calibration",
                threshold=0.2,
                weight=0.6
            )
        ])
        
        # Privacy constraints with different mechanisms
        constraints.extend([
            PrivacyConstraint(
                name="privacy_laplace",
                epsilon=1.0,
                delta=1e-5,
                mechanism="laplace",
                weight=1.0
            ),
            PrivacyConstraint(
                name="privacy_gaussian",
                epsilon=2.0,
                delta=1e-6,
                mechanism="gaussian",
                weight=0.8
            )
        ])
        
        # Transparency constraints
        constraints.extend([
            TransparencyConstraint(
                name="transparency_features",
                explanation_type="feature_importance",
                min_clarity_score=0.8,
                weight=0.9
            ),
            TransparencyConstraint(
                name="transparency_counterfactual",
                explanation_type="counterfactual",
                min_clarity_score=0.7,
                weight=0.7
            )
        ])
        
        # Consent and wellbeing
        constraints.extend([
            ConsentConstraint(
                name="consent_comprehensive",
                consent_types=["data_processing", "profiling", "sharing"],
                enforcement_mode="strict",
                weight=1.0
            ),
            WellbeingConstraint(
                name="wellbeing_time",
                metric="engagement_time",
                max_threshold=120.0,
                weight=0.9
            ),
            WellbeingConstraint(
                name="wellbeing_diversity",
                metric="content_diversity",
                max_threshold=0.7,
                weight=0.7
            )
        ])
        
        return constraints
    
    def study_pairwise_conflicts(self) -> Dict:
        """Study conflicts between all pairs of constraints"""
        logger.info("Studying pairwise constraint conflicts...")
        
        results = {
            'conflict_matrix': {},
            'conflict_types': {},
            'resolution_strategies': {}
        }
        
        # Test all pairs
        for c1, c2 in combinations(self.all_constraints, 2):
            conflict_info = self._analyze_conflict(c1, c2)
            
            pair_key = f"{c1.name}-{c2.name}"
            results['conflict_matrix'][pair_key] = conflict_info['has_conflict']
            
            if conflict_info['has_conflict']:
                results['conflict_types'][pair_key] = conflict_info['conflict_type']
                results['resolution_strategies'][pair_key] = conflict_info['resolution']
        
        # Create conflict graph
        self._create_conflict_graph(results['conflict_matrix'])
        
        return results
    
    def _analyze_conflict(self, c1: EthicalConstraint, c2: EthicalConstraint) -> Dict:
        """Analyze potential conflict between two constraints"""
        # Known conflicts
        conflict_pairs = [
            (ConstraintType.PRIVACY, ConstraintType.TRANSPARENCY),
            (ConstraintType.FAIRNESS, ConstraintType.PRIVACY),
            (ConstraintType.TRANSPARENCY, ConstraintType.CONSENT)
        ]
        
        has_conflict = False
        conflict_type = "none"
        
        # Check for known conflicts
        for pair in conflict_pairs:
            if (c1.constraint_type == pair[0] and c2.constraint_type == pair[1]) or \
               (c1.constraint_type == pair[1] and c2.constraint_type == pair[0]):
                has_conflict = True
                conflict_type = f"{pair[0].value}-{pair[1].value}"
                break
        
        # Test empirically by running both constraints
        if not has_conflict:
            has_conflict, conflict_type = self._test_empirical_conflict(c1, c2)
        
        # Determine resolution strategy
        resolution = None
        if has_conflict:
            resolver = ConflictResolver()
            resolution = resolver.resolve(c1, c2, strategy='negotiation')
        
        return {
            'has_conflict': has_conflict,
            'conflict_type': conflict_type,
            'resolution': resolution
        }
    
    def _test_empirical_conflict(self, c1: EthicalConstraint, 
                                c2: EthicalConstraint) -> Tuple[bool, str]:
        """Test for empirical conflicts by running constraints"""
        # Generate test decisions
        test_decisions = []
        for _ in range(100):
            decision = {
                'user_id': np.random.randint(1, 1000),
                'content_id': np.random.randint(1, 10000),
                'algorithm': 'test',
                'attributes': {
                    'demographic': np.random.choice(['A', 'B', 'C']),
                    'gender': np.random.choice(['M', 'F', 'O']),
                    'age_group': np.random.choice(['18-24', '25-34', '35-44', '45+'])
                }
            }
            test_decisions.append(decision)
        
        # Test constraints
        c1_violations = 0
        c2_violations = 0
        both_violations = 0
        
        for decision in test_decisions:
            c1_satisfied, _, _ = c1.validate(decision, {})
            c2_satisfied, _, _ = c2.validate(decision, {})
            
            if not c1_satisfied:
                c1_violations += 1
            if not c2_satisfied:
                c2_violations += 1
            if not c1_satisfied and not c2_satisfied:
                both_violations += 1
        
        # Check if constraints tend to conflict
        expected_both = (c1_violations / 100) * (c2_violations / 100) * 100
        
        # Significant deviation from independence suggests conflict
        if both_violations > expected_both * 1.5:
            return True, "empirical_positive_correlation"
        elif both_violations < expected_both * 0.5:
            return True, "empirical_negative_correlation"
        
        return False, "none"
    
    def _create_conflict_graph(self, conflict_matrix: Dict):
        """Create and visualize constraint conflict graph"""
        G = nx.Graph()
        
        # Add all constraints as nodes
        for constraint in self.all_constraints:
            G.add_node(constraint.name, 
                      type=constraint.constraint_type.value,
                      weight=constraint.weight)
        
        # Add conflict edges
        for pair_key, has_conflict in conflict_matrix.items():
            if has_conflict:
                c1_name, c2_name = pair_key.split('-')
                G.add_edge(c1_name, c2_name, conflict=True)
        
        # Visualize
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Color nodes by type
        node_colors = []
        type_colors = {
            ConstraintType.FAIRNESS: '#ff7f0e',
            ConstraintType.PRIVACY: '#2ca02c',
            ConstraintType.TRANSPARENCY: '#d62728',
            ConstraintType.CONSENT: '#9467bd',
            ConstraintType.WELLBEING: '#8c564b'
        }
        
        for node in G.nodes():
            node_type = G.nodes[node]['type']
            color = type_colors.get(ConstraintType(node_type), '#1f77b4')
            node_colors.append(color)
        
        # Draw graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=1000, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        
        # Draw conflict edges in red
        conflict_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('conflict')]
        nx.draw_networkx_edges(G, pos, conflict_edges, edge_color='red', 
                              width=2, alpha=0.6)
        
        plt.title("Constraint Conflict Graph", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        
        output_dir = Path('results/figures')
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / 'constraint_conflict_graph.pdf', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def study_composition_strategies(self) -> Dict:
        """Compare different composition strategies"""
        logger.info("Studying constraint composition strategies...")
        
        strategies = ['all', 'minimal', 'balanced', 'optimal', 'adaptive']
        results = {}
        
        # Generate test workload
        workload_config = WorkloadConfig(
            num_requests=5000,
            num_users=10000,
            num_content=100000
        )
        generator = WorkloadGenerator(workload_config)
        decisions = generator.generate()
        
        for strategy in strategies:
            logger.info(f"Testing {strategy} composition strategy")
            
            # Select constraints based on strategy
            selected_constraints = self._select_constraints_by_strategy(strategy)
            
            # Create system with selected constraints
            config = self.config.copy()
            config['constraints'] = [self._constraint_to_config(c) 
                                   for c in selected_constraints]
            
            system = EthicsAwareMLSystem(config)
            
            # Process decisions
            latencies = []
            violations = []
            satisfaction_rates = {}
            
            for decision in tqdm(decisions, desc=strategy, leave=False):
                result = system.process(decision)
                latencies.append(result.get('total_latency_ms', 0))
                
                if 'validation_results' in result:
                    violations.extend(result['validation_results'].get('violations', []))
            
            # Get constraint satisfaction rates
            for constraint in system.constraints:
                satisfaction_rates[constraint.name] = constraint.satisfaction_rate
            
            results[strategy] = {
                'constraints_used': [c.name for c in selected_constraints],
                'num_constraints': len(selected_constraints),
                'latencies': latencies,
                'mean_latency': np.mean(latencies),
                'p95_latency': np.percentile(latencies, 95),
                'total_violations': len(violations),
                'satisfaction_rates': satisfaction_rates,
                'coverage_score': self._calculate_coverage(selected_constraints)
            }
        
        return results
    
    def _select_constraints_by_strategy(self, strategy: str) -> List[EthicalConstraint]:
        """Select constraints based on composition strategy"""
        if strategy == 'all':
            # Include all constraints
            return self.all_constraints
        
        elif strategy == 'minimal':
            # Only essential constraints (one per type)
            selected = []
            for constraint_type in ConstraintType:
                type_constraints = [c for c in self.all_constraints 
                                  if c.constraint_type == constraint_type]
                if type_constraints:
                    # Select highest weight
                    selected.append(max(type_constraints, key=lambda c: c.weight))
            return selected
        
        elif strategy == 'balanced':
            # Balanced selection avoiding conflicts
            selected = []
            selected.append(next(c for c in self.all_constraints 
                               if c.name == "fairness_demographic"))
            selected.append(next(c for c in self.all_constraints 
                               if c.name == "privacy_laplace"))
            selected.append(next(c for c in self.all_constraints 
                               if c.name == "transparency_features"))
            selected.append(next(c for c in self.all_constraints 
                               if c.name == "consent_comprehensive"))
            selected.append(next(c for c in self.all_constraints 
                               if c.name == "wellbeing_time"))
            return selected
        
        elif strategy == 'optimal':
            # Use optimization to find best subset
            finder = OptimalCompositionFinder(self.all_constraints)
            result = finder.find_optimal_subset(min_coverage=0.8, max_conflicts=2)
            return result['selected_constraints']
        
        elif strategy == 'adaptive':
            # Simulate adaptive selection based on context
            manager = DynamicCompositionManager()
            context = {
                'risk_level': 'medium',
                'real_time': False,
                'learning_enabled': True
            }
            result = manager.compose(self.all_constraints, context)
            return result['constraints']
        
        else:
            return self.all_constraints
    
    def _constraint_to_config(self, constraint: EthicalConstraint) -> Dict:
        """Convert constraint object to configuration dict"""
        config = {
            'type': constraint.constraint_type.value,
            'name': constraint.name,
            'weight': constraint.weight
        }
        
        # Add type-specific parameters
        if isinstance(constraint, FairnessConstraint):
            config.update({
                'protected_attribute': constraint.protected_attribute,
                'fairness_metric': constraint.fairness_metric,
                'threshold': constraint.threshold
            })
        elif isinstance(constraint, PrivacyConstraint):
            config.update({
                'epsilon': constraint.epsilon,
                'delta': constraint.delta,
                'mechanism': constraint.mechanism
            })
        elif isinstance(constraint, TransparencyConstraint):
            config.update({
                'explanation_type': constraint.explanation_type,
                'min_clarity_score': constraint.threshold
            })
        elif isinstance(constraint, ConsentConstraint):
            config.update({
                'consent_types': constraint.consent_types,
                'enforcement_mode': constraint.enforcement_mode
            })
        elif isinstance(constraint, WellbeingConstraint):
            config.update({
                'metric': constraint.metric,
                'max_threshold': constraint.threshold
            })
        
        return config
    
    def _calculate_coverage(self, constraints: List[EthicalConstraint]) -> float:
        """Calculate ethical dimension coverage"""
        covered_types = set(c.constraint_type for c in constraints)
        return len(covered_types) / len(ConstraintType)
    
    def study_dynamic_composition(self) -> Dict:
        """Study dynamic constraint composition based on context"""
        logger.info("Studying dynamic constraint composition...")
        
        contexts = [
            {'name': 'high_risk', 'risk_level': 'high', 'real_time': False},
            {'name': 'real_time', 'risk_level': 'low', 'real_time': True},
            {'name': 'learning', 'risk_level': 'medium', 'learning_enabled': True},
            {'name': 'privacy_focused', 'privacy_requirement': 'high'},
            {'name': 'fairness_focused', 'fairness_requirement': 'strict'}
        ]
        
        results = {}
        manager = DynamicCompositionManager()
        
        for context in contexts:
            context_name = context.pop('name')
            
            # Compose constraints for context
            composition_result = manager.compose(self.all_constraints, context)
            
            # Test performance
            selected_constraints = composition_result['constraints']
            config = self.config.copy()
            config['constraints'] = [self._constraint_to_config(c) 
                                   for c in selected_constraints]
            
            # Run small test
            system = EthicsAwareMLSystem(config)
            test_latencies = []
            
            for _ in range(100):
                decision = Decision(
                    user_id=np.random.randint(1, 1000),
                    content_id=np.random.randint(1, 10000),
                    algorithm='test'
                )
                result = system.process(decision)
                test_latencies.append(result.get('total_latency_ms', 0))
            
            results[context_name] = {
                'context': context,
                'strategy': composition_result['strategy'],
                'constraints_selected': [c.name for c in selected_constraints],
                'num_constraints': len(selected_constraints),
                'mean_latency': np.mean(test_latencies),
                'metadata': composition_result.get('metadata', {})
            }
        
        return results
    
    def run_comprehensive_study(self) -> Dict:
        """Run all composition studies"""
        logger.info("Running comprehensive constraint composition study...")
        
        # Study pairwise conflicts
        self.results['pairwise_conflicts'] = self.study_pairwise_conflicts()
        
        # Study composition strategies
        self.results['composition_strategies'] = self.study_composition_strategies()
        
        # Study dynamic composition
        self.results['dynamic_composition'] = self.study_dynamic_composition()
        
        # Generate visualizations
        self._generate_visualizations()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _generate_visualizations(self):
        """Generate composition study visualizations"""
        output_dir = Path('results/figures')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Strategy comparison plot
        if 'composition_strategies' in self.results:
            self._plot_strategy_comparison()
        
        # Conflict heatmap
        if 'pairwise_conflicts' in self.results:
            self._plot_conflict_heatmap()
        
        # Dynamic composition visualization
        if 'dynamic_composition' in self.results:
            self._plot_dynamic_composition()
    
    def _plot_strategy_comparison(self):
        """Plot comparison of composition strategies"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        strategies_data = self.results['composition_strategies']
        strategies = list(strategies_data.keys())
        
        # Latency comparison
        latency_data = [strategies_data[s]['mean_latency'] for s in strategies]
        bars1 = axes[0].bar(strategies, latency_data, color='steelblue')
        axes[0].set_ylabel('Mean Latency (ms)')
        axes[0].set_title('Latency by Composition Strategy')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Add values on bars
        for bar in bars1:
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom')
        
        # Number of constraints vs coverage
        num_constraints = [strategies_data[s]['num_constraints'] for s in strategies]
        coverage = [strategies_data[s]['coverage_score'] for s in strategies]
        
        axes[1].scatter(num_constraints, coverage, s=100, c=range(len(strategies)), 
                       cmap='viridis')
        for i, txt in enumerate(strategies):
            axes[1].annotate(txt, (num_constraints[i], coverage[i]), 
                           xytext=(5, 5), textcoords='offset points')
        axes[1].set_xlabel('Number of Constraints')
        axes[1].set_ylabel('Coverage Score')
        axes[1].set_title('Constraints vs Coverage')
        axes[1].grid(True, alpha=0.3)
        
        # Satisfaction rates heatmap
        satisfaction_matrix = []
        constraint_names = set()
        
        for strategy in strategies:
            rates = strategies_data[strategy]['satisfaction_rates']
            constraint_names.update(rates.keys())
        
        constraint_names = sorted(constraint_names)
        
        for strategy in strategies:
            rates = strategies_data[strategy]['satisfaction_rates']
            row = [rates.get(c, 0) for c in constraint_names]
            satisfaction_matrix.append(row)
        
        sns.heatmap(satisfaction_matrix, xticklabels=constraint_names,
                   yticklabels=strategies, cmap='RdYlGn', center=0.95,
                   vmin=0.9, vmax=1.0, annot=True, fmt='.3f',
                   ax=axes[2])
        axes[2].set_title('Constraint Satisfaction Rates')
        axes[2].tick_params(axis='x', rotation=45)
        
        # Efficiency plot (latency vs violations)
        violations = [strategies_data[s]['total_violations'] for s in strategies]
        axes[3].scatter(latency_data, violations, s=100, c=range(len(strategies)),
                       cmap='plasma')
        for i, txt in enumerate(strategies):
            axes[3].annotate(txt, (latency_data[i], violations[i]),
                           xytext=(5, 5), textcoords='offset points')
        axes[3].set_xlabel('Mean Latency (ms)')
        axes[3].set_ylabel('Total Violations')
        axes[3].set_title('Efficiency Trade-off')
        axes[3].grid(True, alpha=0.3)
        
        plt.suptitle('Constraint Composition Strategy Comparison', fontsize=16)
        plt.tight_layout()
        
        output_dir = Path('results/figures')
        plt.savefig(output_dir / 'composition_strategy_comparison.pdf',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_conflict_heatmap(self):
        """Plot constraint conflict heatmap"""
        conflict_data = self.results['pairwise_conflicts']['conflict_matrix']
        
        # Create matrix
        constraint_names = sorted(set(c.name for c in self.all_constraints))
        n = len(constraint_names)
        conflict_matrix = np.zeros((n, n))
        
        for pair, has_conflict in conflict_data.items():
            c1_name, c2_name = pair.split('-')
            i = constraint_names.index(c1_name)
            j = constraint_names.index(c2_name)
            conflict_matrix[i, j] = 1 if has_conflict else 0
            conflict_matrix[j, i] = conflict_matrix[i, j]
        
        # Plot heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(conflict_matrix, xticklabels=constraint_names,
                   yticklabels=constraint_names, cmap='Reds',
                   cbar_kws={'label': 'Has Conflict'})
        plt.title('Constraint Conflict Matrix', fontsize=16)
        plt.tight_layout()
        
        output_dir = Path('results/figures')
        plt.savefig(output_dir / 'constraint_conflict_heatmap.pdf',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_dynamic_composition(self):
        """Plot dynamic composition results"""
        dynamic_data = self.results['dynamic_composition']
        
        contexts = list(dynamic_data.keys())
        num_constraints = [dynamic_data[c]['num_constraints'] for c in contexts]
        latencies = [dynamic_data[c]['mean_latency'] for c in contexts]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(contexts, num_constraints, color='skyblue', alpha=0.7, 
                      label='Constraints')
        
        # Add latency as line
        ax2 = ax.twinx()
        ax2.plot(contexts, latencies, 'ro-', linewidth=2, markersize=8,
                label='Latency')
        
        ax.set_ylabel('Number of Constraints', fontsize=12)
        ax2.set_ylabel('Mean Latency (ms)', fontsize=12)
        ax.set_xlabel('Context', fontsize=12)
        ax.set_title('Dynamic Constraint Composition by Context', fontsize=14)
        
        # Add values
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        ax.tick_params(axis='x', rotation=45)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        plt.tight_layout()
        
        output_dir = Path('results/figures')
        plt.savefig(output_dir / 'dynamic_composition.pdf',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _save_results(self):
        """Save study results"""
        output_dir = Path('results/data')
        output_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        with open(output_dir / 'composition_study_results.json', 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        # Save summary
        with open(output_dir / 'composition_study_summary.txt', 'w') as f:
            f.write("CONSTRAINT COMPOSITION STUDY SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            if 'pairwise_conflicts' in self.results:
                conflicts = self.results['pairwise_conflicts']['conflict_matrix']
                total_pairs = len(conflicts)
                conflict_pairs = sum(1 for v in conflicts.values() if v)
                f.write(f"Pairwise Conflicts: {conflict_pairs}/{total_pairs} pairs\n\n")
            
            if 'composition_strategies' in self.results:
                f.write("Composition Strategies:\n")
                for strategy, data in self.results['composition_strategies'].items():
                    f.write(f"  {strategy}: {data['num_constraints']} constraints, "
                           f"{data['mean_latency']:.1f}ms latency, "
                           f"{data['coverage_score']:.2f} coverage\n")
                f.write("\n")
            
            if 'dynamic_composition' in self.results:
                f.write("Dynamic Composition:\n")
                for context, data in self.results['dynamic_composition'].items():
                    f.write(f"  {context}: {data['num_constraints']} constraints, "
                           f"strategy: {data['strategy']}\n")


def main():
    """Main entry point"""
    import argparse
    import yaml
    
    parser = argparse.ArgumentParser(description='Run constraint composition study')
    parser.add_argument('--config', type=str, default='configs/experiment_config.yaml',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Run study
    study = ConstraintCompositionStudy(config)
    results = study.run_comprehensive_study()
    
    print("\nConstraint composition study complete!")
    print("Results saved to: results/data/composition_study_results.json")
    print("Visualizations saved to: results/figures/")


if __name__ == "__main__":
    main()