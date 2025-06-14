"""
ethics_framework/core/constraints.py
====================================
Advanced ethical constraint implementations with formal specifications
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
import time
from scipy import stats
from scipy.optimize import minimize_scalar
import logging

logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Enumeration of ethical constraint types"""
    FAIRNESS = "fairness"
    PRIVACY = "privacy"
    TRANSPARENCY = "transparency"
    CONSENT = "consent"
    WELLBEING = "wellbeing"


class ViolationSeverity(Enum):
    """Severity levels for constraint violations"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ConstraintViolation:
    """Detailed information about a constraint violation"""
    constraint_name: str
    constraint_type: ConstraintType
    severity: ViolationSeverity
    violation_score: float
    affected_users: List[int]
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'constraint_name': self.constraint_name,
            'constraint_type': self.constraint_type.value,
            'severity': self.severity.value,
            'violation_score': self.violation_score,
            'affected_users': self.affected_users,
            'timestamp': self.timestamp,
            'details': self.details
        }


class EthicalConstraint(ABC):
    """Abstract base class for all ethical constraints"""
    
    def __init__(self, name: str, constraint_type: ConstraintType, 
                 threshold: float, weight: float = 1.0):
        self.name = name
        self.constraint_type = constraint_type
        self.threshold = threshold
        self.weight = weight
        self.violation_history = []
        self.satisfaction_rate = 1.0
        self._computation_cache = {}
        
    @abstractmethod
    def validate(self, decision: Dict, context: Dict) -> Tuple[bool, float, Optional[ConstraintViolation]]:
        """
        Validate a decision against this constraint
        Returns: (satisfied, computation_time_ms, violation_details)
        """
        pass
    
    @abstractmethod
    def compute_violation_score(self, decision: Dict, context: Dict) -> float:
        """Compute numerical violation score [0, 1]"""
        pass
    
    def update_statistics(self, satisfied: bool, violation: Optional[ConstraintViolation]):
        """Update constraint statistics"""
        if violation:
            self.violation_history.append(violation)
        
        # Update rolling satisfaction rate
        alpha = 0.99  # Exponential moving average factor
        self.satisfaction_rate = alpha * self.satisfaction_rate + (1 - alpha) * (1 if satisfied else 0)


class FairnessConstraint(EthicalConstraint):
    """
    Advanced fairness constraint with multiple fairness metrics
    Supports: demographic parity, equalized odds, calibration
    """
    
    def __init__(self, name: str, protected_attribute: str, 
                 fairness_metric: str = "demographic_parity",
                 threshold: float = 0.1, weight: float = 1.0):
        super().__init__(name, ConstraintType.FAIRNESS, threshold, weight)
        self.protected_attribute = protected_attribute
        self.fairness_metric = fairness_metric
        self.group_statistics = {}
        
    def validate(self, decision: Dict, context: Dict) -> Tuple[bool, float, Optional[ConstraintViolation]]:
        start_time = time.perf_counter()
        
        # Simulate complex fairness computation
        np.random.seed(hash(str(decision)) % 1000)
        
        # Matrix operations for fairness analysis
        size = 20  # Increased for more realistic computation
        feature_matrix = np.random.randn(size, size).astype(np.float32)
        
        if self.fairness_metric == "demographic_parity":
            # Compute demographic parity gap
            group_probs = self._compute_demographic_parity(feature_matrix, decision)
            violation_score = np.abs(group_probs[0] - group_probs[1])
            
        elif self.fairness_metric == "equalized_odds":
            # Compute equalized odds difference
            tpr_gap, fpr_gap = self._compute_equalized_odds(feature_matrix, decision)
            violation_score = max(tpr_gap, fpr_gap)
            
        elif self.fairness_metric == "calibration":
            # Compute calibration difference
            violation_score = self._compute_calibration_gap(feature_matrix, decision)
        else:
            violation_score = 0.0
        
        satisfied = violation_score < self.threshold
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        violation = None
        if not satisfied:
            severity = self._compute_severity(violation_score)
            violation = ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                severity=severity,
                violation_score=violation_score,
                affected_users=decision.get('affected_users', [decision['user_id']]),
                timestamp=time.time(),
                details={
                    'protected_attribute': self.protected_attribute,
                    'fairness_metric': self.fairness_metric,
                    'group_statistics': self.group_statistics
                }
            )
        
        self.update_statistics(satisfied, violation)
        return satisfied, elapsed_ms, violation
    
    def _compute_demographic_parity(self, features: np.ndarray, decision: Dict) -> Tuple[float, float]:
        """Compute demographic parity between groups"""
        # Simulate group probability computation
        A = features @ features.T
        probs = 1 / (1 + np.exp(-np.diagonal(A) * 0.1))
        
        # Split into two groups based on protected attribute
        group_0_prob = np.mean(probs[:len(probs)//2])
        group_1_prob = np.mean(probs[len(probs)//2:])
        
        self.group_statistics['group_0_prob'] = float(group_0_prob)
        self.group_statistics['group_1_prob'] = float(group_1_prob)
        
        return (group_0_prob, group_1_prob)
    
    def _compute_equalized_odds(self, features: np.ndarray, decision: Dict) -> Tuple[float, float]:
        """Compute equalized odds metrics"""
        # Simulate TPR and FPR computation
        predictions = features @ np.random.randn(features.shape[1])
        labels = (np.random.randn(features.shape[0]) > 0).astype(int)
        
        # Compute confusion matrix elements
        tp_0 = np.sum((predictions[:len(predictions)//2] > 0) & (labels[:len(labels)//2] == 1))
        fn_0 = np.sum((predictions[:len(predictions)//2] <= 0) & (labels[:len(labels)//2] == 1))
        fp_0 = np.sum((predictions[:len(predictions)//2] > 0) & (labels[:len(labels)//2] == 0))
        tn_0 = np.sum((predictions[:len(predictions)//2] <= 0) & (labels[:len(labels)//2] == 0))
        
        tp_1 = np.sum((predictions[len(predictions)//2:] > 0) & (labels[len(labels)//2:] == 1))
        fn_1 = np.sum((predictions[len(predictions)//2:] <= 0) & (labels[len(labels)//2:] == 1))
        fp_1 = np.sum((predictions[len(predictions)//2:] > 0) & (labels[len(labels)//2:] == 0))
        tn_1 = np.sum((predictions[len(predictions)//2:] <= 0) & (labels[len(labels)//2:] == 0))
        
        tpr_0 = tp_0 / (tp_0 + fn_0 + 1e-10)
        tpr_1 = tp_1 / (tp_1 + fn_1 + 1e-10)
        fpr_0 = fp_0 / (fp_0 + tn_0 + 1e-10)
        fpr_1 = fp_1 / (fp_1 + tn_1 + 1e-10)
        
        return (abs(tpr_0 - tpr_1), abs(fpr_0 - fpr_1))
    
    def _compute_calibration_gap(self, features: np.ndarray, decision: Dict) -> float:
        """Compute calibration gap between groups"""
        # Simulate calibration computation
        scores = 1 / (1 + np.exp(-features @ np.random.randn(features.shape[1])))
        
        # Bin scores and compute calibration
        n_bins = 5
        bin_edges = np.linspace(0, 1, n_bins + 1)
        
        calibration_gap = 0.0
        for i in range(n_bins):
            mask = (scores >= bin_edges[i]) & (scores < bin_edges[i+1])
            if np.sum(mask) > 0:
                expected = np.mean(scores[mask])
                actual = np.random.beta(2, 2)  # Simulated actual positive rate
                calibration_gap += abs(expected - actual) * np.sum(mask) / len(scores)
        
        return calibration_gap
    
    def _compute_severity(self, violation_score: float) -> ViolationSeverity:
        """Compute violation severity based on score"""
        if violation_score < self.threshold * 2:
            return ViolationSeverity.LOW
        elif violation_score < self.threshold * 5:
            return ViolationSeverity.MEDIUM
        elif violation_score < self.threshold * 10:
            return ViolationSeverity.HIGH
        else:
            return ViolationSeverity.CRITICAL
    
    def compute_violation_score(self, decision: Dict, context: Dict) -> float:
        """Compute numerical violation score"""
        _, _, violation = self.validate(decision, context)
        return violation.violation_score if violation else 0.0


class PrivacyConstraint(EthicalConstraint):
    """
    Advanced privacy constraint with differential privacy
    Implements adaptive privacy budget management
    """
    
    def __init__(self, name: str, epsilon: float = 1.0, delta: float = 1e-5,
                 mechanism: str = "laplace", weight: float = 1.0):
        super().__init__(name, ConstraintType.PRIVACY, epsilon, weight)
        self.epsilon = epsilon
        self.delta = delta
        self.mechanism = mechanism
        self.privacy_budget_consumed = 0.0
        self.privacy_losses = []
        
    def validate(self, decision: Dict, context: Dict) -> Tuple[bool, float, Optional[ConstraintViolation]]:
        start_time = time.perf_counter()
        
        # Simulate privacy mechanism computation
        np.random.seed(hash(str(decision)) % 1000)
        
        # Matrix operations for privacy analysis
        size = 18
        data_matrix = np.random.randn(size, size).astype(np.float32)
        
        # Compute privacy loss
        if self.mechanism == "laplace":
            privacy_loss = self._compute_laplace_privacy_loss(data_matrix, decision)
        elif self.mechanism == "gaussian":
            privacy_loss = self._compute_gaussian_privacy_loss(data_matrix, decision)
        else:
            privacy_loss = self._compute_exponential_privacy_loss(data_matrix, decision)
        
        # Check if within budget
        self.privacy_budget_consumed += privacy_loss
        self.privacy_losses.append(privacy_loss)
        
        satisfied = self.privacy_budget_consumed < self.epsilon
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        violation = None
        if not satisfied:
            violation = ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                severity=ViolationSeverity.HIGH,
                violation_score=self.privacy_budget_consumed / self.epsilon,
                affected_users=[decision['user_id']],
                timestamp=time.time(),
                details={
                    'mechanism': self.mechanism,
                    'budget_consumed': self.privacy_budget_consumed,
                    'epsilon': self.epsilon,
                    'delta': self.delta
                }
            )
        
        self.update_statistics(satisfied, violation)
        return satisfied, elapsed_ms, violation
    
    def _compute_laplace_privacy_loss(self, data: np.ndarray, decision: Dict) -> float:
        """Compute privacy loss for Laplace mechanism"""
        sensitivity = np.max(np.abs(data))
        query_result = np.sum(data) / data.size
        
        # Add Laplace noise
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        
        # Compute actual privacy loss
        actual_loss = np.abs(query_result / (query_result + noise + 1e-10))
        return min(actual_loss * 0.1, self.epsilon * 0.1)  # Scale down for simulation
    
    def _compute_gaussian_privacy_loss(self, data: np.ndarray, decision: Dict) -> float:
        """Compute privacy loss for Gaussian mechanism"""
        sensitivity = np.max(np.abs(data))
        
        # Compute noise scale for (ε,δ)-DP
        c = np.sqrt(2 * np.log(1.25 / self.delta))
        sigma = c * sensitivity / self.epsilon
        
        # Add Gaussian noise
        noise = np.random.normal(0, sigma)
        query_result = np.sum(data) / data.size
        
        # Compute privacy loss using advanced composition
        actual_loss = (query_result**2) / (2 * sigma**2)
        return min(actual_loss * 0.1, self.epsilon * 0.1)
    
    def _compute_exponential_privacy_loss(self, data: np.ndarray, decision: Dict) -> float:
        """Compute privacy loss for exponential mechanism"""
        # Simulate utility scores
        utilities = data @ np.random.randn(data.shape[1])
        
        # Apply exponential mechanism
        probabilities = np.exp(self.epsilon * utilities / (2 * np.max(np.abs(utilities))))
        probabilities /= np.sum(probabilities)
        
        # Compute privacy loss based on selection
        selected = np.random.choice(len(probabilities), p=probabilities)
        privacy_loss = -np.log(probabilities[selected] + 1e-10) / len(probabilities)
        
        return min(privacy_loss * 0.01, self.epsilon * 0.1)
    
    def compute_violation_score(self, decision: Dict, context: Dict) -> float:
        """Compute privacy violation score"""
        return min(self.privacy_budget_consumed / self.epsilon, 1.0)


class TransparencyConstraint(EthicalConstraint):
    """
    Transparency constraint with multi-level explanations
    Supports: feature importance, counterfactual, concept-based
    """
    
    def __init__(self, name: str, explanation_type: str = "feature_importance",
                 min_clarity_score: float = 0.8, weight: float = 1.0):
        super().__init__(name, ConstraintType.TRANSPARENCY, min_clarity_score, weight)
        self.explanation_type = explanation_type
        self.explanation_cache = {}
        
    def validate(self, decision: Dict, context: Dict) -> Tuple[bool, float, Optional[ConstraintViolation]]:
        start_time = time.perf_counter()
        
        # Generate explanation
        np.random.seed(hash(str(decision)) % 1000)
        
        size = 16
        model_internals = np.random.randn(size, size).astype(np.float32)
        
        if self.explanation_type == "feature_importance":
            clarity_score = self._compute_feature_importance(model_internals, decision)
        elif self.explanation_type == "counterfactual":
            clarity_score = self._compute_counterfactual(model_internals, decision)
        elif self.explanation_type == "concept":
            clarity_score = self._compute_concept_explanation(model_internals, decision)
        else:
            clarity_score = 0.5
        
        satisfied = clarity_score >= self.threshold
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        violation = None
        if not satisfied:
            violation = ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                severity=ViolationSeverity.MEDIUM,
                violation_score=1.0 - clarity_score,
                affected_users=[decision['user_id']],
                timestamp=time.time(),
                details={
                    'explanation_type': self.explanation_type,
                    'clarity_score': clarity_score,
                    'required_score': self.threshold
                }
            )
        
        self.update_statistics(satisfied, violation)
        return satisfied, elapsed_ms, violation
    
    def _compute_feature_importance(self, internals: np.ndarray, decision: Dict) -> float:
        """Compute feature importance scores"""
        # SHAP-like computation
        baseline = np.mean(internals, axis=0)
        contributions = internals - baseline
        
        # Compute importance scores
        importance = np.abs(contributions).mean(axis=0)
        importance /= importance.sum()
        
        # Clarity based on concentration of importance
        entropy = -np.sum(importance * np.log(importance + 1e-10))
        max_entropy = np.log(len(importance))
        clarity = 1.0 - (entropy / max_entropy)
        
        return clarity
    
    def _compute_counterfactual(self, internals: np.ndarray, decision: Dict) -> float:
        """Generate counterfactual explanations"""
        # Find minimal change for different outcome
        current_output = internals @ np.random.randn(internals.shape[1])
        current_class = (current_output > 0).astype(int)
        
        # Optimization to find counterfactual
        def distance_func(x):
            modified = internals + x.reshape(internals.shape)
            new_output = modified @ np.random.randn(internals.shape[1])
            new_class = (new_output > 0).astype(int)
            
            if np.array_equal(new_class, current_class):
                return np.inf
            return np.linalg.norm(x)
        
        # Simulate optimization result
        min_distance = np.random.exponential(scale=2.0)
        clarity = np.exp(-min_distance / 10.0)  # Closer counterfactuals = clearer
        
        return clarity
    
    def _compute_concept_explanation(self, internals: np.ndarray, decision: Dict) -> float:
        """Generate concept-based explanations"""
        # Extract high-level concepts
        U, S, Vt = np.linalg.svd(internals, full_matrices=False)
        
        # Concept activation scores
        n_concepts = 5
        concept_scores = S[:n_concepts] / S.sum()
        
        # Clarity based on concept coherence
        coherence = np.sum(concept_scores**2)  # Higher concentration = clearer
        
        return min(coherence * 2, 1.0)
    
    def compute_violation_score(self, decision: Dict, context: Dict) -> float:
        """Compute transparency violation score"""
        _, _, violation = self.validate(decision, context)
        return violation.violation_score if violation else 0.0


class ConsentConstraint(EthicalConstraint):
    """
    Consent management with granular permissions
    """
    
    def __init__(self, name: str, consent_types: List[str], 
                 enforcement_mode: str = "strict", weight: float = 1.0):
        super().__init__(name, ConstraintType.CONSENT, 1.0, weight)
        self.consent_types = consent_types
        self.enforcement_mode = enforcement_mode
        self.consent_database = {}
        
    def validate(self, decision: Dict, context: Dict) -> Tuple[bool, float, Optional[ConstraintViolation]]:
        start_time = time.perf_counter()
        
        user_id = decision['user_id']
        required_consents = self._determine_required_consents(decision, context)
        
        # Simulate consent checking with matrix operations
        np.random.seed(hash(str(decision)) % 1000)
        size = 12
        consent_matrix = np.random.rand(size, size)
        
        # Check each required consent
        missing_consents = []
        for consent_type in required_consents:
            # Simulate database lookup
            lookup_result = consent_matrix[hash(consent_type) % size, hash(user_id) % size]
            has_consent = lookup_result > 0.02  # 98% have consent
            
            if not has_consent:
                missing_consents.append(consent_type)
        
        satisfied = len(missing_consents) == 0
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        violation = None
        if not satisfied:
            severity = ViolationSeverity.CRITICAL if self.enforcement_mode == "strict" else ViolationSeverity.HIGH
            violation = ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                severity=severity,
                violation_score=len(missing_consents) / len(required_consents),
                affected_users=[user_id],
                timestamp=time.time(),
                details={
                    'missing_consents': missing_consents,
                    'required_consents': required_consents,
                    'enforcement_mode': self.enforcement_mode
                }
            )
        
        self.update_statistics(satisfied, violation)
        return satisfied, elapsed_ms, violation
    
    def _determine_required_consents(self, decision: Dict, context: Dict) -> List[str]:
        """Determine which consents are required for this decision"""
        required = []
        
        # Basic data processing consent
        required.append("data_processing")
        
        # Context-specific consents
        if context.get("uses_personal_data", True):
            required.append("personal_data_usage")
        
        if context.get("shares_with_third_party", False):
            required.append("third_party_sharing")
        
        if decision.get("algorithm", "") == "recommendation":
            required.append("algorithmic_profiling")
        
        return required
    
    def compute_violation_score(self, decision: Dict, context: Dict) -> float:
        """Compute consent violation score"""
        _, _, violation = self.validate(decision, context)
        return violation.violation_score if violation else 0.0


class WellbeingConstraint(EthicalConstraint):
    """
    Well-being constraint to prevent harmful patterns
    Monitors: engagement time, content diversity, break patterns
    """
    
    def __init__(self, name: str, metric: str = "engagement_time",
                 max_threshold: float = 120.0, weight: float = 1.0):
        super().__init__(name, ConstraintType.WELLBEING, max_threshold, weight)
        self.metric = metric
        self.user_history = {}
        self.intervention_thresholds = {
            'low': max_threshold * 0.7,
            'medium': max_threshold * 0.85,
            'high': max_threshold
        }
        
    def validate(self, decision: Dict, context: Dict) -> Tuple[bool, float, Optional[ConstraintViolation]]:
        start_time = time.perf_counter()
        
        user_id = decision['user_id']
        
        # Simulate wellbeing analysis
        np.random.seed(hash(str(decision)) % 1000)
        size = 14
        behavior_matrix = np.random.randn(size, size).astype(np.float32)
        
        if self.metric == "engagement_time":
            wellbeing_score = self._analyze_engagement_time(behavior_matrix, user_id)
        elif self.metric == "content_diversity":
            wellbeing_score = self._analyze_content_diversity(behavior_matrix, user_id)
        elif self.metric == "break_patterns":
            wellbeing_score = self._analyze_break_patterns(behavior_matrix, user_id)
        else:
            wellbeing_score = 0.5
        
        # Higher score = more concerning
        satisfied = wellbeing_score < self.threshold
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        violation = None
        if not satisfied:
            severity = self._determine_wellbeing_severity(wellbeing_score)
            violation = ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                severity=severity,
                violation_score=wellbeing_score / self.threshold,
                affected_users=[user_id],
                timestamp=time.time(),
                details={
                    'metric': self.metric,
                    'score': wellbeing_score,
                    'threshold': self.threshold,
                    'recommended_action': self._get_intervention_recommendation(wellbeing_score)
                }
            )
        
        self.update_statistics(satisfied, violation)
        return satisfied, elapsed_ms, violation
    
    def _analyze_engagement_time(self, behavior: np.ndarray, user_id: int) -> float:
        """Analyze user engagement time patterns"""
        # Simulate time series analysis
        time_series = np.abs(behavior @ np.random.randn(behavior.shape[1]))
        
        # Compute engagement metrics
        total_time = np.sum(time_series)
        variance = np.var(time_series)
        trend = np.polyfit(range(len(time_series)), time_series, 1)[0]
        
        # Combine into wellbeing score
        score = (total_time / 100) + (trend * 10) + (1 / (variance + 1))
        return min(score, 200.0)  # Cap at 200
    
    def _analyze_content_diversity(self, behavior: np.ndarray, user_id: int) -> float:
        """Analyze diversity of consumed content"""
        # Simulate content embedding clusters
        embeddings = behavior @ behavior.T
        
        # Compute diversity metrics
        U, S, _ = np.linalg.svd(embeddings)
        
        # Effective rank as diversity measure
        normalized_singular_values = S / S.sum()
        entropy = -np.sum(normalized_singular_values * np.log(normalized_singular_values + 1e-10))
        
        # Low entropy = low diversity = high concern
        max_entropy = np.log(len(S))
        diversity_score = 1.0 - (entropy / max_entropy)
        
        return diversity_score * 150  # Scale to threshold range
    
    def _analyze_break_patterns(self, behavior: np.ndarray, user_id: int) -> float:
        """Analyze user break-taking patterns"""
        # Simulate session data
        session_lengths = np.abs(np.diagonal(behavior))
        break_lengths = np.abs(np.diagonal(behavior[::-1]))
        
        # Compute break pattern metrics
        avg_session = np.mean(session_lengths)
        avg_break = np.mean(break_lengths)
        break_ratio = avg_break / (avg_session + avg_break + 1e-10)
        
        # Low break ratio = concerning
        concern_score = (1.0 - break_ratio) * 150
        
        return concern_score
    
    def _determine_wellbeing_severity(self, score: float) -> ViolationSeverity:
        """Determine severity based on wellbeing score"""
        if score < self.intervention_thresholds['low']:
            return ViolationSeverity.NONE
        elif score < self.intervention_thresholds['medium']:
            return ViolationSeverity.LOW
        elif score < self.intervention_thresholds['high']:
            return ViolationSeverity.MEDIUM
        else:
            return ViolationSeverity.HIGH
    
    def _get_intervention_recommendation(self, score: float) -> str:
        """Get recommended intervention based on score"""
        if score < self.intervention_thresholds['low']:
            return "No intervention needed"
        elif score < self.intervention_thresholds['medium']:
            return "Suggest break reminder"
        elif score < self.intervention_thresholds['high']:
            return "Display wellness tips"
        else:
            return "Implement cooling-off period"
    
    def compute_violation_score(self, decision: Dict, context: Dict) -> float:
        """Compute wellbeing violation score"""
        _, _, violation = self.validate(decision, context)
        return violation.violation_score if violation else 0.0


class ConstraintComposer:
    """
    Manages composition and conflict resolution of multiple constraints
    """
    
    def __init__(self, constraints: List[EthicalConstraint], 
                 composition_mode: str = "intersection"):
        self.constraints = constraints
        self.composition_mode = composition_mode
        self.conflict_history = []
        
    def validate_all(self, decision: Dict, context: Dict) -> Dict[str, Any]:
        """Validate decision against all constraints"""
        results = {
            'overall_satisfied': True,
            'total_computation_time_ms': 0.0,
            'individual_results': {},
            'violations': [],
            'conflict_detected': False
        }
        
        for constraint in self.constraints:
            satisfied, time_ms, violation = constraint.validate(decision, context)
            
            results['individual_results'][constraint.name] = {
                'satisfied': satisfied,
                'computation_time_ms': time_ms,
                'violation': violation.to_dict() if violation else None
            }
            
            results['total_computation_time_ms'] += time_ms
            
            if not satisfied:
                results['violations'].append(violation)
                if self.composition_mode == "intersection":
                    results['overall_satisfied'] = False
        
        # Check for conflicts
        conflicts = self._detect_conflicts(results['violations'])
        if conflicts:
            results['conflict_detected'] = True
            results['conflicts'] = conflicts
            self.conflict_history.extend(conflicts)
        
        return results
    
    def _detect_conflicts(self, violations: List[ConstraintViolation]) -> List[Dict]:
        """Detect conflicts between constraint violations"""
        conflicts = []
        
        for i, v1 in enumerate(violations):
            for v2 in violations[i+1:]:
                # Check for conflicting requirements
                if self._are_conflicting(v1, v2):
                    conflicts.append({
                        'constraint_1': v1.constraint_name,
                        'constraint_2': v2.constraint_name,
                        'conflict_type': self._get_conflict_type(v1, v2),
                        'resolution_strategy': self._suggest_resolution(v1, v2)
                    })
        
        return conflicts
    
    def _are_conflicting(self, v1: ConstraintViolation, v2: ConstraintViolation) -> bool:
        """Check if two violations represent conflicting requirements"""
        # Privacy vs Transparency conflict
        if (v1.constraint_type == ConstraintType.PRIVACY and 
            v2.constraint_type == ConstraintType.TRANSPARENCY):
            return True
        
        # Fairness vs Privacy conflict (group statistics vs individual privacy)
        if (v1.constraint_type == ConstraintType.FAIRNESS and
            v2.constraint_type == ConstraintType.PRIVACY):
            return v1.details.get('fairness_metric') == 'demographic_parity'
        
        return False
    
    def _get_conflict_type(self, v1: ConstraintViolation, v2: ConstraintViolation) -> str:
        """Determine the type of conflict"""
        types = {v1.constraint_type, v2.constraint_type}
        
        if types == {ConstraintType.PRIVACY, ConstraintType.TRANSPARENCY}:
            return "privacy_transparency_tradeoff"
        elif types == {ConstraintType.FAIRNESS, ConstraintType.PRIVACY}:
            return "fairness_privacy_tradeoff"
        else:
            return "general_conflict"
    
    def _suggest_resolution(self, v1: ConstraintViolation, v2: ConstraintViolation) -> str:
        """Suggest resolution strategy for conflicts"""
        conflict_type = self._get_conflict_type(v1, v2)
        
        if conflict_type == "privacy_transparency_tradeoff":
            return "Use privacy-preserving explanations (e.g., differentially private SHAP)"
        elif conflict_type == "fairness_privacy_tradeoff":
            return "Apply fairness constraints at aggregate level with privacy guarantees"
        else:
            return "Prioritize based on severity and stakeholder preferences"


# Factory function for creating constraints
def create_constraint(constraint_config: Dict) -> EthicalConstraint:
    """Factory function to create constraints from configuration"""
    constraint_type = constraint_config['type']
    
    if constraint_type == 'fairness':
        return FairnessConstraint(
            name=constraint_config['name'],
            protected_attribute=constraint_config.get('protected_attribute', 'demographic'),
            fairness_metric=constraint_config.get('fairness_metric', 'demographic_parity'),
            threshold=constraint_config.get('threshold', 0.1),
            weight=constraint_config.get('weight', 1.0)
        )
    elif constraint_type == 'privacy':
        return PrivacyConstraint(
            name=constraint_config['name'],
            epsilon=constraint_config.get('epsilon', 1.0),
            delta=constraint_config.get('delta', 1e-5),
            mechanism=constraint_config.get('mechanism', 'laplace'),
            weight=constraint_config.get('weight', 1.0)
        )
    elif constraint_type == 'transparency':
        return TransparencyConstraint(
            name=constraint_config['name'],
            explanation_type=constraint_config.get('explanation_type', 'feature_importance'),
            min_clarity_score=constraint_config.get('min_clarity_score', 0.8),
            weight=constraint_config.get('weight', 1.0)
        )
    elif constraint_type == 'consent':
        return ConsentConstraint(
            name=constraint_config['name'],
            consent_types=constraint_config.get('consent_types', ['data_processing']),
            enforcement_mode=constraint_config.get('enforcement_mode', 'strict'),
            weight=constraint_config.get('weight', 1.0)
        )
    elif constraint_type == 'wellbeing':
        return WellbeingConstraint(
            name=constraint_config['name'],
            metric=constraint_config.get('metric', 'engagement_time'),
            max_threshold=constraint_config.get('max_threshold', 120.0),
            weight=constraint_config.get('weight', 1.0)
        )
    else:
        raise ValueError(f"Unknown constraint type: {constraint_type}")