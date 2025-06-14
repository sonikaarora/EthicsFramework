"""
Ethics-by-Design Framework - Core Package
Sophisticated 5-layer architecture for ethical AI systems
"""

from .ethics_framework import *

__version__ = "1.0.0"
__author__ = "Ethics-by-Design Research Team"

# Framework metadata
FRAMEWORK_INFO = {
    'version': __version__,
    'layers': 5,
    'constraint_types': ['fairness', 'privacy', 'wellbeing', 'transparency', 'consent'],
    'supported_scenarios': ['social_media', 'hiring', 'content_recommendation'],
    'performance_target': '>200K decisions/second',
    'overhead_target': '<25% average'
} 