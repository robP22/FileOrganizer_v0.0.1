from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

class MetadataExtractor(ABC):
    """Protocol for metadata extraction services"""
    @abstractmethod
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a file"""
        pass


class ConfigProvider(ABC):
    """Abstract interface for configuration access"""
    @abstractmethod
    def get_privacy_setting(self, key: str) -> Any:
        """Get a privacy setting value"""
        pass
    
    @abstractmethod
    def get_metadata_setting(self, key: str) -> Any:
        """Get a metadata setting value"""
        pass
    
    @abstractmethod
    def get_security_setting(self, key: str) -> Any:
        """Get a security setting value"""
        pass
    
    @abstractmethod
    def get_privacy_summary(self) -> str:
        """Get a summary of privacy settings"""
        pass
    
    @abstractmethod
    def set_privacy_setting(self, key: str, value: Any) -> None:
        """Set a privacy setting value"""
        pass
    
    @abstractmethod
    def set_metadata_setting(self, key: str, value: Any) -> None:
        """Set a metadata setting value"""
        pass
    
    @abstractmethod
    def set_security_setting(self, key: str, value: Any) -> None:
        """Set a security setting value"""
        pass
    
    @abstractmethod
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'organization.default_strategy')"""
        pass

    @abstractmethod
    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value using dot notation"""
        pass

    @abstractmethod
    def save_config(self) -> None:
        """Save configuration to disk"""
        pass
