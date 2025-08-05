from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class MediaService:
    """Service for extracting metadata from audio and video files"""
    
    def __init__(self):
        self.audio_formats = {'.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wav', '.wma'}
        self.video_formats = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
    

    def can_extract_metadata(self, file_path: Path) -> bool:
        """Check if file is a supported media format"""
        suffix = file_path.suffix.lower()
        return (suffix in self.audio_formats or suffix in self.video_formats) and MUTAGEN_AVAILABLE
    

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from audio/video file
        
        Returns:
            Dict containing artist, album, genre, duration, quality info
        """
        if not self.can_extract_metadata(file_path):
            return {}
        
        try:
            audiofile = MutagenFile(file_path)
            if audiofile is None:
                return {}
            
            metadata = {}
            
            # Audio-specific metadata
            if file_path.suffix.lower() in self.audio_formats:
                metadata.update(self._extract_audio_metadata(audiofile))
            
            # Video-specific metadata  
            if file_path.suffix.lower() in self.video_formats:
                metadata.update(self._extract_video_metadata(audiofile))
            
            # Common metadata
            metadata.update(self._extract_common_metadata(audiofile))
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return {}
    

    def _extract_audio_metadata(self, audiofile) -> Dict[str, Any]:
        """Extract audio-specific metadata"""
        metadata = {}
        
        # Standard tags
        tag_mapping = {
            'artist': ['TPE1', 'ARTIST', '\xa9ART'],
            'album': ['TALB', 'ALBUM', '\xa9alb'],
            'title': ['TIT2', 'TITLE', '\xa9nam'],
            'genre': ['TCON', 'GENRE', '\xa9gen'],
            'date': ['TDRC', 'DATE', '\xa9day'],
            'albumartist': ['TPE2', 'ALBUMARTIST', 'aART'],
            'track': ['TRCK', 'TRACKNUMBER', 'trkn'],
            'disc': ['TPOS', 'DISCNUMBER', 'disk']
        }
        
        for field, possible_tags in tag_mapping.items():
            for tag in possible_tags:
                if tag in audiofile and audiofile[tag]:
                    value = audiofile[tag][0] if isinstance(audiofile[tag], list) else audiofile[tag]
                    metadata[field] = str(value)
                    break
        
        # Audio quality information
        if hasattr(audiofile, 'info'):
            info = audiofile.info
            if hasattr(info, 'bitrate'):
                metadata['bitrate'] = f"{info.bitrate}kbps"
            if hasattr(info, 'sample_rate'):
                metadata['sample_rate'] = f"{info.sample_rate}Hz"
            if hasattr(info, 'channels'):
                metadata['channels'] = info.channels
            if hasattr(info, 'length'):
                metadata['duration_seconds'] = int(info.length)
                metadata['duration'] = self._format_duration(info.length)
        
        return metadata
    

    def _extract_video_metadata(self, videofile) -> Dict[str, Any]:
        """Extract video-specific metadata"""
        metadata = {}
        
        # Video quality information
        if hasattr(videofile, 'info'):
            info = videofile.info
            if hasattr(info, 'bitrate'):
                metadata['bitrate'] = f"{info.bitrate}kbps"
            if hasattr(info, 'length'):
                metadata['duration_seconds'] = int(info.length)
                metadata['duration'] = self._format_duration(info.length)
        
        return metadata
    

    def _extract_common_metadata(self, mediafile) -> Dict[str, Any]:
        """Extract metadata common to both audio and video"""
        metadata = {}
        
        # File format information
        if hasattr(mediafile, 'mime'):
            metadata['format'] = mediafile.mime[0] if mediafile.mime else 'unknown'
        
        return metadata
    

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS"""
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    

    def get_organization_date(self, file_path: Path) -> Optional[datetime]:
        """Get the best date for organizing this media file"""
        metadata = self.extract_metadata(file_path)
        
        # Try to parse date from metadata
        if 'date' in metadata:
            try:
                # Handle various date formats
                date_str = metadata['date']
                for fmt in ['%Y-%m-%d', '%Y', '%Y-%m']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            except Exception:
                pass
        
        # Fallback to file modification time
        try:
            stat_result = file_path.stat()
            return datetime.fromtimestamp(stat_result.st_mtime)
        except OSError:
            return None
    
    
    def get_organization_info(self, file_path: Path) -> Dict[str, str]:
        """Get key information for file organization"""
        metadata = self.extract_metadata(file_path)
        
        org_info = {}
        
        # For music files
        if file_path.suffix.lower() in self.audio_formats:
            if 'artist' in metadata:
                org_info['artist'] = metadata['artist']
            if 'album' in metadata:
                org_info['album'] = metadata['album']
            if 'genre' in metadata:
                org_info['genre'] = metadata['genre']
        
        # For video files
        if file_path.suffix.lower() in self.video_formats:
            if 'duration_seconds' in metadata:
                duration = metadata['duration_seconds']
                if duration < 300:  # 5 minutes
                    org_info['category'] = 'Short Videos'
                elif duration < 3600:  # 1 hour
                    org_info['category'] = 'Medium Videos'
                else:
                    org_info['category'] = 'Long Videos'
        
        return org_info
