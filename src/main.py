import sys

from services.file_service import FileService
from services.organization_service import OrganizationService
from gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication()

    file_service = FileService()
    organization_service = OrganizationService()

    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()