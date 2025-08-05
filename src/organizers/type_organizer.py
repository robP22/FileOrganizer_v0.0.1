from pathlib import Path
from typing  import Dict

from .base_organizer import BaseOrganizer


class TypeOrganizer(BaseOrganizer):
    def __init__(self, metadata_service, file_service, event_bus, file_utils=None):
        super().__init__(metadata_service, file_service, event_bus, file_utils)
        # Lazy load file types to reduce coupling
        from file_operations.file_types import FILE_TYPE_CATEGORIES
        self.file_type_categories = FILE_TYPE_CATEGORIES
    def get_strategy_name(self) -> str:
        return "Type-based Organization"
    
    def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
        # Input validation is now handled by BaseOrganizer._validate_inputs()
        file_extension     = file_path.suffix.lower()
        category           = self._get_file_category(file_extension, metadata)
        destination_folder = destination_root / category
        
        return self.file_utils.get_unique_file_path(destination_folder, file_path.name)
    
    def _get_file_category(self, file_extension: str, metadata: Dict) -> str:
        for category, extensions in self.file_type_categories.items():
            if file_extension in extensions:
                return category
        
        file_type = metadata.get('type', '').lower()
        if 'image' in file_type:
            return 'Images'
        elif 'video' in file_type:
            return 'Videos'
        elif 'audio' in file_type:
            return 'Audio'
        elif 'document' in file_type or 'text' in file_type:
            return 'Documents'
        
        return 'Other'
