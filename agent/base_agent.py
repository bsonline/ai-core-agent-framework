"""Base Agent Module

Provides the foundational BaseAgent class for building AI agents
with state management, logging, and extensible behavior.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from .state_manager import StateManager


class BaseAgent(ABC):
    """Abstract base class for AI agents.
    
    Provides core functionality including:
    - State management
    - Logging
    - Lifecycle hooks
    - Error handling
    """
    
    def __init__(self, 
                 agent_id: str,
                 state_dir: str = "states",
                 log_dir: str = "logs",
                 autosave: bool = True):
        """Initialize the agent.
        
        Args:
            agent_id: Unique identifier for this agent
            state_dir: Directory for state persistence
            log_dir: Directory for log files
            autosave: Whether to automatically save state
        """
        self.agent_id = agent_id
        self.state_manager = StateManager(state_dir=state_dir, autosave=autosave)
        self.logger = self._setup_logging(log_dir)
        self.is_running = False
        
        self.logger.info(f"Agent {agent_id} initialized")
    
    def _setup_logging(self, log_dir: str) -> logging.Logger:
        """Setup logging for the agent.
        
        Args:
            log_dir: Directory to store log files
            
        Returns:
            Configured logger instance
        """
        import os
        os.makedirs(log_dir, exist_ok=True)
        
        logger = logging.getLogger(self.agent_id)
        logger.setLevel(logging.INFO)
        
        # File handler
        log_file = os.path.join(log_dir, f"{self.agent_id}.log")
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data.
        
        This method must be implemented by subclasses.
        
        Args:
            input_data: Data to process
            
        Returns:
            Processed result
        """
        pass
    
    def run(self, input_data: Any) -> Any:
        """Run the agent with lifecycle hooks.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processing result
        """
        self.is_running = True
        self.logger.info("Starting agent execution")
        
        try:
            self.on_start()
            result = self.process(input_data)
            self.on_success(result)
            return result
        except Exception as e:
            self.logger.error(f"Error during execution: {str(e)}")
            self.on_error(e)
            raise
        finally:
            self.on_stop()
            self.is_running = False
            self.logger.info("Agent execution completed")
    
    def on_start(self) -> None:
        """Hook called when agent starts."""
        self.state_manager.set("last_start", datetime.now().isoformat())
    
    def on_stop(self) -> None:
        """Hook called when agent stops."""
        self.state_manager.set("last_stop", datetime.now().isoformat())
    
    def on_success(self, result: Any) -> None:
        """Hook called on successful execution.
        
        Args:
            result: The successful result
        """
        self.state_manager.set("last_success", datetime.now().isoformat())
    
    def on_error(self, error: Exception) -> None:
        """Hook called on error.
        
        Args:
            error: The exception that occurred
        """
        self.state_manager.set("last_error", {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "type": type(error).__name__
        })
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state.
        
        Returns:
            Dictionary containing agent state
        """
        return self.state_manager.state.copy()
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value.
        
        Args:
            key: State key
            value: State value
        """
        self.state_manager.set(key, value)
    
    def save_state(self, filename: Optional[str] = None) -> str:
        """Save agent state to disk.
        
        Args:
            filename: Optional filename for the state file
            
        Returns:
            Path to saved state file
        """
        if filename is None:
            filename = f"{self.agent_id}_state"
        return self.state_manager.save(filename)
    
    def load_state(self, filename: str) -> None:
        """Load agent state from disk.
        
        Args:
            filename: State file to load
        """
        self.state_manager.load(filename)
        self.logger.info(f"State loaded from {filename}")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(agent_id='{self.agent_id}', running={self.is_running})"
