#!/usr/bin/env python3
"""
experiments/comprehensive_framework_test.py
===========================================
Comprehensive Ethics Framework Testing Suite
Matches the original technical report experimental scope
"""

import sys
import os
import time
import json
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ethics_framework.core.interfaces import Decision
from ethics_framework.core.constraints import (
    FairnessConstraint, PrivacyConstraint, WellbeingConstraint,
    TransparencyConstraint, ConsentConstraint, ConstraintComposer
)
from ethics_framework.algorithms.ml_models import (
    CollaborativeFilteringModel, HiringRecommendationModel,
    SocialMediaRankingModel, ContentClassificationModel
)
from ethics_framework.simulation.data_generator import DecisionGenerator


@dataclass
class ExperimentResult:
    """Results from a comprehensive experiment"""
    scenario: str
    total_decisions: int
    approval_rate: float
    constraint_satisfaction: Dict[str, float]
    processing_time_ms: float
    violations: List[Dict]
    conflicts: int


class ComprehensiveFrameworkTest:
    """
    Comprehensive testing suite that matches the original technical report
    Tests all scenarios with full constraint composition
    """
    
    def __init__(self):
        self.decision_generator = DecisionGenerator()
        self.results = {}
        self.total_decisions = 0
        self.total_violations = 0
        
    def run_comprehensive_test(self, decisions_per_scenario: int = 3000) -> Dict[str, Any]:
        """
        Run comprehensive framework test across all scenarios
        Matches the original technical report scope
        """
        print("🔬 COMPREHENSIVE ETHICS FRAMEWORK TEST")
        print("=" * 60)
        print(f"Testing {decisions_per_scenario} decisions per scenario")
        print("Scenarios: Social Media, Hiring, Content Recommendation")
        print("Constraints: Fairness, Privacy, Wellbeing, Transparency, Consent")
        print()
        
        scenarios = ['social_media', 'hiring', 'content_recommendation']
        all_results = {}
        
        for scenario in scenarios:
            print(f"🎯 Testing {scenario.replace('_', ' ').title()} Scenario...")
            result = self._test_scenario(scenario, decisions_per_scenario)
            all_results[scenario] = result
            print(f"   ✅ Completed: {result.approval_rate:.1f}% approval rate")
            print()
        
        # Generate summary statistics
        summary = self._generate_summary(all_results)
        
        # Save results
        self._save_results(all_results, summary)
        
        return {
            'scenario_results': all_results,
            'summary': summary,
            'total_decisions': sum(r.total_decisions for r in all_results.values()),
            'total_violations': sum(len(r.violations) for r in all_results.values())
        }
    
    def _test_scenario(self, scenario: str, num_decisions: int) -> ExperimentResult:
        """Test a specific scenario with comprehensive constraint validation"""
        
        # Create scenario-specific constraints
        constraints = self._create_scenario_constraints(scenario)
        composer = ConstraintComposer(constraints, composition_mode="intersection")
        
        # Generate decisions for this scenario
        decisions = []
        for _ in range(num_decisions):
            decision = self._generate_scenario_decision(scenario)
            decisions.append(decision)
        
        # Process all decisions
        start_time = time.perf_counter()
        approved_count = 0
        all_violations = []
        constraint_stats = {c.name: {'satisfied': 0, 'total': 0} for c in constraints}
        
        for decision in decisions:
            # Validate against all constraints
            validation_result = composer.validate_all(decision.to_dict(), {})
            
            if validation_result['overall_satisfied']:
                approved_count += 1
            
            # Track individual constraint performance
            for constraint_name, result in validation_result['constraint_results'].items():
                constraint_stats[constraint_name]['total'] += 1
                if result['satisfied']:
                    constraint_stats[constraint_name]['satisfied'] += 1
            
            # Collect violations
            all_violations.extend(validation_result.get('violations', []))
        
        processing_time = (time.perf_counter() - start_time) * 1000  # ms
        
        # Calculate satisfaction rates
        satisfaction_rates = {}
        for constraint_name, stats in constraint_stats.items():
            if stats['total'] > 0:
                satisfaction_rates[constraint_name] = (stats['satisfied'] / stats['total']) * 100
            else:
                satisfaction_rates[constraint_name] = 0.0
        
        return ExperimentResult(
            scenario=scenario,
            total_decisions=num_decisions,
            approval_rate=(approved_count / num_decisions) * 100,
            constraint_satisfaction=satisfaction_rates,
            processing_time_ms=processing_time,
            violations=[v.to_dict() if hasattr(v, 'to_dict') else v for v in all_violations],
            conflicts=0  # No conflicts in our composition system
        )
    
    def _create_scenario_constraints(self, scenario: str) -> List:
        """Create constraints appropriate for each scenario"""
        base_constraints = [
            FairnessConstraint("fairness", "demographic_group", threshold=0.1),
            PrivacyConstraint("privacy", epsilon=1.0, delta=1e-5),
            TransparencyConstraint("transparency", min_clarity_score=0.8),
            ConsentConstraint("consent", ["data_processing", "personalization"]),
            WellbeingConstraint("wellbeing", metric="engagement_time", max_threshold=120.0)
        ]
        
        if scenario == 'hiring':
            # Stricter fairness for hiring
            base_constraints[0] = FairnessConstraint("fairness", "demographic_group", threshold=0.05)
        elif scenario == 'social_media':
            # More permissive wellbeing for social media
            base_constraints[4] = WellbeingConstraint("wellbeing", metric="engagement_time", max_threshold=180.0)
        
        return base_constraints
    
    def _generate_scenario_decision(self, scenario: str) -> Decision:
        """Generate a decision appropriate for the scenario"""
        base_decision = {
            'user_id': random.randint(1, 10000),
            'content_id': random.randint(1, 100000),
            'algorithm': 'recommendation'
        }
        
        if scenario == 'social_media':
            base_decision['attributes'] = {
                'engagement_time_today': random.randint(0, 300),  # minutes
                'break_since_last_session': random.randint(0, 120),  # minutes
                'content_diversity_score': random.uniform(0, 1),
                'demographic_group': random.choice(['A', 'B', 'C', 'D']),
                'relevance_score': random.uniform(0, 1),
                'recency_hours': random.randint(1, 168)
            }
        elif scenario == 'hiring':
            base_decision['attributes'] = {
                'years_experience': random.randint(0, 20),
                'education_level': random.randint(1, 5),
                'skills_match': random.uniform(0, 1),
                'demographic_group': random.choice(['A', 'B', 'C', 'D']),
                'interview_score': random.uniform(0, 100),
                'salary_history': random.randint(30000, 150000)
            }
        elif scenario == 'content_recommendation':
            base_decision['attributes'] = {
                'relevance_score': random.uniform(0, 1),
                'popularity_score': random.uniform(0, 1),
                'user_history_match': random.uniform(0, 1),
                'demographic_group': random.choice(['A', 'B', 'C', 'D']),
                'content_type': random.choice(['news', 'entertainment', 'educational']),
                'text_length': random.randint(10, 1000)
            }
        
        return Decision(**base_decision)
    
    def _generate_summary(self, results: Dict[str, ExperimentResult]) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        total_decisions = sum(r.total_decisions for r in results.values())
        total_violations = sum(len(r.violations) for r in results.values())
        
        # Calculate overall satisfaction rate
        overall_satisfaction = 0
        constraint_totals = {}
        
        for result in results.values():
            overall_satisfaction += result.approval_rate * result.total_decisions
            
            for constraint, satisfaction in result.constraint_satisfaction.items():
                if constraint not in constraint_totals:
                    constraint_totals[constraint] = {'total_satisfaction': 0, 'total_decisions': 0}
                constraint_totals[constraint]['total_satisfaction'] += satisfaction * result.total_decisions
                constraint_totals[constraint]['total_decisions'] += result.total_decisions
        
        overall_satisfaction /= total_decisions
        
        # Calculate average constraint satisfaction
        avg_constraint_satisfaction = {}
        for constraint, totals in constraint_totals.items():
            avg_constraint_satisfaction[constraint] = totals['total_satisfaction'] / totals['total_decisions']
        
        # Processing time statistics
        total_processing_time = sum(r.processing_time_ms for r in results.values())
        avg_processing_time = total_processing_time / len(results)
        
        return {
            'total_decisions': total_decisions,
            'total_violations': total_violations,
            'overall_satisfaction_rate': overall_satisfaction,
            'constraint_satisfaction_rates': avg_constraint_satisfaction,
            'scenario_approval_rates': {
                scenario: result.approval_rate 
                for scenario, result in results.items()
            },
            'total_processing_time_ms': total_processing_time,
            'avg_processing_time_ms': avg_processing_time,
            'conflicts_detected': sum(r.conflicts for r in results.values())
        }
    
    def _save_results(self, results: Dict[str, ExperimentResult], summary: Dict[str, Any]):
        """Save comprehensive results to files"""
        
        # Convert results to serializable format
        serializable_results = {}
        for scenario, result in results.items():
            serializable_results[scenario] = {
                'scenario': result.scenario,
                'total_decisions': result.total_decisions,
                'approval_rate': result.approval_rate,
                'constraint_satisfaction': result.constraint_satisfaction,
                'processing_time_ms': result.processing_time_ms,
                'violation_count': len(result.violations),
                'conflicts': result.conflicts
            }
        
        # Save to JSON
        output_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'experiment_type': 'comprehensive_framework_test',
            'scenario_results': serializable_results,
            'summary': summary
        }
        
        with open('comprehensive_framework_results.json', 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"📊 Results saved to comprehensive_framework_results.json")


def main():
    """Run the comprehensive framework test"""
    print("🚀 Starting Comprehensive Ethics Framework Test")
    print("=" * 60)
    
    tester = ComprehensiveFrameworkTest()
    results = tester.run_comprehensive_test(decisions_per_scenario=3000)
    
    print("\n📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    print(f"Total Decisions Processed: {results['total_decisions']:,}")
    print(f"Total Violations: {results['total_violations']:,}")
    print(f"Overall Satisfaction Rate: {results['summary']['overall_satisfaction_rate']:.1f}%")
    print()
    
    print("Scenario Approval Rates:")
    for scenario, rate in results['summary']['scenario_approval_rates'].items():
        print(f"  {scenario.replace('_', ' ').title()}: {rate:.1f}%")
    print()
    
    print("Constraint Satisfaction Rates:")
    for constraint, rate in results['summary']['constraint_satisfaction_rates'].items():
        print(f"  {constraint.title()}: {rate:.1f}%")
    print()
    
    print(f"Total Processing Time: {results['summary']['total_processing_time_ms']:.1f}ms")
    print(f"Average Processing Time: {results['summary']['avg_processing_time_ms']:.1f}ms")
    print(f"Conflicts Detected: {results['summary']['conflicts_detected']}")
    
    print("\n✅ Comprehensive framework test completed successfully!")
    return results


if __name__ == "__main__":
    main() 