# FileOrganizer - Basic Implementation Guide (GUI-First Approach)

## Overview

This document outlines a GUI-first implementation strategy for the FileOrganizer application. We start with a fully functional UI using mock/stub backend functions, then progressively replace stubs with real implementations while maintaining the working interface throughout development.

---

## Implementation Strategy

### **Core Philosophy: GUI-First Development**
1. **Build working UI first** with mock data and stub functions
2. **Validate user experience** before backend complexity
3. **Replace stubs incrementally** without breaking UI
4. **Maintain demo capability** throughout development process

---

## Development Phases

### **Phase 1: GUI Foundation (Week 1)**
**Goal:** Create fully functional UI with mock backend

#### **Day 1-2: Main Window Structure**
```python
# main_window.py - Full UI layout
class MainWindow(QMainWindow):
    def __init__(self):
        # Complete window setup
        # Directory selection buttons
        # Path display labels  
        # Organize button
        # Status bar
        
    def select_source_directory(self):
        # Mock: Return hardcoded test path
        return "/mock/source/path"
        
    def select_destination_directory(self):
        # Mock: Return hardcoded destination path
        return "/mock/destination/path"
```

#### **Day 2-3: Progress & Feedback UI**
```python
# Progress dialog with cancel capability
class ProgressDialog(QDialog):
    def __init__(self):
        # Progress bar
        # File counter (X of Y files)
        # Current file display
        # Cancel button
        
# Confirmation dialog
class ConfirmationDialog(QDialog):
    def __init__(self, file_count, destination):
        # Review organization settings
        # File count summary
        # Destination path display
        # Confirm/Cancel buttons

# Results dialog  
class ResultsDialog(QDialog):
    def __init__(self, results):
        # Success/error summary
        # Files processed count
        # Error details if any
        # OK button
```

#### **Day 3-4: Organization Configuration UI**
```python
# Configuration widget
class OrganizationConfigWidget(QWidget):
    def __init__(self):
        # Organization strategy selection (Date-based only)
        # Granularity options (Year/Month/Day)
        # Preview of folder structure
        
    def get_mock_configuration(self):
        # Return fake configuration for testing
        return {"strategy": "date", "granularity": "year_month"}
```

#### **Day 4-5: UI Polish & State Management**
```python
# State management and validation
class UIStateManager:
    def __init__(self, main_window):
        # Track UI state (paths selected, ready to organize, etc.)
        # Enable/disable buttons based on state
        # Show validation messages
        
    def update_ui_state(self):
        # Enable organize button only when ready
        # Show status messages
        # Update progress indicators
```

---

### **Phase 2: Backend Stubs Integration (Week 2)**
**Goal:** Connect UI to realistic stub functions

#### **Day 1-2: Service Layer Stubs**
```python
# services/metadata_service.py
class MetadataService:
    def get_basic_info(self, file_path):
        # Return fake FileInfo with random realistic data
        return MockFileInfo(
            path=file_path,
            size=random.randint(1024, 10*1024*1024),
            created=fake_random_date(),
            extension=Path(file_path).suffix
        )
    
    def scan_directory(self, directory_path):
        # Return list of 50-100 fake files
        return generate_mock_file_list(count=75)

# services/validation_service.py  
class ValidationService:
    def validate_paths(self, source, destination):
        # Return realistic validation scenarios
        return MockValidationResult(
            source_exists=True,
            destination_writable=True,
            sufficient_space=random.choice([True, False])  # Sometimes fail
        )
        
    def check_disk_space(self, files, destination):
        # Simulate space calculation
        total_size = sum(f.size for f in files)
        available_space = total_size * random.uniform(0.8, 2.0)  # Sometimes insufficient
        return available_space > total_size

# services/file_service.py
class FileService:
    def move_file(self, source, destination):
        # Log intended operation without actual move
        print(f"MOCK: Would move {source} to {destination}")
        time.sleep(0.1)  # Simulate operation time
        return MockOperationResult(success=True)
```

#### **Day 2-3: Organization Logic Stubs**
```python
# organizers/date_organizer.py
class DateOrganizer:
    def __init__(self, validation_service, file_service):
        self.validation_service = validation_service
        self.file_service = file_service
        
    def organize_files(self, files, destination_path):
        # Simulate organization process with real progress events
        results = []
        
        for i, file_info in enumerate(files):
            # Emit progress event
            self.emit_progress(processed=i, total=len(files), current_file=file_info.name)
            
            # Create mock destination path
            year = file_info.created.year
            month = file_info.created.month
            dest_folder = f"{destination_path}/{year}/{month:02d}"
            
            # Simulate file operation (no actual move)
            result = self.file_service.move_file(file_info.path, dest_folder)
            results.append(result)
            
            time.sleep(0.05)  # Simulate processing time
            
        return MockOrganizationResult(
            files_processed=len(results),
            files_succeeded=len([r for r in results if r.success]),
            files_failed=len([r for r in results if not r.success])
        )
```

#### **Day 3-4: Event System Implementation**
```python
# core/events.py
class EventBus:
    def __init__(self):
        self._subscribers = {}
    
    def subscribe(self, event_type, callback):
        # Basic pub/sub implementation
        
    def emit(self, event_type, data=None):
        # Notify all subscribers

# Event types for UI communication
EVENTS = {
    'VALIDATION_COMPLETE': 'validation_complete',
    'ORGANIZATION_STARTED': 'organization_started', 
    'ORGANIZATION_PROGRESS': 'organization_progress',
    'ORGANIZATION_COMPLETE': 'organization_complete',
    'ERROR_OCCURRED': 'error_occurred'
}

# Integration in main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.event_bus = EventBus()
        self.setup_event_handlers()
        
    def setup_event_handlers(self):
        self.event_bus.subscribe(EVENTS['ORGANIZATION_PROGRESS'], self.update_progress)
        self.event_bus.subscribe(EVENTS['ORGANIZATION_COMPLETE'], self.show_results)
```

#### **Day 4-5: Error Handling Framework**
```python
# core/exceptions.py
class FileOrganizerException(Exception):
    """Base exception for file organizer"""
    
class ValidationError(FileOrganizerException):
    """Raised when validation fails"""
    
class InsufficientSpaceError(FileOrganizerException):
    """Raised when insufficient disk space"""
    
class PermissionError(FileOrganizerException):
    """Raised when permission denied"""

# Mock error scenarios in stubs
class MockValidationService:
    def validate_paths(self, source, destination):
        # Occasionally raise mock errors for testing
        if random.random() < 0.1:  # 10% chance
            raise ValidationError("Mock validation failure for testing")
        return MockValidationResult(success=True)

# Error handling in UI
class MainWindow(QMainWindow):
    def handle_error(self, error_data):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(f"Error: {error_data['message']}")
        error_dialog.exec()
```

---

### **Phase 3: Real Implementation (Week 3+)**
**Goal:** Replace stubs with actual functionality

#### **Step 3.1: File System Operations**
```python
# Replace MockFileInfo with real implementation
class FileInfo:
    def __init__(self, path):
        self.path = Path(path)
        stat = self.path.stat()
        self.size = stat.st_size
        self.created = datetime.fromtimestamp(stat.st_ctime)
        self.name = self.path.name
        self.extension = self.path.suffix

# Replace mock file operations with real ones
class FileService:
    def move_file(self, source_path, destination_path):
        try:
            # Create destination directory if needed
            destination_dir = Path(destination_path).parent
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(source_path, destination_path)
            return OperationResult(success=True, file_path=source_path)
        except Exception as e:
            return OperationResult(success=False, error=str(e), file_path=source_path)
```

#### **Step 3.2: Validation Implementation**
```python
# Replace mock validation with real checks
class ValidationService:
    def validate_paths(self, source, destination):
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            raise ValidationError(f"Source path does not exist: {source}")
            
        if not dest_path.exists():
            raise ValidationError(f"Destination path does not exist: {destination}")
            
        if not os.access(dest_path, os.W_OK):
            raise PermissionError(f"No write permission for: {destination}")
            
        return ValidationResult(success=True)
        
    def check_disk_space(self, files, destination):
        total_size = sum(f.size for f in files)
        _, _, free_space = shutil.disk_usage(destination)
        
        if free_space < total_size:
            raise InsufficientSpaceError(
                f"Insufficient space. Need: {total_size}, Available: {free_space}"
            )
            
        return True
```

#### **Step 3.3: Organization Logic**
```python
# Replace mock organization with real file operations
class DateOrganizer:
    def organize_files(self, files, destination_path):
        results = []
        
        for i, file_info in enumerate(files):
            try:
                # Emit real progress event
                self.event_bus.emit(EVENTS['ORGANIZATION_PROGRESS'], {
                    'processed': i,
                    'total': len(files),
                    'current_file': file_info.name
                })
                
                # Create real destination path
                year = file_info.created.year
                month = file_info.created.month
                dest_folder = Path(destination_path) / str(year) / f"{month:02d}"
                dest_file_path = dest_folder / file_info.name
                
                # Perform real file operation
                result = self.file_service.move_file(file_info.path, dest_file_path)
                results.append(result)
                
            except Exception as e:
                results.append(OperationResult(
                    success=False, 
                    error=str(e), 
                    file_path=file_info.path
                ))
                
        return OrganizationResult(
            files_processed=len(results),
            files_succeeded=len([r for r in results if r.success]),
            files_failed=len([r for r in results if not r.success]),
            failed_files=[r for r in results if not r.success]
        )
```

---

## Mock Data Generators

### **Realistic Test Data**
```python
# Generate fake file list for testing
def generate_mock_file_list(count=100):
    files = []
    for i in range(count):
        # Random file types
        extensions = ['.jpg', '.png', '.mp4', '.mp3', '.pdf', '.docx', '.txt']
        ext = random.choice(extensions)
        
        # Random dates over past 2 years
        start_date = datetime.now() - timedelta(days=730)
        random_date = start_date + timedelta(days=random.randint(0, 730))
        
        files.append(MockFileInfo(
            path=f"/mock/source/file_{i:03d}{ext}",
            size=random.randint(1024, 50*1024*1024),
            created=random_date,
            name=f"file_{i:03d}{ext}",
            extension=ext
        ))
    
    return files

# Simulate realistic error scenarios
def generate_mock_errors():
    error_scenarios = [
        ValidationError("Source directory not found"),
        InsufficientSpaceError("Not enough disk space"),
        PermissionError("Permission denied"),
        FileOrganizerException("Corrupted file detected")
    ]
    return random.choice(error_scenarios)
```

---

## Success Criteria by Phase

### **Phase 1 Complete: Working UI**
- ✅ Complete user interface with all dialogs and feedback
- ✅ User can navigate entire workflow with mock data  
- ✅ Progress tracking and cancellation work
- ✅ Error dialogs display properly
- ✅ UI state management functions correctly

### **Phase 2 Complete: Integrated Stubs**
- ✅ UI responds to backend events in real-time
- ✅ Realistic progress updates during mock operations
- ✅ Error scenarios trigger appropriate UI responses
- ✅ Event system enables clean component communication
- ✅ All user interactions produce expected feedback

### **Phase 3 Complete: Real Implementation**
- ✅ Actual file operations work without UI changes
- ✅ Real validation and error handling
- ✅ Performance acceptable for typical file counts
- ✅ Robust error recovery and user feedback
- ✅ Ready for advanced feature integration

---

## Benefits of This Approach

### **Immediate Value**
- **Working demo** available from day 3-4
- **User feedback** possible early in development
- **Requirements validation** through actual UI interaction
- **Stakeholder confidence** with tangible progress

### **Development Advantages**
- **Parallel development** - UI and backend can be refined simultaneously
- **Risk reduction** - major architectural issues discovered early
- **Incremental delivery** - each phase delivers working software
- **Testing foundation** - UI provides test harness for backend development

### **Architecture Benefits**
- **Clean separation** between UI and business logic proven early
- **Event system** tested with real user interactions
- **Service interfaces** defined by actual usage patterns
- **Error handling** validated with user experience

This GUI-first approach ensures you have a working, demonstrable application quickly while building proper architecture for future enhancements.
