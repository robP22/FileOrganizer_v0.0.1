from core.events import event_bus
from pathlib import Path
from typing import List

class OrganizationService:
    """
    Handles file organization logic and operation
    """

    def __init__(self):
        event_bus.subscribe("organize_requested", self.handle_organize_request)

    def handle_organize_request(self, event):
        """ Handle orgaization request from GUI """
        source_path = event.data.get("source_path")
        destination_path = event.data.get("destination_path")

        files_to_organize = self.scan_directory(source_path)
        print(f"Organization requested: {source_path} -> {destination_path}")

        for file_path in files_to_organize:
            print(f"  - {file_path.name}")

        event_bus.publish("organization_completed", {
            "message": f"Found {len(files_to_organize)} files",
            "file_count": len(files_to_organize)
            })
        

    def scan_directory(self, source_dir: str) -> List[Path]:
        """
        Scans the source directory and returns a list of files.

        Args:
            source_dir: Path to the source directory

        Returns:
            List[Path]: List of files in the source directory
        """
        source_path = Path(source_dir)
        files = []

        for item in source_path.iterdir():
            if item.is_file():
                files.append(item)

        return files
    