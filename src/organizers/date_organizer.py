from datetime import datetime
from pathlib  import Path
from typing   import Dict

from .base_organizer import BaseOrganizer


class DateOrganizer(BaseOrganizer):
    def get_strategy_name(self) -> str:
        return "Date-based Organization"
    
    def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
        # Input validation is now handled by BaseOrganizer._validate_inputs()
        organization_info = self.metadata_service.get_organization_info(file_path)
        organization_date = organization_info.get('date')
        
        if not organization_date:
            organization_date = self.file_utils.get_file_modification_date(file_path)
        
        year_folder  = organization_date.strftime("%Y")
        month_folder = organization_date.strftime("%m")
        
        destination_folder = destination_root / year_folder / month_folder
        
        return self.file_utils.get_unique_file_path(destination_folder, file_path.name)
