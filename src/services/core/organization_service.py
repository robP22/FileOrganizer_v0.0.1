import uuid
from pathlib import Path
from typing  import List, TYPE_CHECKING
from time    import time

from core.events    import event_bus
from core.protocols import ConfigProvider
from file_operations.file_utils import ensure_directory_exists
from models.operation_result    import OperationProgress, FileOperationResult
from services.config.config_service     import privacy_config
from services.metadata.metadata_service import MetadataService

if TYPE_CHECKING:
    from file_operations.file_service   import FileService

class OrganizationService:
    def __init__(self, file_service: "FileService", config_provider: ConfigProvider = None):
        self.file_service     = file_service
        self.config_provider  = config_provider or privacy_config
        self.metadata_service = MetadataService(self.config_provider)
        event_bus.subscribe("organize_requested", self.handle_organize_request)

    def handle_organize_request(self, event) -> None:
        source_path      = event.data.get("source_path")
        destination_path = event.data.get("destination_path")
        strategy         = event.data.get("strategy") or self.config_provider.get_setting("organization.default_strategy", "smart")
        event_bus.publish("organization_started",
                { "strategy": strategy, "status": "Starting organization process",
                  "source_directory": source_path, "destination_directory": destination_path })

        self.organize_files_by_strategy(source_path, destination_path, strategy)

    def scan_directory(self, source_dir: str) -> List[Path]:
        source_path = Path(source_dir)
        files: list = []
        for item in source_path.iterdir():
            if item.is_file():
                files.append(item)
        return files

    def _create_organizer(self, strategy: str):
        """ Factory method for creating organizers. """
        organizer_map = { "date": "organizers.date_organizer.DateOrganizer",
                "type": "organizers.type_organizer.TypeOrganizer",
                "smart": "organizers.smart_organizer.SmartOrganizer" }
        
        module_path = organizer_map.get(strategy, organizer_map["smart"])
        module_name, class_name = module_path.rsplit('.', 1)
        
        try:
            module = __import__(module_name, fromlist=[class_name])
            organizer_class = getattr(module, class_name)
            return organizer_class(self.metadata_service, self.file_service, event_bus)

        except (ImportError, AttributeError):
            from organizers.smart_organizer import SmartOrganizer
            return SmartOrganizer(self.metadata_service, self.file_service, event_bus)

    def organize_files_by_strategy(self, source_dir: str, destination_dir: str, strategy: str):
        organizer = self._create_organizer(strategy)
        try:
            files_to_organize = self.scan_directory(source_dir)
            operation_id = f"organize_{uuid.uuid4().hex[:8]}"
            progress = OperationProgress(
                    operation_id=operation_id, total_files=len(files_to_organize) )
            
            event_bus.publish("organization_progress",
                    { "progress": progress.get_summary(), "status": "Files discovered" })

            for i, file_path in enumerate(files_to_organize):
                start_time = time()
                progress.current_file = file_path.name
                
                try:
                    destination_path = organizer.get_destination_path(
                            file_path, Path(destination_dir),
                            self.metadata_service.extract_comprehensive_metadata(file_path) )

                    if not ensure_directory_exists(destination_path.parent):
                        raise Exception(f"Failed to create directory")
                        
                    success = self.file_service.move_file(str(file_path), str(destination_path))
                    if not success:
                        raise Exception(f"Failed to move file")
                    
                    processing_time = time() - start_time
                    file_size = file_path.stat().st_size if file_path.exists() else 0

                    result = FileOperationResult( source_file=file_path.name,
                            operation="organize", success=True,
                            destination_path=destination_path.name, processing_time=processing_time,
                            file_size=file_size, original_source_path=str(file_path),
                            organized_destination_path=str(destination_path) )
                    
                    progress.add_result(result)

                    event_bus.publish("organization_progress",
                            { "progress": progress.get_summary(), "current_file": file_path.name,
                              "status": "File moved successfully" })
                    
                    event_bus.publish("file_processed",
                            { "file_name": file_path.name, "strategy_used": strategy,
                              "organizer": organizer.get_strategy_name(), "result": result })
                
                except Exception as e:
                    processing_time = time() - start_time
                    result = FileOperationResult( source_file=file_path.name,
                            operation="organize", success=False, error_message=str(e),
                            processing_time=processing_time )
                    
                    progress.add_result(result)
                    event_bus.publish("file_error",
                            { "file_name": file_path.name, "error": str(e),
                              "result": result })

            # Publish completion with rich summary
            event_bus.publish("organization_completed",
                    { "progress": progress.get_summary(), "strategy_used": strategy,
                      "status": "Organization completed successfully",
                      "failed_operations": progress.get_failed_operations(),
                      "source_directory": source_dir, "destination_directory": destination_dir })
            
        except Exception as e:
            event_bus.publish("organization_failed",
                    { "error": str(e), "status": "Organization failed" })
