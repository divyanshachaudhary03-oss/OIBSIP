from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QCheckBox, QSlider, QSpinBox, 
    QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QClipboard
import pyperclip
from generator import SecurePasswordBuilder
from styles import APP_STYLESHEET

class PasswordToolWindow(QMainWindow):
    """Main window for the password generation tool."""
    
    def __init__(self):
        super().__init__()
        self.pwd_builder = SecurePasswordBuilder()
        self._setup_window()
        self._build_interface()
        self._generate_initial_password()
    
    def _setup_window(self):
        """Configure the main window properties."""
        self.setWindowTitle("Secure Password Tool")
        self.setGeometry(120, 120, 580, 680)
        self.setStyleSheet(APP_STYLESHEET)
    
    def _build_interface(self):
        """Construct the complete user interface."""
        # Create central widget and main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create card container
        card_frame = QFrame()
        card_frame.setObjectName("Card")
        card_frame.setFixedWidth(480)
        main_layout.addWidget(card_frame)
        
        # Card content layout
        content_layout = QVBoxLayout(card_frame)
        content_layout.setSpacing(18)
        content_layout.setContentsMargins(35, 35, 35, 35)
        
        # Build interface sections
        self._create_header(content_layout)
        self._create_password_display(content_layout)
        self._create_strength_indicator(content_layout)
        self._create_controls(content_layout)
        self._create_action_buttons(content_layout)
    
    def _create_header(self, parent_layout):
        """Add the title header to the interface."""
        header = QLabel("Password Generator")
        header.setObjectName("Title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(header)
    
    def _create_password_display(self, parent_layout):
        """Create the password output display area."""
        self.pwd_output = QLabel("Generate Your Password")
        self.pwd_output.setObjectName("PasswordDisplay")
        self.pwd_output.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pwd_output.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.pwd_output.setToolTip("Generated password appears here")
        self.pwd_output.setWordWrap(True)
        parent_layout.addWidget(self.pwd_output)
    
    def _create_strength_indicator(self, parent_layout):
        """Add password strength indicator label."""
        self.strength_indicator = QLabel("Strength: Not Evaluated")
        self.strength_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.strength_indicator)
    
    def _create_controls(self, parent_layout):
        """Build all control widgets (length, checkboxes, exclusions)."""
        controls_container = QVBoxLayout()
        controls_container.setSpacing(12)
        parent_layout.addLayout(controls_container)
        
        # Length control section
        self._add_length_control(controls_container)
        
        # Character type checkboxes
        self.uppercase_check = QCheckBox("Include Uppercase (A-Z)")
        self.uppercase_check.setChecked(True)
        self.uppercase_check.setToolTip("Add uppercase letters to password")
        
        self.lowercase_check = QCheckBox("Include Lowercase (a-z)")
        self.lowercase_check.setChecked(True)
        self.lowercase_check.setToolTip("Add lowercase letters to password")
        
        self.numbers_check = QCheckBox("Include Digits (0-9)")
        self.numbers_check.setChecked(True)
        self.numbers_check.setToolTip("Add numeric digits to password")
        
        self.symbols_check = QCheckBox("Include Special Characters (!@#$)")
        self.symbols_check.setChecked(True)
        self.symbols_check.setToolTip("Add special symbols to password")
        
        controls_container.addWidget(self.uppercase_check)
        controls_container.addWidget(self.lowercase_check)
        controls_container.addWidget(self.numbers_check)
        controls_container.addWidget(self.symbols_check)
        
        # Exclusion input section
        self._add_exclusion_control(controls_container)
    
    def _add_length_control(self, parent_layout):
        """Add password length slider and spinbox controls."""
        length_row = QHBoxLayout()
        
        length_text = QLabel("Password Length:")
        
        self.length_slider_widget = QSlider(Qt.Orientation.Horizontal)
        self.length_slider_widget.setRange(4, 64)
        self.length_slider_widget.setValue(12)
        self.length_slider_widget.setToolTip("Adjust password length")
        
        self.length_number_widget = QSpinBox()
        self.length_number_widget.setRange(4, 64)
        self.length_number_widget.setValue(12)
        self.length_number_widget.setToolTip("Set exact length")
        
        # Synchronize slider and spinbox
        self.length_slider_widget.valueChanged.connect(self.length_number_widget.setValue)
        self.length_number_widget.valueChanged.connect(self.length_slider_widget.setValue)
        
        length_row.addWidget(length_text)
        length_row.addWidget(self.length_slider_widget)
        length_row.addWidget(self.length_number_widget)
        
        parent_layout.addLayout(length_row)
    
    def _add_exclusion_control(self, parent_layout):
        """Add character exclusion input field."""
        exclusion_row = QHBoxLayout()
        
        exclusion_text = QLabel("Exclude These Characters:")
        
        self.exclusion_field = QLineEdit()
        self.exclusion_field.setPlaceholderText("e.g., O0Il1")
        self.exclusion_field.setToolTip("Characters to avoid in password")
        
        exclusion_row.addWidget(exclusion_text)
        exclusion_row.addWidget(self.exclusion_field)
        
        parent_layout.addLayout(exclusion_row)
    
    def _create_action_buttons(self, parent_layout):
        """Create generate and copy buttons."""
        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        
        self.generate_button = QPushButton("Generate New Password")
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.clicked.connect(self._handle_generate)
        self.generate_button.setToolTip("Create a new password")
        
        self.copy_button = QPushButton("Copy Password")
        self.copy_button.setObjectName("CopyButton")
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.clicked.connect(self._handle_copy)
        self.copy_button.setToolTip("Copy password to clipboard")
        
        button_row.addWidget(self.generate_button)
        button_row.addWidget(self.copy_button)
        
        parent_layout.addLayout(button_row)
    
    def _handle_generate(self):
        """Handle password generation button click."""
        # Gather user preferences
        desired_length = self.length_number_widget.value()
        want_uppercase = self.uppercase_check.isChecked()
        want_lowercase = self.lowercase_check.isChecked()
        want_numbers = self.numbers_check.isChecked()
        want_symbols = self.symbols_check.isChecked()
        excluded = self.exclusion_field.text()
        
        # Generate password
        result = self.pwd_builder.build_password(
            pwd_length=desired_length,
            include_upper=want_uppercase,
            include_lower=want_lowercase,
            include_numbers=want_numbers,
            include_special=want_symbols,
            forbidden_chars=excluded
        )
        
        # Display result
        self.pwd_output.setText(result)
        
        # Update strength indicator
        if not result.startswith("Error"):
            strength_label, strength_color = self.pwd_builder.evaluate_strength(result)
            self.strength_indicator.setText(f"Strength: {strength_label}")
            self.strength_indicator.setStyleSheet(
                f"color: {strength_color}; font-weight: 600; font-size: 14px;"
            )
        else:
            self.strength_indicator.setText("Strength: Error")
            self.strength_indicator.setStyleSheet(
                "color: #e74c3c; font-weight: 600; font-size: 14px;"
            )
    
    def _handle_copy(self):
        """Handle copy to clipboard button click."""
        current_password = self.pwd_output.text()
        
        if not current_password.startswith("Error") and current_password != "Generate Your Password":
            pyperclip.copy(current_password)
            
            # Provide visual feedback
            self.copy_button.setText("✓ Copied!")
            
            # Reset button text after delay
            QTimer.singleShot(1500, lambda: self.copy_button.setText("Copy Password"))
    
    def _generate_initial_password(self):
        """Generate a password on startup."""
        self._handle_generate()
