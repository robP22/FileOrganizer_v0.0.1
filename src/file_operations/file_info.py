from dataclasses import dataclass
from datetime    import datetime
from pathlib     import Path
from typing      import Dict, Any, Optional, List


@dataclass
class FileInfo:
    """
    Comprehensive file information model.
    Used by organizers to make intelligent organization decisions.
    """
    
    # Basic file properties
    path:       Path
    name:       str
    extension:  str
    size_bytes: int
    
    # Timestamps
    created_date:  Optional[datetime] = None
    modified_date: Optional[datetime] = None
    accessed_date: Optional[datetime] = None
    
    # File type categorization
    file_type: str           = "unknown"  # images, documents, videos, audio, etc.
    mime_type: Optional[str] = None
    
    # Metadata extracted from file content
    metadata: Dict[str, Any] = None
    
    # Organization hints
    suggested_category:    Optional[str] = None
    suggested_subfolder:   Optional[str] = None
    organization_priority: int = 0  # Higher = organize first
    
    def __post_init__(self):
        """Initialize computed fields after dataclass creation"""
        if self.metadata is None:
            self.metadata  = {}
        
        # Extract basic info from path if not provided
        if not self.name:
            self.name      = self.path.name
        if not self.extension:
            self.extension = self.path.suffix.lower()
    
    @classmethod
    def from_path(cls, file_path: Path) -> "FileInfo":
        """Create FileInfo from a file path with basic information"""
        try:
            stat = file_path.stat()
            return cls(
                path         =file_path,
                name         =file_path.name,
                extension    =file_path.suffix.lower(),
                size_bytes   =stat.st_size,
                created_date =datetime.fromtimestamp(stat.st_ctime),
                modified_date=datetime.fromtimestamp(stat.st_mtime),
                accessed_date=datetime.fromtimestamp(stat.st_atime)
            )
        except OSError:
            # Return minimal info if file access fails
            return cls(
                path      =file_path,
                name      =file_path.name,
                extension =file_path.suffix.lower(),
                size_bytes=0
            )
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata extracted from file content"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with default fallback"""
        return self.metadata.get(key, default)
    
    def has_metadata(self, key: str) -> bool:
        """Check if specific metadata exists"""
        return key in self.metadata
    
    def is_image(self) -> bool:
        """Check if file is an image type"""
        return self.file_type == "images" or self.extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    
    def is_document(self) -> bool:
        """Check if file is a document type"""
        return self.file_type == "documents" or self.extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf']
    
    def is_video(self) -> bool:
        """Check if file is a video type"""
        return self.file_type == "videos" or self.extension in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    
    def is_audio(self) -> bool:
        """Check if file is an audio type"""
        return self.file_type == "audio" or self.extension in ['.mp3', '.wav', '.flac', '.aac', '.ogg']
    
    def get_organization_date(self) -> Optional[datetime]:
        """Get the best date to use for organization (metadata > created > modified)"""
        # Try metadata dates first (photo date taken, document created, etc.)
        metadata_date = self.get_metadata('date_taken') or self.get_metadata('date_created')
        if metadata_date:
            return metadata_date
        
        # Fall back to file system dates
        return self.created_date or self.modified_date
    
    def get_size_category(self) -> str:
        """Categorize file by size"""
        if self.size_bytes < 1024 * 1024:  # < 1MB
            return "small"
        elif self.size_bytes < 50 * 1024 * 1024:  # < 50MB
            return "medium"
        else:
            return "large"