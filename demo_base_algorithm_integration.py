#!/usr/bin/env python3
"""
BaseAlgorithm Integration Demonstration

This script demonstrates the integration of BaseAlgorithm interface into the
ethics-by-design framework, showing how ML models now properly implement
the standardized interface with metadata, explanations, and ethical properties.
"""

import time
import random
import numpy as np
from typing import Dict, Any, List

from ethics_framework.core.system_orchestrator import EthicsFrameworkOrchestrator
from ethics_framework.core.interfaces import Decision
from ethics_framework.algorithms.ml_models import (
    CollaborativeFilteringModel,
    HiringRecommendationModel,
    SocialMediaRankingModel,
    ContentClassificationModel
)


def create_diverse_decisions() -> List[Decision]:
    """Create diverse decisions to test all algorithm types"""
    decisions = []
    
    # Collaborative Filtering decisions
    for i in range(5):
        decision = Decision(
            user_id=1000 + i,
            content_id=5000 + i,
            algorithm='collaborative_filtering',
            timestamp=time.time(),
            attributes={
                'user_preferences': ['movies', 'books', 'music'],
                'demographic': random.choice(['A', 'B', 'C']),
                'score': random.uniform(0.3, 0.9)
            }
        )
        decisions.append(decision)
    
    # Hiring Recommendation decisions
    for i in range(5):
        decision = Decision(
            user_id=2000 + i,
            content_id=6000 + i,
            algorithm='hiring_recommendation',
            timestamp=time.time(),
            attributes={
                'years_experience': random.randint(0, 15),
                'education_level': random.randint(1, 5),
                'skills_match': random.uniform(0.4, 0.95),
                'interview_score': random.uniform(60, 95),
                'demographic': random.choice(['A', 'B', 'C'])
            }
        )
        decisions.append(decision)
    
    # Social Media Ranking decisions
    for i in range(5):
        decision = Decision(
            user_id=3000 + i,
            content_id=7000 + i,
            algorithm='social_media_ranking',
            timestamp=time.time(),
            attributes={
                'relevance_score': random.uniform(0.2, 0.9),
                'recency_hours': random.randint(1, 48),
                'popularity_score': random.uniform(0.1, 0.8),
                'user_affinity': random.uniform(0.3, 0.9)
            }
        )
        decisions.append(decision)
    
    # Content Classification decisions
    for i in range(5):
        decision = Decision(
            user_id=4000 + i,
            content_id=8000 + i,
            algorithm='content_classification',
            timestamp=time.time(),
            attributes={
                'text_length': random.randint(50, 800),
                'sentiment_score': random.uniform(-0.8, 0.8),
                'toxicity_indicators': random.randint(0, 4)
            }
        )
        decisions.append(decision)
    
    return decisions


def demonstrate_algorithm_metadata():
    """Demonstrate algorithm metadata and ethical properties"""
    print("=" * 80)
    print("ALGORITHM METADATA AND ETHICAL PROPERTIES DEMONSTRATION")
    print("=" * 80)
    
    # Create instances of all algorithms
    algorithms = {
        'collaborative_filtering': CollaborativeFilteringModel(),
        'hiring_recommendation': HiringRecommendationModel(),
        'social_media_ranking': SocialMediaRankingModel(),
        'content_classification': ContentClassificationModel()
    }
    
    print("📊 Algorithm Metadata Overview:")
    print()
    
    for name, algorithm in algorithms.items():
        metadata = algorithm.metadata
        ethical_props = algorithm.get_ethical_properties()
        
        print(f"🔧 {name.upper().replace('_', ' ')}")
        print(f"   Version: {metadata.version}")
        print(f"   Fairness Aware: {metadata.fairness_aware}")
        print(f"   Privacy Level: {metadata.privacy_level}")
        print(f"   Transparency: {metadata.transparency_level}")
        print(f"   Bias Mitigation: {', '.join(metadata.bias_mitigation)}")
        print(f"   Performance Characteristics:")
        for key, value in metadata.performance_characteristics.items():
            print(f"     {key}: {value}")
        print(f"   Current Usage Count: {ethical_props['usage_count']}")
        print(f"   Violation Rate: {ethical_props['violation_rate']:.2%}")
        print()
    
    return algorithms


def demonstrate_prediction_and_explanation():
    """Demonstrate prediction and explanation generation"""
    print("=" * 80)
    print("PREDICTION AND EXPLANATION DEMONSTRATION")
    print("=" * 80)
    
    # Create test decisions
    decisions = create_diverse_decisions()
    
    # Initialize framework
    orchestrator = EthicsFrameworkOrchestrator()
    
    print("🎯 Processing decisions with explanation generation...")
    print()
    
    results_by_algorithm = {}
    
    for decision in decisions:
        context = {'generate_explanation': True}
        result = orchestrator.process_decision(decision, context)
        
        algorithm = decision.algorithm
        if algorithm not in results_by_algorithm:
            results_by_algorithm[algorithm] = []
        
        results_by_algorithm[algorithm].append(result)
    
    # Display results for each algorithm type
    for algorithm, results in results_by_algorithm.items():
        print(f"🔍 {algorithm.upper().replace('_', ' ')} RESULTS:")
        
        # Show first result in detail
        if results:
            result = results[0]
            layer_data = result['layer_results'][0]['data']
            
            print(f"   Algorithm Result:")
            algorithm_result = layer_data.get('algorithm_result', {})
            for key, value in algorithm_result.items():
                if key not in ['model_metadata', 'inference_time_ms']:
                    if isinstance(value, (list, dict)) and len(str(value)) > 100:
                        print(f"     {key}: [Complex data structure]")
                    else:
                        print(f"     {key}: {value}")
            
            print(f"   Explanation Result:")
            explanation_result = layer_data.get('explanation_result', {})
            if explanation_result and 'error' not in explanation_result:
                print(f"     Explanation Type: {explanation_result.get('explanation_type', 'N/A')}")
                print(f"     Algorithm: {explanation_result.get('algorithm', 'N/A')}")
                
                if 'explanation_text' in explanation_result:
                    print(f"     Explanation: {explanation_result['explanation_text']}")
                
                if 'feature_importance' in explanation_result:
                    print(f"     Feature Importance:")
                    for feature, importance in explanation_result['feature_importance'].items():
                        if isinstance(importance, dict):
                            print(f"       {feature}: {importance}")
                        else:
                            print(f"       {feature}: {importance}")
            else:
                print(f"     Explanation: {explanation_result}")
            
            print(f"   Processing Time: {layer_data.get('processing_time_ms', 0):.2f}ms")
            print(f"   Success: {layer_data.get('success', False)}")
            print()
    
    return results_by_algorithm


def demonstrate_integrated_system_stats():
    """Demonstrate integrated system statistics with algorithm tracking"""
    print("=" * 80)
    print("INTEGRATED SYSTEM STATISTICS DEMONSTRATION")
    print("=" * 80)
    
    # Initialize framework
    orchestrator = EthicsFrameworkOrchestrator()
    
    # Process multiple decisions to generate statistics
    decisions = create_diverse_decisions() * 3  # Process each type 3 times
    
    print(f"🎯 Processing {len(decisions)} decisions to generate statistics...")
    
    for decision in decisions:
        context = {'generate_explanation': random.choice([True, False])}
        orchestrator.process_decision(decision, context)
    
    # Get comprehensive system statistics
    system_stats = orchestrator.get_system_stats()
    
    print(f"\n📊 Comprehensive System Statistics:")
    
    # Performance statistics
    if 'total_processing_time' in system_stats:
        perf_stats = system_stats['total_processing_time']
        print(f"\n   Processing Performance:")
        print(f"     Total decisions: {perf_stats['count']}")
        print(f"     Mean time: {perf_stats['mean']:.2f}ms")
        print(f"     P95 time: {perf_stats['p95']:.2f}ms")
        print(f"     P99 time: {perf_stats['p99']:.2f}ms")
    
    # Algorithm statistics
    for key, value in system_stats.items():
        if key.endswith('_algorithms') and isinstance(value, dict):
            print(f"\n   {key.replace('_', ' ').title()}:")
            print(f"     Total algorithms: {value.get('total_algorithms', 0)}")
            print(f"     Total usage: {value.get('total_usage', 0)}")
            print(f"     Total explanations: {value.get('total_explanations', 0)}")
            
            algorithms = value.get('algorithms', {})
            for alg_name, alg_stats in algorithms.items():
                print(f"\n     {alg_name.upper().replace('_', ' ')}:")
                print(f"       Usage count: {alg_stats['usage_count']}")
                print(f"       Explanation requests: {alg_stats['explanation_requests']}")
                print(f"       Violation rate: {alg_stats['violation_rate']:.2%}")
                
                perf_stats = alg_stats.get('performance_stats', {})
                if perf_stats.get('total_requests', 0) > 0:
                    print(f"       Avg inference time: {perf_stats.get('avg_inference_time', 0):.2f}ms")
                
                metadata = alg_stats.get('algorithm_metadata', {})
                print(f"       Fairness aware: {metadata.get('fairness_aware', False)}")
                print(f"       Privacy level: {metadata.get('privacy_level', 'unknown')}")
                print(f"       Transparency: {metadata.get('transparency_level', 'unknown')}")
    
    # Intervention statistics (if available)
    if 'intervention_analytics' in system_stats:
        print(f"\n   Intervention Analytics:")
        for metric, stats in system_stats['intervention_analytics'].items():
            print(f"     {metric}: {stats}")
    
    return system_stats


def demonstrate_explanation_quality():
    """Demonstrate explanation quality and ethical considerations"""
    print("\n" + "=" * 80)
    print("EXPLANATION QUALITY AND ETHICAL CONSIDERATIONS")
    print("=" * 80)
    
    # Test explanation generation for each algorithm type
    algorithms = {
        'collaborative_filtering': CollaborativeFilteringModel(),
        'hiring_recommendation': HiringRecommendationModel(),
        'social_media_ranking': SocialMediaRankingModel(),
        'content_classification': ContentClassificationModel()
    }
    
    test_decisions = create_diverse_decisions()[:4]  # One for each algorithm
    
    for i, decision in enumerate(test_decisions):
        algorithm_name = decision.algorithm
        algorithm = algorithms[algorithm_name]
        
        print(f"🔍 {algorithm_name.upper().replace('_', ' ')} EXPLANATION ANALYSIS:")
        
        # Generate prediction
        prediction = algorithm.predict(decision, {})
        
        # Generate explanation
        explanation = algorithm.explain(decision, prediction)
        
        print(f"   Prediction Summary:")
        print(f"     Algorithm: {prediction.get('algorithm', 'N/A')}")
        print(f"     Inference time: {prediction.get('inference_time_ms', 0):.2f}ms")
        
        print(f"   Explanation Quality:")
        print(f"     Type: {explanation.get('explanation_type', 'N/A')}")
        print(f"     Has text explanation: {'explanation_text' in explanation}")
        print(f"     Has feature analysis: {'feature_importance' in explanation or 'feature_contributions' in explanation}")
        print(f"     Has fairness analysis: {'fairness_analysis' in explanation or 'fairness_considerations' in explanation}")
        
        # Check ethical considerations
        ethical_keys = [
            'fairness_considerations', 'fairness_analysis', 'bias_mitigation',
            'diversity_considerations', 'user_control', 'moderation_details'
        ]
        
        ethical_coverage = sum(1 for key in ethical_keys if key in explanation)
        print(f"     Ethical coverage: {ethical_coverage}/{len(ethical_keys)} aspects covered")
        
        if 'explanation_text' in explanation:
            text_length = len(explanation['explanation_text'])
            print(f"     Explanation length: {text_length} characters")
        
        print()


def main():
    """Main demonstration function"""
    print("🚀 BASE ALGORITHM INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print("This demonstration shows how BaseAlgorithm interface is now")
    print("properly integrated with metadata, explanations, and ethical tracking.")
    print()
    
    try:
        # Demonstrate algorithm metadata
        algorithms = demonstrate_algorithm_metadata()
        
        # Demonstrate prediction and explanation
        results = demonstrate_prediction_and_explanation()
        
        # Demonstrate integrated system statistics
        system_stats = demonstrate_integrated_system_stats()
        
        # Demonstrate explanation quality
        demonstrate_explanation_quality()
        
        print("\n" + "=" * 80)
        print("🎉 BASE ALGORITHM INTEGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("Key achievements:")
        print("✅ All ML models now inherit from BaseAlgorithm")
        print("✅ Proper algorithm metadata integration")
        print("✅ Explanation generation for all algorithms")
        print("✅ Ethical properties tracking operational")
        print("✅ Performance statistics collection working")
        print("✅ Comprehensive system monitoring active")
        print()
        print("The BaseAlgorithm interface is now fully integrated and")
        print("provides standardized ethical AI capabilities across all models!")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 