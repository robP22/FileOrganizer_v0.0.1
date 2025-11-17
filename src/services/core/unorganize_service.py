from core.events    import event_bus
from pathlib        import Path
from typing         import List, TYPE_CHECKING
from time           import time
import uuid

from file_operations.file_utils import ensure_directory_exists
from models.operation_result    import OperationProgress, FileOperationResult

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from file_operations.file_service import FileService

class UnorganizeService:
    """
    Independent directory unorganizing microservice.
    Takes any directory and unorganizes all files to a target directory.
    """
    
    def __init__(self, file_service: "FileService"):
        self.file_service = file_service
        event_bus.subscribe("unorganize_requested", self.handle_unorganize_request)
    
    def handle_unorganize_request(self, event):
        """Handle unorganize request from GUI"""
        source_directory = event.data.get("source_directory")
        target_directory = event.data.get("target_directory")
        self.unorganize_directory(source_directory, target_directory)
    
    def unorganize_directory(self, source_dir: str, target_dir: str) -> bool:
        """ Unorganize a directory by moving all files from subdirectories to target directory. """
        try:
            source_path = Path(source_dir)
            target_path = Path(target_dir)
            
            if not source_path.exists():
                event_bus.publish("unorganize_failed",
                        { "error": f"Source directory does not exist: {source_dir}" })
                return False
            
            if not ensure_directory_exists(target_path):
                event_bus.publish("unorganize_failed",
                        { "error": f"Failed to create target directory: {target_dir}" })
                return False

            all_files = self._scan_directory_recursive(source_path)
            if not all_files:
                event_bus.publish("unorganize_completed",
                        { "message": "No files found to unorganize", "files_processed": 0 })
                return True
            
            # Create progress tracker
            operation_id = f"unorganize_{uuid.uuid4().hex[:8]}"
            progress = OperationProgress(
                    operation_id=operation_id, total_files=len(all_files))
            
            event_bus.publish("unorganize_started",
                    { "operation_id": operation_id, "file_count": len(all_files),
                      "source_directory": source_dir, "target_directory": target_dir })

            # Begin processing files
            for file_path in all_files:
                self._process_file(file_path, target_path, progress)
            
            event_bus.publish("unorganize_completed",
                    { "progress": progress.get_summary(), "operation_id": operation_id,
                      "files_processed": progress.processed_files,
                      "failed_operations": progress.get_failed_operations() })

            return True
            
        except Exception as e:
            event_bus.publish("unorganize_failed", { "error": str(e) })
            return False
    
    def _scan_directory_recursive(self, source_path: Path) -> List[Path]:
        """Recursively scan directory for all files"""
        files = []

        def scan_recursive(path: Path):
            try:
                for item in path.iterdir():
                    if item.is_file():
                        files.append(item)
                    elif item.is_dir():
                        scan_recursive(item)

            except PermissionError:
                # Skip directories we can't access
                pass
        
        scan_recursive(source_path)
        return files
    
    def _process_file(self, file_path: Path, target_directory: Path, progress: OperationProgress):
        """Process a single file for unorganizing"""
        start_time = time()
        progress.current_file = file_path.name
        
        try:
            destination_path = self._get_unique_destination_path(target_directory, file_path.name)
            success = self.file_service.move_file(str(file_path), str(destination_path))

            processing_time = time() - start_time
            file_size = file_path.stat().st_size if file_path.exists() else 0
            
            result = FileOperationResult(
                    source_file=file_path.name, operation="unorganize",
                    success=success, destination_path=destination_path.name,
                    processing_time=processing_time, file_size=file_size )
            
            if not success:
                result.error_message = "Failed to move file"

            progress.add_result(result)
            
            event_bus.publish("unorganize_progress",
                    { "progress": progress.get_summary(), "current_file": file_path.name,
                      "status": "File moved" if success else "File move failed" })
            
        except Exception as e:
            processing_time = time() - start_time
            result = FileOperationResult( source_file=file_path.name,
                    operation="unorganize", success=False, error_message=str(e),
                    processing_time=processing_time )
            
            progress.add_result(result)
            event_bus.publish("file_error",
                    { "file_name": file_path.name, "error": str(e),
                      "operation": "unorganize" })
    
    def _get_unique_destination_path(self, target_directory: Path, filename: str) -> Path:
        """Get a unique destination path, handling filename conflicts"""
        destination = target_directory / filename
        if not destination.exists():
            return destination

        stem    = Path(filename).stem
        suffix  = Path(filename).suffix
        counter = 1
        
        while destination.exists():
            new_filename = f"{stem}_unorg_{counter}{suffix}"
            destination  = target_directory / new_filename
            counter += 1
        
        return destination
