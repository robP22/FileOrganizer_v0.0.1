import os
import platform
import subprocess

from typing import Optional
from pathlib import Path, PurePath
from core.events import event_bus
from PySide6.QtWidgets import QFileDialog


class FileService:
    """ Handles file operations with the native file manager """

    def __init__(self):
        event_bus.subscribe("file_manager_requested", self.handle_file_manager_request)


    def _validate_and_sanitize_path(self, path_input: Optional[str]) -> Optional[str]:
        """
        Validates and sanitizes the input path.
        
        Returns:
            str: Safe absolute path or None if invalid
            
        Security Protections:
        - Path traversal prevention (../)
        - Null byte injection prevention
        - System directory protection
        - Path length limits
        """
        if not path_input:
            return os.getcwd() # Safe default to current working directory
        
        try:
            # Remove null bytes (null byte injection prevention)
            clean_path = path_input.replace('\0', '')
            # Prevent path traversal attacks
            path = Path(clean_path).resolve()
            # Prevent access to system directories
            abs_path = str(path.absolute())

            if not self._is_safe_directory(abs_path):
                return None
            
            if len(abs_path) > 4096: # Path length limit
                return None
            
            return abs_path
        
        except (OSError, ValueError, RuntimeError):
            return None


    def _is_safe_directory(self, abs_path: str) -> bool:
        """
        Check if the path is safe (not a system directory).
        
        Args:
            abs_path: Absolute path to check
            
        Returns:
            bool: True if safe, False otherwise
        """
        path_lower = abs_path.lower()

        dangerous_paths = {
        # macOS system directories
        '/system', '/usr/bin', '/usr/sbin', '/bin', '/sbin',
        '/etc', '/var/log', '/private/etc', '/private/var/log',
        
        # Windows system directories  
        'c:\\windows', 'c:\\program files', 'c:\\program files (x86)',
        'c:\\programdata', 'c:\\system volume information',
        
        # Linux system directories
        '/boot', '/dev', '/proc', '/sys', '/run'
        }

        for danger in dangerous_paths:
            if path_lower.startswith(danger.lower()):
                return False
            
        try:
            path_obj = Path(abs_path)
            return path_obj.exists() and path_obj.is_dir()
        
        except (OSError, ValueError):
            return False


    def handle_file_manager_request(self, event):
        """ Handle file manager request from GUI """
        directory_type = event.data.get("directory_type")
        directory_path = event.data.get("directory_path")

        success, selected_path = self._open_native_file_manager(directory_path)

        if success and selected_path:
            event_bus.publish("file_manager_opened", {
                "directory_type": directory_type,
                "selected_path": selected_path
                })
        else:
            event_bus.publish("file_manager_failed", {
                "directory_type": directory_type
                })


    def _open_native_file_manager(self, directory_path: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Opens native directory selection dialog and captures selected path.

        Args:
            directory_path: Starting directory (optional)
        
        Returns:
            tuple: (success: bool, selected_path: str or None)
        """
        try:
            # Use Qt's native directory dialog
            selected_directory = QFileDialog.getExistingDirectory(
                None, "Select Directory",
                directory_path or os.getcwd(),
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
                )
            
            if selected_directory:
                safe_path = self._validate_and_sanitize_path(selected_directory)
                if safe_path:
                    return True, safe_path  # safe
                else:
                    return False, None      # unsafe
            else:
                return False, None          # cancelled
                
        except Exception as e:
            return False, None


    def validate_directory(self, directory_path: str) -> bool:
        """
        Validates that a directory path exists and is accessible.
        
        Args:
            directory_path: Path to validate
            
        Returns:
            bool: True if valid directory, False otherwise
        """
        safe_path = self._validate_and_sanitize_path(directory_path)
        return safe_path is not None