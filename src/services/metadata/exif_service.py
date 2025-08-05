from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import exifread
    from PIL import Image
    from PIL.ExifTags import TAGS
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False

from services.config.privacy_logger import privacy_logger


class ExifService:
    """Service for extracting EXIF metadata from images"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif', '.cr2', '.nef', '.arw', '.dng'}
    

    def can_extract_metadata(self, file_path: Path) -> bool:
        """Check if file is a supported image format"""
        return file_path.suffix.lower() in self.supported_formats and EXIF_AVAILABLE
    

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract comprehensive EXIF metadata from image file
        
        Returns:
            Dict containing camera info, GPS, dates, technical specs
        """
        if not self.can_extract_metadata(file_path):
            return {}
        
        metadata = {}
        
        try:
            # Use PIL for basic EXIF data
            with Image.open(file_path) as img:
                exifdata = img.getexif()
                
                if exifdata:
                    # Camera information
                    metadata.update(self._extract_camera_info(exifdata))
                    
                    # GPS information
                    gps_data = self._extract_gps_info(exifdata)
                    if gps_data:
                        metadata['gps'] = gps_data
                    
                    # Date information
                    date_taken = self._extract_date_taken(exifdata)
                    if date_taken:
                        metadata['date_taken'] = date_taken
                    
                    # Technical specs
                    metadata.update(self._extract_technical_specs(exifdata))
        
        except Exception as e:
            privacy_logger.log_error("ExifService", "extract_metadata", e, str(file_path))
        
        return metadata
    

    def _extract_camera_info(self, exifdata) -> Dict[str, str]:
        """Extract camera make, model, lens info"""
        camera_info = {}
        
        # Camera make and model
        if 271 in exifdata:  # Make
            camera_info['camera_make'] = str(exifdata[271])
        if 272 in exifdata:  # Model
            camera_info['camera_model'] = str(exifdata[272])
        if 305 in exifdata:  # Software
            camera_info['software'] = str(exifdata[305])
        
        # Lens information
        if 42036 in exifdata:  # Lens model
            camera_info['lens_model'] = str(exifdata[42036])
        
        return camera_info
    

    def _extract_gps_info(self, exifdata) -> Optional[Dict[str, float]]:
        """Extract GPS coordinates if available"""
        try:
            gps_info = exifdata.get_ifd(0x8825)  # GPS IFD
            if not gps_info:
                return None
            
            def convert_to_degrees(value):
                """Convert GPS coordinates to decimal degrees"""
                d, m, s = value
                return d + (m / 60.0) + (s / 3600.0)
            
            gps_data = {}
            
            if 2 in gps_info and 1 in gps_info:  # Latitude
                lat = convert_to_degrees(gps_info[2])
                if gps_info[1] == 'S':
                    lat = -lat
                gps_data['latitude'] = lat
            
            if 4 in gps_info and 3 in gps_info:  # Longitude
                lon = convert_to_degrees(gps_info[4])
                if gps_info[3] == 'W':
                    lon = -lon
                gps_data['longitude'] = lon
            
            if 6 in gps_info:  # Altitude
                gps_data['altitude'] = float(gps_info[6])
            
            return gps_data if gps_data else None
        
        except Exception:
            return None
    

    def _extract_date_taken(self, exifdata) -> Optional[datetime]:
        """Extract the date photo was taken"""
        # Try different date fields
        date_tags = [36867, 36868, 306]  # DateTimeOriginal, DateTimeDigitized, DateTime
        
        for tag in date_tags:
            if tag in exifdata:
                try:
                    date_str = str(exifdata[tag])
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    continue
        
        return None
    

    def _extract_technical_specs(self, exifdata) -> Dict[str, Any]:
        """Extract technical photography specs"""
        specs = {}
        
        # ISO
        if 34855 in exifdata:
            specs['iso'] = int(exifdata[34855])
        
        # Aperture
        if 33437 in exifdata:  # FNumber
            specs['aperture'] = f"f/{float(exifdata[33437])}"
        
        # Shutter speed
        if 33434 in exifdata:  # ExposureTime
            exposure = exifdata[33434]
            if exposure < 1:
                specs['shutter_speed'] = f"1/{int(1/exposure)}"
            else:
                specs['shutter_speed'] = f"{exposure}s"
        
        # Focal length
        if 37386 in exifdata:
            specs['focal_length'] = f"{float(exifdata[37386])}mm"
        
        # Image dimensions
        if 256 in exifdata and 257 in exifdata:  # ImageWidth, ImageLength
            specs['width'] = int(exifdata[256])
            specs['height'] = int(exifdata[257])
        
        return specs
    

    def get_organization_date(self, file_path: Path) -> Optional[datetime]:
        """Get the best date for organizing this image"""
        metadata = self.extract_metadata(file_path)
        
        # Prefer date taken from EXIF
        if 'date_taken' in metadata:
            return metadata['date_taken']
        
        # Fallback to file modification time
        try:
            stat_result = file_path.stat()
            return datetime.fromtimestamp(stat_result.st_mtime)
        except OSError:
            return None
