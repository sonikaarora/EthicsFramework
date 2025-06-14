"""
Base Algorithm Interface

Defines the interface that all ML algorithms must implement to integrate
with the ethics framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import numpy as np

from ..core.interfaces import Decision


@dataclass
class AlgorithmMetadata:
    """Metadata about an algorithm's ethical properties"""
    name: str
    version: str
    fairness_aware: bool
    privacy_level: str  # 'low', 'medium', 'high'
    transparency_level: str  # 'black_box', 'interpretable', 'explainable'
    bias_mitigation: List[str]  # List of bias mitigation techniques
    performance_characteristics: Dict[str, Any]


class BaseAlgorithm(ABC):
    """Base class for all ML algorithms in the ethics framework"""
    
    def __init__(self, name: str, metadata: AlgorithmMetadata):
        self.name = name
        self.metadata = metadata
        self.usage_count = 0
        self.violation_rate = 0.0
        self.performance_stats = {
            'total_inference_time': 0.0,
            'avg_inference_time': 0.0,
            'total_requests': 0
        }
    
    @abstractmethod
    def predict(self, decision: Decision, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction for the given decision
        
        Args:
            decision: The decision request
            context: Additional context for the prediction
            
        Returns:
            Dictionary containing prediction results and metadata
        """
        pass
    
    @abstractmethod
    def explain(self, decision: Decision, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for the prediction
        
        Args:
            decision: The original decision request
            prediction: The prediction result
            
        Returns:
            Dictionary containing explanation information
        """
        pass
    
    def update_performance_stats(self, inference_time: float):
        """Update performance statistics"""
        self.performance_stats['total_inference_time'] += inference_time
        self.performance_stats['total_requests'] += 1
        self.performance_stats['avg_inference_time'] = (
            self.performance_stats['total_inference_time'] / 
            self.performance_stats['total_requests']
        )
    
    def get_ethical_properties(self) -> Dict[str, Any]:
        """Get ethical properties of this algorithm"""
        return {
            'fairness_aware': self.metadata.fairness_aware,
            'privacy_level': self.metadata.privacy_level,
            'transparency_level': self.metadata.transparency_level,
            'bias_mitigation': self.metadata.bias_mitigation,
            'violation_rate': self.violation_rate,
            'usage_count': self.usage_count
        }
    
    def simulate_inference(self, complexity_factor: int = 80) -> float:
        """
        Simulate ML inference with configurable complexity
        
        Args:
            complexity_factor: Size of matrix operations to simulate
            
        Returns:
            Inference time in milliseconds
        """
        start_time = time.perf_counter()
        
        # Simulate ML computation with matrix operations
        matrix_a = np.random.rand(complexity_factor, complexity_factor)
        matrix_b = np.random.rand(complexity_factor, complexity_factor)
        result = np.dot(matrix_a, matrix_b)
        
        # Add some additional computation to simulate model complexity
        result = np.sum(result) + np.mean(result) + np.std(result)
        
        end_time = time.perf_counter()
        inference_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        self.update_performance_stats(inference_time)
        return inference_time 