"""State Manager for AI Agents

Provides persistent state management with JSON serialization,
autosave capabilities, and state validation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StateManager:
    """Manages agent state with persistence and validation.
    
    Features:
    - JSON-based state persistence
    - Automatic state saving
    - State validation
    - Timestamp tracking
    - Backup and restore capabilities
    """
    
    def __init__(self, state_dir: str = "states", autosave: bool = True):
        """Initialize the StateManager.
        
        Args:
            state_dir: Directory to store state files
            autosave: Whether to automatically save state on changes
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.autosave = autosave
        self.state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def set(self, key: str, value: Any) -> None:
        """Set a state value.
        
        Args:
            key: State key
            value: State value (must be JSON serializable)
        """
        self.state[key] = value
        self.metadata["updated_at"] = datetime.now().isoformat()
        
        if self.autosave:
            self.save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value.
        
        Args:
            key: State key
            default: Default value if key doesn't exist
            
        Returns:
            The state value or default
        """
        return self.state.get(key, default)
    
    def delete(self, key: str) -> bool:
        """Delete a state value.
        
        Args:
            key: State key to delete
            
        Returns:
            True if key was deleted, False if it didn't exist
        """
        if key in self.state:
            del self.state[key]
            self.metadata["updated_at"] = datetime.now().isoformat()
            
            if self.autosave:
                self.save()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all state values."""
        self.state.clear()
        self.metadata["updated_at"] = datetime.now().isoformat()
        
        if self.autosave:
            self.save()
    
    def save(self, filename: Optional[str] = None) -> str:
        """Save state to disk.
        
        Args:
            filename: Optional filename (without extension)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = self.state_dir / f"{filename}.json"
        
        data = {
            "metadata": self.metadata,
            "state": self.state
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(filepath)
    
    def load(self, filename: str) -> None:
        """Load state from disk.
        
        Args:
            filename: Filename (with or without .json extension)
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.state_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"State file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.state = data.get("state", {})
        self.metadata = data.get("metadata", {})
        self.metadata["updated_at"] = datetime.now().isoformat()
    
    def list_states(self) -> list:
        """List all saved state files.
        
        Returns:
            List of state filenames
        """
        return [f.name for f in self.state_dir.glob("*.json")]
    
    def backup(self, backup_dir: Optional[str] = None) -> str:
        """Create a backup of current state.
        
        Args:
            backup_dir: Optional backup directory
            
        Returns:
            Path to backup file
        """
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = self.state_dir / "backups"
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_filepath = backup_path / f"{backup_filename}.json"
        
        data = {
            "metadata": self.metadata,
            "state": self.state
        }
        
        with open(backup_filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(backup_filepath)
    
    def validate_state(self, schema: Dict[str, type]) -> bool:
        """Validate state against a schema.
        
        Args:
            schema: Dictionary mapping keys to expected types
            
        Returns:
            True if valid, False otherwise
        """
        for key, expected_type in schema.items():
            if key in self.state:
                if not isinstance(self.state[key], expected_type):
                    return False
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get state metadata.
        
        Returns:
            Metadata dictionary
        """
        return self.metadata.copy()
    
    def __repr__(self) -> str:
        return f"StateManager(state_dir='{self.state_dir}', items={len(self.state)})"
