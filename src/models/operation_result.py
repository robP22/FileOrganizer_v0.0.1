from dataclasses import dataclass, field
from datetime    import datetime
from pathlib     import Path
from typing      import List, Dict, Any, Optional


@dataclass
class FileOperationResult:
    """Result of a single file operation"""
    
    source_file:      str  # Just filename for security
    operation:        str  # "move", "copy", "organize", "unorganize"
    success:          bool
    destination_path: Optional[str] = None  # Just filename for security
    error_message:    Optional[str] = None
    processing_time:  float         = 0.0  # seconds
    file_size:        int           = 0    # bytes
    
    # Enhanced tracking for unorganize operations
    original_source_path:   Optional[str] = None  # Full path for unorganize (stored securely)
    organized_destination_path: Optional[str] = None  # Full organized path for unorganize
    

@dataclass
class OperationProgress:
    """Real-time progress tracking for batch operations"""
    
    operation_id:     str
    total_files:      int
    processed_files:  int           = 0
    successful_files: int           = 0
    failed_files:     int           = 0
    start_time:       datetime      = field(default_factory=datetime.now)
    current_file:     Optional[str] = None  # Current file being processed
    
    # Results tracking
    results:          List[FileOperationResult] = field(default_factory=list)
    
    # Performance metrics
    avg_processing_time: float = 0.0
    estimated_remaining: float = 0.0  # seconds
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage (0-100)"""
        if self.total_files == 0:
            return 100.0
        return (self.processed_files / self.total_files) * 100.0
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def files_per_second(self) -> float:
        """Calculate processing rate"""
        if self.elapsed_time == 0:
            return 0.0
        return self.processed_files / self.elapsed_time
    
    def add_result(self, result: FileOperationResult):
        """Add a file operation result and update metrics"""
        self.results.append(result)
        self.processed_files += 1
        
        if result.success:
            self.successful_files += 1
        else:
            self.failed_files += 1
        
        # Update performance metrics
        if self.processed_files > 0:
            total_time              = sum(r.processing_time for r in self.results)
            self.avg_processing_time = total_time / self.processed_files
            
            remaining_files         = self.total_files - self.processed_files
            self.estimated_remaining = remaining_files * self.avg_processing_time
    
    def get_failed_operations(self) -> List[FileOperationResult]:
        """Get list of failed operations for retry"""
        return [r for r in self.results if not r.success]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operation summary for UI display"""
        return {
            "operation_id":        self.operation_id,
            "total_files":         self.total_files,
            "processed":           self.processed_files,
            "successful":          self.successful_files,
            "failed":              self.failed_files,
            "completion_percent":  round(self.completion_percentage, 1),
            "elapsed_seconds":     round(self.elapsed_time, 1),
            "files_per_second":    round(self.files_per_second, 2),
            "estimated_remaining": round(self.estimated_remaining, 1),
            "results":             [self._result_to_dict(r) for r in self.results]
        }
    
    def _result_to_dict(self, result: 'FileOperationResult') -> Dict[str, Any]:
        """Convert FileOperationResult to dictionary"""
        return {
            "source_file": result.source_file,
            "operation": result.operation,
            "success": result.success,
            "destination_path": result.destination_path,
            "error_message": result.error_message,
            "processing_time": result.processing_time,
            "file_size": result.file_size,
            "original_source_path": result.original_source_path,
            "organized_destination_path": result.organized_destination_path
        }