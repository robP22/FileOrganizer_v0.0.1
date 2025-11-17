import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from file_operations.file_service       import FileService
from services.core.organization_service import OrganizationService
from services.core.unorganize_service   import UnorganizeService
from services.config.config_service     import privacy_config
from core.config_interface import ConfigAdapter
from gui.main_window       import MainWindow
from PySide6.QtWidgets     import QApplication

def main():
    app = QApplication()

    config_adapter = ConfigAdapter(privacy_config)
    file_service   = FileService()
    organization_service = OrganizationService(file_service, config_adapter)
    unorganize_service   = UnorganizeService(file_service)

    window = MainWindow(config_provider=config_adapter)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
