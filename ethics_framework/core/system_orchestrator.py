"""
5-Layer Ethics-by-Design System Orchestrator

This module implements the complete 5-layer architecture for ethics-by-design
AI systems as described in the technical report.
"""

import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

from .interfaces import Decision, LayerInterface, SystemOrchestrator
from .constraints import (
    ConstraintComposer, 
    FairnessConstraint,
    PrivacyConstraint,
    TransparencyConstraint,
    ConsentConstraint,
    WellbeingConstraint
)
from ..algorithms.registry import AlgorithmRegistry
from ..algorithms.hierarchical_intervention import (
    HierarchicalInterventionSystem,
    create_intervention_system
)
from ..algorithms.adaptive_optimizer import (
    ConstraintThresholdOptimizer,
    PolicyParameterOptimizer,
    OptimizationTarget,
    OptimizationResult
)
from ..algorithms.ml_models import (
    CollaborativeFilteringModel, 
    HiringRecommendationModel,
    SocialMediaRankingModel,
    ContentClassificationModel
)


@dataclass
class LayerResult:
    """Result from a single layer processing"""
    layer_name: str
    processing_time_ms: float
    success: bool
    data: Dict[str, Any]
    violations: List[Any] = None
    intervention_applied: bool = False
    intervention_result: Optional[Dict[str, Any]] = None


class Layer1_EthicalAIServices(LayerInterface):
    """Layer 1: Ethical AI Services - Core algorithm execution with embedded constraints"""
    
    def __init__(self, intervention_system: Optional[HierarchicalInterventionSystem] = None,
                 constraint_optimizer: Optional[ConstraintThresholdOptimizer] = None):
        self.name = "Layer1_EthicalAIServices"
        self.algorithm_registry = AlgorithmRegistry()
        self.intervention_system = intervention_system
        self.constraint_optimizer = constraint_optimizer
        self.ml_models = {}
        self.performance_metrics = defaultdict(list)
        self.optimization_history = []
        self._initialize_algorithms()
        self._initialize_constraints()
        self._setup_optimization_targets()
    
    def _initialize_algorithms(self):
        """Initialize all available ML algorithms"""
        self.ml_models = {
            'collaborative_filtering': CollaborativeFilteringModel(),
            'hiring_recommendation': HiringRecommendationModel(),
            'social_media_ranking': SocialMediaRankingModel(),
            'content_classification': ContentClassificationModel()
        }
        
        # Register algorithms with metadata for tracking
        self.algorithm_metadata = {}
        for name, model in self.ml_models.items():
            self.algorithm_metadata[name] = {
                'model': model,
                'ethical_properties': model.get_ethical_properties(),
                'performance_stats': model.performance_stats,
                'usage_count': 0,
                'explanation_requests': 0
            }
    
    def _initialize_constraints(self):
        """Initialize ethical constraints"""
        constraints = [
            FairnessConstraint(
                name="demographic_parity",
                protected_attribute="demographic",
                fairness_metric="demographic_parity",
                threshold=0.1
            ),
            PrivacyConstraint(
                name="differential_privacy",
                epsilon=1.0,
                delta=1e-5,
                mechanism="laplace"
            ),
            TransparencyConstraint(
                name="explainability",
                explanation_type="feature_importance",
                min_clarity_score=0.8
            ),
            ConsentConstraint(
                name="user_consent",
                consent_types=["data_processing", "personalization"],
                enforcement_mode="strict"
            ),
            WellbeingConstraint(
                name="digital_wellbeing",
                metric="engagement_time",
                max_threshold=120.0
            )
        ]
        
        self.constraint_composer = ConstraintComposer(
            constraints=constraints,
            composition_mode="intersection"
        )
    
    def _setup_optimization_targets(self):
        """Setup optimization targets for constraint thresholds"""
        if self.constraint_optimizer:
            # Add optimization targets for each constraint
            self.constraint_optimizer.add_constraint_target(
                "fairness", target_satisfaction_rate=0.85, tolerance=0.05, weight=1.0
            )
            self.constraint_optimizer.add_constraint_target(
                "privacy", target_satisfaction_rate=0.90, tolerance=0.03, weight=1.2
            )
            self.constraint_optimizer.add_constraint_target(
                "transparency", target_satisfaction_rate=0.80, tolerance=0.05, weight=0.8
            )
            self.constraint_optimizer.add_constraint_target(
                "consent", target_satisfaction_rate=0.95, tolerance=0.02, weight=1.5
            )
            self.constraint_optimizer.add_constraint_target(
                "wellbeing", target_satisfaction_rate=0.88, tolerance=0.04, weight=1.1
            )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ML algorithm with ethical constraints and interventions"""
        start_time = time.perf_counter()
        
        try:
            decision = Decision(**input_data['decision'])
            context = input_data.get('context', {})
            
            # Execute ML algorithm
            algorithm_result = None
            explanation_result = None
            
            if decision.algorithm in self.ml_models:
                model = self.ml_models[decision.algorithm]
                
                # Execute prediction using BaseAlgorithm interface
                algorithm_result = model.predict(decision, context)
                
                # Update algorithm usage tracking
                if decision.algorithm in self.algorithm_metadata:
                    self.algorithm_metadata[decision.algorithm]['usage_count'] += 1
                
                # Generate explanation if requested or if violations detected
                if context.get('generate_explanation', True):
                    try:
                        explanation_result = model.explain(decision, algorithm_result)
                        if decision.algorithm in self.algorithm_metadata:
                            self.algorithm_metadata[decision.algorithm]['explanation_requests'] += 1
                    except Exception as e:
                        explanation_result = {
                            'error': f'Explanation generation failed: {str(e)}',
                            'algorithm': decision.algorithm
                        }
                
            else:
                # Fallback for unknown algorithms
                algorithm_result = {
                    'algorithm': decision.algorithm,
                    'error': f'Unknown algorithm: {decision.algorithm}',
                    'predictions': [],
                    'inference_time_ms': 0.0
                }
            
            # Validate against ethical constraints
            validation_results = self.constraint_composer.validate_all(
                decision.to_dict(), context
            )
            
            # Extract violations for intervention processing
            violations = []
            
            # Check if validation_results has violations list
            if validation_results.get('violations'):
                for violation in validation_results['violations']:
                    if hasattr(violation, 'to_dict'):
                        violation_dict = violation.to_dict()
                    else:
                        violation_dict = violation
                    
                    violations.append({
                        'constraint_type': violation_dict.get('constraint_type', 'unknown'),
                        'violation_score': violation_dict.get('violation_score', 0.5),
                        'severity': violation_dict.get('severity', 'MEDIUM'),
                        'details': violation_dict.get('details', {}),
                        'message': violation_dict.get('message', 'Constraint violation detected')
                    })
            
            # Also check individual results for violations
            elif validation_results.get('individual_results'):
                for constraint_name, constraint_result in validation_results['individual_results'].items():
                    if not constraint_result.get('satisfied', True) and constraint_result.get('violation'):
                        violation = constraint_result['violation']
                        if hasattr(violation, 'to_dict'):
                            violation_dict = violation.to_dict()
                        else:
                            violation_dict = violation
                        
                        violations.append({
                            'constraint_type': violation_dict.get('constraint_type', constraint_name),
                            'violation_score': violation_dict.get('violation_score', 0.5),
                            'severity': violation_dict.get('severity', 'MEDIUM'),
                            'details': violation_dict.get('details', {}),
                            'message': violation_dict.get('message', f'{constraint_name} constraint violation detected')
                        })
            
            # Apply hierarchical intervention if violations exist and system is available
            intervention_result = None
            intervention_applied = False
            modified_decision = decision.to_dict()
            
            if violations and self.intervention_system:
                intervention_response = self.intervention_system.evaluate_and_intervene(
                    decision=decision.to_dict(),
                    violations=violations
                )
                
                intervention_applied = intervention_response.get('intervention_applied', False)
                if intervention_applied:
                    intervention_result = intervention_response
                    
                    # Apply intervention modifications to decision if needed
                    if 'result' in intervention_response and 'modified_decision' in intervention_response['result']:
                        modified_decision = intervention_response['result']['modified_decision']
                    
                    # If intervention blocks the decision, mark as unsuccessful
                    if intervention_response.get('level') in ['TEMPORARY_SUSPENSION', 'PERMANENT_RESTRICTION']:
                        end_time = time.perf_counter()
                        processing_time = (end_time - start_time) * 1000
                        
                        return {
                            'algorithm_result': None,
                            'validation_results': validation_results,
                            'violations': violations,
                            'intervention_applied': True,
                            'intervention_result': intervention_result,
                            'modified_decision': None,  # Decision blocked
                            'processing_time_ms': processing_time,
                            'layer': self.name,
                            'success': False,
                            'blocked_reason': f"Decision blocked by {intervention_response.get('level')} intervention"
                        }
            
            end_time = time.perf_counter()
            processing_time = (end_time - start_time) * 1000
            
            # Collect performance metrics for optimization
            self._collect_performance_metrics(validation_results, processing_time, violations)
            
            # Run optimization if enough data collected
            self._run_optimization_if_needed()
            
            return {
                'algorithm_result': algorithm_result,
                'explanation_result': explanation_result,
                'validation_results': validation_results,
                'violations': violations,
                'intervention_applied': intervention_applied,
                'intervention_result': intervention_result,
                'modified_decision': modified_decision,
                'processing_time_ms': processing_time,
                'layer': self.name,
                'success': True,
                'algorithm_metadata': self.algorithm_metadata.get(decision.algorithm, {}).get('ethical_properties', {}) if decision.algorithm in self.algorithm_metadata else {}
            }
            
        except Exception as e:
            end_time = time.perf_counter()
            processing_time = (end_time - start_time) * 1000
            
            return {
                'error': str(e),
                'processing_time_ms': processing_time,
                'layer': self.name,
                'success': False,
                'intervention_applied': False
            }
    
    def _collect_performance_metrics(self, validation_results: Dict[str, Any], 
                                   processing_time: float, violations: List[Dict]):
        """Collect performance metrics for optimization"""
        if not self.constraint_optimizer:
            return
        
        # Calculate constraint satisfaction rates
        constraint_satisfaction = {}
        
        if 'individual_results' in validation_results:
            for constraint_name, result in validation_results['individual_results'].items():
                satisfied = result.get('satisfied', True)
                constraint_satisfaction[f"{constraint_name}_satisfaction_current"] = 1.0 if satisfied else 0.0
        
        # Add performance metrics
        constraint_satisfaction.update({
            'throughput_current': 1000.0 / max(processing_time, 0.001),  # requests per second
            'latency_current': processing_time / 1000.0,  # seconds
            'violation_count_current': len(violations),
            'overall_satisfaction_current': 1.0 if not violations else 0.0
        })
        
        # Store metrics
        self.performance_metrics['satisfaction_data'].append(constraint_satisfaction)
        self.performance_metrics['processing_times'].append(processing_time)
        self.performance_metrics['violation_counts'].append(len(violations))
    
    def _run_optimization_if_needed(self):
        """Run constraint threshold optimization if enough data collected"""
        if not self.constraint_optimizer:
            return
        
        # Run optimization every 50 decisions
        if len(self.performance_metrics['satisfaction_data']) % 50 == 0 and len(self.performance_metrics['satisfaction_data']) > 0:
            try:
                # Calculate average satisfaction rates over recent decisions
                recent_data = self.performance_metrics['satisfaction_data'][-50:]
                
                # Aggregate metrics
                aggregated_feedback = {}
                for key in recent_data[0].keys():
                    values = [data[key] for data in recent_data if key in data]
                    aggregated_feedback[key] = np.mean(values) if values else 0.0
                
                # Run optimization
                optimization_result = self.constraint_optimizer.optimize_thresholds(aggregated_feedback)
                
                # Store optimization history
                self.optimization_history.append({
                    'timestamp': time.time(),
                    'result': optimization_result,
                    'feedback': aggregated_feedback
                })
                
                # Apply optimized thresholds to constraints (simplified)
                optimized_thresholds = self.constraint_optimizer.get_optimized_thresholds()
                self._apply_optimized_thresholds(optimized_thresholds)
                
            except Exception as e:
                # Log optimization error but don't fail the system
                print(f"Optimization error: {e}")
    
    def _apply_optimized_thresholds(self, thresholds: Dict[str, float]):
        """Apply optimized thresholds to constraints"""
        # This is a simplified implementation
        # In practice, you'd update the actual constraint objects
        for constraint_name, threshold in thresholds.items():
            # Update constraint thresholds based on optimization results
            # This would require constraint objects to support dynamic threshold updates
            pass
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        if not self.constraint_optimizer:
            return {'optimization_enabled': False}
        
        return {
            'optimization_enabled': True,
            'optimization_runs': len(self.optimization_history),
            'current_thresholds': self.constraint_optimizer.get_optimized_thresholds(),
            'optimization_history': self.optimization_history[-10:],  # Last 10 runs
            'performance_metrics_collected': len(self.performance_metrics['satisfaction_data'])
        }
    
    def get_algorithm_stats(self) -> Dict[str, Any]:
        """Get comprehensive algorithm statistics and metadata"""
        algorithm_stats = {}
        
        for algorithm_name, metadata in self.algorithm_metadata.items():
            model = metadata['model']
            algorithm_stats[algorithm_name] = {
                'ethical_properties': metadata['ethical_properties'],
                'usage_count': metadata['usage_count'],
                'explanation_requests': metadata['explanation_requests'],
                'performance_stats': model.performance_stats,
                'algorithm_metadata': {
                    'name': model.metadata.name,
                    'version': model.metadata.version,
                    'fairness_aware': model.metadata.fairness_aware,
                    'privacy_level': model.metadata.privacy_level,
                    'transparency_level': model.metadata.transparency_level,
                    'bias_mitigation': model.metadata.bias_mitigation,
                    'performance_characteristics': model.metadata.performance_characteristics
                },
                'violation_rate': model.violation_rate
            }
        
        return {
            'total_algorithms': len(self.ml_models),
            'algorithms': algorithm_stats,
            'total_usage': sum(meta['usage_count'] for meta in self.algorithm_metadata.values()),
            'total_explanations': sum(meta['explanation_requests'] for meta in self.algorithm_metadata.values())
        }


class EthicsFrameworkOrchestrator(SystemOrchestrator):
    """Complete 5-layer ethics-by-design system orchestrator with hierarchical intervention"""
    
    def __init__(self, intervention_config: Optional[Dict[str, Any]] = None,
                 optimization_config: Optional[Dict[str, Any]] = None):
        # Initialize hierarchical intervention system
        self.intervention_system = create_intervention_system(intervention_config)
        
        # Initialize adaptive optimizers
        self.constraint_optimizer = None
        self.policy_optimizer = None
        
        if optimization_config is None:
            optimization_config = {'enabled': True, 'optimizer_type': 'gradient_descent'}
        
        if optimization_config.get('enabled', True):
            optimizer_type = optimization_config.get('optimizer_type', 'gradient_descent')
            self.constraint_optimizer = ConstraintThresholdOptimizer(optimizer_type=optimizer_type)
            self.policy_optimizer = PolicyParameterOptimizer(optimizer_type=optimizer_type)
            
            # Setup policy optimization targets
            self._setup_policy_optimization_targets()
        
        # Initialize layers with intervention system and optimizers
        self.layers = [
            Layer1_EthicalAIServices(
                intervention_system=self.intervention_system,
                constraint_optimizer=self.constraint_optimizer
            ),
        ]
        
        self.performance_stats = defaultdict(list)
        self.intervention_stats = defaultdict(list)
        self.optimization_stats = defaultdict(list)
        self._lock = threading.RLock()
    
    def _setup_policy_optimization_targets(self):
        """Setup optimization targets for policy parameters"""
        if self.policy_optimizer:
            # Add policy optimization targets
            self.policy_optimizer.add_policy_target(
                "fairness_policy", target_compliance_rate=0.90, tolerance=0.02, weight=1.0
            )
            self.policy_optimizer.add_policy_target(
                "privacy_policy", target_compliance_rate=0.95, tolerance=0.01, weight=1.5
            )
            self.policy_optimizer.add_policy_target(
                "transparency_policy", target_compliance_rate=0.85, tolerance=0.03, weight=0.8
            )
            self.policy_optimizer.add_policy_target(
                "governance_policy", target_compliance_rate=0.92, tolerance=0.02, weight=1.2
            )
    
    def process_decision(self, decision: Decision, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process decision through all layers with intervention support"""
        start_time = time.perf_counter()
        
        if context is None:
            context = {}
        
        # Prepare input data
        input_data = {
            'decision': decision.to_dict(),
            'context': context
        }
        
        layer_results = []
        accumulated_data = input_data.copy()
        total_interventions = 0
        
        # Process through each layer sequentially
        for layer in self.layers:
            layer_result = layer.process(accumulated_data)
            
            # Track intervention statistics
            intervention_applied = layer_result.get('intervention_applied', False)
            if intervention_applied:
                total_interventions += 1
                intervention_result = layer_result.get('intervention_result', {})
                intervention_level = intervention_result.get('level', 'UNKNOWN')
                
                with self._lock:
                    self.intervention_stats['total_interventions'].append(1)
                    self.intervention_stats[f'interventions_{intervention_level}'].append(1)
                    self.intervention_stats['intervention_processing_time'].append(
                        layer_result.get('processing_time_ms', 0)
                    )
            
            # Create layer result record
            layer_record = LayerResult(
                layer_name=layer.name,
                processing_time_ms=layer_result.get('processing_time_ms', 0),
                success=layer_result.get('success', False),
                data=layer_result,
                violations=layer_result.get('violations', []),
                intervention_applied=intervention_applied,
                intervention_result=layer_result.get('intervention_result')
            )
            
            layer_results.append(layer_record)
            
            # Accumulate data for next layer
            accumulated_data.update(layer_result)
            
            # Stop processing if layer failed (including intervention blocks)
            if not layer_result.get('success', False):
                break
        
        # Calculate total processing time
        end_time = time.perf_counter()
        total_processing_time = (end_time - start_time) * 1000
        
        # Update performance statistics
        with self._lock:
            self.performance_stats['total_processing_time'].append(total_processing_time)
            for layer_result in layer_results:
                self.performance_stats[f'{layer_result.layer_name}_time'].append(
                    layer_result.processing_time_ms
                )
        
        # Compile final result
        final_result = {
            'decision_id': f"{decision.user_id}_{decision.content_id}_{int(decision.timestamp)}",
            'layer_results': [lr.__dict__ for lr in layer_results],
            'total_processing_time_ms': total_processing_time,
            'overall_success': all(lr.success for lr in layer_results),
            'interventions_applied': total_interventions,
            'timestamp': time.time()
        }
        
        return final_result
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system performance statistics including interventions and optimization"""
        with self._lock:
            stats = {}
            
            # Performance statistics
            for metric_name, values in self.performance_stats.items():
                if values:
                    stats[metric_name] = {
                        'count': len(values),
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'p50': np.percentile(values, 50),
                        'p95': np.percentile(values, 95),
                        'p99': np.percentile(values, 99)
                    }
            
            # Intervention statistics
            intervention_summary = {}
            for metric_name, values in self.intervention_stats.items():
                if values:
                    intervention_summary[metric_name] = {
                        'count': len(values),
                        'total': sum(values),
                        'mean': np.mean(values),
                        'std': np.std(values)
                    }
            
            if intervention_summary:
                stats['intervention_analytics'] = intervention_summary
            
            # Get intervention system analytics
            if hasattr(self.intervention_system, 'get_analytics'):
                stats['detailed_intervention_analytics'] = self.intervention_system.get_analytics()
            
            # Optimization statistics
            optimization_summary = {}
            for metric_name, values in self.optimization_stats.items():
                if values:
                    optimization_summary[metric_name] = {
                        'count': len(values),
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'latest': values[-1] if values else None
                    }
            
            if optimization_summary:
                stats['optimization_analytics'] = optimization_summary
            
            # Get detailed optimization stats from layers
            for layer in self.layers:
                if hasattr(layer, 'get_optimization_stats'):
                    layer_opt_stats = layer.get_optimization_stats()
                    if layer_opt_stats.get('optimization_enabled', False):
                        stats[f'{layer.name}_optimization'] = layer_opt_stats
                
                # Get algorithm statistics from Layer 1
                if hasattr(layer, 'get_algorithm_stats'):
                    algorithm_stats = layer.get_algorithm_stats()
                    stats[f'{layer.name}_algorithms'] = algorithm_stats
            
            # Policy optimization stats
            if self.policy_optimizer:
                stats['policy_optimization'] = {
                    'enabled': True,
                    'current_weights': self.policy_optimizer.get_optimized_policy_weights(),
                    'optimization_history_length': len(self.policy_optimizer.compliance_history)
                }
            
            return stats
    
    def get_intervention_system(self) -> HierarchicalInterventionSystem:
        """Get access to the intervention system for direct interaction"""
        return self.intervention_system
    
    def update_intervention_effectiveness(self, user_id: int, intervention_id: str, 
                                        outcome: Dict[str, Any]):
        """Update intervention effectiveness based on user behavior"""
        if hasattr(self.intervention_system, 'update_effectiveness'):
            self.intervention_system.update_effectiveness(user_id, intervention_id, outcome)
    
    def run_policy_optimization(self, compliance_feedback: Dict[str, Any]) -> Optional[OptimizationResult]:
        """Run policy parameter optimization"""
        if not self.policy_optimizer:
            return None
        
        try:
            result = self.policy_optimizer.optimize_policies(compliance_feedback)
            
            # Track optimization statistics
            with self._lock:
                self.optimization_stats['policy_optimization_runs'].append(1)
                self.optimization_stats['policy_objective_values'].append(result.objective_value)
                self.optimization_stats['policy_improvements'].append(result.improvement)
            
            return result
        except Exception as e:
            print(f"Policy optimization error: {e}")
            return None
    
    def get_optimized_parameters(self) -> Dict[str, Any]:
        """Get all current optimized parameters"""
        parameters = {}
        
        if self.constraint_optimizer:
            parameters['constraint_thresholds'] = self.constraint_optimizer.get_optimized_thresholds()
        
        if self.policy_optimizer:
            parameters['policy_weights'] = self.policy_optimizer.get_optimized_policy_weights()
        
        return parameters 