from .base_organizer import BaseOrganizer
from core.validation_manager import get_validator
from datetime import datetime
from pathlib  import Path
from typing   import Dict, Tuple

class SmartOrganizer(BaseOrganizer):
    def __init__(self, metadata_service, file_service, event_bus, validator=None, file_utils=None):
        super().__init__(metadata_service, file_service, event_bus, file_utils)
        from file_operations.file_types import FILE_TYPE_CATEGORIES, MEDIA_EXTENSIONS, DOCUMENT_EXTENSIONS

        self.file_type_categories = FILE_TYPE_CATEGORIES
        self.media_types    = MEDIA_EXTENSIONS
        self.document_types = DOCUMENT_EXTENSIONS
        self.recent_days_threshold = 30
        self.large_collection_size = 100

        self.validator = validator or get_validator()
    
    def get_strategy_name(self) -> str:
        return "Smart Organization"
    
    def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
        file_extension = file_path.suffix.lower()
        
        if not self.validator.validate_file_extension(file_extension):
            raise ValueError(f"Invalid or dangerous file extension: {file_extension}")
        
        organization_date = self.metadata_service.get_best_organization_date(file_path)
        organization_info = self.metadata_service.get_organization_info(file_path)

        strategy = self._select_strategy(file_path, file_extension, organization_info, organization_date)
        if strategy == 'date_primary':
            return self._organize_by_date_primary(file_path, destination_root, organization_date)
        elif strategy == 'type_date':
            return self._organize_by_type_then_date(file_path, destination_root, organization_date)
        elif strategy == 'date_type':
            return self._organize_by_date_then_type(file_path, destination_root, organization_date)
        else:
            return self._organize_by_type_primary(file_path, destination_root)
    
    def _select_strategy(self, file_path: Path, file_extension: str, organization_info: Dict, organization_date) -> str:
        now = datetime.now()

        if organization_date:
            days_old  = (now - organization_date).days
            is_recent = days_old <= self.recent_days_threshold
        else:
            mod_time  = self.file_utils.get_file_modification_date(file_path)
            is_recent = (now - mod_time).days <= self.recent_days_threshold
        
        if is_recent:
            return 'date_primary'
        if file_extension in self.media_types and self._has_rich_metadata(organization_info):
            return 'date_type'
        if file_extension in self.document_types:
            return 'date_type'
        
        return 'date_type'
    
    def _has_rich_metadata(self, organization_info: Dict) -> bool:
        rich_fields = ['camera', 'has_location', 'artist', 'album', 'author', 'creator']
        return any(organization_info.get(field) for field in rich_fields)
    
    def _get_organization_date(self, file_path: Path, organization_date) -> datetime:
        """Get organization date, falling back to file modification time."""
        if not organization_date:
            return self.file_utils.get_file_modification_date(file_path)
        return organization_date
    
    def _get_date_folders(self, organization_date: datetime) -> Tuple[str, str]:
        """Get year and month folder names from date."""
        return organization_date.strftime("%Y"), organization_date.strftime("%m")
    
    def _validate_destination_path(self, destination_path: Path) -> Path:
        """Validate and return safe destination path."""
        # Validate path safety
        if not self.validator.validate_and_sanitize_path(str(destination_path)):
            raise ValueError(f"Invalid destination path: {destination_path}")
        return destination_path
    
    def _organize_by_date_primary(self, file_path: Path, destination_root: Path, organization_date) -> Path:
        organization_date  = self._get_organization_date(file_path, organization_date)
        year_folder, month_folder = self._get_date_folders(organization_date)
        destination_folder = destination_root / year_folder / month_folder
        validated_path     = self._validate_destination_path(destination_folder)

        return self.file_utils.get_unique_file_path(validated_path, file_path.name)
    
    def _organize_by_type_then_date(self, file_path: Path, destination_root: Path, organization_date) -> Path:
        file_category      = self._get_file_category(file_path.suffix.lower())
        organization_date  = self._get_organization_date(file_path, organization_date)
        year_folder, month_folder = self._get_date_folders(organization_date)
        destination_folder = destination_root / file_category / year_folder / month_folder
        validated_path     = self._validate_destination_path(destination_folder)

        return self.file_utils.get_unique_file_path(validated_path, file_path.name)
    
    def _organize_by_date_then_type(self, file_path: Path, destination_root: Path, organization_date) -> Path:
        organization_date  = self._get_organization_date(file_path, organization_date)
        year_folder, month_folder = self._get_date_folders(organization_date)
        file_category      = self._get_file_category(file_path.suffix.lower())
        destination_folder = destination_root / year_folder / month_folder / file_category
        validated_path     = self._validate_destination_path(destination_folder)

        return self.file_utils.get_unique_file_path(validated_path, file_path.name)
    
    def _organize_by_type_primary(self, file_path: Path, destination_root: Path) -> Path:
        file_category      = self._get_file_category(file_path.suffix.lower())
        destination_folder = destination_root / file_category
        validated_path     = self._validate_destination_path(destination_folder)

        return self.file_utils.get_unique_file_path(validated_path, file_path.name)
    
    def _get_file_category(self, file_extension: str) -> str:
        """Get file category for organization."""
        for category, extensions in self.file_type_categories.items():
            if file_extension in extensions:
                return category
        return 'Other'
