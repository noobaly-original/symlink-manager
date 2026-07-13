"""
Settings and configuration management for the Symlink application.
Handles saving and loading user preferences and history.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class SettingsManager:
    """Manages application settings and history."""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize settings manager.
        
        Args:
            config_dir: Custom config directory path
        """
        if config_dir is None:
            # Use standard config directory for the OS
            if os.name == 'nt':  # Windows
                config_dir = os.path.expandvars(r'%APPDATA%\SymlinkApp')
            else:  # macOS and Linux
                config_dir = os.path.expanduser('~/.config/symlink_app')
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_dir / 'settings.json'
        self.history_file = self.config_dir / 'history.json'
        self.symlinks_file = self.config_dir / 'managed_symlinks.json'
        
        self.settings = self._load_settings()
        self.history = self._load_history()
        self.symlinks = self._load_symlinks()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default settings
        return {
            'window_geometry': {'width': 800, 'height': 600},
            'auto_expand_paths': True,
            'relative_by_default': False,
            'confirm_before_create': True,
            'theme': 'dark',
            'show_source_content': False,
            'last_source_dir': str(Path.home()),
            'last_target_dir': str(Path.home()),
            'minimize_to_tray': True,
            'start_on_login': False,
        }
    
    def _load_history(self) -> Dict[str, List[str]]:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default history structure
        return {
            'sources': [],
            'targets': [],
            'creations': [],  # Track each symlink creation
        }
    
    def _load_symlinks(self) -> Dict[str, list]:
        """Load managed symlinks from file."""
        if self.symlinks_file.exists():
            try:
                with open(self.symlinks_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default symlinks structure
        return {
            'symlinks': [],  # List of tracked symlinks
        }
    
    def save_settings(self) -> bool:
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            logging.warning(f"Error saving settings: {e}")
            return False
    
    def save_history(self) -> bool:
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            return True
        except Exception as e:
            logging.warning(f"Error saving history: {e}")
            return False
    
    def save_symlinks(self) -> bool:
        """Save managed symlinks to file."""
        try:
            with open(self.symlinks_file, 'w') as f:
                json.dump(self.symlinks, f, indent=2)
            return True
        except Exception as e:
            logging.warning(f"Error saving symlinks: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self.settings[key] = value
        self.save_settings()
    
    def add_to_history(self, path: str, path_type: str = 'both') -> None:
        """
        Add a path to history.
        
        Args:
            path: Path to add
            path_type: 'source', 'target', or 'both'
        """
        if path_type in ('source', 'both'):
            if path not in self.history['sources']:
                self.history['sources'].insert(0, path)
                # Keep only last 50 items
                self.history['sources'] = self.history['sources'][:50]
        
        if path_type in ('target', 'both'):
            if path not in self.history['targets']:
                self.history['targets'].insert(0, path)
                # Keep only last 50 items
                self.history['targets'] = self.history['targets'][:50]
        
        self.save_history()
    
    def record_creation(self, source: str, target: str, success: bool, message: str = '') -> None:
        """
        Record a symlink creation attempt.
        
        Args:
            source: Source path
            target: Target path
            success: Whether creation was successful
            message: Additional message
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'target': target,
            'success': success,
            'message': message,
        }
        self.history['creations'].insert(0, record)
        # Keep only last 200 items
        self.history['creations'] = self.history['creations'][:200]
        self.save_history()
    
    def get_history(self, path_type: str = 'sources', limit: int = 20) -> List[str]:
        """
        Get history items.
        
        Args:
            path_type: 'sources', 'targets', or 'creations'
            limit: Maximum number of items to return
            
        Returns:
            List of history items
        """
        if path_type == 'creations':
            return self.history.get('creations', [])[:limit]
        return self.history.get(path_type, [])[:limit]
    
    def get_most_used_destinations(self, limit: int = 10) -> List[tuple]:
        """
        Get most frequently used target destinations.
        
        Args:
            limit: Maximum number of destinations to return
            
        Returns:
            List of tuples (path, count)
        """
        from collections import Counter
        
        # Count successful creations by target path
        successful_targets = [
            record['target']
            for record in self.history.get('creations', [])
            if record.get('success', False)
        ]
        
        counts = Counter(successful_targets)
        return counts.most_common(limit)
    
    def get_most_used_sources(self, limit: int = 10) -> List[tuple]:
        """
        Get most frequently used source paths.
        
        Args:
            limit: Maximum number of sources to return
            
        Returns:
            List of tuples (path, count)
        """
        from collections import Counter
        
        # Count successful creations by source path
        successful_sources = [
            record['source']
            for record in self.history.get('creations', [])
            if record.get('success', False)
        ]
        
        counts = Counter(successful_sources)
        return counts.most_common(limit)
    
    def clear_history(self, path_type: str = 'all') -> None:
        """
        Clear history.
        
        Args:
            path_type: 'sources', 'targets', 'creations', or 'all'
        """
        if path_type in ('sources', 'all'):
            self.history['sources'] = []
        if path_type in ('targets', 'all'):
            self.history['targets'] = []
        if path_type in ('creations', 'all'):
            self.history['creations'] = []
        self.save_history()
    
    def add_symlink(self, source: str, target: str, notes: str = '') -> bool:
        """
        Add a symlink to the managed list.
        
        Args:
            source: Source path
            target: Target symlink path
            notes: Optional user notes
            
        Returns:
            True if added successfully
        """
        symlink_entry = {
            'id': len(self.symlinks['symlinks']) + 1,
            'source': source,
            'target': target,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'active': True,
        }
        
        # Check if this symlink already exists
        for link in self.symlinks['symlinks']:
            if link['target'] == target:
                return False  # Already tracked
        
        self.symlinks['symlinks'].append(symlink_entry)
        self.save_symlinks()
        return True
    
    def remove_symlink(self, target: str) -> bool:
        """
        Remove a symlink from the managed list.
        
        Args:
            target: Target symlink path
            
        Returns:
            True if removed successfully
        """
        original_count = len(self.symlinks['symlinks'])
        self.symlinks['symlinks'] = [
            link for link in self.symlinks['symlinks']
            if link['target'] != target
        ]
        
        if len(self.symlinks['symlinks']) < original_count:
            self.save_symlinks()
            return True
        return False
    
    def get_all_symlinks(self) -> List[dict]:
        """Get all managed symlinks."""
        return self.symlinks.get('symlinks', [])
    
    def update_symlink(self, target: str, notes: str = '', active: bool = True) -> bool:
        """
        Update a symlink's metadata.
        
        Args:
            target: Target symlink path
            notes: Updated notes
            active: Whether symlink is active
            
        Returns:
            True if updated successfully
        """
        for link in self.symlinks['symlinks']:
            if link['target'] == target:
                link['notes'] = notes
                link['active'] = active
                self.save_symlinks()
                return True
        return False
    
    def get_symlink_by_target(self, target: str) -> dict:
        """Get a symlink entry by target path."""
        for link in self.symlinks['symlinks']:
            if link['target'] == target:
                return link
        return None
    
    def verify_symlinks(self) -> dict:
        """
        Verify which tracked symlinks still exist.
        
        Returns:
            Dictionary with status of each symlink
        """
        from pathlib import Path
        
        status = {
            'total': len(self.symlinks['symlinks']),
            'active': 0,
            'broken': 0,
            'missing': 0,
            'symlinks': []
        }
        
        for link in self.symlinks['symlinks']:
            target_path = Path(link['target'])
            
            if target_path.is_symlink():
                status['active'] += 1
                link_status = 'active'
                
                # Check if target exists
                if not target_path.exists():
                    status['broken'] += 1
                    link_status = 'broken'
            else:
                status['missing'] += 1
                link_status = 'missing'
            
            status['symlinks'].append({
                'target': link['target'],
                'source': link['source'],
                'status': link_status,
                'notes': link['notes'],
            })
        
        return status
