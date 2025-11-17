from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from services.core.validation_service import ValidationService

class ValidationServiceManager:
    """Manager for managing ValidationService instances"""
    _instance: Optional['ValidationService'] = None
    
    @classmethod
    def get_instance(cls) -> 'ValidationService':
        """Get singleton ValidationService instance"""
        if cls._instance is None:
            # Lazy import to avoid circular dependencies
            from services.core.validation_service import ValidationService
            cls._instance = ValidationService()
        return cls._instance
    
    @classmethod
    def create_new_instance(cls) -> 'ValidationService':
        """Create a new ValidationService instance (for testing)"""
        # Lazy import to avoid circular dependencies
        from services.core.validation_service import ValidationService
        return ValidationService()
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)"""
        cls._instance = None


# Convenience function for easy access
def get_validator() -> 'ValidationService':
    """Get the shared ValidationService instance"""
    return ValidationServiceManager.get_instance()
