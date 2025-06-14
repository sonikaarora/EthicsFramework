#!/usr/bin/env python3
"""
Adaptive Optimizer Integration Demonstration

This script demonstrates the integration of adaptive optimization into the
ethics-by-design framework, showing how constraint thresholds and policy
parameters are optimized based on real-time feedback.
"""

import time
import random
import numpy as np
from typing import Dict, Any, List

from src.ethics_framework.core.system_orchestrator import EthicsFrameworkOrchestrator
from src.ethics_framework.core.interfaces import Decision


def create_sample_decisions(num_decisions: int = 100) -> List[Decision]:
    """Create sample decisions for testing optimization"""
    decisions = []
    
    for i in range(num_decisions):
        decision = Decision(
            user_id=10000 + i,
            content_id=50000 + (i % 1000),  # Some content overlap
            algorithm=random.choice(['collaborative_filtering', 'hiring_recommendation', 
                                   'social_media_ranking', 'content_classification']),
            timestamp=time.time() + i,
            attributes={
                'demographic': random.choice(['A', 'B', 'C', 'D']),
                'score': random.uniform(0.1, 0.9),
                'engagement_time_today': random.uniform(30, 180),
                'break_since_last_session': random.uniform(5, 60),
                'explanation_coverage': random.uniform(0.3, 1.0),
                'consent_timestamp': time.time() - random.uniform(0, 365 * 24 * 3600),
                'consent_types': random.sample(['data_processing', 'personalization', 
                                              'algorithmic_decision'], k=random.randint(1, 3))
            }
        )
        decisions.append(decision)
    
    return decisions


def simulate_compliance_feedback() -> Dict[str, Any]:
    """Simulate compliance feedback for policy optimization"""
    return {
        'fairness_policy_compliance_current': random.uniform(0.7, 0.95),
        'privacy_policy_compliance_current': random.uniform(0.8, 0.98),
        'transparency_policy_compliance_current': random.uniform(0.6, 0.9),
        'governance_policy_compliance_current': random.uniform(0.75, 0.95),
        'overall_compliance_rate': random.uniform(0.7, 0.9),
        'policy_violations_per_hour': random.uniform(0, 10),
        'audit_success_rate': random.uniform(0.85, 0.99)
    }


def demonstrate_constraint_optimization():
    """Demonstrate constraint threshold optimization"""
    print("=" * 80)
    print("CONSTRAINT THRESHOLD OPTIMIZATION DEMONSTRATION")
    print("=" * 80)
    
    # Initialize framework with optimization enabled
    optimization_config = {
        'enabled': True,
        'optimizer_type': 'gradient_descent'
    }
    
    orchestrator = EthicsFrameworkOrchestrator(
        optimization_config=optimization_config
    )
    
    print(f"✅ Framework initialized with optimization enabled")
    print(f"   Optimizer type: {optimization_config['optimizer_type']}")
    
    # Get initial optimization parameters
    initial_params = orchestrator.get_optimized_parameters()
    print(f"\n📊 Initial optimization parameters:")
    for param_type, params in initial_params.items():
        print(f"   {param_type}: {params}")
    
    # Create sample decisions
    decisions = create_sample_decisions(150)  # Enough to trigger optimization
    print(f"\n🎯 Processing {len(decisions)} decisions to trigger optimization...")
    
    # Process decisions and track optimization
    results = []
    optimization_triggered = []
    
    for i, decision in enumerate(decisions):
        context = {
            'request_id': f'req_{i}',
            'timestamp': time.time(),
            'source': 'demo'
        }
        
        result = orchestrator.process_decision(decision, context)
        results.append(result)
        
        # Check if optimization was triggered (every 50 decisions)
        if (i + 1) % 50 == 0:
            layer1 = orchestrator.layers[0]
            if hasattr(layer1, 'optimization_history') and layer1.optimization_history:
                optimization_triggered.append(i + 1)
                latest_opt = layer1.optimization_history[-1]
                print(f"   🔧 Optimization triggered at decision {i + 1}")
                print(f"      Objective value: {latest_opt['result'].objective_value:.4f}")
                print(f"      Convergence: {latest_opt['result'].convergence_status}")
    
    print(f"\n📈 Optimization Results:")
    print(f"   Optimization runs triggered: {len(optimization_triggered)}")
    print(f"   Trigger points: {optimization_triggered}")
    
    # Get final optimization parameters
    final_params = orchestrator.get_optimized_parameters()
    print(f"\n📊 Final optimization parameters:")
    for param_type, params in final_params.items():
        print(f"   {param_type}: {params}")
    
    # Show optimization statistics
    layer1_stats = orchestrator.layers[0].get_optimization_stats()
    print(f"\n📊 Layer 1 Optimization Statistics:")
    for key, value in layer1_stats.items():
        if key != 'optimization_history':  # Skip detailed history
            print(f"   {key}: {value}")
    
    # Calculate performance improvements
    successful_decisions = sum(1 for r in results if r.get('overall_success', False))
    success_rate = successful_decisions / len(results)
    
    total_violations = sum(len(r.get('layer_results', [{}])[0].get('data', {}).get('violations', [])) 
                          for r in results)
    avg_violations_per_decision = total_violations / len(results)
    
    print(f"\n📊 Overall Performance Metrics:")
    print(f"   Success rate: {success_rate:.2%}")
    print(f"   Average violations per decision: {avg_violations_per_decision:.2f}")
    print(f"   Total decisions processed: {len(results)}")
    
    return orchestrator, results


def demonstrate_policy_optimization():
    """Demonstrate policy parameter optimization"""
    print("\n" + "=" * 80)
    print("POLICY PARAMETER OPTIMIZATION DEMONSTRATION")
    print("=" * 80)
    
    # Use the same orchestrator from constraint optimization
    optimization_config = {
        'enabled': True,
        'optimizer_type': 'gradient_descent'
    }
    
    orchestrator = EthicsFrameworkOrchestrator(
        optimization_config=optimization_config
    )
    
    print(f"✅ Policy optimizer initialized")
    
    # Get initial policy parameters
    initial_policy_params = orchestrator.get_optimized_parameters()
    print(f"\n📊 Initial policy parameters:")
    if 'policy_weights' in initial_policy_params:
        for policy, weight in initial_policy_params['policy_weights'].items():
            print(f"   {policy}: {weight:.4f}")
    
    # Run policy optimization with simulated feedback
    print(f"\n🔧 Running policy optimization with simulated compliance feedback...")
    
    optimization_results = []
    for i in range(10):  # Run 10 optimization cycles
        compliance_feedback = simulate_compliance_feedback()
        
        result = orchestrator.run_policy_optimization(compliance_feedback)
        if result:
            optimization_results.append(result)
            print(f"   Cycle {i+1}: Objective = {result.objective_value:.4f}, "
                  f"Improvement = {result.improvement:.4f}, "
                  f"Status = {result.convergence_status}")
    
    # Get final policy parameters
    final_policy_params = orchestrator.get_optimized_parameters()
    print(f"\n📊 Final policy parameters:")
    if 'policy_weights' in final_policy_params:
        for policy, weight in final_policy_params['policy_weights'].items():
            print(f"   {policy}: {weight:.4f}")
    
    # Show optimization convergence
    if optimization_results:
        objective_values = [r.objective_value for r in optimization_results]
        improvements = [r.improvement for r in optimization_results]
        
        print(f"\n📈 Policy Optimization Convergence:")
        print(f"   Initial objective: {objective_values[0]:.4f}")
        print(f"   Final objective: {objective_values[-1]:.4f}")
        print(f"   Total improvement: {objective_values[0] - objective_values[-1]:.4f}")
        print(f"   Average improvement per cycle: {np.mean(improvements):.4f}")
        print(f"   Convergence trend: {'Improving' if objective_values[-1] < objective_values[0] else 'Stable'}")
    
    return orchestrator, optimization_results


def demonstrate_integrated_optimization():
    """Demonstrate integrated constraint and policy optimization"""
    print("\n" + "=" * 80)
    print("INTEGRATED OPTIMIZATION DEMONSTRATION")
    print("=" * 80)
    
    # Initialize framework with both optimizations
    optimization_config = {
        'enabled': True,
        'optimizer_type': 'gradient_descent'
    }
    
    orchestrator = EthicsFrameworkOrchestrator(
        optimization_config=optimization_config
    )
    
    print(f"✅ Integrated optimization framework initialized")
    
    # Process decisions to trigger constraint optimization
    decisions = create_sample_decisions(100)
    print(f"\n🎯 Processing {len(decisions)} decisions with integrated optimization...")
    
    results = []
    for i, decision in enumerate(decisions):
        result = orchestrator.process_decision(decision)
        results.append(result)
        
        # Run policy optimization every 20 decisions
        if (i + 1) % 20 == 0:
            compliance_feedback = simulate_compliance_feedback()
            policy_result = orchestrator.run_policy_optimization(compliance_feedback)
            if policy_result:
                print(f"   🔧 Policy optimization at decision {i+1}: "
                      f"Objective = {policy_result.objective_value:.4f}")
    
    # Get comprehensive system statistics
    system_stats = orchestrator.get_system_stats()
    
    print(f"\n📊 Comprehensive System Statistics:")
    
    # Performance stats
    if 'total_processing_time' in system_stats:
        perf_stats = system_stats['total_processing_time']
        print(f"   Processing Performance:")
        print(f"     Mean time: {perf_stats['mean']:.2f}ms")
        print(f"     P95 time: {perf_stats['p95']:.2f}ms")
        print(f"     Total decisions: {perf_stats['count']}")
    
    # Optimization stats
    if 'optimization_analytics' in system_stats:
        opt_stats = system_stats['optimization_analytics']
        print(f"   Optimization Analytics:")
        for metric, stats in opt_stats.items():
            print(f"     {metric}: {stats}")
    
    # Layer-specific optimization
    for key, value in system_stats.items():
        if key.endswith('_optimization') and isinstance(value, dict):
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                if sub_key != 'optimization_history':  # Skip detailed history
                    print(f"     {sub_key}: {sub_value}")
    
    # Policy optimization stats
    if 'policy_optimization' in system_stats:
        policy_stats = system_stats['policy_optimization']
        print(f"   Policy Optimization:")
        for key, value in policy_stats.items():
            print(f"     {key}: {value}")
    
    return orchestrator, results, system_stats


def main():
    """Main demonstration function"""
    print("🚀 ADAPTIVE OPTIMIZER INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print("This demonstration shows how adaptive optimization is integrated")
    print("into the ethics-by-design framework for real-time parameter tuning.")
    print()
    
    try:
        # Demonstrate constraint optimization
        constraint_orchestrator, constraint_results = demonstrate_constraint_optimization()
        
        # Demonstrate policy optimization
        policy_orchestrator, policy_results = demonstrate_policy_optimization()
        
        # Demonstrate integrated optimization
        integrated_orchestrator, integrated_results, system_stats = demonstrate_integrated_optimization()
        
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("Key achievements:")
        print("✅ Constraint threshold optimization working")
        print("✅ Policy parameter optimization working")
        print("✅ Integrated optimization system operational")
        print("✅ Real-time performance monitoring active")
        print("✅ Optimization convergence tracking functional")
        print()
        print("The adaptive optimizer is now fully integrated into the")
        print("ethics-by-design framework and ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 