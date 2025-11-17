import os
import unicodedata
from typing  import Optional
from pathlib import Path

class ValidationService:
    """Centralized validation and security service for file operations"""
    def __init__(self):
        self.max_path_length = 4096
        self.dangerous_paths = {
                # macOS system directories
                '/system', '/usr/bin', '/usr/sbin', '/bin', '/sbin',
                '/etc', '/var/log', '/private/etc', '/private/var/log',

                # Windows system directories
                'c:\\windows', 'c:\\program files', 'c:\\program files (x86)',
                'c:\\programdata', 'c:\\system volume information',

                # Linux system directories
                '/boot', '/dev', '/proc', '/sys', '/run'
                }

    def validate_and_sanitize_path(self, path_input: Optional[str]) -> Optional[str]:
        """
        Validates and sanitizes the input path for both files and directories.
        Returns:
            str: Safe absolute path or None if invalid
        """
        if not path_input:
            return os.getcwd()  # Safe default to current working directory
        
        try:
            # Remove null bytes (null byte injection prevention)
            clean_path = path_input.replace('\0', '')
            
            # Prevent path traversal attacks
            path     = Path(clean_path).resolve()
            abs_path = str(path.absolute())

            if len(abs_path) > self.max_path_length:
                return None
            if not self.is_symlink_safe(path):
                return None
            if not self.is_safe_path(abs_path):
                return None
            
            return abs_path
        
        except (OSError, ValueError, RuntimeError) as e:
            return None

    def is_safe_path(self, abs_path: str) -> bool:
        """
        Check if the path is safe (not a system directory).
        Works for both files and directories.
        """
        path_lower = abs_path.lower()

        for danger in self.dangerous_paths:
            if path_lower.startswith(danger.lower()):
                return False
            
        try:
            path_obj = Path(abs_path)

            if path_obj.is_file():
                return True

            elif path_obj.exists() and path_obj.is_dir():
                return True

            else:
                # Walk up the path until we find an existing directory
                current_path = path_obj
                while not current_path.exists() and current_path != current_path.parent:
                    current_path = current_path.parent

                if current_path.exists() and current_path.is_dir():
                    try:
                        path_obj.relative_to(current_path)
                        return True
                    except ValueError:
                        return False
                
                return False
        
        except (OSError, ValueError):
            return False

    def is_symlink_safe(self, path: Path) -> bool:
        """ Check if path or any parent contains symlinks. """
        try:
            if path.is_symlink():
                return False

            for parent in path.parents:
                if parent.is_symlink():
                    return False
            
            return True
        except (OSError, ValueError):
            return False

    def validate_filename(self, filename: str) -> bool:
        """ Validate individual filename for security. """
        if not filename:
            return False

        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0', '/', '\\']
        if any(char in filename for char in dangerous_chars):
            return False
        
        # Check for control characters
        if any(ord(char) < 32 for char in filename):
            return False

        # Check for Unicode normalization attacks
        try:
            normalized = unicodedata.normalize('NFKC', filename)
            if normalized != filename:
                return False
        except (ValueError, TypeError):
            return False

        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
            'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        if filename.upper() in reserved_names:
            return False

        if len(filename) > 255:  # Most filesystems have 255 char limit
            return False
        
        return True

    def validate_directory(self, directory_path: str) -> bool:
        """ Validates that a directory path exists and is accessible. """
        safe_path = self.validate_and_sanitize_path(directory_path)
        if not safe_path:
            return False
            
        try:
            path_obj = Path(safe_path)
            return path_obj.exists() and path_obj.is_dir()
        except (OSError, ValueError):
            return False

    def validate_file_extension(self, file_extension: str) -> bool:
        """ Validate file extension for safety. """
        if not file_extension:
            return False
            
        # Remove leading dot and convert to lowercase
        ext = file_extension.lstrip('.').lower()

        dangerous_extensions = {
            'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
            'app', 'deb', 'pkg', 'dmg', 'rpm', 'run', 'msi', 'dll', 'so'
        }
        if ext in dangerous_extensions:
            return False

        if len(ext) > 10:
            return False

        if not ext.isalnum():
            return False
            
        return True
