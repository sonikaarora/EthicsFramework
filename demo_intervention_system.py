#!/usr/bin/env python3
"""
Comprehensive Demo of Hierarchical Intervention System Integration

This script demonstrates the complete hierarchical intervention system
integrated into the ethics-by-design framework, showing:
- Different intervention levels (soft nudge, warning, limitation, suspension)
- Escalation based on user behavior patterns
- Real-time constraint violation detection
- Intervention effectiveness tracking
"""

import sys
import os
import time
from typing import Dict, Any, List

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ethics_framework.core.system_orchestrator import EthicsFrameworkOrchestrator
from ethics_framework.core.interfaces import Decision


def create_demo_scenarios() -> List[Dict[str, Any]]:
    """Create demonstration scenarios with different violation patterns"""
    
    scenarios = [
        # Scenario 1: Progressive escalation for repeat offender
        {
            "name": "Progressive Escalation Demo",
            "description": "Shows how interventions escalate for repeat violations",
            "decisions": [
                {
                    "user_id": 2001,
                    "algorithm": "social_media_ranking",
                    "content_id": 2001001,
                    "attributes": {
                        "action": "rank_content",
                        "engagement_weight": 0.9,  # High engagement focus
                        "diversity_factor": 0.1,   # Low diversity (fairness issue)
                        "user_activity_hours": 8,  # High usage (wellbeing issue)
                        "content_type": "controversial"
                    },
                    "expected_violations": ["transparency", "fairness", "wellbeing"]
                },
                # Repeat the same pattern to trigger escalation
                {
                    "user_id": 2001,
                    "algorithm": "social_media_ranking", 
                    "content_id": 2001002,
                    "attributes": {
                        "action": "rank_content",
                        "engagement_weight": 0.95,
                        "diversity_factor": 0.05,
                        "user_activity_hours": 10,
                        "content_type": "controversial"
                    },
                    "expected_violations": ["transparency", "fairness", "wellbeing"]
                },
                {
                    "user_id": 2001,
                    "algorithm": "social_media_ranking",
                    "content_id": 2001003,
                    "attributes": {
                        "action": "rank_content",
                        "engagement_weight": 0.98,
                        "diversity_factor": 0.02,
                        "user_activity_hours": 12,
                        "content_type": "controversial"
                    },
                    "expected_violations": ["transparency", "fairness", "wellbeing"]
                }
            ]
        },
        
        # Scenario 2: Different constraint violations
        {
            "name": "Multi-Constraint Violation Demo",
            "description": "Shows different types of constraint violations",
            "decisions": [
                {
                    "user_id": 2002,
                    "algorithm": "hiring_recommendation",
                    "content_id": 2002001,
                    "attributes": {
                        "action": "score_candidate",
                        "experience_weight": 0.95,  # Heavy bias toward experience
                        "education_weight": 0.9,    # Heavy bias toward education
                        "demographic_factor": 0.05, # Low demographic consideration
                        "bias_correction": False     # No bias correction
                    },
                    "expected_violations": ["fairness", "transparency"]
                },
                {
                    "user_id": 2003,
                    "algorithm": "collaborative_filtering",
                    "content_id": 2003001,
                    "attributes": {
                        "action": "recommend_content",
                        "similarity_threshold": 0.95,      # Very high similarity
                        "diversity_weight": 0.05,          # Very low diversity
                        "privacy_level": "low",             # Low privacy
                        "personalization_strength": 0.98   # Very high personalization
                    },
                    "expected_violations": ["privacy", "fairness", "transparency"]
                }
            ]
        },
        
        # Scenario 3: Cooldown and effectiveness tracking
        {
            "name": "Cooldown and Effectiveness Demo",
            "description": "Shows cooldown periods and effectiveness tracking",
            "decisions": [
                {
                    "user_id": 2004,
                    "algorithm": "content_classification",
                    "content_id": 2004001,
                    "attributes": {
                        "action": "classify_content",
                        "confidence_threshold": 0.3,  # Low confidence threshold
                        "bias_detection": False,       # No bias detection
                        "explanation_required": False  # No explanations
                    },
                    "expected_violations": ["transparency"]
                },
                # Immediate repeat (should be in cooldown)
                {
                    "user_id": 2004,
                    "algorithm": "content_classification",
                    "content_id": 2004002,
                    "attributes": {
                        "action": "classify_content",
                        "confidence_threshold": 0.2,
                        "bias_detection": False,
                        "explanation_required": False
                    },
                    "expected_violations": ["transparency"]
                }
            ]
        }
    ]
    
    return scenarios


def run_scenario_demo(orchestrator: EthicsFrameworkOrchestrator, scenario: Dict[str, Any]):
    """Run a complete scenario demonstration"""
    
    print(f"\n{'='*60}")
    print(f"🎬 SCENARIO: {scenario['name']}")
    print(f"📝 {scenario['description']}")
    print(f"{'='*60}")
    
    scenario_results = []
    
    for i, decision_config in enumerate(scenario['decisions'], 1):
        print(f"\n🔍 Decision {i}: User {decision_config['user_id']} - {decision_config['algorithm']}")
        
        # Create decision
        decision = Decision(
            user_id=decision_config['user_id'],
            content_id=decision_config['content_id'],
            algorithm=decision_config['algorithm'],
            attributes=decision_config['attributes'],
            timestamp=time.time()
        )
        
        # Process decision
        start_time = time.perf_counter()
        result = orchestrator.process_decision(decision)
        processing_time = (time.perf_counter() - start_time) * 1000
        
        # Analyze results
        success = result.get('overall_success', False)
        interventions_applied = result.get('interventions_applied', 0)
        
        # Get detailed information
        layer_results = result.get('layer_results', [])
        if layer_results:
            layer_data = layer_results[0].get('data', {})
            violations = layer_data.get('violations', [])
            intervention_result = layer_data.get('intervention_result')
            
            print(f"   ⏱️  Processing time: {processing_time:.2f}ms")
            print(f"   ✅ Success: {success}")
            print(f"   🛡️  Interventions applied: {interventions_applied}")
            print(f"   🔍 Violations detected: {len(violations)}")
            
            if violations:
                violation_types = [v.get('constraint_type', 'unknown') for v in violations]
                violation_scores = [f"{v.get('violation_score', 0):.3f}" for v in violations]
                print(f"   ⚠️  Violation types: {', '.join(violation_types)}")
                print(f"   📊 Violation scores: [{', '.join(violation_scores)}]")
            
            if intervention_result and intervention_result.get('intervention_applied'):
                level = intervention_result.get('level', 'UNKNOWN')
                intervention_details = intervention_result.get('result', {})
                
                print(f"   📋 Intervention level: {level}")
                
                if 'message' in intervention_details:
                    print(f"   💬 Message: {intervention_details['message']}")
                
                if 'duration_seconds' in intervention_details:
                    print(f"   ⏰ Duration: {intervention_details['duration_seconds']}s")
                
                if 'actions' in intervention_details:
                    print(f"   🎯 Available actions: {', '.join(intervention_details['actions'])}")
            
            elif interventions_applied == 0 and violations:
                print(f"   🚫 Intervention blocked (likely cooldown)")
        
        # Store results
        scenario_results.append({
            'decision': decision_config,
            'result': result,
            'processing_time_ms': processing_time
        })
        
        # Small delay between decisions to simulate real usage
        time.sleep(0.1)
    
    return scenario_results


def demonstrate_intervention_system():
    """Main demonstration function"""
    
    print("🎭 Hierarchical Intervention System - Comprehensive Demo")
    print("=" * 70)
    
    # Initialize orchestrator with custom intervention configuration
    intervention_config = {
        'thresholds': {
            'soft_nudge': 0.2,
            'explicit_warning': 0.4,
            'feature_limitation': 0.6,
            'temporary_suspension': 0.8,
            'permanent_restriction': 0.95
        },
        'cooldown_periods': {
            'soft_nudge': 30,      # 30 seconds for demo
            'explicit_warning': 60, # 1 minute for demo
            'feature_limitation': 120, # 2 minutes for demo
            'temporary_suspension': 300, # 5 minutes for demo
        },
        'escalation_factors': {
            'repeat_violation': 1.3,
            'severity_multiplier': 1.4,
            'time_decay': 0.9
        }
    }
    
    orchestrator = EthicsFrameworkOrchestrator(intervention_config=intervention_config)
    
    print(f"✅ System initialized with hierarchical intervention")
    print(f"📊 Intervention thresholds: {intervention_config['thresholds']}")
    print(f"⏰ Cooldown periods: {intervention_config['cooldown_periods']}")
    
    # Get demonstration scenarios
    scenarios = create_demo_scenarios()
    
    all_results = []
    
    # Run each scenario
    for scenario in scenarios:
        scenario_results = run_scenario_demo(orchestrator, scenario)
        all_results.extend(scenario_results)
    
    # Final system statistics
    print(f"\n{'='*60}")
    print(f"📈 FINAL SYSTEM STATISTICS")
    print(f"{'='*60}")
    
    system_stats = orchestrator.get_system_stats()
    
    # Performance statistics
    if 'total_processing_time' in system_stats:
        perf_stats = system_stats['total_processing_time']
        print(f"⏱️  Processing Performance:")
        print(f"   - Total decisions: {perf_stats['count']}")
        print(f"   - Average time: {perf_stats['mean']:.2f}ms")
        print(f"   - 95th percentile: {perf_stats['p95']:.2f}ms")
    
    # Intervention statistics
    if 'intervention_analytics' in system_stats:
        intervention_stats = system_stats['intervention_analytics']
        total_interventions = intervention_stats.get('total_interventions', {}).get('total', 0)
        print(f"\n🛡️  Intervention Statistics:")
        print(f"   - Total interventions: {total_interventions}")
        
        for key, stats in intervention_stats.items():
            if key.startswith('interventions_') and key != 'total_interventions':
                level = key.replace('interventions_', '')
                count = stats.get('total', 0)
                if count > 0:
                    print(f"   - {level}: {count}")
    
    # Detailed intervention system analytics
    if 'detailed_intervention_analytics' in system_stats:
        detailed_stats = system_stats['detailed_intervention_analytics']
        print(f"\n📊 Detailed Intervention Analytics:")
        print(f"   - System total interventions: {detailed_stats.get('total_interventions', 0)}")
        
        interventions_by_level = detailed_stats.get('interventions_by_level', {})
        if interventions_by_level:
            print(f"   - Interventions by level:")
            for level, count in interventions_by_level.items():
                print(f"     • {level}: {count}")
    
    # Demonstrate direct intervention system access
    print(f"\n🔧 Direct Intervention System Access:")
    intervention_system = orchestrator.get_intervention_system()
    
    # Test direct intervention
    test_violations = [
        {
            'constraint_type': 'wellbeing',
            'violation_score': 0.85,
            'severity': 'HIGH',
            'details': {'usage_hours': 12, 'break_ratio': 0.1},
            'message': 'Excessive usage without adequate breaks detected'
        }
    ]
    
    direct_result = intervention_system.evaluate_and_intervene(
        decision={'user_id': 9999, 'action': 'direct_test'},
        violations=test_violations
    )
    
    print(f"   - Direct intervention test:")
    print(f"     • Applied: {direct_result.get('intervention_applied', False)}")
    print(f"     • Level: {direct_result.get('level', 'NONE')}")
    
    if direct_result.get('result'):
        result_details = direct_result['result']
        if 'message' in result_details:
            print(f"     • Message: {result_details['message']}")
    
    print(f"\n✅ Demonstration completed successfully!")
    print(f"🎉 Hierarchical intervention system is fully operational and integrated!")
    
    return all_results


if __name__ == "__main__":
    try:
        demo_results = demonstrate_intervention_system()
        print(f"\n🏆 Demo completed with {len(demo_results)} decisions processed")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 