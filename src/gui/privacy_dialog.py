from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QCheckBox, QGroupBox, QPushButton, QTextEdit,
                               QComboBox, QSpinBox, QFormLayout)
from PySide6.QtCore import Qt
from core.protocols import ConfigProvider


class PrivacySettingsDialog(QDialog):
    """Privacy and security settings configuration dialog"""
    
    def __init__(self, parent=None, config_provider: ConfigProvider = None):
        super().__init__(parent)
        self.config_provider = config_provider
        self.setWindowTitle("Privacy & Security Settings")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Privacy Controls Section
        privacy_group = QGroupBox("Privacy Controls")
        privacy_layout = QFormLayout(privacy_group)
        
        self.enable_debug_cb = QCheckBox("Enable debug logging (may expose file paths)")
        self.sanitize_errors_cb = QCheckBox("Sanitize error messages (recommended)")
        self.local_only_cb = QCheckBox("Local-only mode (no network access)")
        self.secure_delete_cb = QCheckBox("Securely delete temporary files")
        
        privacy_layout.addRow("Debug Logging:", self.enable_debug_cb)
        privacy_layout.addRow("Error Sanitization:", self.sanitize_errors_cb)
        privacy_layout.addRow("Local Only Mode:", self.local_only_cb)
        privacy_layout.addRow("Secure Deletion:", self.secure_delete_cb)
        
        layout.addWidget(privacy_group)
        
        # Metadata Extraction Controls
        metadata_group = QGroupBox("Metadata Extraction")
        metadata_layout = QFormLayout(metadata_group)
        
        self.extract_gps_cb = QCheckBox("Extract GPS location from photos")
        self.extract_camera_cb = QCheckBox("Extract camera information")
        self.extract_personal_cb = QCheckBox("Extract personal info (author, artist)")
        self.cache_metadata_cb = QCheckBox("Cache metadata for faster processing")
        self.clear_cache_cb = QCheckBox("Clear cache when app closes")
        
        metadata_layout.addRow("GPS Location:", self.extract_gps_cb)
        metadata_layout.addRow("Camera Info:", self.extract_camera_cb)
        metadata_layout.addRow("Personal Info:", self.extract_personal_cb)
        metadata_layout.addRow("Cache Metadata:", self.cache_metadata_cb)
        metadata_layout.addRow("Clear Cache:", self.clear_cache_cb)
        
        layout.addWidget(metadata_group)
        
        # Security Controls
        security_group = QGroupBox("Security Settings")
        security_layout = QFormLayout(security_group)
        
        self.validate_paths_cb = QCheckBox("Validate all file paths")
        self.block_system_cb = QCheckBox("Block system directories")
        self.confirm_paths_cb = QCheckBox("Confirm sensitive operations")
        self.symlink_protection_cb = QCheckBox("Enable symlink protection")
        self.scan_executables_cb = QCheckBox("Scan for executable files")
        
        self.max_file_size = QSpinBox()
        self.max_file_size.setRange(1, 1000)
        self.max_file_size.setSuffix(" MB")
        self.max_file_size.setValue(100)
        
        security_layout.addRow("Path Validation:", self.validate_paths_cb)
        security_layout.addRow("System Protection:", self.block_system_cb)
        security_layout.addRow("Operation Confirmation:", self.confirm_paths_cb)
        security_layout.addRow("Symlink Protection:", self.symlink_protection_cb)
        security_layout.addRow("Executable Scanning:", self.scan_executables_cb)
        security_layout.addRow("Max File Size:", self.max_file_size)
        
        layout.addWidget(security_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.apply_button = QPushButton("Apply Settings")
        self.cancel_button = QPushButton("Cancel")
        
        self.reset_button.clicked.connect(self.reset_to_defaults)
        self.apply_button.clicked.connect(self.apply_settings)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals to update summary
        self.connect_signals()
    
    def connect_signals(self):
        """Connect checkboxes to update privacy summary"""
        checkboxes = [
            self.enable_debug_cb, self.sanitize_errors_cb, self.local_only_cb,
            self.secure_delete_cb, self.extract_gps_cb, self.extract_camera_cb,
            self.extract_personal_cb, self.cache_metadata_cb, self.clear_cache_cb,
            self.validate_paths_cb, self.block_system_cb, self.confirm_paths_cb,
            self.symlink_protection_cb, self.scan_executables_cb
        ]
    
    def load_current_settings(self):
        """Load current settings from privacy config"""
        if not self.config_provider:
            return
            
        # Privacy settings
        self.enable_debug_cb.setChecked(self.config_provider.get_privacy_setting('enable_debug_logging'))
        self.sanitize_errors_cb.setChecked(self.config_provider.get_privacy_setting('sanitize_error_messages'))
        self.local_only_cb.setChecked(self.config_provider.get_privacy_setting('local_only_mode'))
        self.secure_delete_cb.setChecked(self.config_provider.get_privacy_setting('secure_delete_temp_files'))
        
        # Metadata settings
        self.extract_gps_cb.setChecked(self.config_provider.get_metadata_setting('extract_gps_location'))
        self.extract_camera_cb.setChecked(self.config_provider.get_metadata_setting('extract_camera_info'))
        self.extract_personal_cb.setChecked(self.config_provider.get_metadata_setting('extract_personal_info'))
        self.cache_metadata_cb.setChecked(self.config_provider.get_metadata_setting('cache_metadata_locally'))
        self.clear_cache_cb.setChecked(self.config_provider.get_metadata_setting('clear_cache_on_exit'))
        
        # Security settings
        self.validate_paths_cb.setChecked(self.config_provider.get_security_setting('validate_all_paths'))
        self.block_system_cb.setChecked(self.config_provider.get_security_setting('block_system_directories'))
        self.confirm_paths_cb.setChecked(self.config_provider.get_security_setting('require_path_confirmation'))
        self.symlink_protection_cb.setChecked(self.config_provider.get_security_setting('enable_symlink_protection'))
        self.scan_executables_cb.setChecked(self.config_provider.get_security_setting('scan_for_executables'))
        self.max_file_size.setValue(self.config_provider.get_security_setting('maximum_file_size_mb'))
    
    def reset_to_defaults(self):
        """Reset all settings to privacy-first defaults"""
        # Privacy-first defaults
        self.enable_debug_cb.setChecked(False)
        self.sanitize_errors_cb.setChecked(True)
        self.local_only_cb.setChecked(True)
        self.secure_delete_cb.setChecked(True)
        
        # Conservative metadata defaults
        self.extract_gps_cb.setChecked(False)  # Privacy-first: no GPS by default
        self.extract_camera_cb.setChecked(True)
        self.extract_personal_cb.setChecked(False)  # Privacy-first: no personal info by default
        self.cache_metadata_cb.setChecked(True)
        self.clear_cache_cb.setChecked(True)  # Privacy-first: clear cache
        
        # Security-first defaults
        self.validate_paths_cb.setChecked(True)
        self.block_system_cb.setChecked(True)
        self.confirm_paths_cb.setChecked(True)
        self.symlink_protection_cb.setChecked(True)
        self.scan_executables_cb.setChecked(True)
        self.max_file_size.setValue(100)
    
    def apply_settings(self):
        """Apply settings to privacy config and close dialog"""
        if not self.config_provider:
            return
            
        # Update privacy settings
        self.config_provider.set_privacy_setting('enable_debug_logging', self.enable_debug_cb.isChecked())
        self.config_provider.set_privacy_setting('sanitize_error_messages', self.sanitize_errors_cb.isChecked())
        self.config_provider.set_privacy_setting('local_only_mode', self.local_only_cb.isChecked())
        self.config_provider.set_privacy_setting('secure_delete_temp_files', self.secure_delete_cb.isChecked())
        
        # Update metadata settings
        self.config_provider.set_metadata_setting('extract_gps_location', self.extract_gps_cb.isChecked())
        self.config_provider.set_metadata_setting('extract_camera_info', self.extract_camera_cb.isChecked())
        self.config_provider.set_metadata_setting('extract_personal_info', self.extract_personal_cb.isChecked())
        self.config_provider.set_metadata_setting('cache_metadata_locally', self.cache_metadata_cb.isChecked())
        self.config_provider.set_metadata_setting('clear_cache_on_exit', self.clear_cache_cb.isChecked())
        
        # Update security settings
        self.config_provider.set_security_setting('validate_all_paths', self.validate_paths_cb.isChecked())
        self.config_provider.set_security_setting('block_system_directories', self.block_system_cb.isChecked())
        self.config_provider.set_security_setting('require_path_confirmation', self.confirm_paths_cb.isChecked())
        self.config_provider.set_security_setting('enable_symlink_protection', self.symlink_protection_cb.isChecked())
        self.config_provider.set_security_setting('scan_for_executables', self.scan_executables_cb.isChecked())
        self.config_provider.set_security_setting('maximum_file_size_mb', self.max_file_size.value())
        
        # Save configuration
        self.config_provider.save_config()
        
        # Update global privacy logger
        from services.privacy_logger import privacy_logger
        privacy_logger.enable_debug = self.enable_debug_cb.isChecked()
        
        self.accept()
