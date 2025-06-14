"""
Simulation Module

This module provides data generation and scenario simulation capabilities
for testing the ethics framework across different domains and use cases.
"""

from .data_generator import DecisionGenerator, ScenarioDataGenerator, GenerationConfig

__all__ = [
    'DecisionGenerator',
    'ScenarioDataGenerator', 
    'GenerationConfig'
]
