"""
ethics_framework/algorithms/constraint_composition.py
=====================================================
Advanced algorithms for composing ethical constraints
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
from itertools import combinations, product
import networkx as nx
from scipy.optimize import linprog
import logging

from ..core.constraints import EthicalConstraint, ConstraintType

logger = logging.getLogger(__name__)


@dataclass
class CompositionRule:
    """Rule for composing two constraints"""
    constraint_types: Tuple[ConstraintType, ConstraintType]
    composition_type: str  # 'intersection', 'union', 'priority', 'weighted'
    parameters: Dict[str, Any]
    
    def applies_to(self, c1: ConstraintType, c2: ConstraintType) -> bool:
        """Check if rule applies to given constraint types"""
        return (c1, c2) == self.constraint_types or (c2, c1) == self.constraint_types


class ConstraintGraph:
    """
    Graph representation of constraint relationships
    Nodes: Constraints
    Edges: Relationships (conflict, complement, neutral)
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.constraint_map = {}
        
    def add_constraint(self, constraint: EthicalConstraint):
        """Add constraint as node"""
        self.graph.add_node(constraint.name, 
                          constraint=constraint,
                          type=constraint.constraint_type)
        self.constraint_map[constraint.name] = constraint
        
    def add_relationship(self, c1_name: str, c2_name: str, 
                        relationship: str, strength: float = 1.0):
        """Add relationship between constraints"""
        self.graph.add_edge(c1_name, c2_name, 
                          relationship=relationship,
                          strength=strength)
        
    def find_conflicts(self) -> List[Tuple[str, str]]:
        """Find all conflicting constraint pairs"""
        conflicts = []
        for u, v, data in self.graph.edges(data=True):
            if data.get('relationship') == 'conflict':
                conflicts.append((u, v))
        return conflicts
    
    def find_complements(self) -> List[Tuple[str, str]]:
        """Find complementary constraint pairs"""
        complements = []
        for u, v, data in self.graph.edges(data=True):
            if data.get('relationship') == 'complement':
                complements.append((u, v))
        return complements
    
    def get_constraint_clusters(self) -> List[Set[str]]:
        """Find clusters of related constraints"""
        # Convert to undirected for clustering
        undirected = self.graph.to_undirected()
        
        # Find connected components
        clusters = []
        for component in nx.connected_components(undirected):
            clusters.append(component)
            
        return clusters
    
    def compute_compatibility_score(self, constraint_set: Set[str]) -> float:
        """Compute compatibility score for a set of constraints"""
        if len(constraint_set) <= 1:
            return 1.0
        
        score = 1.0
        
        # Check all pairs
        for c1, c2 in combinations(constraint_set, 2):
            if self.graph.has_edge(c1, c2):
                edge_data = self.graph[c1][c2]
                relationship = edge_data.get('relationship')
                strength = edge_data.get('strength', 1.0)
                
                if relationship == 'conflict':
                    score *= (1 - strength)
                elif relationship == 'complement':
                    score *= (1 + strength * 0.5)
                    
        return max(0, min(1, score))


class OptimalCompositionFinder:
    """
    Find optimal composition of constraints using optimization
    """
    
    def __init__(self, constraints: List[EthicalConstraint]):
        self.constraints = constraints
        self.n_constraints = len(constraints)
        
        # Build constraint graph
        self.graph = ConstraintGraph()
        for c in constraints:
            self.graph.add_constraint(c)
            
        # Detect relationships
        self._detect_relationships()
        
    def _detect_relationships(self):
        """Automatically detect relationships between constraints"""
        
        # Known conflicts
        known_conflicts = [
            (ConstraintType.PRIVACY, ConstraintType.TRANSPARENCY),
            (ConstraintType.FAIRNESS, ConstraintType.PRIVACY),
        ]
        
        # Known complements
        known_complements = [
            (ConstraintType.CONSENT, ConstraintType.PRIVACY),
            (ConstraintType.FAIRNESS, ConstraintType.TRANSPARENCY),
        ]
        
        # Add relationships based on constraint types
        for i, c1 in enumerate(self.constraints):
            for j, c2 in enumerate(self.constraints[i+1:], i+1):
                # Check for conflicts
                for conf_pair in known_conflicts:
                    if (c1.constraint_type == conf_pair[0] and 
                        c2.constraint_type == conf_pair[1]) or \
                       (c1.constraint_type == conf_pair[1] and 
                        c2.constraint_type == conf_pair[0]):
                        self.graph.add_relationship(
                            c1.name, c2.name, 'conflict', 0.7
                        )
                        
                # Check for complements
                for comp_pair in known_complements:
                    if (c1.constraint_type == comp_pair[0] and 
                        c2.constraint_type == comp_pair[1]) or \
                       (c1.constraint_type == comp_pair[1] and 
                        c2.constraint_type == comp_pair[0]):
                        self.graph.add_relationship(
                            c1.name, c2.name, 'complement', 0.5
                        )
    
    def find_optimal_subset(self, min_coverage: float = 0.8,
                          max_conflicts: int = 1) -> Dict[str, Any]:
        """
        Find optimal subset of constraints that:
        - Maximizes coverage of ethical dimensions
        - Minimizes conflicts
        - Respects computational budget
        """
        
        # Binary variables for each constraint (include/exclude)
        # Objective: maximize weighted sum of included constraints
        # while minimizing conflicts
        
        # Constraint weights (importance)
        weights = np.array([c.weight for c in self.constraints])
        
        # Conflict matrix
        conflict_matrix = self._build_conflict_matrix()
        
        # Coverage matrix (which ethical dimensions each constraint covers)
        coverage_matrix = self._build_coverage_matrix()
        
        # Formulate as integer linear program
        # Variables: x_i (binary) for each constraint
        # Maximize: sum(w_i * x_i) - lambda * sum(conflict_ij * x_i * x_j)
        
        # Since we can't directly handle quadratic terms in linprog,
        # we'll use a greedy approximation
        
        best_subset = None
        best_score = -float('inf')
        
        # Try different subset sizes
        for size in range(1, self.n_constraints + 1):
            # Generate all combinations of given size
            for subset_indices in combinations(range(self.n_constraints), size):
                subset = set(subset_indices)
                
                # Check constraints
                if not self._check_subset_constraints(subset, min_coverage, max_conflicts):
                    continue
                
                # Compute score
                score = self._compute_subset_score(subset, weights, conflict_matrix)
                
                if score > best_score:
                    best_score = score
                    best_subset = subset
        
        if best_subset is None:
            # Fallback: include all constraints
            best_subset = set(range(self.n_constraints))
        
        # Convert to result format
        selected_constraints = [self.constraints[i] for i in best_subset]
        
        return {
            'selected_constraints': selected_constraints,
            'indices': list(best_subset),
            'score': best_score,
            'coverage': self._compute_coverage(best_subset),
            'conflicts': self._count_conflicts(best_subset, conflict_matrix),
            'compatibility_score': self.graph.compute_compatibility_score(
                {c.name for c in selected_constraints}
            )
        }
    
    def _build_conflict_matrix(self) -> np.ndarray:
        """Build conflict matrix between constraints"""
        matrix = np.zeros((self.n_constraints, self.n_constraints))
        
        for i, c1 in enumerate(self.constraints):
            for j, c2 in enumerate(self.constraints):
                if i != j and self.graph.graph.has_edge(c1.name, c2.name):
                    edge_data = self.graph.graph[c1.name][c2.name]
                    if edge_data.get('relationship') == 'conflict':
                        matrix[i, j] = edge_data.get('strength', 1.0)
                        
        return matrix
    
    def _build_coverage_matrix(self) -> np.ndarray:
        """Build coverage matrix for ethical dimensions"""
        # Dimensions: fairness, privacy, transparency, consent, wellbeing
        dimensions = [ct for ct in ConstraintType]
        n_dimensions = len(dimensions)
        
        matrix = np.zeros((self.n_constraints, n_dimensions))
        
        for i, constraint in enumerate(self.constraints):
            dim_index = dimensions.index(constraint.constraint_type)
            matrix[i, dim_index] = 1.0
            
        return matrix
    
    def _check_subset_constraints(self, subset: Set[int], 
                                min_coverage: float,
                                max_conflicts: int) -> bool:
        """Check if subset satisfies constraints"""
        # Check coverage
        coverage = self._compute_coverage(subset)
        if coverage < min_coverage:
            return False
        
        # Check conflicts
        conflict_matrix = self._build_conflict_matrix()
        conflicts = self._count_conflicts(subset, conflict_matrix)
        if conflicts > max_conflicts:
            return False
        
        return True
    
    def _compute_coverage(self, subset: Set[int]) -> float:
        """Compute ethical dimension coverage"""
        coverage_matrix = self._build_coverage_matrix()
        
        # Which dimensions are covered
        covered_dims = np.zeros(coverage_matrix.shape[1])
        for i in subset:
            covered_dims = np.maximum(covered_dims, coverage_matrix[i])
        
        return np.mean(covered_dims)
    
    def _count_conflicts(self, subset: Set[int], 
                        conflict_matrix: np.ndarray) -> int:
        """Count number of conflicts in subset"""
        conflicts = 0
        for i in subset:
            for j in subset:
                if i < j and conflict_matrix[i, j] > 0:
                    conflicts += 1
        return conflicts
    
    def _compute_subset_score(self, subset: Set[int],
                            weights: np.ndarray,
                            conflict_matrix: np.ndarray) -> float:
        """Compute score for constraint subset"""
        # Positive: sum of weights
        weight_sum = sum(weights[i] for i in subset)
        
        # Negative: conflicts
        conflict_penalty = 0
        for i in subset:
            for j in subset:
                if i < j:
                    conflict_penalty += conflict_matrix[i, j]
        
        # Bonus for coverage
        coverage_bonus = self._compute_coverage(subset) * 2.0
        
        return weight_sum + coverage_bonus - conflict_penalty


class DynamicCompositionManager:
    """
    Manages dynamic composition of constraints based on context
    """
    
    def __init__(self):
        self.composition_rules = []
        self.composition_cache = {}
        self.performance_history = []
        
    def add_rule(self, rule: CompositionRule):
        """Add composition rule"""
        self.composition_rules.append(rule)
        
    def compose(self, constraints: List[EthicalConstraint],
               context: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically compose constraints based on context"""
        
        # Generate cache key
        cache_key = self._generate_cache_key(constraints, context)
        
        # Check cache
        if cache_key in self.composition_cache:
            return self.composition_cache[cache_key]
        
        # Determine composition strategy based on context
        strategy = self._select_strategy(context)
        
        # Apply composition
        if strategy == 'optimal':
            result = self._compose_optimal(constraints, context)
        elif strategy == 'priority':
            result = self._compose_priority(constraints, context)
        elif strategy == 'adaptive':
            result = self._compose_adaptive(constraints, context)
        else:
            result = self._compose_default(constraints)
        
        # Cache result
        self.composition_cache[cache_key] = result
        
        # Record performance
        self.performance_history.append({
            'timestamp': np.datetime64('now'),
            'strategy': strategy,
            'num_constraints': len(constraints),
            'context': context,
            'result': result
        })
        
        return result
    
    def _generate_cache_key(self, constraints: List[EthicalConstraint],
                          context: Dict[str, Any]) -> str:
        """Generate cache key for composition"""
        constraint_names = sorted(c.name for c in constraints)
        context_items = sorted(context.items())
        return f"{','.join(constraint_names)}_{str(context_items)}"
    
    def _select_strategy(self, context: Dict[str, Any]) -> str:
        """Select composition strategy based on context"""
        
        # High-risk contexts need optimal composition
        if context.get('risk_level', 'medium') == 'high':
            return 'optimal'
        
        # Real-time contexts need fast composition
        if context.get('real_time', False):
            return 'priority'
        
        # Learning contexts need adaptive composition
        if context.get('learning_enabled', False):
            return 'adaptive'
        
        return 'default'
    
    def _compose_optimal(self, constraints: List[EthicalConstraint],
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Use optimization to find best composition"""
        finder = OptimalCompositionFinder(constraints)
        
        min_coverage = context.get('min_coverage', 0.8)
        max_conflicts = context.get('max_conflicts', 1)
        
        result = finder.find_optimal_subset(min_coverage, max_conflicts)
        
        return {
            'strategy': 'optimal',
            'constraints': result['selected_constraints'],
            'metadata': result
        }
    
    def _compose_priority(self, constraints: List[EthicalConstraint],
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Compose based on priority ordering"""
        
        # Sort by priority (weight)
        sorted_constraints = sorted(constraints, 
                                  key=lambda c: c.weight, 
                                  reverse=True)
        
        # Take top constraints up to budget
        budget = context.get('constraint_budget', len(constraints))
        selected = sorted_constraints[:budget]
        
        return {
            'strategy': 'priority',
            'constraints': selected,
            'metadata': {
                'total_weight': sum(c.weight for c in selected)
            }
        }
    
    def _compose_adaptive(self, constraints: List[EthicalConstraint],
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptive composition based on historical performance"""
        
        # Analyze historical performance
        recent_history = self.performance_history[-100:]
        
        # Learn which combinations work well
        successful_combinations = self._identify_successful_combinations(
            recent_history
        )
        
        # Try to match successful patterns
        for combo in successful_combinations:
            if self._matches_pattern(constraints, combo):
                return {
                    'strategy': 'adaptive',
                    'constraints': combo['constraints'],
                    'metadata': {
                        'learned_from_history': True,
                        'success_rate': combo['success_rate']
                    }
                }
        
        # Fallback to default
        return self._compose_default(constraints)
    
    def _compose_default(self, constraints: List[EthicalConstraint]) -> Dict[str, Any]:
        """Default composition: include all constraints"""
        return {
            'strategy': 'default',
            'constraints': constraints,
            'metadata': {
                'method': 'include_all'
            }
        }
    
    def _identify_successful_combinations(self, 
                                        history: List[Dict]) -> List[Dict]:
        """Identify successful constraint combinations from history"""
        # Placeholder for learning logic
        # In practice, would use ML to identify patterns
        return []
    
    def _matches_pattern(self, constraints: List[EthicalConstraint],
                        pattern: Dict) -> bool:
        """Check if constraints match a pattern"""
        # Placeholder for pattern matching
        return False


class ConflictResolver:
    """
    Resolves conflicts between constraints
    """
    
    def __init__(self):
        self.resolution_strategies = {
            'priority': self._resolve_by_priority,
            'negotiation': self._resolve_by_negotiation,
            'relaxation': self._resolve_by_relaxation,
            'transformation': self._resolve_by_transformation
        }
        
    def resolve(self, c1: EthicalConstraint, c2: EthicalConstraint,
               strategy: str = 'negotiation') -> Dict[str, Any]:
        """Resolve conflict between two constraints"""
        
        if strategy not in self.resolution_strategies:
            strategy = 'negotiation'
            
        resolver = self.resolution_strategies[strategy]
        return resolver(c1, c2)
    
    def _resolve_by_priority(self, c1: EthicalConstraint, 
                           c2: EthicalConstraint) -> Dict[str, Any]:
        """Resolve by choosing higher priority constraint"""
        if c1.weight >= c2.weight:
            return {
                'resolution': 'priority',
                'selected': c1,
                'rejected': c2,
                'reason': f'{c1.name} has higher priority'
            }
        else:
            return {
                'resolution': 'priority',
                'selected': c2,
                'rejected': c1,
                'reason': f'{c2.name} has higher priority'
            }
    
    def _resolve_by_negotiation(self, c1: EthicalConstraint,
                              c2: EthicalConstraint) -> Dict[str, Any]:
        """Resolve by finding middle ground"""
        
        # Adjust thresholds to find compromise
        if hasattr(c1, 'threshold') and hasattr(c2, 'threshold'):
            # Average thresholds
            new_threshold = (c1.threshold + c2.threshold) / 2
            
            return {
                'resolution': 'negotiation',
                'compromise': {
                    'constraint_1': {
                        'name': c1.name,
                        'original_threshold': c1.threshold,
                        'new_threshold': new_threshold
                    },
                    'constraint_2': {
                        'name': c2.name,
                        'original_threshold': c2.threshold,
                        'new_threshold': new_threshold
                    }
                }
            }
        
        # Fallback to priority
        return self._resolve_by_priority(c1, c2)
    
    def _resolve_by_relaxation(self, c1: EthicalConstraint,
                             c2: EthicalConstraint) -> Dict[str, Any]:
        """Resolve by relaxing constraints"""
        
        # Relax both constraints by 10%
        relaxation_factor = 0.1
        
        return {
            'resolution': 'relaxation',
            'adjustments': {
                c1.name: {
                    'factor': 1 + relaxation_factor,
                    'description': 'Relaxed by 10%'
                },
                c2.name: {
                    'factor': 1 + relaxation_factor,
                    'description': 'Relaxed by 10%'
                }
            }
        }
    
    def _resolve_by_transformation(self, c1: EthicalConstraint,
                                 c2: EthicalConstraint) -> Dict[str, Any]:
        """Resolve by transforming constraints"""
        
        # Transform into a composite constraint
        return {
            'resolution': 'transformation',
            'result': 'composite_constraint',
            'description': f'Merged {c1.name} and {c2.name} into composite',
            'parameters': {
                'type': 'weighted_sum',
                'weights': {
                    c1.name: c1.weight / (c1.weight + c2.weight),
                    c2.name: c2.weight / (c1.weight + c2.weight)
                }
            }
        }