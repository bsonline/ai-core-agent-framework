"""Tests for BaseAgent

Comprehensive test suite for the BaseAgent class.
"""

import pytest
import tempfile
from pathlib import Path

from agent.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    def process(self, input_data):
        """Simple process implementation."""
        return f"Processed: {input_data}"


class TestBaseAgent:
    """Test suite for BaseAgent."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for tests."""
        with tempfile.TemporaryDirectory() as state_dir:
            with tempfile.TemporaryDirectory() as log_dir:
                yield state_dir, log_dir
    
    @pytest.fixture
    def agent(self, temp_dirs):
        """Create a test agent instance."""
        state_dir, log_dir = temp_dirs
        return TestAgent(
            agent_id="test_agent",
            state_dir=state_dir,
            log_dir=log_dir,
            autosave=False
        )
    
    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_id == "test_agent"
        assert agent.is_running == False
        assert agent.state_manager is not None
        assert agent.logger is not None
    
    def test_process(self, agent):
        """Test process method."""
        result = agent.process("test input")
        assert result == "Processed: test input"
    
    def test_run(self, agent):
        """Test run method with lifecycle hooks."""
        result = agent.run("test data")
        assert result == "Processed: test data"
        assert agent.get_state().get("last_start") is not None
        assert agent.get_state().get("last_stop") is not None
        assert agent.get_state().get("last_success") is not None
    
    def test_on_error(self, agent):
        """Test error handling."""
        class ErrorAgent(BaseAgent):
            def process(self, input_data):
                raise ValueError("Test error")
        
        error_agent = ErrorAgent(
            agent_id="error_agent",
            state_dir=agent.state_manager.state_dir,
            log_dir=Path(agent.logger.handlers[0].baseFilename).parent,
            autosave=False
        )
        
        with pytest.raises(ValueError):
            error_agent.run("data")
        
        error_info = error_agent.get_state().get("last_error")
        assert error_info is not None
        assert "Test error" in error_info["error"]
    
    def test_state_management(self, agent):
        """Test state management methods."""
        agent.set_state("key1", "value1")
        assert agent.get_state()["key1"] == "value1"
    
    def test_save_and_load_state(self, agent):
        """Test state persistence."""
        agent.set_state("key1", "value1")
        agent.set_state("key2", 42)
        
        filepath = agent.save_state("test_state")
        assert Path(filepath).exists()
        
        # Create new agent and load state
        new_agent = TestAgent(
            agent_id="new_agent",
            state_dir=str(agent.state_manager.state_dir),
            log_dir=str(Path(agent.logger.handlers[0].baseFilename).parent),
            autosave=False
        )
        new_agent.load_state("test_state.json")
        
        assert new_agent.get_state()["key1"] == "value1"
        assert new_agent.get_state()["key2"] == 42
    
    def test_logging(self, agent, temp_dirs):
        """Test logging functionality."""
        state_dir, log_dir = temp_dirs
        log_file = Path(log_dir) / f"{agent.agent_id}.log"
        
        agent.logger.info("Test log message")
        
        # Check log file exists
        assert log_file.exists()
    
    def test_repr(self, agent):
        """Test string representation."""
        repr_str = repr(agent)
        assert "TestAgent" in repr_str
        assert "test_agent" in repr_str
        assert "running=False" in repr_str
