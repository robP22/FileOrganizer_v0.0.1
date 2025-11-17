# FileOrganizer v0.0.1

A **privacy-focused, cross-platform desktop application** for organizing and unorganizing files with intelligent metadata-based categorization and flexible organization strategies.

## Overview

FileOrganizer provides a clean, intuitive GUI for managing file organization workflows. Built with **zero data collection** and **local-only processing**, all operations happen entirely on your device. The application features both organization (structuring messy directories) and unorganizing (flattening organized structures) capabilities with real-time progress tracking and comprehensive error handling.

### Privacy & Security Features
- **Local-Only Processing**: All operations happen entirely on your device
- **Zero Telemetry**: No data collection, analytics, or usage tracking  
- **Granular Privacy Controls**: Configurable metadata extraction settings
- **No Network Dependencies**: Never connects to internet or cloud services
- **Secure File Operations**: Path validation and permission verification

### Key Features
- **Dual Functionality**: Both organize and unorganize operations
- **Smart Organization**: Multiple organization strategies (Smart, Date-based, Type-based)
- **Microservice Architecture**: Decoupled, independent services
- **Event-Driven Design**: Real-time progress and status updates
- **Cross-Platform**: Windows, macOS, and Linux support
- **Native File Integration**: System file manager integration

---

## Current Functionality

### Organization Features
- **Smart Organization**: Intelligent file placement based on metadata and file age
- **Date-Based Organization**: Organize by year/month folder structures  
- **Type-Based Organization**: Categorize by file type (Images, Videos, Documents, etc.)
- **Metadata Extraction**: Photo EXIF, audio tags, document properties
- **Progress Tracking**: Real-time operation feedback

### Unorganize Features  
- **Directory Flattening**: Unorganize any nested directory structure
- **File Conflict Handling**: Automatic filename deduplication
- **Recursive Processing**: Process all subdirectories
- **Independent Microservice**: Decoupled from organization logic

### User Interface
- **Clean GUI**: Source/destination directory selection
- **Menu Integration**: Privacy settings accessible via top menu
- **Progress Feedback**: Real-time operation status
- **Error Handling**: Comprehensive error reporting and recovery

---

## Quick Start

### Installation & Setup
1. **Clone Repository**: `git clone <repository-url>`
2. **Install Uv**: `pip install uv`
3. **Initialize Uv**: `uv init`
4. **Install Dependencies**: `uv sync`
5. **Run Application**: `python3 src/main.py` or `python src/main.py`

### Basic Usage
1. **Launch** the application
2. **Select Source Directory** containing files to organize/unorganize
3. **Select Destination Directory** for processed files
4. **Choose Operation**:
   - **Organize**: Click "Organize Files" for intelligent file organization
   - **Unorganize**: Click "Unorganize" to flatten directory structures
5. **Monitor Progress** via real-time status updates
6. **Access Privacy Settings** via top menu for configuration

---

## Architecture Overview

### Current Architecture
- **Event-Driven Communication**: Pub/sub system for component decoupling
- **Microservice Design**: Independent services for organize/unorganize operations
- **Strategy Pattern**: Multiple organization algorithms (Smart, Date, Type)
- **Service Injection**: Clean dependency management

### Core Components
- **OrganizationService**: Handles intelligent file organization
- **UnorganizeService**: Independent directory flattening microservice  
- **FileService**: Cross-platform file operations and validation
- **MetadataService**: File metadata extraction and analysis
- **GUI Layer**: PySide6-based user interface with native OS integration

---

## Current Implementation

### Organization Strategies

#### Smart Organization
- **Adaptive Logic**: Automatically selects best organization approach
- **Recent File Handling**: Date-primary organization for files < 30 days old  
- **Media Intelligence**: Uses rich metadata for photos/videos/audio
- **Document Processing**: Author and date-based categorization
- **Fallback Strategy**: Type-then-date for files without rich metadata

#### Date-Based Organization  
- **Year/Month Structure**: `YYYY/MM/` folder hierarchy
- **Metadata Dates**: Uses creation/modified/EXIF dates intelligently
- **Consistent Placement**: Predictable folder structures

#### Type-Based Organization
- **Category Detection**: Images, Videos, Audio, Documents, Other
- **Extension Mapping**: Comprehensive file type recognition  
- **Metadata Enhancement**: Uses file content analysis beyond extensions

### Unorganize Operations
- **Directory Flattening**: Recursively processes nested structures
- **Conflict Resolution**: Automatic filename deduplication  
- **Progress Tracking**: Real-time processing feedback
- **Error Handling**: Graceful handling of access issues and conflicts

### File Operations
- **Safe Moves**: Atomic file operations with validation
- **Permission Checking**: Pre-flight validation of file access
- **Path Normalization**: Cross-platform path handling
- **Directory Creation**: Automatic folder structure creation

### Privacy & Security
- **Configurable Metadata**: Choose what data to extract
- **Local Processing**: No network dependencies
- **Validation Framework**: Input sanitization and path security
- **Error Sanitization**: Configurable error message detail levels

---

4. **Cross-Platform Support**
   - Windows, macOS, and Linux compatibility
   - OS-specific file explorer integration
   - Platform-aware path normalization
   - Native UI styling and behavior

4. **Progress & Status Management**
   - Real-time progress tracking (processed/total files)
   - Status bar with visual indicators (Ready/Processing/Error)
   - Comprehensive error reporting and recovery

5. **Error Handling**
   - **Critical Errors** (disk space, destination conflicts): Stop entire process
   - **Non-Critical Errors** (corrupted files): Save for retry, continue with remaining files
   - User choice for retry/skip failed operations

### User Interface
- **Main Window**: Directory selection, status display, action buttons
- **Confirmation Modal**: Configuration review before execution
- **Progress Dialog**: Real-time operation feedback
- **Results Dialog**: Success/error summary with details

---

## Technical Stack

### Framework & Libraries
- **GUI Framework**: PySide6 (Qt for Python) - Cross-platform native UI
- **File Operations**: Python pathlib, shutil - Robust file system operations  
- **Configuration**: JSON-based settings persistence
- **Architecture**: Event-driven with microservice patterns

### Current Project Structure
```
src/
├── core/
│   ├── events.py              # Event system (pub/sub)
│   ├── protocols.py           # Interface definitions
│   ├── config_interface.py    # Configuration adapter
│   └── validation_manager.py  # Input validation framework
├── models/
│   └── operation_result.py    # Results and progress tracking
├── services/
│   ├── core/
│   │   ├── organization_service.py  # Main organization logic
│   │   ├── unorganize_service.py    # Directory flattening microservice
│   │   └── validation_service.py    # File metadata extraction
│   ├── config/
│   │   ├── config_service.py        # Privacy and app configuration
│   │   └── privacy_logger.py        # Privacy logging
│   ├── metadata/
│   │   ├── document_service.py      # document metadata extraction
│   │   ├── exif_service.py          # File metadata extraction
│   │   ├── media_service.py         # File metadata extraction
│   │   └── metadata_service.py      # File metadata extraction
│   ├── platform/
│   │   └── platform_service.py      # File metadata extraction
├── organizers/
│   ├── base_organizer.py      # Abstract organization strategy
│   ├── smart_organizer.py     # Intelligent file organization  
│   ├── date_organizer.py      # Date-based organization
│   └── type_organizer.py      # Type-based organization
├── file_operations/
│   ├── file_info.py           # File info metadata
│   ├── file_service.py        # Cross-platform file operations
│   ├── file_utils.py          # Utility functions
│   └── file_types.py          # File type categorization
├── gui/
│   ├── main_window.py         # Main application window
│   └── privacy_dialog.py      # Privacy settings interface
├── pyproject.toml             # Environment and dependencies
├── README.md                  # Application documentation
└── main.py                    # Application entry point
```

### Technology Decisions
- **PySide6**: Chosen for native OS integration and cross-platform compatibility
- **Event-Driven Architecture**: Enables loose coupling and easier testing
- **Microservice Pattern**: Independent services for different operations  
- **Strategy Pattern**: Pluggable organization algorithms
- **JSON Configuration**: Human-readable settings persistence

---

### Technology Stack
- **GUI Framework**: PySide6 (Qt for Python)
- **File Operations**: `pathlib`, `shutil`, `os`
- **Configuration**: JSON-based settings persistence
- **Testing**: Real file system testing with pytest
- **Architecture Patterns**: Event-driven, Command, Observer, Strategy
- **File Analysis Libraries**:
  - **ExifRead**: Photo metadata extraction (GPS, camera, timestamps)
  - **Pillow (PIL)**: Image properties and validation
  - **python-magic**: True file type detection beyond extensions
  - **pymediainfo**: Audio/video metadata and technical specifications
  - **python-docx/PyPDF2**: Document metadata extraction

---

## Data Requirements

### Application State
- Source directory path and validation status
- Destination directory path and validation status
- Organization configuration (rule-based, date-based, or template-based)
- Active organization rules and priorities
- Current operating system and platform-specific settings
- Operation progress and status
- Error tracking and retry queue

### File Metadata
- Absolute file path
- File name and extension
- File size and creation date
- Accessibility and permission status
- Corruption check results
- **Enhanced Metadata Fields**:
  - **Photos**: GPS coordinates, camera make/model, shooting parameters
  - **Audio**: Artist, album, genre, bitrate, duration
  - **Video**: Resolution, codec, frame rate, duration
  - **Documents**: Author, title, company, word/page count
  - **True file types**: Actual format beyond file extensions

### Configuration Persistence
- User preferences (JSON format)
- Organization rules and templates
- Rule priorities and enabled states
- Folder path templates and patterns
- Application settings and window state

---

## Error Handling Strategy

## Development Status

### Completed Features
- **Core Organization**: Smart, Date-based, and Type-based organization strategies
- **Unorganize Functionality**: Independent microservice for directory flattening
- **GUI Framework**: Clean PySide6 interface with source/destination selection
- **Event System**: Pub/sub architecture for component communication
- **Privacy Controls**: Configurable metadata extraction and privacy settings
- **File Operations**: Safe file moving with conflict resolution
- **Progress Tracking**: Real-time operation feedback
- **Cross-Platform**: Windows, macOS, and Linux compatibility

### In Development
- **Enhanced Metadata**: Expanded photo, audio, and document metadata extraction
- **Rule Engine**: Advanced conditional logic for file organization
- **Error Recovery**: Comprehensive retry and recovery mechanisms
- **Performance Optimization**: Threading and batch processing improvements

### Future Roadmap
- **Template System**: User-defined organization templates
- **Duplicate Detection**: Intelligent duplicate file handling
- **Plugin Architecture**: Custom organizer extensions
- **Automation**: Scheduled and watch-folder operations
- **Advanced Analytics**: Organization insights and reporting

---

## Contributing
    Please contact me before beginning development.

### Getting Started
1. **Fork** the repository
2. **Install Uv**: `pip install uv`
3. **Initialize Uv**: `uv init`
4. **Install Dependencies**: `uv sync`
5. **Start development**: Follow the event-driven architecture patterns

### Code Style
- **Type Hints**: Use Python type annotations
- **Documentation**: Docstrings for all public methods
- **Event Patterns**: Follow pub/sub patterns for component communication
- **Testing**: Include unit tests for new functionality
  - Test files were previously uncommited and no longer exist due to memory loss

### Architecture Guidelines
- **Loose Coupling**: Use dependency injection and event communication
- **Single Responsibility**: Each service handles one primary concern
- **Security**: Maintain local-only processing principles
- **Cross-Platform**: Ensure compatibility across operating systems

---
   - Comprehensive error handling and recovery
   - Native file explorer integration on Windows, macOS, and Linux

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Support

For issues, feature requests, or contributions:
- **GitHub Issues**: Report bugs and request features
