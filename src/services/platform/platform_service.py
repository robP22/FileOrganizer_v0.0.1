import os
import platform
import subprocess
from typing  import Optional, Tuple
from pathlib import Path
from enum    import Enum


class Platform(Enum):
    WINDOWS = "windows"
    MACOS   = "macos"
    LINUX   = "linux"
    UNKNOWN = "unknown"


class PlatformService:
    """Cross-platform OS integration service"""
    
    def __init__(self):
        self.current_platform = self._detect_platform()
    
    def _detect_platform(self) -> Platform:
        """Detect the current operating system"""
        system = platform.system().lower()

        if system   == "windows":
            return Platform.WINDOWS
        elif system == "darwin":
            return Platform.MACOS
        elif system == "linux":
            return Platform.LINUX
        else:
            return Platform.UNKNOWN
    
    def open_file_manager(self, directory_path: Path) -> bool:
        """Open native file manager at specified directory"""
        try:
            if self.current_platform   == Platform.WINDOWS:
                subprocess.run(['explorer', str(directory_path)], check=True)
            elif self.current_platform == Platform.MACOS:
                subprocess.run(['open', str(directory_path)], check=True)
            elif self.current_platform == Platform.LINUX:
                # Try common Linux file managers
                for command in ['xdg-open', 'nautilus', 'dolphin', 'thunar']:
                    try:
                        subprocess.run([command, str(directory_path)], check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    return False
            else:
                return False
            return True
        
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_platform_specific_paths(self) -> dict:
        """Get platform-specific important directories"""
        # All platforms use the same paths in modern systems
        return {
            'home': Path.home(),
            'documents': Path.home() / "Documents",
            'desktop': Path.home() / "Desktop",
            'downloads': Path.home() / "Downloads"
        }
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for current platform"""
        return os.path.normpath(path)
    
    def is_hidden_file(self, file_path: Path) -> bool:
        """Check if file is hidden (platform-specific logic)"""
        if self.current_platform == Platform.WINDOWS:
            # On Windows, check file attributes
            try:
                import stat
                return bool(file_path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                return file_path.name.startswith('.')
        else:
            # On Unix-like systems (macOS, Linux), files starting with . are hidden
            return file_path.name.startswith('.')