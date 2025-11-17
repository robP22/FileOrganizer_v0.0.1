from typing import Any
from core.protocols import ConfigProvider

class ConfigAdapter(ConfigProvider):
    """Adapter that wraps the existing privacy_config to provide interface"""
    def __init__(self, config_instance):
        self._config = config_instance
    
    def get_privacy_setting(self, key: str) -> Any:
        return self._config.get_privacy_setting(key)
    
    def get_metadata_setting(self, key: str) -> Any:
        return self._config.get_metadata_setting(key)
    
    def get_security_setting(self, key: str) -> Any:
        return self._config.get_security_setting(key)
    
    def get_privacy_summary(self) -> str:
        return self._config.get_privacy_summary()
    
    def set_privacy_setting(self, key: str, value: Any) -> None:
        self._config.config['privacy'][key] = value
    
    def set_metadata_setting(self, key: str, value: Any) -> None:
        self._config.config['metadata'][key] = value
    
    def set_security_setting(self, key: str, value: Any) -> None:
        self._config.config['security'][key] = value

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._config.get_setting(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        self._config.set_setting(key, value)
    
    def save_config(self) -> None:
        self._config.save_config()
