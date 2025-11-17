from abc       import ABC, abstractmethod
from pathlib   import Path
from typing    import Dict, List, Any

class BaseOrganizer(ABC):
    def __init__(self, metadata_service, file_service, event_bus, file_utils=None):
        self.metadata_service = metadata_service
        self.file_service     = file_service
        self.file_utils       = file_utils or self._get_default_file_utils()
        self.event_bus        = event_bus

        self.errors = 0
        self.files_processed = 0
        self.files_moved     = 0

    def _get_default_file_utils(self):
        """Lazy load file utilities to reduce coupling"""
        from file_operations import file_utils
        return file_utils
    
    def reset_counters(self):
        self.files_processed = 0
        self.files_moved     = 0
        self.errors          = 0
    
    @abstractmethod
    def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        pass
    
    def organize_files(self, file_paths: List[Path], destination_root: Path) -> Dict[str, Any]:
        self.reset_counters()
        destination_root.mkdir(parents=True, exist_ok=True)
        
        total_files = len(file_paths)
        self.event_bus.publish('organization_started',
                { 'strategy': self.get_strategy_name(), 'total_files': total_files,
                  'destination': str(destination_root) })
        
        for file_path in file_paths:
            try:
                self._organize_single_file(file_path, destination_root)
                self.files_processed += 1
                
                progress = (self.files_processed / total_files) * 100
                self.event_bus.publish('organization_progress',
                        { 'processed': self.files_processed, 'total': total_files,
                          'progress': progress, 'current_file_name': file_path.name })
            except Exception as e:
                self.errors += 1
                self.event_bus.publish('organization_error',
                        { 'file_name': file_path.name, 'error': str(e) })
        
        self.event_bus.publish('organization_completed',
                { 'strategy': self.get_strategy_name(), 'processed': self.files_processed,
                  'moved': self.files_moved, 'errors': self.errors })
        
        return { 'strategy': self.get_strategy_name(), 'files_processed': self.files_processed,
                 'files_moved': self.files_moved, 'errors': self.errors,
                 'success_rate': (self.files_moved / self.files_processed * 100) if self.files_processed > 0 else 0 }
    
    def _validate_inputs(self, file_path: Path, destination_root: Path):
        """Common input validation for all organizers"""
        if not file_path or not file_path.exists():
            raise ValueError(f"Invalid or non-existent file path: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        if not destination_root:
            raise ValueError("Destination root cannot be empty")
    
    def _validate_security(self, file_path: Path):
        """Security validation for all organizers"""
        if hasattr(self, 'validator') and self.validator:
            if not self.validator.validate_file_extension(file_path.suffix):
                raise ValueError(f"Dangerous file extension: {file_path.suffix}")
    
    def _extract_metadata_safely(self, file_path: Path) -> Dict:
        """Extract metadata with error handling"""
        try:
            return self.metadata_service.extract_comprehensive_metadata(file_path)
        except Exception as e:
            # Log the error, continue with basic metadata
            self.event_bus.publish('metadata_extraction_failed',
                    { 'file_name': file_path.name, 'error': str(e) })

            return { 'type': 'unknown', 'creation_date': None,
                     'modification_date': file_path.stat().st_mtime }
    
    def _organize_single_file(self, file_path: Path, destination_root: Path):
        self._validate_inputs(file_path, destination_root)
        self._validate_security(file_path)

        metadata         = self._extract_metadata_safely(file_path)
        destination_path = self.get_destination_path(file_path, destination_root, metadata)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.file_service.move_file(str(file_path), str(destination_path)):
            self.files_moved += 1
        else:
            raise RuntimeError(f"Failed to move file from {file_path} to {destination_path}")
