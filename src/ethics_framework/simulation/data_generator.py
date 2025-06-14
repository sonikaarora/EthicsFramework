"""
Data Generation for Ethics Framework Testing

This module provides sophisticated data generation capabilities for testing
the ethics framework across different scenarios and use cases.
"""

import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np

from ..core.interfaces import Decision


@dataclass
class GenerationConfig:
    """Configuration for data generation"""
    scenario: str
    num_decisions: int
    user_id_range: tuple = (1, 10000)
    content_id_range: tuple = (1, 100000)
    seed: Optional[int] = None


class DecisionGenerator:
    """Enhanced decision generator with realistic data patterns"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        # Realistic data distributions
        self.user_behavior_profiles = {
            'light_user': {'engagement_multiplier': 0.3, 'diversity_preference': 0.8},
            'moderate_user': {'engagement_multiplier': 0.6, 'diversity_preference': 0.5},
            'heavy_user': {'engagement_multiplier': 1.2, 'diversity_preference': 0.2},
            'diverse_user': {'engagement_multiplier': 0.7, 'diversity_preference': 0.9}
        }
        
        self.demographic_groups = ['group_a', 'group_b', 'group_c', 'group_d']
        self.education_levels = ['high_school', 'bachelors', 'masters', 'phd']
        self.content_types = ['text', 'image', 'video', 'link']
        
    def generate_decision(self, scenario: str, user_id: Optional[int] = None, 
                         content_id: Optional[int] = None) -> Decision:
        """Generate a single decision with realistic attributes"""
        
        # Generate base decision data
        if user_id is None:
            user_id = random.randint(1, 10000)
        if content_id is None:
            content_id = random.randint(1, 100000)
        
        algorithm = random.choice(['recommendation', 'classification', 'ranking'])
        
        # Generate scenario-specific attributes
        if scenario == 'social_media':
            attributes = self._generate_social_media_attributes(user_id, content_id)
        elif scenario == 'hiring':
            attributes = self._generate_hiring_attributes(user_id)
        elif scenario == 'content_recommendation':
            attributes = self._generate_content_recommendation_attributes(user_id, content_id)
        else:
            attributes = self._generate_generic_attributes()
        
        return Decision(
            user_id=user_id,
            content_id=content_id,
            algorithm=algorithm,
            attributes=attributes,
            timestamp=time.time()
        )
    
    def generate_batch(self, config: GenerationConfig) -> List[Decision]:
        """Generate a batch of decisions for a specific scenario"""
        decisions = []
        
        for _ in range(config.num_decisions):
            user_id = random.randint(*config.user_id_range)
            content_id = random.randint(*config.content_id_range)
            decision = self.generate_decision(config.scenario, user_id, content_id)
            decisions.append(decision)
        
        return decisions
    
    def _generate_social_media_attributes(self, user_id: int, content_id: int) -> Dict[str, Any]:
        """Generate realistic social media attributes"""
        
        # Assign user behavior profile
        profile_name = random.choice(list(self.user_behavior_profiles.keys()))
        profile = self.user_behavior_profiles[profile_name]
        
        # Generate engagement patterns
        base_engagement = random.randint(0, 300)  # minutes today
        engagement_time_today = int(base_engagement * profile['engagement_multiplier'])
        
        # Generate break patterns
        if engagement_time_today > 60:
            break_since_last_session = random.randint(0, 30)  # Recent heavy usage
        else:
            break_since_last_session = random.randint(30, 180)  # Longer breaks
        
        # Content diversity based on user profile
        base_diversity = random.uniform(0.2, 0.9)
        content_diversity_score = base_diversity * profile['diversity_preference']
        
        return {
            'engagement_time_today': engagement_time_today,
            'break_since_last_session': break_since_last_session,
            'content_diversity_score': content_diversity_score,
            'content_type': random.choice(self.content_types),
            'user_profile': profile_name,
            'demographic_group': random.choice(self.demographic_groups),
            'score': random.uniform(0.1, 0.9)
        }
    
    def _generate_hiring_attributes(self, user_id: int) -> Dict[str, Any]:
        """Generate realistic hiring attributes with bias patterns"""
        
        demographic_group = random.choice(self.demographic_groups)
        
        # Simulate realistic experience distributions
        years_experience = np.random.gamma(2, 3)  # Gamma distribution for experience
        years_experience = max(0, min(25, int(years_experience)))
        
        # Education level with some demographic correlation (simulating bias)
        if demographic_group in ['group_a', 'group_b']:
            education_weights = [0.4, 0.3, 0.2, 0.1]  # Less advanced degrees
        else:
            education_weights = [0.2, 0.3, 0.3, 0.2]  # More balanced
        
        education_level = np.random.choice(self.education_levels, p=education_weights)
        
        # Skills match with some randomness
        base_skills = random.uniform(40, 95)
        
        # Simulate potential bias in skills assessment
        if demographic_group == 'group_a':
            skills_match = base_skills * random.uniform(0.85, 1.0)  # Slight penalty
        else:
            skills_match = base_skills * random.uniform(0.95, 1.05)  # Slight advantage
        
        skills_match = max(0, min(100, skills_match))
        
        # Interview score
        interview_score = random.uniform(0.3, 0.9)
        
        return {
            'years_experience': years_experience,
            'education_level': education_level,
            'skills_match': skills_match,
            'interview_score': interview_score,
            'demographic_group': demographic_group,
            'score': random.uniform(0.1, 0.9)
        }
    
    def _generate_content_recommendation_attributes(self, user_id: int, content_id: int) -> Dict[str, Any]:
        """Generate content recommendation attributes"""
        
        # Content relevance with user preferences
        relevance_score = random.uniform(0.2, 0.95)
        
        # Popularity with power-law distribution (some content much more popular)
        popularity = np.random.pareto(1.16) + 1  # Pareto distribution
        popularity = min(popularity / 10, 1.0)  # Normalize to 0-1
        
        # User history match
        user_history_match = random.uniform(0.1, 0.9)
        
        # Content age (newer content might be preferred)
        content_age_days = np.random.exponential(7)  # Exponential decay
        content_age_days = min(content_age_days, 365)
        
        return {
            'relevance_score': relevance_score,
            'popularity': popularity,
            'user_history_match': user_history_match,
            'content_age_days': content_age_days,
            'content_type': random.choice(self.content_types),
            'demographic_group': random.choice(self.demographic_groups),
            'score': random.uniform(0.1, 0.9)
        }
    
    def _generate_generic_attributes(self) -> Dict[str, Any]:
        """Generate generic attributes for unknown scenarios"""
        return {
            'score': random.uniform(0.1, 0.9),
            'demographic_group': random.choice(self.demographic_groups),
            'feature_1': random.uniform(0, 1),
            'feature_2': random.uniform(0, 1),
            'feature_3': random.uniform(0, 1)
        }


class ScenarioDataGenerator:
    """Advanced scenario-specific data generation with realistic patterns"""
    
    def __init__(self, seed: Optional[int] = None):
        self.decision_generator = DecisionGenerator(seed)
        self.scenario_configs = {
            'social_media': {
                'user_base_size': 50000,
                'content_pool_size': 1000000,
                'daily_decisions_per_user': (10, 200),
                'peak_hours': [12, 13, 18, 19, 20, 21]
            },
            'hiring': {
                'user_base_size': 10000,
                'content_pool_size': 50000,
                'daily_decisions_per_user': (1, 5),
                'peak_hours': [9, 10, 11, 14, 15, 16]
            },
            'content_recommendation': {
                'user_base_size': 100000,
                'content_pool_size': 500000,
                'daily_decisions_per_user': (5, 50),
                'peak_hours': [8, 12, 17, 20, 21, 22]
            }
        }
    
    def generate_realistic_dataset(self, scenario: str, num_decisions: int, 
                                 time_span_hours: int = 24) -> List[Decision]:
        """Generate a realistic dataset with temporal patterns"""
        
        if scenario not in self.scenario_configs:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        config = self.scenario_configs[scenario]
        decisions = []
        
        # Generate decisions with realistic temporal distribution
        for i in range(num_decisions):
            # Simulate time distribution (more activity during peak hours)
            hour = random.choices(
                range(24), 
                weights=self._get_hourly_weights(config['peak_hours'])
            )[0]
            
            # Generate decision with temporal context
            decision = self.decision_generator.generate_decision(scenario)
            
            # Adjust timestamp to reflect hour
            base_time = time.time() - (time_span_hours * 3600)
            decision.timestamp = base_time + (hour * 3600) + random.uniform(0, 3600)
            
            decisions.append(decision)
        
        # Sort by timestamp for realistic ordering
        decisions.sort(key=lambda d: d.timestamp)
        
        return decisions
    
    def generate_biased_dataset(self, scenario: str, num_decisions: int, 
                              bias_type: str = 'demographic') -> List[Decision]:
        """Generate dataset with intentional bias for testing fairness constraints"""
        
        decisions = []
        
        for _ in range(num_decisions):
            decision = self.decision_generator.generate_decision(scenario)
            
            # Introduce bias based on type
            if bias_type == 'demographic' and scenario == 'hiring':
                # Bias hiring decisions against certain groups
                if decision.attributes['demographic_group'] == 'group_a':
                    decision.attributes['skills_match'] *= 0.8  # Reduce skills assessment
                    decision.attributes['interview_score'] *= 0.9  # Reduce interview score
            
            elif bias_type == 'popularity' and scenario == 'content_recommendation':
                # Bias toward popular content
                if decision.attributes['popularity'] > 0.7:
                    decision.attributes['relevance_score'] *= 1.2  # Boost relevance
            
            elif bias_type == 'engagement' and scenario == 'social_media':
                # Bias toward high-engagement users
                if decision.attributes['engagement_time_today'] > 120:
                    decision.attributes['content_diversity_score'] *= 0.5  # Reduce diversity
            
            decisions.append(decision)
        
        return decisions
    
    def _get_hourly_weights(self, peak_hours: List[int]) -> List[float]:
        """Generate hourly weights for realistic temporal distribution"""
        weights = [1.0] * 24  # Base weight for all hours
        
        # Increase weights for peak hours
        for hour in peak_hours:
            weights[hour] = 3.0
        
        # Reduce weights for late night/early morning
        for hour in [0, 1, 2, 3, 4, 5, 6]:
            weights[hour] = 0.2
        
        return weights
    
    def generate_stress_test_data(self, scenario: str, num_decisions: int) -> List[Decision]:
        """Generate edge cases and stress test data"""
        
        decisions = []
        
        for i in range(num_decisions):
            decision = self.decision_generator.generate_decision(scenario)
            
            # Introduce edge cases every 10th decision
            if i % 10 == 0:
                if scenario == 'social_media':
                    # Extreme engagement times
                    decision.attributes['engagement_time_today'] = random.choice([0, 480])  # 0 or 8 hours
                    decision.attributes['break_since_last_session'] = random.choice([0, 1440])  # 0 or 24 hours
                
                elif scenario == 'hiring':
                    # Extreme qualifications
                    decision.attributes['years_experience'] = random.choice([0, 30])
                    decision.attributes['skills_match'] = random.choice([0, 100])
                
                elif scenario == 'content_recommendation':
                    # Extreme popularity/relevance
                    decision.attributes['popularity'] = random.choice([0.0, 1.0])
                    decision.attributes['relevance_score'] = random.choice([0.0, 1.0])
            
            decisions.append(decision)
        
        return decisions 