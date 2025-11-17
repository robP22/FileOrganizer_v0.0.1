FILE_TYPE_CATEGORIES = {
    'Images': {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
        '.svg', '.webp', '.ico', '.raw', '.cr2', '.nef', '.orf', '.dng'
    },
    'Documents': {
        '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', 
        '.xlsx', '.ppt', '.pptx', '.csv', '.md', '.tex'
    },
    'Videos': {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', 
        '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv'
    },
    'Audio': {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', 
        '.opus', '.aiff', '.au'
    },
    'Archives': {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', 
        '.tar.gz', '.tar.bz2', '.tar.xz'
    },
    'Code': {
        '.py', '.js', '.html', '.css', '.cpp', '.c', '.java', 
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts'
    },
    'Executables': {
        '.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.app', 
        '.apk', '.ipa'
    }
}

MEDIA_EXTENSIONS = (
        FILE_TYPE_CATEGORIES['Images'] |
        FILE_TYPE_CATEGORIES['Videos'] |
        FILE_TYPE_CATEGORIES['Audio'] )

DOCUMENT_EXTENSIONS = FILE_TYPE_CATEGORIES['Documents']