import os
import shutil

from typing import Optional
from pathlib import Path
from core.events import event_bus
from core.validation_manager import get_validator
from PySide6.QtWidgets import QFileDialog
from .file_utils import ensure_directory_exists

class FileService:
    """ Handles file operations with the native file manager """
    def __init__(self, validator=None):
        self.validator = validator or get_validator()
        event_bus.subscribe("file_manager_requested", self.handle_file_manager_request)

    def handle_file_manager_request(self, event):
        """ Handle file manager request from GUI """
        directory_type = event.data.get("directory_type")
        directory_path = event.data.get("directory_path")

        success, selected_path = self._open_native_file_manager(directory_path)
        if success and selected_path:
            event_bus.publish("file_manager_opened", {
                "directory_type": directory_type,
                "selected_path": selected_path
                })
        else:
            event_bus.publish("file_manager_failed", {
                "directory_type": directory_type
                })

    def _open_native_file_manager(self, directory_path: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """ Opens native directory selection dialog and captures selected path. """
        try:
            selected_directory = QFileDialog.getExistingDirectory(
                    None, "Select Directory", directory_path or os.getcwd(),
                    QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks )
            
            if selected_directory:
                safe_path = self.validator.validate_and_sanitize_path(selected_directory)
                if safe_path:
                    return True, safe_path
                else:
                    return False, None
            else:
                return False, None
                
        except Exception as e:
            return False, None

    def validate_directory(self, directory_path: str) -> bool:
        """ Validates that a directory path exists and is accessible. """
        return self.validator.validate_directory(directory_path)

    # -----------------------------------------------------------------------------------------------------
    # FIXME We could add a layer of abstraction as these two methods only change the callable between them.
    # -----------------------------------------------------------------------------------------------------
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """ Moves a single file from 'source_path' to 'destination_path'. """
        try:
            safe_source = self.validator.validate_and_sanitize_path(source_path)
            safe_destination = self.validator.validate_and_sanitize_path(destination_path)
            if not safe_source or not safe_destination:
                return False
            
            destination_dir = Path(safe_destination).parent
            if not ensure_directory_exists(destination_dir):
                return False

            shutil.move(safe_source, safe_destination)
            return True
        
        except Exception as e:
            print(f"Error moving file: {e}")
            return False

    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """ Copies a single file from 'source_path' to 'destination_path'. """
        try:
            safe_source = self.validator.validate_and_sanitize_path(source_path)
            safe_destination = self.validator.validate_and_sanitize_path(destination_path)

            if not safe_source or not safe_destination:
                return False
            
            destination_dir = Path(safe_destination).parent
            if not ensure_directory_exists(destination_dir):
                return False

            shutil.copy2(safe_source, safe_destination)
            return True
        
        except Exception as e:
            print(f"Error copying file: {e}")
            return False