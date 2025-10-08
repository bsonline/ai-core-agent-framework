"""Tests for StateManager

Comprehensive test suite for the StateManager class.
"""

import json
import os
import pytest
import tempfile
from pathlib import Path

from agent.state_manager import StateManager


class TestStateManager:
    """Test suite for StateManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create a StateManager instance for tests."""
        return StateManager(state_dir=temp_dir, autosave=False)
    
    def test_initialization(self, temp_dir):
        """Test StateManager initialization."""
        sm = StateManager(state_dir=temp_dir)
        assert sm.state == {}
        assert sm.state_dir == Path(temp_dir)
        assert sm.autosave == True
        assert "created_at" in sm.metadata
        assert "version" in sm.metadata
    
    def test_set_and_get(self, state_manager):
        """Test setting and getting state values."""
        state_manager.set("key1", "value1")
        assert state_manager.get("key1") == "value1"
        
        state_manager.set("key2", 42)
        assert state_manager.get("key2") == 42
    
    def test_get_default(self, state_manager):
        """Test getting with default value."""
        result = state_manager.get("nonexistent", "default")
        assert result == "default"
    
    def test_delete(self, state_manager):
        """Test deleting state values."""
        state_manager.set("key1", "value1")
        assert state_manager.delete("key1") == True
        assert state_manager.get("key1") is None
        
        assert state_manager.delete("nonexistent") == False
    
    def test_clear(self, state_manager):
        """Test clearing all state."""
        state_manager.set("key1", "value1")
        state_manager.set("key2", "value2")
        state_manager.clear()
        assert state_manager.state == {}
    
    def test_save_and_load(self, state_manager, temp_dir):
        """Test saving and loading state."""
        state_manager.set("key1", "value1")
        state_manager.set("key2", 42)
        
        filepath = state_manager.save("test_state")
        assert os.path.exists(filepath)
        
        # Load into new instance
        new_sm = StateManager(state_dir=temp_dir, autosave=False)
        new_sm.load("test_state.json")
        
        assert new_sm.get("key1") == "value1"
        assert new_sm.get("key2") == 42
    
    def test_list_states(self, state_manager, temp_dir):
        """Test listing saved states."""
        state_manager.set("key1", "value1")
        state_manager.save("state1")
        state_manager.save("state2")
        
        states = state_manager.list_states()
        assert "state1.json" in states
        assert "state2.json" in states
    
    def test_backup(self, state_manager, temp_dir):
        """Test state backup."""
        state_manager.set("key1", "value1")
        backup_path = state_manager.backup()
        
        assert os.path.exists(backup_path)
        assert "backup_" in backup_path
    
    def test_validate_state(self, state_manager):
        """Test state validation."""
        state_manager.set("name", "test")
        state_manager.set("count", 42)
        
        schema = {"name": str, "count": int}
        assert state_manager.validate_state(schema) == True
        
        schema = {"name": int}  # Wrong type
        assert state_manager.validate_state(schema) == False
    
    def test_autosave(self, temp_dir):
        """Test autosave functionality."""
        sm = StateManager(state_dir=temp_dir, autosave=True)
        sm.set("key1", "value1")
        
        # Check that a file was created
        files = list(Path(temp_dir).glob("*.json"))
        assert len(files) > 0
    
    def test_metadata(self, state_manager):
        """Test metadata tracking."""
        metadata = state_manager.get_metadata()
        assert "created_at" in metadata
        assert "updated_at" in metadata
        assert "version" in metadata
    
    def test_json_serialization(self, state_manager, temp_dir):
        """Test JSON serialization of complex types."""
        state_manager.set("list", [1, 2, 3])
        state_manager.set("dict", {"a": 1, "b": 2})
        
        filepath = state_manager.save("complex_state")
        
        # Load and verify
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["state"]["list"] == [1, 2, 3]
        assert data["state"]["dict"] == {"a": 1, "b": 2}
