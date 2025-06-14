"""
ethics_framework/simulation/workload_generator.py
=================================================
Advanced workload generation for realistic experiment scenarios
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import time
from scipy import stats
from enum import Enum
import json
import pandas as pd

from ..core.interfaces import Decision


class UserDistribution(Enum):
    """Types of user distributions"""
    UNIFORM = "uniform"
    POWER_LAW = "power_law"
    NORMAL = "normal"
    BIMODAL = "bimodal"
    EXPONENTIAL = "exponential"


class ContentDistribution(Enum):
    """Types of content distributions"""
    UNIFORM = "uniform"
    LONG_TAIL = "long_tail"
    VIRAL = "viral"
    SEASONAL = "seasonal"
    TRENDING = "trending"


class TemporalPattern(Enum):
    """Temporal access patterns"""
    CONSTANT = "constant"
    DAILY_CYCLE = "daily_cycle"
    WEEKLY_CYCLE = "weekly_cycle"
    BURSTY = "bursty"
    EVENT_DRIVEN = "event_driven"


@dataclass
class WorkloadConfig:
    """Configuration for workload generation"""
    num_requests: int
    num_users: int
    num_content: int
    user_distribution: UserDistribution = UserDistribution.POWER_LAW
    content_distribution: ContentDistribution = ContentDistribution.LONG_TAIL
    temporal_pattern: TemporalPattern = TemporalPattern.DAILY_CYCLE
    algorithms: List[str] = field(default_factory=lambda: ['recommendation', 'ranking'])
    demographics: List[str] = field(default_factory=lambda: ['A', 'B', 'C', 'D'])
    start_time: float = field(default_factory=time.time)
    duration_hours: float = 24.0
    seed: Optional[int] = 42
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'num_requests': self.num_requests,
            'num_users': self.num_users,
            'num_content': self.num_content,
            'user_distribution': self.user_distribution.value,
            'content_distribution': self.content_distribution.value,
            'temporal_pattern': self.temporal_pattern.value,
            'algorithms': self.algorithms,
            'demographics': self.demographics,
            'duration_hours': self.duration_hours
        }


class UserBehaviorModel:
    """Models realistic user behavior patterns"""
    
    def __init__(self, user_id: int, demographics: str, seed: Optional[int] = None):
        self.user_id = user_id
        self.demographics = demographics
        self.rng = np.random.RandomState(seed if seed else user_id)
        
        # User characteristics
        self.activity_level = self.rng.beta(2, 5)  # Most users are moderate
        self.preference_diversity = self.rng.beta(3, 3)  # Balanced
        self.session_length_mean = self.rng.gamma(2, 15)  # Minutes
        self.peak_hours = self._generate_peak_hours()
        self.content_preferences = self._generate_content_preferences()
        
    def _generate_peak_hours(self) -> List[int]:
        """Generate user's peak activity hours"""
        # Most users active in evening
        base_hours = [19, 20, 21, 22]
        
        # Add some variation
        offset = self.rng.randint(-3, 4)
        peak_hours = [(h + offset) % 24 for h in base_hours]
        
        # Some users also active in morning
        if self.rng.random() < 0.3:
            peak_hours.extend([7, 8, 9])
        
        return peak_hours
    
    def _generate_content_preferences(self) -> Dict[str, float]:
        """Generate content category preferences"""
        categories = ['entertainment', 'news', 'education', 'sports', 'gaming']
        
        # Generate preference weights
        weights = self.rng.dirichlet(np.ones(len(categories)) * 2)
        
        return dict(zip(categories, weights))
    
    def get_activity_probability(self, hour: int) -> float:
        """Get probability of user being active at given hour"""
        base_prob = self.activity_level * 0.1
        
        if hour in self.peak_hours:
            return min(base_prob * 5, 0.9)
        elif abs(hour - self.peak_hours[0]) <= 2:
            return min(base_prob * 2, 0.5)
        else:
            return base_prob
    
    def generate_session(self, current_time: float) -> Dict[str, Any]:
        """Generate a user session"""
        session_length = self.rng.exponential(self.session_length_mean)
        
        return {
            'start_time': current_time,
            'duration_minutes': session_length,
            'device': self.rng.choice(['mobile', 'desktop', 'tv', 'tablet'],
                                    p=[0.4, 0.3, 0.2, 0.1]),
            'connection_quality': self.rng.choice(['high', 'medium', 'low'],
                                                p=[0.6, 0.3, 0.1])
        }


class ContentModel:
    """Models content characteristics and popularity"""
    
    def __init__(self, content_id: int, num_content: int, 
                 distribution: ContentDistribution, seed: Optional[int] = None):
        self.content_id = content_id
        self.rng = np.random.RandomState(seed if seed else content_id)
        
        # Content metadata
        self.category = self._assign_category()
        self.quality_score = self.rng.beta(4, 2)  # Skewed towards quality
        self.release_time = self._generate_release_time(num_content)
        self.base_popularity = self._generate_popularity(distribution, num_content)
        
        # Content features for recommendation
        self.features = self.rng.randn(32)  # 32-dimensional embedding
        
    def _assign_category(self) -> str:
        """Assign content category"""
        categories = ['entertainment', 'news', 'education', 'sports', 'gaming']
        # Realistic category distribution
        probs = [0.4, 0.2, 0.15, 0.15, 0.1]
        return self.rng.choice(categories, p=probs)
    
    def _generate_release_time(self, num_content: int) -> float:
        """Generate content release time"""
        # Mix of old and new content
        if self.content_id < num_content * 0.2:
            # Old catalog content
            days_ago = self.rng.uniform(30, 365)
        elif self.content_id < num_content * 0.8:
            # Recent content
            days_ago = self.rng.uniform(1, 30)
        else:
            # Fresh content
            days_ago = self.rng.uniform(0, 1)
        
        return time.time() - (days_ago * 24 * 3600)
    
    def _generate_popularity(self, distribution: ContentDistribution, 
                           num_content: int) -> float:
        """Generate base popularity based on distribution"""
        
        if distribution == ContentDistribution.UNIFORM:
            return self.rng.uniform(0, 1)
            
        elif distribution == ContentDistribution.LONG_TAIL:
            # Power law distribution
            rank = self.content_id / num_content
            return (1 - rank) ** 2.5
            
        elif distribution == ContentDistribution.VIRAL:
            # Few items extremely popular
            if self.content_id < num_content * 0.01:
                return self.rng.uniform(0.8, 1.0)
            elif self.content_id < num_content * 0.1:
                return self.rng.uniform(0.3, 0.7)
            else:
                return self.rng.uniform(0, 0.3)
                
        elif distribution == ContentDistribution.SEASONAL:
            # Popularity varies with time
            phase = (self.content_id / num_content) * 2 * np.pi
            return 0.5 + 0.4 * np.sin(phase)
            
        else:  # TRENDING
            # Recent content more popular
            age_days = (time.time() - self.release_time) / (24 * 3600)
            return np.exp(-age_days / 7) * self.quality_score
    
    def get_temporal_popularity(self, current_time: float) -> float:
        """Get popularity at specific time"""
        age_days = (current_time - self.release_time) / (24 * 3600)
        
        # Decay factor
        decay = np.exp(-age_days / 30)
        
        # Add some random variation
        noise = self.rng.normal(0, 0.1)
        
        return np.clip(self.base_popularity * decay + noise, 0, 1)


class WorkloadGenerator:
    """Generates realistic workloads for experiments"""
    
    def __init__(self, config: WorkloadConfig):
        self.config = config
        if config.seed:
            np.random.seed(config.seed)
        
        # Initialize models
        self._initialize_users()
        self._initialize_content()
        
    def _initialize_users(self):
        """Initialize user behavior models"""
        self.users = {}
        
        for user_id in range(1, self.config.num_users + 1):
            # Assign demographics based on realistic distribution
            if user_id <= self.config.num_users * 0.3:
                demographic = 'A'
            elif user_id <= self.config.num_users * 0.55:
                demographic = 'B'
            elif user_id <= self.config.num_users * 0.8:
                demographic = 'C'
            else:
                demographic = 'D'
            
            self.users[user_id] = UserBehaviorModel(
                user_id, demographic, seed=self.config.seed
            )
    
    def _initialize_content(self):
        """Initialize content models"""
        self.content = {}
        
        for content_id in range(1, self.config.num_content + 1):
            self.content[content_id] = ContentModel(
                content_id, 
                self.config.num_content,
                self.config.content_distribution,
                seed=self.config.seed
            )
    
    def generate(self) -> List[Decision]:
        """Generate complete workload"""
        decisions = []
        
        # Generate timeline
        timeline = self._generate_timeline()
        
        for timestamp, user_id in timeline:
            # Get user model
            user = self.users.get(user_id % self.config.num_users + 1)
            
            # Select content based on user preferences and popularity
            content_id = self._select_content(user, timestamp)
            
            # Create decision
            decision = self._create_decision(user, content_id, timestamp)
            decisions.append(decision)
        
        return decisions
    
    def _generate_timeline(self) -> List[Tuple[float, int]]:
        """Generate temporal sequence of user requests"""
        timeline = []
        
        if self.config.temporal_pattern == TemporalPattern.CONSTANT:
            # Uniform distribution over time
            interval = self.config.duration_hours * 3600 / self.config.num_requests
            for i in range(self.config.num_requests):
                timestamp = self.config.start_time + i * interval
                user_id = self._select_user(self.config.user_distribution)
                timeline.append((timestamp, user_id))
                
        elif self.config.temporal_pattern == TemporalPattern.DAILY_CYCLE:
            # Realistic daily pattern
            timeline = self._generate_daily_pattern()
            
        elif self.config.temporal_pattern == TemporalPattern.BURSTY:
            # Bursty traffic pattern
            timeline = self._generate_bursty_pattern()
            
        else:
            # Default to constant
            return self._generate_timeline_constant()
        
        return timeline[:self.config.num_requests]
    
    def _generate_daily_pattern(self) -> List[Tuple[float, int]]:
        """Generate requests following daily activity pattern"""
        timeline = []
        
        # Define hourly activity levels (normalized)
        hourly_activity = [
            0.1, 0.05, 0.05, 0.05, 0.05, 0.1,   # 0-5 AM: Very low
            0.2, 0.4, 0.5, 0.4, 0.3, 0.3,       # 6-11 AM: Morning peak
            0.4, 0.3, 0.3, 0.4, 0.5, 0.6,       # 12-17 PM: Afternoon
            0.7, 0.9, 1.0, 0.9, 0.7, 0.3        # 18-23 PM: Evening peak
        ]
        
        # Normalize to probabilities
        total_activity = sum(hourly_activity)
        hourly_probs = [a / total_activity for a in hourly_activity]
        
        # Distribute requests across hours
        current_time = self.config.start_time
        
        for hour in range(24):
            hour_requests = int(self.config.num_requests * hourly_probs[hour % 24])
            
            for _ in range(hour_requests):
                # Add random offset within hour
                offset = np.random.uniform(0, 3600)
                timestamp = current_time + hour * 3600 + offset
                
                # Select active user based on their patterns
                user_id = self._select_active_user(hour)
                timeline.append((timestamp, user_id))
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x[0])
        
        return timeline
    
    def _generate_bursty_pattern(self) -> List[Tuple[float, int]]:
        """Generate bursty traffic pattern"""
        timeline = []
        
        # Parameters for burst generation
        num_bursts = max(10, self.config.num_requests // 100)
        burst_size_mean = self.config.num_requests // num_bursts
        
        current_time = self.config.start_time
        
        for _ in range(num_bursts):
            # Burst size
            burst_size = int(np.random.poisson(burst_size_mean))
            
            # Burst duration (concentrated)
            burst_duration = np.random.exponential(300)  # 5 minutes average
            
            # Generate requests within burst
            for _ in range(burst_size):
                offset = np.random.uniform(0, burst_duration)
                timestamp = current_time + offset
                user_id = self._select_user(self.config.user_distribution)
                timeline.append((timestamp, user_id))
            
            # Time until next burst
            inter_burst_time = np.random.exponential(3600)  # 1 hour average
            current_time += burst_duration + inter_burst_time
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x[0])
        
        return timeline
    
    def _select_user(self, distribution: UserDistribution) -> int:
        """Select user based on distribution"""
        if distribution == UserDistribution.UNIFORM:
            return np.random.randint(1, self.config.num_users + 1)
            
        elif distribution == UserDistribution.POWER_LAW:
            # Pareto distribution (80-20 rule)
            x = np.random.pareto(1.16) + 1
            user_id = int(x * self.config.num_users / 10) % self.config.num_users + 1
            return user_id
            
        elif distribution == UserDistribution.NORMAL:
            # Normal distribution centered at middle
            mean = self.config.num_users / 2
            std = self.config.num_users / 6
            user_id = int(np.random.normal(mean, std))
            return max(1, min(user_id, self.config.num_users))
            
        else:
            return np.random.randint(1, self.config.num_users + 1)
    
    def _select_active_user(self, hour: int) -> int:
        """Select user who is likely active at given hour"""
        # Try multiple users until finding active one
        max_attempts = 100
        
        for _ in range(max_attempts):
            user_id = self._select_user(self.config.user_distribution)
            user = self.users[user_id]
            
            if np.random.random() < user.get_activity_probability(hour):
                return user_id
        
        # Fallback to random user
        return np.random.randint(1, self.config.num_users + 1)
    
    def _select_content(self, user: UserBehaviorModel, timestamp: float) -> int:
        """Select content based on user preferences and popularity"""
        # Combine user preferences with content popularity
        scores = []
        
        # Sample subset of content for efficiency
        sample_size = min(1000, self.config.num_content)
        content_ids = np.random.choice(
            range(1, self.config.num_content + 1),
            size=sample_size,
            replace=False
        )
        
        for content_id in content_ids:
            content = self.content[content_id]
            
            # User-content affinity
            category_preference = user.content_preferences.get(
                content.category, 0.1
            )
            
            # Temporal popularity
            popularity = content.get_temporal_popularity(timestamp)
            
            # Combine scores
            score = 0.7 * category_preference + 0.3 * popularity
            
            # Add noise for exploration
            score += np.random.normal(0, 0.1)
            
            scores.append((content_id, score))
        
        # Select based on scores (softmax-like)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Higher scores more likely, but not deterministic
        probs = np.array([s[1] for s in scores[:20]])  # Top 20
        probs = np.exp(probs * 2) / np.sum(np.exp(probs * 2))
        
        selected_idx = np.random.choice(20, p=probs)
        return scores[selected_idx][0]
    
    def _create_decision(self, user: UserBehaviorModel, 
                        content_id: int, timestamp: float) -> Decision:
        """Create decision object"""
        # Generate session if needed
        session = user.generate_session(timestamp)
        
        # Select algorithm
        algorithm = np.random.choice(self.config.algorithms)
        
        # Create decision
        return Decision(
            user_id=user.user_id,
            content_id=content_id,
            algorithm=algorithm,
            attributes={
                'demographic': user.demographics,
                'device': session['device'],
                'session_duration': session['duration_minutes'],
                'hour_of_day': int((timestamp % 86400) / 3600),
                'day_of_week': int((timestamp % 604800) / 86400),
                'user_activity_level': user.activity_level,
                'content_category': self.content[content_id].category,
                'content_age_days': (timestamp - self.content[content_id].release_time) / 86400
            },
            timestamp=timestamp
        )
    
    def generate_batch(self, batch_size: int) -> List[Decision]:
        """Generate a batch of decisions"""
        return [self._create_decision(
            self.users[np.random.randint(1, self.config.num_users + 1)],
            np.random.randint(1, self.config.num_content + 1),
            time.time()
        ) for _ in range(batch_size)]
    
    def save_workload(self, decisions: List[Decision], filepath: str):
        """Save workload to file"""
        data = {
            'config': self.config.to_dict(),
            'decisions': [
                {
                    'user_id': d.user_id,
                    'content_id': d.content_id,
                    'algorithm': d.algorithm,
                    'attributes': d.attributes,
                    'timestamp': d.timestamp
                }
                for d in decisions
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_workload(filepath: str) -> List[Decision]:
        """Load workload from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        decisions = []
        for d in data['decisions']:
            decision = Decision(
                user_id=d['user_id'],
                content_id=d['content_id'],
                algorithm=d['algorithm'],
                attributes=d['attributes'],
                timestamp=d['timestamp']
            )
            decisions.append(decision)
        
        return decisions
    
    def get_workload_statistics(self, decisions: List[Decision]) -> Dict[str, Any]:
        """Analyze workload characteristics"""
        df = pd.DataFrame([
            {
                'user_id': d.user_id,
                'content_id': d.content_id,
                'algorithm': d.algorithm,
                'hour': d.attributes.get('hour_of_day', 0),
                'demographic': d.attributes.get('demographic', 'unknown'),
                'device': d.attributes.get('device', 'unknown'),
                'category': d.attributes.get('content_category', 'unknown')
            }
            for d in decisions
        ])
        
        stats = {
            'total_requests': len(decisions),
            'unique_users': df['user_id'].nunique(),
            'unique_content': df['content_id'].nunique(),
            'algorithm_distribution': df['algorithm'].value_counts().to_dict(),
            'demographic_distribution': df['demographic'].value_counts().to_dict(),
            'device_distribution': df['device'].value_counts().to_dict(),
            'category_distribution': df['category'].value_counts().to_dict(),
            'hourly_distribution': df['hour'].value_counts().sort_index().to_dict(),
            'user_activity': {
                'mean_requests_per_user': len(decisions) / df['user_id'].nunique(),
                'max_requests_single_user': df['user_id'].value_counts().max(),
                'min_requests_single_user': df['user_id'].value_counts().min()
            },
            'content_popularity': {
                'mean_requests_per_content': len(decisions) / df['content_id'].nunique(),
                'max_requests_single_content': df['content_id'].value_counts().max(),
                'min_requests_single_content': df['content_id'].value_counts().min(),
                'gini_coefficient': self._calculate_gini(df['content_id'].value_counts().values)
            }
        }
        
        return stats
    
    def _calculate_gini(self, values: np.ndarray) -> float:
        """Calculate Gini coefficient for inequality measurement"""
        sorted_values = np.sort(values)
        n = len(values)
        cumsum = np.cumsum(sorted_values)
        return (2 * np.sum((n - np.arange(n)) * sorted_values)) / (n * cumsum[-1]) - 1


def create_scenario_workload(scenario: str, num_requests: int = 10000) -> List[Decision]:
    """Create workload for specific scenario"""
    
    if scenario == "video_streaming":
        config = WorkloadConfig(
            num_requests=num_requests,
            num_users=100000,
            num_content=1000000,
            user_distribution=UserDistribution.POWER_LAW,
            content_distribution=ContentDistribution.LONG_TAIL,
            temporal_pattern=TemporalPattern.DAILY_CYCLE,
            algorithms=['recommendation', 'continue_watching', 'trending']
        )
    
    elif scenario == "social_media":
        config = WorkloadConfig(
            num_requests=num_requests,
            num_users=1000000,
            num_content=10000000,
            user_distribution=UserDistribution.POWER_LAW,
            content_distribution=ContentDistribution.VIRAL,
            temporal_pattern=TemporalPattern.BURSTY,
            algorithms=['feed_ranking', 'friend_suggestions', 'ad_targeting']
        )
    
    elif scenario == "gaming":
        config = WorkloadConfig(
            num_requests=num_requests,
            num_users=50000,
            num_content=1000,  # Game modes/maps
            user_distribution=UserDistribution.NORMAL,
            content_distribution=ContentDistribution.UNIFORM,
            temporal_pattern=TemporalPattern.DAILY_CYCLE,
            algorithms=['matchmaking', 'team_balancing']
        )
    
    elif scenario == "news":
        config = WorkloadConfig(
            num_requests=num_requests,
            num_users=500000,
            num_content=100000,
            user_distribution=UserDistribution.BIMODAL,
            content_distribution=ContentDistribution.TRENDING,
            temporal_pattern=TemporalPattern.EVENT_DRIVEN,
            algorithms=['personalization', 'breaking_news', 'topic_clustering']
        )
    
    else:
        # Default configuration
        config = WorkloadConfig(
            num_requests=num_requests,
            num_users=100000,
            num_content=1000000
        )
    
    generator = WorkloadGenerator(config)
    return generator.generate()