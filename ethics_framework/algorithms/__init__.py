"""
Algorithm Registry and ML Model Integration

This module provides the algorithm registry system that enables plugging
any ML model into the ethics framework with proper constraint validation.
All ML models now inherit from BaseAlgorithm for standardized ethical AI capabilities.
"""

from .registry import AlgorithmRegistry
from .ml_models import (
    CollaborativeFilteringModel,
    ContentClassificationModel,
    HiringRecommendationModel,
    SocialMediaRankingModel,
    create_model
)
from .base_algorithm import BaseAlgorithm, AlgorithmMetadata
from .adaptive_optimizer import (
    ConstraintThresholdOptimizer,
    PolicyParameterOptimizer,
    OptimizationTarget,
    OptimizationResult
)
from .hierarchical_intervention import (
    HierarchicalInterventionSystem,
    create_intervention_system
)

__all__ = [
    'AlgorithmRegistry',
    'BaseAlgorithm',
    'AlgorithmMetadata',
    'CollaborativeFilteringModel',
    'ContentClassificationModel', 
    'HiringRecommendationModel',
    'SocialMediaRankingModel',
    'create_model',
    'ConstraintThresholdOptimizer',
    'PolicyParameterOptimizer',
    'OptimizationTarget',
    'OptimizationResult',
    'HierarchicalInterventionSystem',
    'create_intervention_system'
]
