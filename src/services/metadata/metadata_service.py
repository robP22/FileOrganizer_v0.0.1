from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from core.protocols import MetadataExtractor, ConfigProvider


class MetadataService:
    """
    Consolidated metadata service with internal registry pattern.
    Prevents coupling by using dependency injection and protocols.
    """
    def __init__(self, config_provider: Optional[ConfigProvider] = None):
        self.config_provider = config_provider
        self._extractors: Dict[str, MetadataExtractor] = {}
        self._fallback_extractor: Optional[MetadataExtractor] = None
        
        # File type mappings (centralized)
        self.image_extensions    = { '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.cr2', '.nef', '.arw', '.dng', '.bmp', '.gif' }
        self.audio_extensions    = { '.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wav', '.wma' }
        self.video_extensions    = { '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v' }
        self.document_extensions = { '.docx', '.xlsx', '.pptx', '.pdf', '.txt', '.md', '.rtf' }

        self._setup_extractors()
    
    def _setup_extractors(self):
        """Setup extractors with lazy loading to prevent import coupling"""
        try:
            from services.metadata.exif_service import ExifService

            exif_service = ExifService()
            for ext in self.image_extensions:
                self._extractors[ext] = exif_service

            self._fallback_extractor = exif_service

        except ImportError:
            pass
        
        try:
            from services.metadata.media_service import MediaService

            media_service = MediaService()
            for ext in list(self.audio_extensions) + list(self.video_extensions):
                self._extractors[ext] = media_service

        except ImportError:
            pass
        
        try:
            from services.metadata.document_service import DocumentService

            document_service = DocumentService()
            for ext in self.document_extensions:
                self._extractors[ext] = document_service

        except ImportError:
            pass
    
    def register_extractor(self, file_extensions: list, extractor: MetadataExtractor):
        """Register an extractor for specific file extensions (for testing/extension)"""
        for ext in file_extensions:
            self._extractors[ext.lower()] = extractor
    
    def get_file_type(self, file_path: Path) -> str:
        """Determine the general category of the file"""
        suffix = file_path.suffix.lower()
        
        if suffix in self.image_extensions:
            return 'image'
        elif suffix in self.audio_extensions:
            return 'audio'
        elif suffix in self.video_extensions:
            return 'video'
        elif suffix in self.document_extensions:
            return 'document'
        else:
            return 'other'
    
    def _get_extractor_for_file(self, file_path: Path) -> Optional[MetadataExtractor]:
        """Get appropriate extractor for a file"""
        extension = file_path.suffix.lower()
        if extension in self._extractors:
            return self._extractors[extension]
        
        return self._fallback_extractor
    
    def _apply_privacy_filtering(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privacy settings to filter metadata"""
        if not self.config_provider:
            filtered       = dict(metadata)
            sensitive_keys = ['gps', 'location', 'author', 'creator', 'owner', 'user', 'editor']
            for key in sensitive_keys:
                if key in filtered:
                    del filtered[key]
            
            return filtered
        
        # Use config provider for privacy settings
        extract_gps = self.config_provider.get_metadata_setting('extract_gps_location')
        extract_personal = self.config_provider.get_metadata_setting('extract_personal_info')
        
        filtered = dict(metadata)
        if not extract_gps and 'gps' in filtered:
            del filtered['gps']
        
        if not extract_personal:
            personal_keys = ['author', 'creator', 'owner', 'user', 'editor']
            for key in personal_keys:
                if key in filtered:
                    del filtered[key]
        
        return filtered
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a file using appropriate service"""
        if not file_path.exists():
            return {}
        
        extractor = self._get_extractor_for_file(file_path)
        metadata = {}
        if extractor:
            try:
                metadata = extractor.extract_metadata(file_path)
            except Exception as e:
                # Silent failure to prevent path exposure in logs
                pass

        metadata = self._apply_privacy_filtering(metadata)
        try:
            stat = file_path.stat()
            metadata.update({ 'file_size': stat.st_size,
                    'created_date': datetime.fromtimestamp(stat.st_ctime),
                    'modified_date': datetime.fromtimestamp(stat.st_mtime),
                    'file_type': self.get_file_type(file_path),
                    'file_name': file_path.name,
                    'file_extension': file_path.suffix.lower() })
        except (OSError, FileNotFoundError):
            pass
        
        return metadata
    
    def extract_comprehensive_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract comprehensive metadata including organization info.
        Maintains compatibility with existing code.
        """
        metadata      = self.extract_metadata(file_path)
        creation_date = self.get_creation_date(file_path)

        if creation_date:
            metadata['organization_date'] = creation_date
            metadata['year']  = creation_date.year
            metadata['month'] = creation_date.month

        metadata['is_media']      = self.is_media_file(file_path)
        metadata['file_category'] = self.get_file_type(file_path)
        
        return metadata
    
    def get_creation_date(self, file_path: Path) -> Optional[datetime]:
        """Get the creation date of a file"""
        metadata = self.extract_metadata(file_path)
        
        # Try different metadata fields for creation date
        for date_field in ['creation_date', 'date_taken', 'created_date', 'modified_date']:
            if date_field in metadata and metadata[date_field]:
                return metadata[date_field]
        
        return None
    
    def get_organization_info(self, file_path: Path) -> Dict[str, Any]:
        """Get organization-specific metadata for file placement"""
        metadata = self.extract_comprehensive_metadata(file_path)
        organization_info = {
            'file_type': metadata.get('file_category', 'other'),
            'creation_date': metadata.get('organization_date'),
            'is_media': metadata.get('is_media', False),
            'file_size': metadata.get('file_size', 0)
        }

        if organization_info['creation_date']:
            date = organization_info['creation_date']
            organization_info['year'] = date.year
            organization_info['month'] = date.month
        
        return organization_info
    
    def is_media_file(self, file_path: Path) -> bool:
        """Check if file is a media file (image, audio, or video)"""
        file_type = self.get_file_type(file_path)
        return file_type in ['image', 'audio', 'video']
    
    def get_best_organization_date(self, file_path: Path) -> datetime:
        """ Get the most appropriate date for organizing this file. """
        file_type = self.get_file_type(file_path)
        extractor = self._get_extractor_for_file(file_path)

        if extractor and hasattr(extractor, 'get_organization_date'):
            try:
                date = extractor.get_organization_date(file_path)
                if date:
                    return date
            except Exception:
                pass

        try:
            stat_result = file_path.stat()
            if hasattr(stat_result, 'st_birthtime'):
                return datetime.fromtimestamp(stat_result.st_birthtime)
            else:
                return datetime.fromtimestamp(stat_result.st_mtime)
                
        except (OSError, ValueError):
            # Ultimate fallback to current time
            return datetime.now()
