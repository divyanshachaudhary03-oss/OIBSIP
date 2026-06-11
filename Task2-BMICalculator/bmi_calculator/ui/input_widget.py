from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QFormLayout, QInputDialog
)
from PyQt6.QtCore import pyqtSignal, Qt

class DataEntryPanel(QWidget):
    """Widget for entering BMI calculation data."""
    
    # Custom signals
    calculation_requested = pyqtSignal(float, float)  # weight, height
    user_selection_changed = pyqtSignal(int)  # user_id
    new_user_requested = pyqtSignal(str)  # username
    user_deletion_requested = pyqtSignal(int)  # user_id
    
    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self._build_ui()
    
    def _build_ui(self):
        """Construct the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_label = QLabel("🏥 BMI Health Calculator")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 800;
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(138, 43, 226, 0.3),
                                            stop:1 rgba(255, 0, 110, 0.3));
                padding: 20px;
                border-radius: 15px;
                border: 2px solid rgba(138, 43, 226, 0.5);
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # User selection section
        user_section_label = QLabel("👤 User Management")
        user_section_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #c77dff;
                padding: 8px;
            }
        """)
        main_layout.addWidget(user_section_label)
        
        user_row = QHBoxLayout()
        user_row.setSpacing(10)
        
        user_label = QLabel("Select User:")
        user_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        
        self.user_dropdown = QComboBox()
        self.user_dropdown.setMinimumHeight(40)
        self.user_dropdown.currentIndexChanged.connect(self._on_user_selection_changed)
        
        self.add_user_button = QPushButton("➕ Add New User")
        self.add_user_button.setMinimumHeight(40)
        self.add_user_button.clicked.connect(self._handle_add_user)
        
        self.delete_user_button = QPushButton("Delete User")
        self.delete_user_button.setMinimumHeight(40)
        self.delete_user_button.clicked.connect(self._handle_delete_user)
        
        user_row.addWidget(user_label)
        user_row.addWidget(self.user_dropdown, 2)
        user_row.addWidget(self.add_user_button)
        user_row.addWidget(self.delete_user_button)
        main_layout.addLayout(user_row)
        
        # Separator
        main_layout.addSpacing(10)
        
        # Input form section
        form_section_label = QLabel("📊 Enter Your Measurements")
        form_section_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #c77dff;
                padding: 8px;
            }
        """)
        main_layout.addWidget(form_section_label)
        
        form = QFormLayout()
        form.setSpacing(15)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.weight_field = QLineEdit()
        self.weight_field.setPlaceholderText("e.g., 70.5")
        self.weight_field.setMinimumHeight(45)
        
        self.height_field = QLineEdit()
        self.height_field.setPlaceholderText("e.g., 1.75")
        self.height_field.setMinimumHeight(45)
        
        weight_label = QLabel("Body Weight (kg):")
        weight_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        height_label = QLabel("Body Height (m):")
        height_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        
        form.addRow(weight_label, self.weight_field)
        form.addRow(height_label, self.height_field)
        main_layout.addLayout(form)
        
        # Calculate button
        main_layout.addSpacing(10)
        self.calculate_button = QPushButton("🔍 Calculate My BMI")
        self.calculate_button.setMinimumHeight(50)
        self.calculate_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 800;
            }
        """)
        self.calculate_button.clicked.connect(self._handle_calculation)
        main_layout.addWidget(self.calculate_button)
        
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self._reload_user_list()
    
    def _reload_user_list(self):
        """Refresh the user dropdown with current data."""
        self.user_dropdown.blockSignals(True)
        self.user_dropdown.clear()
        
        users = self.data_store.fetch_all_users()
        for user_id, username in users:
            self.user_dropdown.addItem(username, user_id)
        
        self.user_dropdown.blockSignals(False)
        
        if self.user_dropdown.count() > 0:
            self._on_user_selection_changed()
    
    def _handle_add_user(self):
        """Handle the add user button click."""
        username, confirmed = QInputDialog.getText(
            self, "Register New User", "Enter username:"
        )
        if confirmed and username:
            self.new_user_requested.emit(username)
    
    def _on_user_selection_changed(self):
        """Handle user dropdown selection change."""
        user_id = self.user_dropdown.currentData()
        if user_id is not None:
            self.user_selection_changed.emit(user_id)
    
    def _handle_calculation(self):
        """Handle calculate button click."""
        try:
            weight = float(self.weight_field.text())
            height = float(self.height_field.text())
            self.calculation_requested.emit(weight, height)
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input",
                "Please enter valid numeric values for weight and height."
            )
    
    def refresh_users(self):
        """Public method to refresh user list."""
        self._reload_user_list()
    
    def _handle_delete_user(self):
        """Handle the delete user button click."""
        user_id = self.user_dropdown.currentData()
        if user_id is None:
            QMessageBox.warning(
                self, "No User Selected",
                "Please select a user to delete."
            )
            return
        
        username = self.user_dropdown.currentText()
        confirmation = QMessageBox.question(
            self, 'Confirm Deletion',
            f"Are you sure you want to delete user '{username}' and all their BMI records?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            self.user_deletion_requested.emit(user_id)
