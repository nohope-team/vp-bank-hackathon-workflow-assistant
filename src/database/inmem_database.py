import json
import os
from typing import Any, Dict, Optional

class InMemoryDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load data from JSON file if it exists"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {}
                self.save()  # Ensure file is created if it was empty or invalid
    
    def save(self) -> None:
        """Save data to JSON file"""
        with open(self.file_path, 'w+') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        return self.data.get(key, [])
    
    def set(self, key: str, value: Any) -> None:
        """Set value for key and persist to file"""
        self.data[key] = value
        self.save()
    
    def delete(self, key: str) -> bool:
        """Delete key and persist to file"""
        if key in self.data:
            del self.data[key]
            self.save()
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self.data
    
    def keys(self) -> list:
        """Get all keys"""
        return list(self.data.keys())
    
    def clear(self) -> None:
        """Clear all data and persist to file"""
        self.data.clear()
        self.save()