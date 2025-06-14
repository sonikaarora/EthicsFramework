"""
ethics_framework/algorithms/hierarchical_intervention.py
========================================================
Hierarchical intervention system with escalating responses
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
from collections import defaultdict, deque
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class InterventionLevel(Enum):
    """Levels of intervention severity"""
    NONE = 0
    SOFT_NUDGE = 1
    EXPLICIT_WARNING = 2
    FEATURE_LIMITATION = 3
    TEMPORARY_SUSPENSION = 4
    PERMANENT_RESTRICTION = 5


class InterventionType(Enum):
    """Types of interventions"""
    INFORMATIONAL = "informational"
    BEHAVIORAL = "behavioral"
    RESTRICTIVE = "restrictive"
    PUNITIVE = "punitive"


@dataclass
class InterventionConfig:
    """Configuration for intervention system"""
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        'soft_nudge': 0.3,
        'explicit_warning': 0.5,
        'feature_limitation': 0.7,
        'temporary_suspension': 0.85,
        'permanent_restriction': 0.95
    })
    cooldown_periods: Dict[str, float] = field(default_factory=lambda: {
        'soft_nudge': 300,  # 5 minutes
        'explicit_warning': 900,  # 15 minutes
        'feature_limitation': 3600,  # 1 hour
        'temporary_suspension': 86400,  # 24 hours
        'permanent_restriction': float('inf')
    })
    escalation_factors: Dict[str, float] = field(default_factory=lambda: {
        'repeat_violation': 1.2,
        'severity_multiplier': 1.5,
        'time_decay': 0.95
    })
    max_interventions_per_user: int = 100
    intervention_history_window: int = 86400  # 24 hours


@dataclass
class InterventionRecord:
    """Record of an intervention"""
    user_id: int
    level: InterventionLevel
    timestamp: float
    violation_score: float
    violations: List[Dict[str, Any]]
    intervention_result: Dict[str, Any]
    effectiveness: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'level': self.level.name,
            'timestamp': self.timestamp,
            'violation_score': self.violation_score,
            'violations': self.violations,
            'intervention_result': self.intervention_result,
            'effectiveness': self.effectiveness
        }


class InterventionStrategy(ABC):
    """Abstract base class for intervention strategies"""
    
    @abstractmethod
    def apply(self, decision: Dict[str, Any], 
             violations: List[Dict[str, Any]],
             user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intervention strategy"""
        pass
    
    @abstractmethod
    def get_effectiveness_metrics(self) -> Dict[str, float]:
        """Get effectiveness metrics for this strategy"""
        pass


class SoftNudgeStrategy(InterventionStrategy):
    """Gentle nudge without restricting functionality"""
    
    def __init__(self):
        self.applications = 0
        self.acknowledged = 0
        self.behavior_changed = 0
        
    def apply(self, decision: Dict[str, Any], 
             violations: List[Dict[str, Any]],
             user_context: Dict[str, Any]) -> Dict[str, Any]:
        
        self.applications += 1
        
        # Analyze violations to create contextual message
        primary_violation = max(violations, 
                              key=lambda v: v.get('violation_score', 0))
        constraint_type = primary_violation.get('constraint_type', 'unknown')
        
        # Contextual messages based on violation type and user history
        messages = self._generate_contextual_messages(
            constraint_type, user_context
        )
        
        # Select most appropriate message
        message = self._select_message(messages, user_context)
        
        # Determine display parameters
        display_params = self._calculate_display_params(user_context)
        
        return {
            'intervention_type': InterventionType.INFORMATIONAL,
            'modified_decision': decision,  # No modification
            'message': message,
            'display_type': display_params['type'],
            'duration_seconds': display_params['duration'],
            'position': display_params['position'],
            'style': display_params['style'],
            'actions': ['dismiss', 'learn_more'],
            'tracking_id': f"nudge_{int(time.time())}_{decision.get('user_id', 0)}"
        }
    
    def _generate_contextual_messages(self, constraint_type: str,
                                    user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contextual messages based on violation and user"""
        
        messages = []
        user_history = user_context.get('intervention_history', [])
        
        # Base messages by constraint type
        base_messages = {
            'wellbeing': [
                {
                    'text': "You've been active for a while. Time for a break? 🌟",
                    'tone': 'friendly',
                    'urgency': 'low'
                },
                {
                    'text': "Your digital wellbeing matters. Consider a short pause.",
                    'tone': 'caring',
                    'urgency': 'medium'
                }
            ],
            'privacy': [
                {
                    'text': "This action may share more data than usual. Review settings?",
                    'tone': 'informative',
                    'urgency': 'medium'
                },
                {
                    'text': "Privacy tip: You can control what data is shared.",
                    'tone': 'helpful',
                    'urgency': 'low'
                }
            ],
            'fairness': [
                {
                    'text': "Explore diverse content for a richer experience!",
                    'tone': 'encouraging',
                    'urgency': 'low'
                },
                {
                    'text': "Discover something new? We have varied recommendations.",
                    'tone': 'suggestive',
                    'urgency': 'low'
                }
            ]
        }
        
        # Get relevant messages
        relevant_messages = base_messages.get(constraint_type, [
            {
                'text': "Please review this action for optimal experience.",
                'tone': 'neutral',
                'urgency': 'low'
            }
        ])
        
        # Personalize based on user history
        for msg in relevant_messages:
            personalized = msg.copy()
            
            # Adjust based on previous interventions
            if len(user_history) > 5:
                personalized['urgency'] = 'medium'
                personalized['text'] = "⚠️ " + personalized['text']
            
            messages.append(personalized)
        
        return messages
    
    def _select_message(self, messages: List[Dict[str, Any]],
                       user_context: Dict[str, Any]) -> str:
        """Select most appropriate message"""
        
        # Simple selection based on user preferences
        user_prefs = user_context.get('communication_preferences', {})
        
        if user_prefs.get('prefers_direct', False):
            # Select more direct messages
            urgent_messages = [m for m in messages if m['urgency'] != 'low']
            if urgent_messages:
                return urgent_messages[0]['text']
        
        # Default to first message
        return messages[0]['text'] if messages else "Please review this action."
    
    def _calculate_display_params(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate display parameters based on context"""
        
        device = user_context.get('device', 'desktop')
        
        params = {
            'desktop': {
                'type': 'tooltip',
                'duration': 5,
                'position': 'top-right',
                'style': 'subtle'
            },
            'mobile': {
                'type': 'banner',
                'duration': 3,
                'position': 'bottom',
                'style': 'compact'
            },
            'tv': {
                'type': 'overlay',
                'duration': 7,
                'position': 'center',
                'style': 'large'
            }
        }
        
        return params.get(device, params['desktop'])
    
    def get_effectiveness_metrics(self) -> Dict[str, float]:
        """Get effectiveness metrics"""
        if self.applications == 0:
            return {'effectiveness': 0.0}
        
        return {
            'applications': self.applications,
            'acknowledgment_rate': self.acknowledged / self.applications,
            'behavior_change_rate': self.behavior_changed / self.applications,
            'effectiveness': (self.acknowledged + self.behavior_changed) / (2 * self.applications)
        }


class ExplicitWarningStrategy(InterventionStrategy):
    """Clear warning requiring user acknowledgment"""
    
    def __init__(self):
        self.applications = 0
        self.user_responses = defaultdict(int)
        
    def apply(self, decision: Dict[str, Any], 
             violations: List[Dict[str, Any]],
             user_context: Dict[str, Any]) -> Dict[str, Any]:
        
        self.applications += 1
        
        # Create detailed warning
        warning_content = self._create_warning_content(violations)
        
        # Determine warning severity
        severity = self._calculate_severity(violations)
        
        return {
            'intervention_type': InterventionType.BEHAVIORAL,
            'modified_decision': decision,
            'message': warning_content['message'],
            'detailed_explanation': warning_content['details'],
            'display_type': 'modal',
            'requires_acknowledgment': True,
            'severity': severity,
            'options': [
                {'id': 'proceed', 'text': 'Proceed Anyway', 'style': 'secondary'},
                {'id': 'cancel', 'text': 'Cancel', 'style': 'primary'},
                {'id': 'learn', 'text': 'Learn More', 'style': 'link'}
            ],
            'timeout_seconds': 30,
            'timeout_action': 'cancel'
        }
    
    def _create_warning_content(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive warning content"""
        
        # Group violations by type
        violations_by_type = defaultdict(list)
        for v in violations:
            violations_by_type[v.get('constraint_type', 'unknown')].append(v)
        
        # Create main message
        if len(violations_by_type) > 1:
            message = "⚠️ Multiple Ethical Concerns Detected"
        else:
            constraint_type = list(violations_by_type.keys())[0]
            message = f"⚠️ {constraint_type.title()} Concern Detected"
        
        # Create detailed explanation
        details = []
        for constraint_type, type_violations in violations_by_type.items():
            severity = max(v.get('violation_score', 0) for v in type_violations)
            
            if constraint_type == 'wellbeing':
                details.append(
                    f"• Wellbeing: Extended usage detected ({severity*100:.0f}% threshold)"
                )
            elif constraint_type == 'privacy':
                details.append(
                    f"• Privacy: Sensitive data may be exposed ({severity*100:.0f}% risk)"
                )
            elif constraint_type == 'fairness':
                details.append(
                    f"• Fairness: Potential bias detected ({severity*100:.0f}% disparity)"
                )
            else:
                details.append(
                    f"• {constraint_type.title()}: Violation detected ({severity*100:.0f}%)"
                )
        
        return {
            'message': message,
            'details': "\n".join(details)
        }
    
    def _calculate_severity(self, violations: List[Dict[str, Any]]) -> str:
        """Calculate overall severity level"""
        
        max_score = max(v.get('violation_score', 0) for v in violations)
        
        if max_score > 0.8:
            return 'critical'
        elif max_score > 0.6:
            return 'high'
        elif max_score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def get_effectiveness_metrics(self) -> Dict[str, float]:
        """Get effectiveness metrics"""
        if self.applications == 0:
            return {'effectiveness': 0.0}
        
        total_responses = sum(self.user_responses.values())
        cancel_rate = self.user_responses['cancel'] / max(total_responses, 1)
        learn_rate = self.user_responses['learn'] / max(total_responses, 1)
        
        return {
            'applications': self.applications,
            'response_rate': total_responses / self.applications,
            'cancel_rate': cancel_rate,
            'learn_more_rate': learn_rate,
            'effectiveness': (cancel_rate + learn_rate) / 2
        }


class FeatureLimitationStrategy(InterventionStrategy):
    """Restrict features based on violations"""
    
    def __init__(self):
        self.applications = 0
        self.restrictions_applied = defaultdict(int)
        self.compliance_improvements = 0
        
    def apply(self, decision: Dict[str, Any], 
             violations: List[Dict[str, Any]],
             user_context: Dict[str, Any]) -> Dict[str, Any]:
        
        self.applications += 1
        
        # Determine restrictions based on violations
        restrictions = self._determine_restrictions(violations, user_context)
        
        # Modify decision based on restrictions
        modified_decision = self._apply_restrictions(decision.copy(), restrictions)
        
        # Track restrictions
        for r in restrictions:
            self.restrictions_applied[r['type']] += 1
        
        return {
            'intervention_type': InterventionType.RESTRICTIVE,
            'modified_decision': modified_decision,
            'message': self._create_restriction_message(restrictions),
            'restrictions': restrictions,
            'duration_minutes': self._calculate_duration(violations),
            'appeal_available': True,
            'alternative_actions': self._suggest_alternatives(restrictions)
        }
    
    def _determine_restrictions(self, violations: List[Dict[str, Any]],
                              user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine appropriate restrictions"""
        
        restrictions = []
        
        for violation in violations:
            constraint_type = violation.get('constraint_type', '')
            severity = violation.get('violation_score', 0)
            
            if constraint_type == 'wellbeing':
                if severity > 0.7:
                    restrictions.append({
                        'type': 'usage_limit',
                        'parameter': 'session_duration',
                        'limit': 30,  # 30 minutes
                        'unit': 'minutes'
                    })
                restrictions.append({
                    'type': 'feature_disable',
                    'feature': 'autoplay',
                    'reason': 'wellbeing_protection'
                })
                
            elif constraint_type == 'privacy':
                restrictions.append({
                    'type': 'data_minimization',
                    'scope': 'personal_data',
                    'level': 'anonymous_only'
                })
                if severity > 0.8:
                    restrictions.append({
                        'type': 'feature_disable',
                        'feature': 'data_sharing',
                        'reason': 'privacy_protection'
                    })
                    
            elif constraint_type == 'fairness':
                restrictions.append({
                    'type': 'algorithm_adjustment',
                    'parameter': 'diversity_boost',
                    'value': 2.0
                })
                restrictions.append({
                    'type': 'content_filter',
                    'filter': 'increase_variety',
                    'strength': 'high'
                })
        
        return restrictions
    
    def _apply_restrictions(self, decision: Dict[str, Any],
                          restrictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply restrictions to decision"""
        
        for restriction in restrictions:
            if restriction['type'] == 'usage_limit':
                decision['max_duration'] = restriction['limit']
                
            elif restriction['type'] == 'feature_disable':
                if 'disabled_features' not in decision:
                    decision['disabled_features'] = []
                decision['disabled_features'].append(restriction['feature'])
                
            elif restriction['type'] == 'data_minimization':
                decision['privacy_mode'] = restriction['level']
                
            elif restriction['type'] == 'algorithm_adjustment':
                if 'algorithm_params' not in decision:
                    decision['algorithm_params'] = {}
                decision['algorithm_params'][restriction['parameter']] = restriction['value']
                
            elif restriction['type'] == 'content_filter':
                if 'content_filters' not in decision:
                    decision['content_filters'] = []
                decision['content_filters'].append(restriction['filter'])
        
        decision['restrictions_applied'] = True
        return decision
    
    def _create_restriction_message(self, restrictions: List[Dict[str, Any]]) -> str:
        """Create user-friendly restriction message"""
        
        if not restrictions:
            return "Some features have been adjusted for your protection."
        
        messages = []
        
        feature_restrictions = [r for r in restrictions if r['type'] == 'feature_disable']
        if feature_restrictions:
            features = [r['feature'] for r in feature_restrictions]
            messages.append(f"Disabled: {', '.join(features)}")
        
        usage_limits = [r for r in restrictions if r['type'] == 'usage_limit']
        if usage_limits:
            for limit in usage_limits:
                messages.append(f"Limited to {limit['limit']} {limit['unit']}")
        
        if not messages:
            return "Some features have been adjusted for your protection."
        
        return "Temporary restrictions: " + "; ".join(messages)
    
    def _calculate_duration(self, violations: List[Dict[str, Any]]) -> int:
        """Calculate restriction duration based on violations"""
        
        base_duration = 30  # 30 minutes base
        
        # Increase based on severity
        max_severity = max(v.get('violation_score', 0) for v in violations)
        
        if max_severity > 0.8:
            return base_duration * 4  # 2 hours
        elif max_severity > 0.6:
            return base_duration * 2  # 1 hour
        else:
            return base_duration
    
    def _suggest_alternatives(self, restrictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest alternative actions"""
        
        alternatives = []
        
        if any(r['type'] == 'usage_limit' for r in restrictions):
            alternatives.append({
                'action': 'take_break',
                'description': 'Take a refreshing break',
                'benefit': 'Improve focus and wellbeing'
            })
        
        if any(r['type'] == 'feature_disable' and r['feature'] == 'autoplay' for r in restrictions):
            alternatives.append({
                'action': 'manual_selection',
                'description': 'Browse and choose content manually',
                'benefit': 'More intentional engagement'
            })
        
        if any(r['type'] == 'data_minimization' for r in restrictions):
            alternatives.append({
                'action': 'review_privacy',
                'description': 'Review your privacy settings',
                'benefit': 'Better control over your data'
            })
        
        return alternatives
    
    def get_effectiveness_metrics(self) -> Dict[str, float]:
        """Get effectiveness metrics"""
        if self.applications == 0:
            return {'effectiveness': 0.0}
        
        most_common_restriction = max(self.restrictions_applied.items(),
                                    key=lambda x: x[1])[0] if self.restrictions_applied else 'none'
        
        return {
            'applications': self.applications,
            'total_restrictions': sum(self.restrictions_applied.values()),
            'most_common_restriction': most_common_restriction,
            'compliance_improvement_rate': self.compliance_improvements / self.applications,
            'effectiveness': self.compliance_improvements / self.applications
        }


class TemporarySuspensionStrategy(InterventionStrategy):
    """Temporary suspension of functionality"""
    
    def __init__(self):
        self.applications = 0
        self.appeals_received = 0
        self.appeals_granted = 0
        
    def apply(self, decision: Dict[str, Any], 
             violations: List[Dict[str, Any]],
             user_context: Dict[str, Any]) -> Dict[str, Any]:
        
        self.applications += 1
        
        # Calculate suspension parameters
        suspension_params = self._calculate_suspension(violations, user_context)
        
        return {
            'intervention_type': InterventionType.PUNITIVE,
            'modified_decision': None,  # Block decision
            'message': suspension_params['message'],
            'suspension_type': suspension_params['type'],
            'duration_minutes': suspension_params['duration'],
            'blocked_features': suspension_params['blocked_features'],
            'appeal_available': True,
            'appeal_process': {
                'method': 'automated_review',
                'estimated_time': '5-10 minutes',
                'success_probability': self._estimate_appeal_success(user_context)
            },
            'educational_resources': self._get_educational_resources(violations)
        }
    
    def _calculate_suspension(self, violations: List[Dict[str, Any]],
                            user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate suspension parameters"""
        
        # Base duration on violation severity
        max_severity = max(v.get('violation_score', 0) for v in violations)
        repeat_offenses = len(user_context.get('intervention_history', []))
        
        if max_severity > 0.9 or repeat_offenses > 10:
            duration = 1440  # 24 hours
            suspension_type = 'full'
            message = ("Your account has been temporarily suspended due to "
                      "repeated or severe violations of our ethical guidelines.")
        elif max_severity > 0.8 or repeat_offenses > 5:
            duration = 360  # 6 hours
            suspension_type = 'partial'
            message = ("Some features have been temporarily suspended. "
                      "Please review our community guidelines.")
        else:
            duration = 60  # 1 hour
            suspension_type = 'limited'
            message = ("This action has been blocked. Please try again later "
                      "or contact support.")
        
        # Determine blocked features
        blocked_features = []
        for v in violations:
            if v.get('constraint_type') == 'wellbeing':
                blocked_features.extend(['streaming', 'autoplay', 'recommendations'])
            elif v.get('constraint_type') == 'privacy':
                blocked_features.extend(['data_export', 'sharing', 'third_party_apps'])
            elif v.get('constraint_type') == 'fairness':
                blocked_features.extend(['algorithmic_feed', 'personalization'])
        
        return {
            'duration': duration,
            'type': suspension_type,
            'message': message,
            'blocked_features': list(set(blocked_features))
        }
    
    def _estimate_appeal_success(self, user_context: Dict[str, Any]) -> float:
        """Estimate probability of successful appeal"""
        
        # Factors affecting appeal success
        history_length = len(user_context.get('intervention_history', []))
        time_since_last = time.time() - user_context.get('last_intervention_time', 0)
        user_reputation = user_context.get('reputation_score', 0.5)
        
        # Calculate probability
        base_probability = 0.3
        
        # Positive factors
        if time_since_last > 86400 * 7:  # More than a week
            base_probability += 0.2
        if user_reputation > 0.8:
            base_probability += 0.2
        
        # Negative factors
        if history_length > 5:
            base_probability -= 0.1 * min(history_length / 10, 0.3)
        
        return max(0.1, min(0.9, base_probability))
    
    def _get_educational_resources(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get relevant educational resources"""
        
        resources = []
        constraint_types = set(v.get('constraint_type') for v in violations)
        
        resource_map = {
            'wellbeing': {
                'title': 'Digital Wellbeing Guide',
                'url': '/help/digital-wellbeing',
                'estimated_reading_time': '5 minutes'
            },
            'privacy': {
                'title': 'Privacy Best Practices',
                'url': '/help/privacy-guide',
                'estimated_reading_time': '7 minutes'
            },
            'fairness': {
                'title': 'Understanding Algorithmic Fairness',
                'url': '/help/fairness-explained',
                'estimated_reading_time': '10 minutes'
            }
        }
        
        for constraint_type in constraint_types:
            if constraint_type in resource_map:
                resources.append(resource_map[constraint_type])
        
        return resources
    
    def get_effectiveness_metrics(self) -> Dict[str, float]:
        """Get effectiveness metrics"""
        if self.applications == 0:
            return {'effectiveness': 0.0}
        
        appeal_rate = self.appeals_received / self.applications
        appeal_success_rate = self.appeals_granted / max(self.appeals_received, 1)
        
        # High effectiveness if few appeals or low success rate
        effectiveness = 1 - (appeal_rate * appeal_success_rate)
        
        return {
            'applications': self.applications,
            'appeal_rate': appeal_rate,
            'appeal_success_rate': appeal_success_rate,
            'effectiveness': effectiveness
        }


class HierarchicalInterventionSystem:
    """Complete hierarchical intervention system"""
    
    def __init__(self, config: Optional[InterventionConfig] = None):
        self.config = config or InterventionConfig()
        
        # Initialize strategies
        self.strategies = {
            InterventionLevel.SOFT_NUDGE: SoftNudgeStrategy(),
            InterventionLevel.EXPLICIT_WARNING: ExplicitWarningStrategy(),
            InterventionLevel.FEATURE_LIMITATION: FeatureLimitationStrategy(),
            InterventionLevel.TEMPORARY_SUSPENSION: TemporarySuspensionStrategy()
        }
        
        # State tracking
        self.intervention_history = defaultdict(list)
        self.active_interventions = {}
        self.effectiveness_scores = defaultdict(float)
        
        # Analytics
        self.total_interventions = 0
        self.interventions_by_level = defaultdict(int)
        
    def evaluate_and_intervene(self, decision: Dict[str, Any],
                              violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main entry point for intervention system"""
        
        user_id = decision.get('user_id', 0)
        
        # Calculate violation score
        violation_score = self._calculate_violation_score(violations)
        
        # Get user context
        user_context = self._get_user_context(user_id)
        
        # Determine intervention level
        level = self._determine_intervention_level(
            violation_score, user_context
        )
        
        # Check cooldown
        if self._is_in_cooldown(user_id, level):
            return {
                'intervention_applied': False,
                'reason': 'cooldown_active',
                'cooldown_remaining': self._get_cooldown_remaining(user_id, level)
            }
        
        # Apply intervention
        if level == InterventionLevel.NONE:
            return {
                'intervention_applied': False,
                'reason': 'threshold_not_exceeded'
            }
        
        # Get appropriate strategy
        strategy = self.strategies.get(level)
        if not strategy:
            logger.error(f"No strategy for level {level}")
            return {
                'intervention_applied': False,
                'error': 'strategy_not_found'
            }
        
        # Apply strategy
        result = strategy.apply(decision, violations, user_context)
        
        # Record intervention
        self._record_intervention(user_id, level, violation_score, violations, result)
        
        # Update analytics
        self.total_interventions += 1
        self.interventions_by_level[level] += 1
        
        return {
            'intervention_applied': True,
            'level': level.name,
            'result': result
        }
    
    def _calculate_violation_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate aggregate violation score"""
        
        if not violations:
            return 0.0
        
        # Weighted sum based on severity
        severity_weights = {
            'CRITICAL': 1.0,
            'HIGH': 0.7,
            'MEDIUM': 0.4,
            'LOW': 0.2
        }
        
        total_score = 0.0
        for violation in violations:
            severity = violation.get('severity', 'MEDIUM')
            weight = severity_weights.get(severity, 0.5)
            score = violation.get('violation_score', 0.5)
            
            # Apply constraint-specific multipliers
            constraint_type = violation.get('constraint_type', '')
            if constraint_type == 'consent':
                weight *= 2.0  # Critical
            elif constraint_type == 'wellbeing':
                weight *= 1.5
            
            total_score += weight * score
        
        return min(total_score / len(violations), 1.0)
    
    def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user context"""
        
        # Get intervention history
        user_history = self.intervention_history.get(user_id, [])
        
        # Filter to recent history (within window)
        current_time = time.time()
        recent_history = [
            h for h in user_history
            if current_time - h.timestamp < self.config.intervention_history_window
        ]
        
        # Calculate user metrics
        intervention_count = len(recent_history)
        if recent_history:
            last_intervention_time = max(h.timestamp for h in recent_history)
            avg_violation_score = np.mean([h.violation_score for h in recent_history])
        else:
            last_intervention_time = 0
            avg_violation_score = 0
        
        return {
            'intervention_history': recent_history,
            'intervention_count': intervention_count,
            'last_intervention_time': last_intervention_time,
            'average_violation_score': avg_violation_score,
            'reputation_score': self._calculate_reputation(user_id),
            'device': 'desktop',  # Would come from actual context
            'communication_preferences': {}  # Would come from user settings
        }
    
    def _calculate_reputation(self, user_id: int) -> float:
        """Calculate user reputation score"""
        
        # Simple reputation based on intervention history
        history = self.intervention_history.get(user_id, [])
        
        if not history:
            return 0.7  # Default neutral reputation
        
        # Recent interventions hurt reputation more
        current_time = time.time()
        reputation = 1.0
        
        for record in history:
            age_days = (current_time - record.timestamp) / 86400
            impact = 0.1 * np.exp(-age_days / 30)  # Decay over time
            reputation -= impact
        
        return max(0.0, min(1.0, reputation))
    
    def _determine_intervention_level(self, violation_score: float,
                                    user_context: Dict[str, Any]) -> InterventionLevel:
        """Determine appropriate intervention level"""
        
        # Base level from score
        thresholds = self.config.thresholds
        
        if violation_score < thresholds['soft_nudge']:
            base_level = InterventionLevel.NONE
        elif violation_score < thresholds['explicit_warning']:
            base_level = InterventionLevel.SOFT_NUDGE
        elif violation_score < thresholds['feature_limitation']:
            base_level = InterventionLevel.EXPLICIT_WARNING
        elif violation_score < thresholds['temporary_suspension']:
            base_level = InterventionLevel.FEATURE_LIMITATION
        else:
            base_level = InterventionLevel.TEMPORARY_SUSPENSION
        
        # Escalate based on history
        intervention_count = user_context['intervention_count']
        
        if intervention_count > 20 and base_level.value < 4:
            return InterventionLevel(base_level.value + 2)
        elif intervention_count > 10 and base_level.value < 5:
            return InterventionLevel(base_level.value + 1)
        
        return base_level
    
    def _is_in_cooldown(self, user_id: int, level: InterventionLevel) -> bool:
        """Check if user is in cooldown for level"""
        
        key = f"{user_id}_{level.name}"
        if key not in self.active_interventions:
            return False
        
        intervention = self.active_interventions[key]
        elapsed = time.time() - intervention['timestamp']
        cooldown = self.config.cooldown_periods.get(level.name.lower(), 0)
        
        if elapsed >= cooldown:
            del self.active_interventions[key]
            return False
        
        return True
    
    def _get_cooldown_remaining(self, user_id: int, level: InterventionLevel) -> float:
        """Get remaining cooldown time"""
        
        key = f"{user_id}_{level.name}"
        if key not in self.active_interventions:
            return 0.0
        
        intervention = self.active_interventions[key]
        elapsed = time.time() - intervention['timestamp']
        cooldown = self.config.cooldown_periods.get(level.name.lower(), 0)
        
        return max(0, cooldown - elapsed)
    
    def _record_intervention(self, user_id: int, level: InterventionLevel,
                           violation_score: float, violations: List[Dict[str, Any]],
                           result: Dict[str, Any]):
        """Record intervention for history and active tracking"""
        
        record = InterventionRecord(
            user_id=user_id,
            level=level,
            timestamp=time.time(),
            violation_score=violation_score,
            violations=violations,
            intervention_result=result
        )
        
        # Add to history
        self.intervention_history[user_id].append(record)
        
        # Limit history size
        if len(self.intervention_history[user_id]) > self.config.max_interventions_per_user:
            self.intervention_history[user_id] = self.intervention_history[user_id][-self.config.max_interventions_per_user:]
        
        # Add to active interventions
        key = f"{user_id}_{level.name}"
        self.active_interventions[key] = {
            'timestamp': time.time(),
            'record': record
        }
    
    def update_effectiveness(self, user_id: int, intervention_id: str,
                           outcome: Dict[str, Any]):
        """Update intervention effectiveness based on outcomes"""
        
        # Find the intervention record
        for record in self.intervention_history.get(user_id, []):
            if record.intervention_result.get('tracking_id') == intervention_id:
                # Calculate effectiveness
                if outcome.get('user_complied', False):
                    effectiveness = 1.0
                elif outcome.get('user_acknowledged', False):
                    effectiveness = 0.5
                else:
                    effectiveness = 0.0
                
                record.effectiveness = effectiveness
                
                # Update strategy effectiveness
                level = record.level
                self.effectiveness_scores[level] = (
                    0.9 * self.effectiveness_scores[level] + 0.1 * effectiveness
                )
                break
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        
        # Calculate per-level metrics
        level_metrics = {}
        for level, strategy in self.strategies.items():
            level_metrics[level.name] = strategy.get_effectiveness_metrics()
        
        # User distribution
        users_by_intervention_count = defaultdict(int)
        for user_id, history in self.intervention_history.items():
            count = len(history)
            if count == 0:
                bucket = '0'
            elif count <= 5:
                bucket = '1-5'
            elif count <= 10:
                bucket = '6-10'
            else:
                bucket = '11+'
            users_by_intervention_count[bucket] += 1
        
        # Temporal analysis
        if self.intervention_history:
            all_interventions = []
            for history in self.intervention_history.values():
                all_interventions.extend(history)
            
            if all_interventions:
                timestamps = [r.timestamp for r in all_interventions]
                hourly_distribution = defaultdict(int)
                
                for ts in timestamps:
                    hour = int((ts % 86400) / 3600)
                    hourly_distribution[hour] += 1
        else:
            hourly_distribution = {}
        
        return {
            'total_interventions': self.total_interventions,
            'interventions_by_level': dict(self.interventions_by_level),
            'level_metrics': level_metrics,
            'effectiveness_scores': dict(self.effectiveness_scores),
            'unique_users_affected': len(self.intervention_history),
            'users_by_intervention_count': dict(users_by_intervention_count),
            'hourly_distribution': dict(hourly_distribution),
            'active_interventions': len(self.active_interventions)
        }


def create_intervention_system(config_dict: Optional[Dict[str, Any]] = None) -> HierarchicalInterventionSystem:
    """Factory function to create intervention system"""
    
    if config_dict:
        config = InterventionConfig(**config_dict)
    else:
        config = InterventionConfig()
    
    return HierarchicalInterventionSystem(config)