# FileOrganizer v0.0.1 - Complete Function & Library Reference

## **📚 EXTERNAL LIBRARIES USED**

### **🖼️ GUI Framework - PySide6 (Qt)**
```python
from PySide6.QtWidgets import (
    QApplication,     # Main application object, event loop
    QMainWindow,      # Main window with menu bar, status bar
    QWidget,          # Base widget class
    QVBoxLayout,      # Vertical box layout manager
    QHBoxLayout,      # Horizontal box layout manager
    QLabel,           # Text display widget
    QPushButton,      # Clickable button widget
    QFileDialog,      # File/folder selection dialogs
    QDialog,          # Modal dialog base class
    QCheckBox,        # Boolean checkbox widget
    QMenuBar,         # Menu bar container
    QMenu             # Individual menu
)
from PySide6.QtGui import QAction        # Menu actions
from PySide6.QtCore import Qt            # Qt constants and enums
```

**How it works**: PySide6 provides Python bindings for Qt, enabling cross-platform GUI development. The event loop (`app.exec()`) handles user interactions, window management, and system events.

### **🗂️ File & Path Handling - pathlib**
```python
from pathlib import Path    # Modern, object-oriented path handling

# Key methods used:
Path.exists()              # Check if path exists
Path.is_file()             # Check if path is a file
Path.is_dir()              # Check if path is a directory
Path.mkdir(parents=True)   # Create directories recursively
Path.iterdir()             # List directory contents
Path.rglob('*')           # Recursive file search
Path.stat()               # Get file statistics (size, dates)
Path.suffix               # File extension (.jpg, .pdf)
Path.stem                 # Filename without extension
Path.name                 # Full filename
str(Path)                 # Convert to string for legacy APIs
```

**Why pathlib**: Modern, cross-platform, object-oriented alternative to `os.path`. Handles Windows/Mac/Linux path differences automatically.

### **📸 Image Processing - PIL (Pillow)**
```python
from PIL import Image           # Image file handling
from PIL.ExifTags import TAGS   # EXIF tag name mapping

# Key functions:
Image.open(file_path)          # Open image file
image.getexif()               # Extract EXIF metadata dictionary
TAGS.get(tag_id, tag_id)      # Convert numeric tag to readable name
```

**How it works**: Pillow reads image files and extracts embedded metadata (camera settings, GPS coordinates, timestamps) from the EXIF data.

### **🎵 Media Metadata - mutagen**
```python
from mutagen import File as MutagenFile  # Audio/video metadata
from mutagen.id3 import ID3NoHeaderError # MP3 error handling

# Key functionality:
MutagenFile(file_path)        # Load media file
audiofile.info.length        # Duration in seconds
audiofile.info.bitrate       # Audio quality (kbps)
audiofile['TIT2']            # Title tag (varies by format)
audiofile['TPE1']            # Artist tag
```

**How it works**: Mutagen reads metadata tags from various audio/video formats (MP3, FLAC, MP4, etc.) and provides unified access to title, artist, album information.

### **📄 Document Processing - PyPDF2**
```python
from PyPDF2 import PdfReader    # PDF metadata extraction

# Key functions:
PdfReader(file_path)           # Open PDF file
reader.metadata               # Document properties dictionary
reader.pages                  # List of PDF pages
```

**How it works**: PyPDF2 parses PDF file structure to extract document properties like title, author, creation date, and page count.

### **🔢 Data Structures & Utilities**
```python
from typing import (
    Dict, List, Any, Optional,  # Type hints for better code safety
    Callable, Tuple            # Function and tuple types
)
from dataclasses import dataclass  # Automatic class generation
from abc import ABC, abstractmethod  # Abstract base classes
from datetime import datetime      # Date/time handling
import shutil                     # High-level file operations
import os                        # Operating system interface
import tempfile                  # Temporary file/directory creation
```

---

## **🔧 CORE FUNCTION BREAKDOWN BY MODULE**

### **🎯 `main.py` - Application Bootstrap**

#### **`main()` Function**
```python
def main():
    app = QApplication()                                    # Creates Qt application instance
    config_adapter = ConfigAdapter(privacy_config)         # Wraps configuration access
    file_service = FileService()                          # File operation service
    organization_service = OrganizationService(           # Main business logic service
        file_service, config_adapter
    )
    window = MainWindow(config_provider=config_adapter)   # Main GUI window
    window.show()                                         # Display window
    app.exec()                                           # Start Qt event loop
```

**Purpose**: Composition root that wires up all dependencies and starts the application.

---

### **🎨 `gui/main_window.py` - User Interface**

#### **GUI Setup Functions**
```python
def __init__(self, config_provider: ConfigProvider = None):
    # Initializes window, subscribes to events, sets up UI

def initUI(self):
    # Creates main layout with buttons and labels
    main_layout = QVBoxLayout()                          # Vertical layout container
    central_widget = QWidget()                           # Central widget container
    self.setGeometry(100, 100, 800, 600)               # Window size and position
```

#### **File Selection Functions**
```python
def select_source_directory(self):
    folder = QFileDialog.getExistingDirectory(          # Opens folder selection dialog
        self, "Select Source Directory"
    )
    if folder:
        self.source_path = folder                       # Stores selected path
        self.update_organize_button_state()             # Enables organize button if ready

def select_destination_directory(self):
    # Similar to source selection but for destination folder
```

**How QFileDialog works**: Opens native OS file selection dialog, returns selected path or empty string if cancelled.

#### **Event Publishing Function**
```python
def start_organization(self):
    if self.source_path and self.destination_path:
        event_bus.publish("organize_requested", {        # Publishes event to service layer
            "source_path": self.source_path,
            "destination_path": self.destination_path
        })
```

**Event Flow**: User clicks → GUI publishes event → Service receives event → Organization begins

---

### **🎯 `core/events.py` - Event System**

#### **Event Data Structure**
```python
@dataclass
class Event:
    type: str                    # Event identifier ("organize_requested")
    data: Dict[str, Any] = None  # Event payload (source/dest paths)
```

#### **EventBus Core Functions**
```python
def subscribe(self, event_type: str, callback: Callable[[Event], None]):
    # Registers function to be called when event_type is published
    if event_type not in self.subscribers:
        self.subscribers[event_type] = []              # Create subscriber list
    self.subscribers[event_type].append(callback)     # Add callback to list

def publish(self, event_type: str, data: Dict[str, Any] = None):
    # Sends event to all registered subscribers
    event = Event(type=event_type, data=data or {})   # Create event object
    if event.type in self.subscribers:
        for callback in self.subscribers[event.type]:  # Call each subscriber
            try:
                callback(event)                        # Execute callback with event
            except Exception as e:
                print(f"Error in event handler: {e}") # Error isolation
```

**How Pub/Sub works**: Publishers send events without knowing who receives them. Subscribers listen for specific event types. This decouples components.

---

### **🔧 `services/organization_service.py` - Main Orchestrator**

#### **Service Initialization**
```python
def __init__(self, file_service: FileService, config_provider: ConfigProvider = None):
    self.file_service = file_service                    # Injected file operations
    self.metadata_service = MetadataService(config_provider)  # Creates metadata service
    event_bus.subscribe("organize_requested",           # Listens for GUI events
                       self.handle_organize_request)
```

#### **Strategy Selection Logic**
```python
def organize_files_by_strategy(self, source_dir: str, destination_dir: str, strategy: str):
    organizer_classes = {
        "date": DateOrganizer,    # Organize by file dates
        "type": TypeOrganizer,    # Organize by file extensions
        "smart": SmartOrganizer   # Intelligent organization
    }
    organizer_class = organizer_classes.get(strategy, SmartOrganizer)  # Default to smart
    organizer = organizer_class(                       # Create organizer instance
        self.metadata_service, self.file_service, event_bus
    )
```

**Strategy Pattern**: Runtime selection of organization algorithm without changing client code.

#### **Directory Scanning**
```python
def scan_directory(self, path: str) -> List[Path]:
    directory = Path(path)
    files = []
    for item in directory.rglob('*'):                   # Recursive search
        if item.is_file():                              # Only files, not directories
            files.append(item)
    return files
```

**How rglob works**: Recursively searches directory tree using glob patterns (`*` = all files).

---

### **🗂️ `services/file_service.py` - File Operations**

#### **Safe File Moving**
```python
def move_file(self, source_path: str, destination_path: str) -> bool:
    try:
        source = Path(source_path)
        destination = Path(destination_path)
        
        if not source.exists():                         # Validation
            return False
            
        destination.parent.mkdir(parents=True, exist_ok=True)  # Create destination folder
        shutil.move(str(source), str(destination))     # Actual file move
        return True                                     # Success
    except Exception as e:
        return False                                    # Failure (with logging)
```

**Error Handling**: Each operation wrapped in try/catch, returns boolean success indicator, creates directories as needed.

#### **File Information Extraction**
```python
def get_file_info(self, file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    stat = path.stat()                                  # Get file statistics
    return {
        'size': stat.st_size,                          # File size in bytes
        'modified': datetime.fromtimestamp(stat.st_mtime),  # Modification date
        'created': datetime.fromtimestamp(stat.st_ctime),   # Creation date
        'permissions': oct(stat.st_mode)[-3:]          # Permission bits
    }
```

**How stat() works**: System call that returns file metadata (size, dates, permissions) from filesystem.

---

### **📊 `services/metadata_service.py` - Data Extraction Hub**

#### **Comprehensive Metadata Extraction**
```python
def extract_comprehensive_metadata(self, file_path: Path) -> Dict[str, Any]:
    metadata = {}
    
    # Basic filesystem metadata
    metadata.update(self._extract_basic_metadata(file_path))
    
    # Image files - EXIF data
    if file_path.suffix.lower() in {'.jpg', '.jpeg', '.tiff'}:
        metadata.update(self._extract_exif_metadata(file_path))
    
    # Audio/Video files
    elif file_path.suffix.lower() in {'.mp3', '.mp4', '.avi'}:
        metadata.update(self._extract_media_metadata(file_path))
    
    # Documents
    elif file_path.suffix.lower() in {'.pdf', '.docx'}:
        metadata.update(self._extract_document_metadata(file_path))
    
    return metadata
```

**Service Composition**: Coordinates multiple specialized services based on file type.

#### **Organization-Specific Data**
```python
def get_organization_info(self, file_path: Path) -> Dict[str, Any]:
    # Extracts only data needed for file organization
    metadata = self.extract_comprehensive_metadata(file_path)
    return {
        'creation_date': metadata.get('creation_date'),
        'file_type': file_path.suffix.lower(),
        'category': self._determine_category(file_path)
    }
```

**Data Filtering**: Returns only organization-relevant metadata to improve performance.

---

### **🛡️ `services/validation_service.py` - Security Layer**

#### **Path Security Validation**
```python
def is_valid_file_path(self, path: str) -> bool:
    try:
        path_obj = Path(path).resolve()                 # Resolve symlinks, relative paths
        
        # Check for dangerous patterns
        if self.is_system_directory(path_obj):          # Protect system folders
            return False
        if '..' in str(path_obj):                       # Prevent path traversal
            return False
        if self.has_dangerous_extension(path_obj):      # Block dangerous files
            return False
            
        return True
    except Exception:
        return False                                    # Invalid paths fail safely
```

**Security Layers**:
1. **Path Resolution**: Converts to absolute path, resolves symlinks
2. **System Protection**: Blocks access to `/System`, `/usr`, etc.
3. **Traversal Prevention**: Detects `../` path traversal attempts
4. **Extension Filtering**: Blocks `.exe`, `.bat`, etc.

#### **Dangerous Extension Detection**
```python
def has_dangerous_extension(self, path: Path) -> bool:
    dangerous_extensions = {
        '.exe', '.bat', '.cmd', '.scr',               # Windows executables
        '.app', '.dmg',                               # Mac applications
        '.sh', '.bash',                               # Shell scripts
        '.py', '.js'                                  # Script files
    }
    return path.suffix.lower() in dangerous_extensions
```

---

### **🎯 `organizers/base_organizer.py` - Template Pattern**

#### **Template Method Implementation**
```python
def organize_files(self, file_paths: List[Path], destination_root: Path) -> Dict[str, Any]:
    self.reset_counters()                             # Initialize statistics
    
    for file_path in file_paths:
        try:
            self._organize_single_file(file_path, destination_root)  # Process each file
            self.files_processed += 1
        except Exception as e:
            self.errors += 1                          # Track errors
    
    return {                                          # Return statistics
        'files_processed': self.files_processed,
        'files_moved': self.files_moved,
        'errors': self.errors
    }
```

**Template Method Pattern**: Defines algorithm structure in base class, concrete classes implement specific steps.

#### **Single File Processing**
```python
def _organize_single_file(self, file_path: Path, destination_root: Path):
    # Extract metadata for organization decision
    metadata = self.metadata_service.extract_comprehensive_metadata(file_path)
    
    # Get destination path using strategy-specific logic
    destination_path = self.get_destination_path(file_path, destination_root, metadata)
    
    # Move the file
    if self.file_service.move_file(str(file_path), str(destination_path)):
        self.files_moved += 1
        # Publish success event (no file paths for security)
        self.event_bus.publish("file_processed", {
            "file_name": file_path.name,              # Only filename, not full path
            "strategy_used": self.get_strategy_name()
        })
```

**Security Note**: Events contain only filenames, never full paths, to prevent information disclosure.

---

### **📅 `organizers/date_organizer.py` - Date Strategy**

#### **Date-Based Path Generation**
```python
def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
    # Get file date (creation or modification)
    file_date = metadata.get('creation_date') or metadata.get('modification_date')
    
    if file_date:
        year_folder = destination_root / str(file_date.year)        # 2025/
        month_folder = year_folder / f"{file_date.month:02d}"       # 2025/01/
    else:
        month_folder = destination_root / "undated"                 # Fallback folder
    
    return get_unique_file_path(month_folder, file_path.name)      # Handle duplicates
```

**Date Hierarchy**: Creates `YYYY/MM/` folder structure based on file dates.

---

### **📂 `organizers/type_organizer.py` - Type Strategy**

#### **Type-Based Categorization**
```python
def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
    file_extension = file_path.suffix.lower()
    
    # Map extensions to categories
    category_mapping = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp'},
        'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf'},
        'videos': {'.mp4', '.avi', '.mkv', '.mov'},
        'audio': {'.mp3', '.flac', '.wav', '.m4a'},
        'archives': {'.zip', '.rar', '.7z', '.tar'}
    }
    
    # Find matching category
    for category, extensions in category_mapping.items():
        if file_extension in extensions:
            category_folder = destination_root / category.title()  # "Images", "Documents"
            return get_unique_file_path(category_folder, file_path.name)
    
    # Default category for unknown types
    other_folder = destination_root / "Other"
    return get_unique_file_path(other_folder, file_path.name)
```

**Type Mapping**: Groups file extensions into logical categories for organization.

---

### **🧠 `organizers/smart_organizer.py` - Intelligent Strategy**

#### **Hybrid Organization Logic**
```python
def get_destination_path(self, file_path: Path, destination_root: Path, metadata: Dict) -> Path:
    # Combine type and date information for intelligent organization
    file_date = metadata.get('creation_date') or metadata.get('modification_date')
    file_type = self._get_file_category(file_path)
    
    if file_type == 'photos' and file_date:
        # Photos organized by date
        return destination_root / "Photos" / str(file_date.year) / f"{file_date.month:02d}" / file_path.name
    elif file_type == 'documents':
        # Documents organized by type and year
        year = file_date.year if file_date else "unknown"
        return destination_root / "Documents" / str(year) / file_path.name
    else:
        # Default to type-based organization
        return destination_root / file_type.title() / file_path.name
```

**Smart Logic**: Uses both file type and date information to create optimal organization structure.

---

### **🛠️ `utils/file_utils.py` - Utility Functions**

#### **Unique Path Generation**
```python
def get_unique_file_path(destination_folder: Path, filename: str) -> Path:
    destination_path = destination_folder / filename
    
    if not destination_path.exists():
        return destination_path                         # No conflict
    
    # Handle name conflicts by adding counter
    stem = Path(filename).stem                          # "document"
    suffix = Path(filename).suffix                      # ".pdf"
    counter = 1
    
    while destination_path.exists():
        new_filename = f"{stem}_{counter}{suffix}"      # "document_1.pdf"
        destination_path = destination_folder / new_filename
        counter += 1
    
    return destination_path
```

**Conflict Resolution**: Automatically handles duplicate filenames by adding numeric suffixes.

#### **Date Extraction**
```python
def get_file_modification_date(file_path: Path) -> datetime:
    return datetime.fromtimestamp(file_path.stat().st_mtime)
```

**System Integration**: Converts Unix timestamp to Python datetime object.

---

## **🔄 DATA FLOW & COMMUNICATION**

### **Event-Driven Communication Flow**
```
1. User clicks "Organize Files" button
   ↓
2. MainWindow.start_organization() publishes "organize_requested" event
   ↓
3. OrganizationService.handle_organize_request() receives event
   ↓
4. Scans source directory for files
   ↓
5. For each file:
   a. MetadataService extracts file information
   b. Strategy organizer determines destination path
   c. ValidationService checks path security
   d. FileService moves the file
   e. Progress events published
   ↓
6. Completion events published back to GUI
```

### **Dependency Injection Chain**
```
main.py creates:
├── ConfigAdapter (wraps privacy_config)
├── FileService (no dependencies)
├── OrganizationService
│   ├── Takes FileService and ConfigAdapter
│   └── Creates MetadataService internally
└── MainWindow (takes ConfigAdapter)

Each organizer receives:
├── MetadataService (for file analysis)
├── FileService (for file operations)
└── EventBus (for progress reporting)
```

This architecture provides **clean separation of concerns**, **loose coupling through events**, **dependency injection for testability**, and **security through validation layers**.
