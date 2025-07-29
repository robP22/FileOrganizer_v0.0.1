import sys
from gui import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    """ Launches the GUI """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()