"""
Core module for the ethics-by-design framework.

This module contains the fundamental interfaces, constraints, and layer
implementations that form the foundation of the ethics framework.
"""

from .interfaces import Decision, LayerInterface, SystemOrchestrator, LayerMetrics
from .constraints import (
    EthicalConstraint,
    FairnessConstraint,
    PrivacyConstraint,
    WellbeingConstraint,
    TransparencyConstraint,
    ConsentConstraint,
    ConstraintType,
    ViolationSeverity,
    ConstraintViolation,
    create_constraint
)

__all__ = [
    # Interfaces
    'Decision', 'LayerInterface', 'SystemOrchestrator', 'LayerMetrics',
    
    # Constraints
    'EthicalConstraint', 'FairnessConstraint', 'PrivacyConstraint', 
    'WellbeingConstraint', 'TransparencyConstraint', 'ConsentConstraint',
    'ConstraintType', 'ViolationSeverity', 'ConstraintViolation', 'create_constraint'
] 