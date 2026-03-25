"""JSON storage handler with exception handling."""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

class StorageException(Exception):
    """Custom exception for storage operations."""
    pass

class JSONStorage:
    """Handle JSON file operations with exception handling."""
    
    def __init__(self, data_dir: str = "data"):
        self._data_dir = data_dir
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """Ensure data directory exists."""
        try:
            if not os.path.exists(self._data_dir):
                os.makedirs(self._data_dir)
        except OSError as e:
            raise StorageException(f"Failed to create data directory: {e}")
    
    def save_data(self, filename: str, data: Any) -> bool:
        """
        Save data to JSON file with exception handling.
        
        Args:
            filename: Name of the file
            data: Data to save
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            StorageException: If save operation fails
        """
        filepath = os.path.join(self._data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        
        except TypeError as e:
            raise StorageException(f"Data serialization error: {e}")
        
        except IOError as e:
            raise StorageException(f"File write error: {e}")
        
        except Exception as e:
            raise StorageException(f"Unexpected error during save: {e}")
    
    def load_data(self, filename: str) -> Any:
        """
        Load data from JSON file with exception handling.
        
        Args:
            filename: Name of the file
        
        Returns:
            Loaded data or None if file doesn't exist
        
        Raises:
            StorageException: If load operation fails
        """
        filepath = os.path.join(self._data_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except json.JSONDecodeError as e:
            raise StorageException(f"Invalid JSON format: {e}")
        
        except IOError as e:
            raise StorageException(f"File read error: {e}")
        
        except Exception as e:
            raise StorageException(f"Unexpected error during load: {e}")
    
    def delete_data(self, filename: str) -> bool:
        """
        Delete JSON file with exception handling.
        
        Args:
            filename: Name of the file
        
        Returns:
            True if successful, False if file doesn't exist
        
        Raises:
            StorageException: If delete operation fails
        """
        filepath = os.path.join(self._data_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return False
            
            os.remove(filepath)
            return True
        
        except OSError as e:
            raise StorageException(f"File deletion error: {e}")
        
        except Exception as e:
            raise StorageException(f"Unexpected error during delete: {e}")
    
    def list_files(self) -> List[str]:
        """
        List all JSON files in data directory.
        
        Returns:
            List of filenames
        
        Raises:
            StorageException: If listing fails
        """
        try:
            if not os.path.exists(self._data_dir):
                return []
            
            return [f for f in os.listdir(self._data_dir) 
                   if f.endswith('.json')]
        
        except OSError as e:
            raise StorageException(f"Directory listing error: {e}")
    
    def backup_data(self, filename: str) -> bool:
        """
        Create backup of JSON file.
        
        Args:
            filename: Name of the file to backup
        
        Returns:
            True if successful
        
        Raises:
            StorageException: If backup fails
        """
        filepath = os.path.join(self._data_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filename}.backup_{timestamp}"
            backup_filepath = os.path.join(self._data_dir, backup_filename)
            
            with open(filepath, 'r', encoding='utf-8') as source:
                data = json.load(source)
            
            with open(backup_filepath, 'w', encoding='utf-8') as backup:
                json.dump(data, backup, indent=4, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            raise StorageException(f"Backup operation failed: {e}")
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """
        Get information about a JSON file.
        
        Args:
            filename: Name of the file
        
        Returns:
            Dictionary with file information
        
        Raises:
            StorageException: If operation fails
        """
        filepath = os.path.join(self._data_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return {"exists": False}
            
            stat = os.stat(filepath)
            
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "size_kb": stat.st_size / 1024,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        
        except OSError as e:
            raise StorageException(f"Failed to get file info: {e}")

# Convenience functions with exception handling
def safe_save(storage: JSONStorage, filename: str, data: Any) -> tuple:
    """
    Safely save data with exception handling.
    
    Returns:
        Tuple of (success: bool, error_message: str or None)
    """
    try:
        storage.save_data(filename, data)
        return (True, None)
    except StorageException as e:
        return (False, str(e))
    except Exception as e:
        return (False, f"Unexpected error: {e}")

def safe_load(storage: JSONStorage, filename: str) -> tuple:
    """
    Safely load data with exception handling.
    
    Returns:
        Tuple of (data: Any or None, error_message: str or None)
    """
    try:
        data = storage.load_data(filename)
        return (data, None)
    except StorageException as e:
        return (None, str(e))
    except Exception as e:
        return (None, f"Unexpected error: {e}")
