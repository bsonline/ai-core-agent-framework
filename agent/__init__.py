"""AI Core Agent Framework

A comprehensive framework for building AI agents with state management,
persistence, and testing capabilities.
"""

from .base_agent import BaseAgent
from .state_manager import StateManager

__version__ = "1.0.0"
__all__ = ["BaseAgent", "StateManager"]
