import json
import os
from core.protocols import ConfigProvider
from pathlib import Path
from typing  import Dict, Any, Optional


class PrivacyConfig(ConfigProvider):
    def __init__(self):
        self.config_dir      = Path.home() / ".file_organizer"
        self.config_file     = self.config_dir / "privacy_config.json"
        self.ensure_config_dir()
        
        # Default privacy-first settings
        self.default_config  = {
            "privacy": {
                "enable_debug_logging":         False,
                "sanitize_error_messages":      True,
                "local_only_mode":              True,
                "minimize_metadata_collection": False,
                "secure_delete_temp_files":     True,
                "disable_crash_reporting":      True
            },
            "security": {
                "validate_all_paths":           True,
                "block_system_directories":     True,
                "require_path_confirmation":    True,
                "enable_symlink_protection":    True,
                "maximum_file_size_mb":         100,
                "scan_for_executables":         True
            },
            "metadata": {
                "extract_gps_location":         True,  # User choice for photos
                "extract_camera_info":          True,
                "extract_personal_info":        True,  # Author names, etc.
                "cache_metadata_locally":       True,
                "clear_cache_on_exit":          False
            },
            "ui": {
                "show_file_paths_in_ui":        True,
                "confirm_sensitive_operations": True,
                "remember_directory_choices":   False,  # Privacy-focused default
                "auto_save_window_state":       False
            },
            "organization": {
                "default_strategy": "smart",
                "create_date_folders": True,
                "preserve_folder_structure": False,
                "file_extensions": {
                    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                    "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
                    "videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv"],
                    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"]
                }
            }
        }
        
        self.config          = self.load_config()
    
    def ensure_config_dir(self) -> None:
        """Create config directory with appropriate permissions"""
        try:
            self.config_dir.mkdir(mode=0o700, exist_ok=True)  # User-only access
        except OSError:
            # Fallback to current directory if home directory not writable
            self.config_dir  = Path.cwd() / ".file_organizer"
            self.config_file = self.config_dir / "privacy_config.json"
            self.config_dir.mkdir(mode=0o700, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with privacy-first defaults"""
        if not self.config_file.exists():
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                user_config  = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            config           = self.default_config.copy()
            self._deep_merge(config, user_config)
            return config
            
        except (json.JSONDecodeError, OSError):
            # Return defaults if config is corrupted
            return self.default_config.copy()
    
    def save_config(self) -> None:
        """Save configuration with secure permissions"""
        try:
            # Create backup of existing config
            if self.config_file.exists():
                backup_file  = self.config_file.with_suffix('.json.backup')
                self.config_file.rename(backup_file)
            
            # Write new config with user-only permissions
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)
            
            # Set secure permissions (user-only read/write)
            os.chmod(self.config_file, 0o600)
            
        except OSError:
            pass  # Fail silently to avoid breaking application
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge override config into base config"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key]    = value
    
    def get_privacy_setting(self, key: str) -> Any:
        """Get privacy setting with safe default"""
        return self.config.get("privacy", {}).get(key, False)
    
    def get_security_setting(self, key: str) -> Any:
        """Get security setting with safe default"""
        return self.config.get("security", {}).get(key, True)
    
    def get_metadata_setting(self, key: str) -> Any:
        """Get metadata setting with privacy-conscious default"""
        return self.config.get("metadata", {}).get(key, False)
    
    def get_ui_setting(self, key: str) -> Any:
        """Get UI setting with privacy-conscious default"""
        return self.config.get("ui", {}).get(key, False)
    
    def update_privacy_setting(self, key: str, value: Any) -> None:
        """Update privacy setting and save"""
        if "privacy" not in self.config:
            self.config["privacy"]  = {}
        self.config["privacy"][key] = value
        self.save_config()
    
    # ConfigProvider abstract method implementations
    def set_privacy_setting(self, key: str, value: Any) -> None:
        """Set a privacy setting value"""
        self.update_privacy_setting(key, value)
    
    def set_metadata_setting(self, key: str, value: Any) -> None:
        """Set a metadata setting value"""
        if "metadata" not in self.config:
            self.config["metadata"] = {}
        self.config["metadata"][key] = value
        self.save_config()
    
    def set_security_setting(self, key: str, value: Any) -> None:
        """Set a security setting value"""
        if "security" not in self.config:
            self.config["security"] = {}
        self.config["security"][key] = value
        self.save_config()
    
    def enable_debug_mode(self, enable: bool = True) -> None:
        """Enable/disable debug logging with user consent"""
        self.update_privacy_setting("enable_debug_logging", enable)
        
        # Update global privacy logger with lazy import
        try:
            from services.config.privacy_logger import privacy_logger
            privacy_logger.enable_debug = enable
        except ImportError:
            pass  # Privacy logger not available
    
    def get_privacy_summary(self) -> str:
        """Get human-readable privacy summary for user"""
        privacy = self.config.get("privacy", {})
        
        summary = "🔒 Privacy Settings Summary:\n"
        summary += f"  • Debug Logging: {'Enabled' if privacy.get('enable_debug_logging') else 'Disabled'}\n"
        summary += f"  • Local Only Mode: {'Yes' if privacy.get('local_only_mode') else 'No'}\n"
        summary += f"  • Error Message Sanitization: {'Yes' if privacy.get('sanitize_error_messages') else 'No'}\n"
        summary += f"  • Secure Temp File Deletion: {'Yes' if privacy.get('secure_delete_temp_files') else 'No'}\n"
        
        metadata = self.config.get("metadata", {})
        summary += f"  • GPS Location Extraction: {'Yes' if metadata.get('extract_gps_location') else 'No'}\n"
        summary += f"  • Personal Info Extraction: {'Yes' if metadata.get('extract_personal_info') else 'No'}\n"
        
        return summary

    def get_setting(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set_setting(self, key: str, value: Any):
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()

    def get_organization_settings(self) -> Dict[str, Any]:
        return self.config.get("organization", {})

# Global configuration instance
privacy_config = PrivacyConfig()
