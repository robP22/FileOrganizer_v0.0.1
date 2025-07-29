# MVP Document: File Organizer Application

## Overview

This application helps users organize files from a selected directory by reading file metadata (creation date) and moving these files into newly created folders based on year, month, or day, according to user-selected options. The app provides an interface to open the OS file explorer, and checks available space before moving files. The MVP targets Windows, with plans for cross-platform support.

---

## Features (MVP)

1. **Open OS-specific File Explorer**
   - Open Windows File Explorer at a selected path.

2. **Read File Metadata**
   - Read creation date, file size, and file extension/type for each file in the source directory.

3. **User Directory Selection**
   - User selects a source directory containing files to organize.
   - User selects a target directory for organized files.

4. **Create Organizational Folders**
   - Create new folders in the target directory based on file creation date.
   - Folder structure options:
     - By year
     - By year/month
     - By year/month/day

5. **Move Files**
   - Move files from the source directory into appropriate folders in the target directory.
   - Support common media types (.mp3, .wav, .mp4, etc.).

6. **Disk Space Check**
   - Ensure sufficient free space in the target directory before moving files.

7. **Verify Files Are Not Corrupt**
   - Perform basic integrity checks (e.g., file size > 0).
   - Advanced corruption checks are deferred for future versions.

---

## Out of Scope (for MVP)

- File deletion/removal (user responsibility).
- Advanced file corruption detection.
- Support for non-Windows operating systems (planned for post-MVP).
- Organization based on metadata other than creation date.

---

## Data Requirements

- **Source Directory Path:** User-selected folder containing files.
- **Target Directory Path:** User-selected destination for organized files.
- **File Metadata for Each File:**
  - Absolute file path
  - File name
  - File extension/type
  - File size
  - Date created
- **User Organization Preference:**
  - Year, Year/Month, or Year/Month/Day
- **Disk Space Information:**
  - Total size of files to move
  - Available space in target directory
- **Operating System Info:** To enable OS-specific explorer opening.

---

## Technical Approach

- **GUI Framework:** PySide6 (Qt for Python).
- **File Operations:** `os`, `pathlib`, `shutil`
- **Disk Space:** `shutil.disk_usage`
- **OS Integration:** `os.startfile` for Windows Explorer.
- **Testing:** TDD with `pytest` or `unittest`.
- **Application Structure:** Modular monolith, with clear separation for GUI, file operations, and utility functions.

---

## Example Test Data

- **Source Directory:** `E:\musiic prod\Beats`
- **Example File:** `E:\musiic prod\Beats\3phrase cmin 151 @robP.mp3`
- **Target Directory:** `C:\Users\rober\Documents\NewDirNameHere`
- **File Types:** `.mp3`, `.wav`, `.mp4` (not limited to these)

---

## Future Considerations

- Cross-platform support (macOS, Linux)
- More robust file integrity checks
- User-configurable organization rules (beyond dates)
- Automated duplicate detection

---

## Success Criteria

- User can select a source and target directory.
- App organizes files by creation date into folders.
- App opens Windows Explorer at target location.
- No files are moved if there is insufficient disk space.
- Supported file types are correctly handled.

---

## File/Folder Structure Table

| File/Folder         | Purpose                                                    |
|---------------------|------------------------------------------------------------|
| `src/main.py`       | Entry point, launches the GUI                              |
| `src/gui.py`        | Main window, user interactions, directory selection        |
| `src/organizer.py`  | File organization logic, moving files, folder creation     |
| `src/file_utils.py` | File metadata reading, integrity checks, listing files     |
| `src/os_utils.py`   | OS-specific operations (Explorer, disk space)              |
| `src/config.py`     | Load/save user config/settings                             |
| `tests/`            | Test suite for modules                                     |
| `tests/test_gui.py` | Tests for GUI logic                                        |
| `tests/test_organizer.py` | Tests for organizer logic                           |
| `tests/test_file_utils.py`| Tests for file utils                                |
| `tests/test_os_utils.py`  | Tests for os utils                                  |

---

## Function Signatures, Imports, and Responsibilities

### main.py

```python
from PySide6.QtWidgets import QApplication
from gui import MainWindow

def run_app() -> None:
    """Launches the GUI."""
```

---

### gui.py

```python
from PySide6.QtWidgets import QMainWindow, QFileDialog, QPushButton, QComboBox, QLabel, QVBoxLayout, QWidget
from os_utils import open_file_explorer
from organizer import organize_files
from config import load_config, save_config

class MainWindow(QMainWindow):
    def init_ui(self) -> None:
        """Sets up GUI elements."""

    def select_source_directory(self) -> str:
        """Returns the selected source directory path."""

    def select_target_directory(self) -> str:
        """Returns the selected target directory path."""

    def get_granularity_selection(self) -> str:
        """Returns granularity: 'year', 'year_month', or 'year_month_day'."""

    def on_organize_clicked(self) -> None:
        """Triggers organization process."""

    def on_open_in_explorer_clicked(self, path: str) -> None:
        """Opens the OS file explorer at the specified path."""
```

---

### organizer.py

```python
from file_utils import list_files_in_directory, get_file_metadata, is_file_corrupt
from os_utils import check_disk_space
import os
import shutil

def organize_files(source_dir: str, target_dir: str, granularity: str) -> dict:
    """
    Organizes files and returns a summary dict (files moved, folders created, errors).
    """

def create_organization_structure(target_dir: str, files: list, granularity: str) -> dict:
    """
    Maps folder paths to file lists.
    """

def move_files(mapping: dict) -> dict:
    """
    Moves files according to mapping, returns dict (files moved, errors).
    """
```

---

### file_utils.py

```python
import os
from pathlib import Path
import datetime
import mimetypes
import stat

def list_files_in_directory(directory: str) -> list:
    """Returns a list of file paths in the directory."""

def get_file_metadata(file_path: str) -> dict:
    """Returns FileInfo dict (path, created, size, extension)."""

def is_file_corrupt(file_path: str) -> bool:
    """Quick integrity check, returns True if corrupt."""
```

---

### os_utils.py

```python
import os
import platform
import subprocess
import shutil

def open_file_explorer(path: str) -> None:
    """Opens the file explorer at the specified path."""

def get_disk_free_space(path: str) -> int:
    """Returns free bytes at path."""

def check_disk_space(target_dir: str, total_size_needed: int) -> bool:
    """Returns True if enough space is available at target_dir."""
```

---

### config.py

```python
import json
import os

def load_config() -> dict:
    """Loads user settings."""

def save_config(config: dict) -> None:
    """Saves user settings."""
```

---

### tests/

Each test file will have test functions like:
- `test_select_source_directory()`
- `test_organize_files()`
- `test_is_file_corrupt()`
- etc.

---