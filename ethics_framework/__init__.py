"""
Ethics-by-Design Framework

A comprehensive framework for integrating ethical constraints into AI systems
with a 5-layer architecture supporting fairness, privacy, transparency, and wellbeing.
"""

from .core.interfaces import Decision, LayerInterface, SystemOrchestrator
from .core.constraints import (
    EthicalConstraint, 
    FairnessConstraint, 
    PrivacyConstraint, 
    WellbeingConstraint,
    TransparencyConstraint,
    ConsentConstraint,
    ConstraintComposer
)
from .core.system_orchestrator import EthicsFrameworkOrchestrator

from .algorithms.registry import AlgorithmRegistry
from .algorithms.base_algorithm import BaseAlgorithm, AlgorithmMetadata
from .algorithms.ml_models import (
    CollaborativeFilteringModel,
    HiringRecommendationModel,
    SocialMediaRankingModel,
    ContentClassificationModel
)

from .simulation.data_generator import DecisionGenerator, ScenarioDataGenerator, GenerationConfig

__version__ = "1.0.0"

__all__ = [
    # Core interfaces
    'Decision',
    'LayerInterface', 
    'SystemOrchestrator',
    
    # Constraints
    'EthicalConstraint',
    'FairnessConstraint',
    'PrivacyConstraint', 
    'WellbeingConstraint',
    'TransparencyConstraint',
    'ConsentConstraint',
    'ConstraintComposer',
    
    # System orchestrator
    'EthicsFrameworkOrchestrator',
    
    # Algorithm components
    'AlgorithmRegistry',
    'BaseAlgorithm',
    'AlgorithmMetadata',
    'CollaborativeFilteringModel',
    'HiringRecommendationModel',
    'SocialMediaRankingModel',
    'ContentClassificationModel',
    
    # Simulation components
    'DecisionGenerator',
    'ScenarioDataGenerator',
    'GenerationConfig'
] 