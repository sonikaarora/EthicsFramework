"""
Adaptive Optimizer for Ethics-by-Design Framework

Implements adaptive optimization algorithms for constraint thresholds,
policy parameters, and system performance based on real-time feedback.
"""

import numpy as np
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import threading
from collections import deque, defaultdict


@dataclass
class OptimizationTarget:
    """Represents an optimization target with constraints"""
    name: str
    current_value: float
    target_value: float
    tolerance: float
    weight: float = 1.0
    constraint_type: str = "equality"  # equality, inequality_upper, inequality_lower


@dataclass
class OptimizationResult:
    """Result of an optimization iteration"""
    iteration: int
    parameters: Dict[str, float]
    objective_value: float
    constraint_violations: List[str]
    convergence_status: str
    improvement: float


class AdaptiveOptimizer(ABC):
    """Abstract base class for adaptive optimization algorithms"""
    
    def __init__(self, learning_rate: float = 0.01, convergence_threshold: float = 0.001):
        self.learning_rate = learning_rate
        self.convergence_threshold = convergence_threshold
        self.optimization_history = []
        self.current_parameters = {}
        self.iteration_count = 0
        self._lock = threading.RLock()
    
    @abstractmethod
    def optimize_step(self, targets: List[OptimizationTarget], 
                     feedback: Dict[str, Any]) -> OptimizationResult:
        """Perform one optimization step"""
        pass
    
    @abstractmethod
    def update_parameters(self, gradient: Dict[str, float]) -> Dict[str, float]:
        """Update parameters based on gradient"""
        pass
    
    def check_convergence(self, recent_results: List[OptimizationResult]) -> bool:
        """Check if optimization has converged"""
        if len(recent_results) < 3:
            return False
        
        recent_improvements = [r.improvement for r in recent_results[-3:]]
        avg_improvement = np.mean(recent_improvements)
        
        return avg_improvement < self.convergence_threshold


class GradientDescentOptimizer(AdaptiveOptimizer):
    """Gradient descent optimizer for constraint parameters"""
    
    def __init__(self, learning_rate: float = 0.01, momentum: float = 0.9, 
                 convergence_threshold: float = 0.001):
        super().__init__(learning_rate, convergence_threshold)
        self.momentum = momentum
        self.velocity = {}
    
    def optimize_step(self, targets: List[OptimizationTarget], 
                     feedback: Dict[str, Any]) -> OptimizationResult:
        """Perform gradient descent optimization step"""
        with self._lock:
            self.iteration_count += 1
            
            # Calculate objective function value
            objective_value = self._calculate_objective(targets, feedback)
            
            # Compute gradients
            gradients = self._compute_gradients(targets, feedback)
            
            # Update parameters
            old_parameters = self.current_parameters.copy()
            self.current_parameters = self.update_parameters(gradients)
            
            # Check constraint violations
            violations = self._check_constraint_violations(targets, feedback)
            
            # Calculate improvement
            improvement = 0.0
            if len(self.optimization_history) > 0:
                prev_objective = self.optimization_history[-1].objective_value
                improvement = abs(objective_value - prev_objective)
            
            # Determine convergence status
            convergence_status = "continuing"
            if len(self.optimization_history) >= 3:
                recent_results = self.optimization_history[-3:]
                if self.check_convergence(recent_results):
                    convergence_status = "converged"
            
            result = OptimizationResult(
                iteration=self.iteration_count,
                parameters=self.current_parameters.copy(),
                objective_value=objective_value,
                constraint_violations=violations,
                convergence_status=convergence_status,
                improvement=improvement
            )
            
            self.optimization_history.append(result)
            return result
    
    def update_parameters(self, gradients: Dict[str, float]) -> Dict[str, float]:
        """Update parameters using momentum-based gradient descent"""
        updated_params = {}
        
        for param_name, gradient in gradients.items():
            # Initialize velocity if needed
            if param_name not in self.velocity:
                self.velocity[param_name] = 0.0
            
            # Update velocity with momentum
            self.velocity[param_name] = (
                self.momentum * self.velocity[param_name] - 
                self.learning_rate * gradient
            )
            
            # Update parameter
            current_value = self.current_parameters.get(param_name, 0.5)
            updated_params[param_name] = current_value + self.velocity[param_name]
            
            # Clamp to valid range [0, 1] for most parameters
            updated_params[param_name] = np.clip(updated_params[param_name], 0.0, 1.0)
        
        return updated_params
    
    def _calculate_objective(self, targets: List[OptimizationTarget], 
                           feedback: Dict[str, Any]) -> float:
        """Calculate weighted objective function value"""
        total_objective = 0.0
        total_weight = 0.0
        
        for target in targets:
            current_value = feedback.get(f"{target.name}_current", target.current_value)
            
            if target.constraint_type == "equality":
                error = abs(current_value - target.target_value)
            elif target.constraint_type == "inequality_upper":
                error = max(0, current_value - target.target_value)
            elif target.constraint_type == "inequality_lower":
                error = max(0, target.target_value - current_value)
            else:
                error = abs(current_value - target.target_value)
            
            weighted_error = target.weight * error
            total_objective += weighted_error
            total_weight += target.weight
        
        return total_objective / max(total_weight, 1.0)
    
    def _compute_gradients(self, targets: List[OptimizationTarget], 
                          feedback: Dict[str, Any]) -> Dict[str, float]:
        """Compute gradients using finite differences"""
        gradients = {}
        epsilon = 1e-6
        
        # Get current objective value
        current_objective = self._calculate_objective(targets, feedback)
        
        # Compute gradient for each parameter
        for param_name in self.current_parameters:
            # Perturb parameter slightly
            original_value = self.current_parameters[param_name]
            self.current_parameters[param_name] = original_value + epsilon
            
            # Calculate perturbed objective
            perturbed_objective = self._calculate_objective(targets, feedback)
            
            # Compute finite difference gradient
            gradient = (perturbed_objective - current_objective) / epsilon
            gradients[param_name] = gradient
            
            # Restore original value
            self.current_parameters[param_name] = original_value
        
        return gradients
    
    def _check_constraint_violations(self, targets: List[OptimizationTarget], 
                                   feedback: Dict[str, Any]) -> List[str]:
        """Check for constraint violations"""
        violations = []
        
        for target in targets:
            current_value = feedback.get(f"{target.name}_current", target.current_value)
            
            if target.constraint_type == "equality":
                if abs(current_value - target.target_value) > target.tolerance:
                    violations.append(f"{target.name}_equality_violation")
            elif target.constraint_type == "inequality_upper":
                if current_value > target.target_value + target.tolerance:
                    violations.append(f"{target.name}_upper_bound_violation")
            elif target.constraint_type == "inequality_lower":
                if current_value < target.target_value - target.tolerance:
                    violations.append(f"{target.name}_lower_bound_violation")
        
        return violations


class BayesianOptimizer(AdaptiveOptimizer):
    """Bayesian optimization for expensive objective functions"""
    
    def __init__(self, learning_rate: float = 0.01, exploration_weight: float = 0.1,
                 convergence_threshold: float = 0.001):
        super().__init__(learning_rate, convergence_threshold)
        self.exploration_weight = exploration_weight
        self.observed_points = []
        self.observed_values = []
    
    def optimize_step(self, targets: List[OptimizationTarget], 
                     feedback: Dict[str, Any]) -> OptimizationResult:
        """Perform Bayesian optimization step"""
        with self._lock:
            self.iteration_count += 1
            
            # Calculate objective function value
            objective_value = self._calculate_objective(targets, feedback)
            
            # Store observation
            current_point = list(self.current_parameters.values())
            self.observed_points.append(current_point)
            self.observed_values.append(objective_value)
            
            # Select next point using acquisition function
            next_parameters = self._select_next_point()
            
            # Update parameters
            old_parameters = self.current_parameters.copy()
            self.current_parameters = next_parameters
            
            # Check constraint violations
            violations = self._check_constraint_violations(targets, feedback)
            
            # Calculate improvement
            improvement = 0.0
            if len(self.optimization_history) > 0:
                prev_objective = self.optimization_history[-1].objective_value
                improvement = abs(objective_value - prev_objective)
            
            result = OptimizationResult(
                iteration=self.iteration_count,
                parameters=self.current_parameters.copy(),
                objective_value=objective_value,
                constraint_violations=violations,
                convergence_status="continuing",
                improvement=improvement
            )
            
            self.optimization_history.append(result)
            return result
    
    def update_parameters(self, gradient: Dict[str, float]) -> Dict[str, float]:
        """Update parameters (not used in Bayesian optimization)"""
        return self.current_parameters
    
    def _select_next_point(self) -> Dict[str, float]:
        """Select next point using acquisition function"""
        # Simplified acquisition function (random search with bias toward good regions)
        if len(self.observed_values) == 0:
            # Random initialization
            return {param: np.random.uniform(0, 1) for param in self.current_parameters}
        
        # Find best observed point
        best_idx = np.argmin(self.observed_values)
        best_point = self.observed_points[best_idx]
        
        # Add noise for exploration
        noise_scale = self.exploration_weight / (1 + self.iteration_count * 0.1)
        next_point = {}
        
        for i, param_name in enumerate(self.current_parameters.keys()):
            if i < len(best_point):
                base_value = best_point[i]
            else:
                base_value = 0.5
            
            noise = np.random.normal(0, noise_scale)
            next_point[param_name] = np.clip(base_value + noise, 0.0, 1.0)
        
        return next_point
    
    def _calculate_objective(self, targets: List[OptimizationTarget], 
                           feedback: Dict[str, Any]) -> float:
        """Calculate objective function value"""
        total_objective = 0.0
        total_weight = 0.0
        
        for target in targets:
            current_value = feedback.get(f"{target.name}_current", target.current_value)
            error = abs(current_value - target.target_value)
            weighted_error = target.weight * error
            total_objective += weighted_error
            total_weight += target.weight
        
        return total_objective / max(total_weight, 1.0)
    
    def _check_constraint_violations(self, targets: List[OptimizationTarget], 
                                   feedback: Dict[str, Any]) -> List[str]:
        """Check for constraint violations"""
        violations = []
        
        for target in targets:
            current_value = feedback.get(f"{target.name}_current", target.current_value)
            if abs(current_value - target.target_value) > target.tolerance:
                violations.append(f"{target.name}_violation")
        
        return violations


class ConstraintThresholdOptimizer:
    """Optimizer specifically for constraint thresholds"""
    
    def __init__(self, optimizer_type: str = "gradient_descent"):
        if optimizer_type == "gradient_descent":
            self.optimizer = GradientDescentOptimizer()
        elif optimizer_type == "bayesian":
            self.optimizer = BayesianOptimizer()
        else:
            raise ValueError(f"Unknown optimizer type: {optimizer_type}")
        
        self.constraint_targets = {}
        self.performance_history = deque(maxlen=100)
    
    def add_constraint_target(self, constraint_name: str, target_satisfaction_rate: float,
                            tolerance: float = 0.05, weight: float = 1.0):
        """Add a constraint optimization target"""
        target = OptimizationTarget(
            name=f"{constraint_name}_satisfaction",
            current_value=0.5,
            target_value=target_satisfaction_rate,
            tolerance=tolerance,
            weight=weight,
            constraint_type="equality"
        )
        self.constraint_targets[constraint_name] = target
        
        # Initialize parameter if not exists
        if f"{constraint_name}_threshold" not in self.optimizer.current_parameters:
            self.optimizer.current_parameters[f"{constraint_name}_threshold"] = 0.5
    
    def optimize_thresholds(self, performance_feedback: Dict[str, Any]) -> OptimizationResult:
        """Optimize constraint thresholds based on performance feedback"""
        targets = list(self.constraint_targets.values())
        
        # Add performance targets
        if "throughput_current" in performance_feedback:
            throughput_target = OptimizationTarget(
                name="throughput",
                current_value=performance_feedback["throughput_current"],
                target_value=performance_feedback.get("throughput_target", 200000),
                tolerance=10000,
                weight=0.5,
                constraint_type="inequality_lower"
            )
            targets.append(throughput_target)
        
        if "latency_current" in performance_feedback:
            latency_target = OptimizationTarget(
                name="latency",
                current_value=performance_feedback["latency_current"],
                target_value=performance_feedback.get("latency_target", 1.0),
                tolerance=0.2,
                weight=0.3,
                constraint_type="inequality_upper"
            )
            targets.append(latency_target)
        
        # Perform optimization step
        result = self.optimizer.optimize_step(targets, performance_feedback)
        
        # Store performance history
        self.performance_history.append({
            'timestamp': time.time(),
            'parameters': result.parameters.copy(),
            'objective_value': result.objective_value,
            'feedback': performance_feedback.copy()
        })
        
        return result
    
    def get_optimized_thresholds(self) -> Dict[str, float]:
        """Get current optimized constraint thresholds"""
        thresholds = {}
        for param_name, value in self.optimizer.current_parameters.items():
            if param_name.endswith("_threshold"):
                constraint_name = param_name.replace("_threshold", "")
                thresholds[constraint_name] = value
        return thresholds
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get optimization history"""
        return self.optimizer.optimization_history.copy()


class PolicyParameterOptimizer:
    """Optimizer for governance policy parameters"""
    
    def __init__(self, optimizer_type: str = "gradient_descent"):
        if optimizer_type == "gradient_descent":
            self.optimizer = GradientDescentOptimizer(learning_rate=0.005)
        elif optimizer_type == "bayesian":
            self.optimizer = BayesianOptimizer(exploration_weight=0.05)
        else:
            raise ValueError(f"Unknown optimizer type: {optimizer_type}")
        
        self.policy_targets = {}
        self.compliance_history = deque(maxlen=50)
    
    def add_policy_target(self, policy_name: str, target_compliance_rate: float,
                         tolerance: float = 0.02, weight: float = 1.0):
        """Add a policy optimization target"""
        target = OptimizationTarget(
            name=f"{policy_name}_compliance",
            current_value=0.5,
            target_value=target_compliance_rate,
            tolerance=tolerance,
            weight=weight,
            constraint_type="equality"
        )
        self.policy_targets[policy_name] = target
        
        # Initialize parameter if not exists
        if f"{policy_name}_weight" not in self.optimizer.current_parameters:
            self.optimizer.current_parameters[f"{policy_name}_weight"] = 0.5
    
    def optimize_policies(self, compliance_feedback: Dict[str, Any]) -> OptimizationResult:
        """Optimize policy parameters based on compliance feedback"""
        targets = list(self.policy_targets.values())
        
        # Perform optimization step
        result = self.optimizer.optimize_step(targets, compliance_feedback)
        
        # Store compliance history
        self.compliance_history.append({
            'timestamp': time.time(),
            'parameters': result.parameters.copy(),
            'objective_value': result.objective_value,
            'feedback': compliance_feedback.copy()
        })
        
        return result
    
    def get_optimized_policy_weights(self) -> Dict[str, float]:
        """Get current optimized policy weights"""
        weights = {}
        for param_name, value in self.optimizer.current_parameters.items():
            if param_name.endswith("_weight"):
                policy_name = param_name.replace("_weight", "")
                weights[policy_name] = value
        return weights


# Export classes
__all__ = [
    'OptimizationTarget', 'OptimizationResult', 'AdaptiveOptimizer',
    'GradientDescentOptimizer', 'BayesianOptimizer',
    'ConstraintThresholdOptimizer', 'PolicyParameterOptimizer'
]