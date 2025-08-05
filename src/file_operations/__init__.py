"""
File operations package for FileOrganizer.

This package contains file operations, utilities, and types.
"""
# Always available imports
from .file_utils import ensure_directory_exists, get_unique_file_path, get_file_modification_date
from .file_types import FILE_TYPE_CATEGORIES, MEDIA_EXTENSIONS, DOCUMENT_EXTENSIONS

# Conditional import for FileService (requires PySide6)
try:
    from .file_service import FileService
    _file_service_available = True
except ImportError:
    _file_service_available = False
    FileService = None

__all__ = [
    'ensure_directory_exists',
    'get_unique_file_path', 
    'get_file_modification_date',
    'FILE_TYPE_CATEGORIES',
    'MEDIA_EXTENSIONS',
    'DOCUMENT_EXTENSIONS',
]

# Only export FileService if it's available
if _file_service_available:
    __all__.append('FileService')
