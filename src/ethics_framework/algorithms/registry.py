"""
ethics_framework/algorithms/registry.py
======================================
Algorithm Registry System for Ethics-by-Design Framework
"""

import time
import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class AlgorithmMetadata:
    """Metadata for registered algorithms"""
    name: str
    description: str
    version: str
    ethical_properties: Dict[str, Any]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    usage_count: int = 0
    violation_rate: float = 0.0
    last_used: float = field(default_factory=time.time)


class AlgorithmRegistry:
    """
    Central registry for ML algorithms with ethics integration
    Manages algorithm lifecycle and performance tracking
    """
    
    def __init__(self):
        self.algorithms: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, AlgorithmMetadata] = {}
        self.performance_history: Dict[str, List[Dict]] = {}
        
    def register_algorithm(self, name: str, algorithm_func: Callable, 
                          metadata: AlgorithmMetadata) -> bool:
        """Register an algorithm with the ethics framework"""
        try:
            self.algorithms[name] = {
                'function': algorithm_func,
                'metadata': metadata,
                'registered_at': time.time(),
                'active': True
            }
            self.metadata[name] = metadata
            self.performance_history[name] = []
            
            logger.info(f"Algorithm '{name}' registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register algorithm '{name}': {e}")
            return False
    
    def get_algorithm(self, name: str) -> Optional[Callable]:
        """Get registered algorithm function"""
        if name in self.algorithms and self.algorithms[name]['active']:
            # Update usage statistics
            self.metadata[name].usage_count += 1
            self.metadata[name].last_used = time.time()
            return self.algorithms[name]['function']
        return None
    
    def list_algorithms(self) -> List[str]:
        """List all registered algorithm names"""
        return [name for name, algo in self.algorithms.items() if algo['active']]
    
    def get_metadata(self, name: str) -> Optional[AlgorithmMetadata]:
        """Get algorithm metadata"""
        return self.metadata.get(name)
    
    def update_performance(self, name: str, metrics: Dict[str, float]):
        """Update algorithm performance metrics"""
        if name in self.metadata:
            self.metadata[name].performance_metrics.update(metrics)
            self.performance_history[name].append({
                'timestamp': time.time(),
                'metrics': metrics.copy()
            })
    
    def deactivate_algorithm(self, name: str) -> bool:
        """Deactivate an algorithm"""
        if name in self.algorithms:
            self.algorithms[name]['active'] = False
            logger.info(f"Algorithm '{name}' deactivated")
            return True
        return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        active_algorithms = [name for name, algo in self.algorithms.items() if algo['active']]
        total_usage = sum(meta.usage_count for meta in self.metadata.values())
        
        return {
            'total_algorithms': len(self.algorithms),
            'active_algorithms': len(active_algorithms),
            'total_usage': total_usage,
            'algorithm_list': active_algorithms,
            'average_violation_rate': sum(meta.violation_rate for meta in self.metadata.values()) / len(self.metadata) if self.metadata else 0
        }


# Global registry instance
_global_registry = AlgorithmRegistry()

def get_global_registry() -> AlgorithmRegistry:
    """Get the global algorithm registry instance"""
    return _global_registry 