from core.events import event_bus
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.source_path = None           # Store selected source directory
        self.destination_path = None             # Store selected destination directory
        self.setWindowTitle("File Organizer")

        event_bus.subscribe("file_manager_opened", self.on_file_manager_opened)
        event_bus.subscribe("file_manager_failed", self.on_file_manager_failed)

        self.setGeometry(100, 100, 800, 600)
        self.initUI()


    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        main_layout.addLayout(self.sourceDirectory())
        main_layout.addLayout(self.destinationDirectory())

        organize_button = QPushButton("Organize Files")
        organize_button.clicked.connect(self.start_organization)
        organize_button.setEnabled(False)

        self.organize_button = organize_button

        main_layout.addWidget(organize_button)
        main_layout.addStretch()


    def sourceDirectory(self):
        source_layout = QHBoxLayout()
        self.source_label = QLabel("Source Directory: Not selected")

        source_button = QPushButton("Browse Source")
        source_button.clicked.connect(self.open_source_file_manager)

        source_layout.addWidget(self.source_label)
        source_layout.addWidget(source_button)

        return source_layout


    def destinationDirectory(self):
        destination_layout = QHBoxLayout()
        self.destination_label = QLabel("Destination Directory: Not selected")

        destination_button = QPushButton("Browse Destination")
        destination_button.clicked.connect(self.open_destination_file_manager)

        destination_layout.addWidget(self.destination_label)
        destination_layout.addWidget(destination_button)

        return destination_layout
    

    def open_source_file_manager(self):
        """ Opens native file manager to source directory through FileService """
        event_bus.publish("file_manager_requested", {"directory_type": "source"})


    def open_destination_file_manager(self):
        """ Opens native file manager to destination directory through FileService """
        event_bus.publish("file_manager_requested", {"directory_type": "destination"})


    def on_file_manager_opened(self, event):
        """ Handle successful file manager opening """
        directory_type = event.data.get("directory_type")
        selected_path = event.data.get("selected_path")

        if directory_type == "source":
            self.source_path = selected_path
            self.source_label.setText(f"Source Directory: {selected_path}")
        
        elif directory_type == "destination":
            self.destination_path = selected_path
            self.destination_label.setText(f"Destination Directory: {selected_path}")

        self.update_organize_button_state()


    def on_file_manager_failed(self, event):
        """ Handle file manager opening failure """
        directory_type = event.data.get("directory_type")

        if directory_type == "source":
            self.source_label.setText("Source Directory: Error opening file manager")

        elif directory_type == "destination":
            self.destination_label.setText("Destination Directory: Error opening file manager")


    def update_organize_button_state(self):
        """ Enable organize button only when both directories have been selected """
        both_selected = self.source_path is not None and self.destination_path is not None
        self.organize_button.setEnabled(both_selected)


    def start_organization(self):
        """ Handle organize button click - publish organize request to event """
        if self.source_path and self.destination_path:
            event_bus.publish("organize_requested", {
                "source_path": self.source_path,
                "destination_path": self.destination_path
            })