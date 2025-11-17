from pathlib import Path
from typing import Optional
from datetime import datetime

class PrivacyLogger:
    """Privacy-focused logging service that sanitizes sensitive information"""
    def __init__(self, enable_debug: bool = False):
        self.enable_debug = enable_debug
        self.user_home = str(Path.home())
    
    def sanitize_path(self, path_str: str) -> str:
        """Replace sensitive path information with generic placeholders"""
        if not path_str:
            return "EMPTY_PATH"

        sanitized = path_str.replace(self.user_home, "<USER_HOME>")
        sensitive_replacements = { "/Users/": "/Users/<USER>/", "C:\\Users\\": "C:\\Users\\<USER>\\",
                "/home/": "/home/<USER>/", "Documents": "<DOCUMENTS>", "Desktop": "<DESKTOP>",
                "Downloads": "<DOWNLOADS>", "Pictures": "<PICTURES>", "Music": "<MUSIC>",
                "Videos": "<VIDEOS>" }
        
        for sensitive, replacement in sensitive_replacements.items():
            if sensitive in sanitized:
                sanitized = sanitized.replace(sensitive, replacement, 1)
        
        return sanitized
    
    def log_error(self, component: str, operation: str, error: Exception, 
                  file_path: Optional[str] = None) -> None:
        """Log errors with privacy protection"""
        if not self.enable_debug:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        sanitized_path = self.sanitize_path(str(file_path)) if file_path else "N/A"
        
        print(f"[{timestamp}] ERROR in {component}.{operation}: "
              f"Path: {sanitized_path}, Error: {type(error).__name__}")
    
    def log_info(self, component: str, message: str, file_path: Optional[str] = None) -> None:
        """Log informational messages with privacy protection"""
        if not self.enable_debug:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        sanitized_path = self.sanitize_path(str(file_path)) if file_path else ""
        
        if file_path:
            print(f"[{timestamp}] {component}: {message} (Path: {sanitized_path})")
        else:
            print(f"[{timestamp}] {component}: {message}")


privacy_logger = PrivacyLogger(enable_debug=False)  # Disabled by default for privacy
