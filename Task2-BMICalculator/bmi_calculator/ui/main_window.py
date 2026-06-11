from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from .input_widget import DataEntryPanel
from .history_widget import TrendsDisplayPanel
from ..database import BMIDataStore
from ..logic import HealthMetricsCalculator

class BMITrackerWindow(QMainWindow):
    """Main application window for BMI tracking."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏥 BMI Health Tracker - Modern Edition")
        self.setGeometry(100, 100, 950, 720)
        
        self.data_store = BMIDataStore()
        self._setup_interface()
    
    def _setup_interface(self):
        """Initialize the user interface."""
        self.tab_container = QTabWidget()
        self.setCentralWidget(self.tab_container)
        
        # Calculator tab
        self.entry_panel = DataEntryPanel(self.data_store)
        self.entry_panel.calculation_requested.connect(self._process_bmi_calculation)
        self.entry_panel.user_selection_changed.connect(self._load_user_history)
        self.entry_panel.new_user_requested.connect(self._register_new_user)
        self.entry_panel.user_deletion_requested.connect(self._delete_user)
        self.tab_container.addTab(self.entry_panel, "BMI Calculator")
        
        # History tab
        self.trends_panel = TrendsDisplayPanel()
        self.trends_panel.clear_history_button.clicked.connect(self._clear_user_history)
        self.tab_container.addTab(self.trends_panel, "History & Trends")
        
        # Load initial data if users exist
        if self.entry_panel.user_dropdown.count() > 0:
            self.entry_panel._on_user_selection_changed()
    
    def _register_new_user(self, username):
        """Register a new user in the system."""
        user_id = self.data_store.register_user(username)
        if user_id:
            QMessageBox.information(
                self, "Registration Successful",
                f"User '{username}' has been registered successfully!"
            )
            self.entry_panel.refresh_users()
        else:
            QMessageBox.warning(
                self, "Registration Failed",
                f"User '{username}' already exists in the system!"
            )
    
    def _process_bmi_calculation(self, weight, height):
        """Process BMI calculation request."""
        try:
            bmi_value = HealthMetricsCalculator.compute_body_mass_index(weight, height)
            health_category = HealthMetricsCalculator.determine_health_category(bmi_value)
            
            current_user_id = self.entry_panel.user_dropdown.currentData()
            if current_user_id is None:
                QMessageBox.warning(
                    self, "No User Selected",
                    "Please select or register a user before calculating BMI."
                )
                return
            
            # Save the calculation
            self.data_store.save_bmi_entry(current_user_id, weight, height, bmi_value)
            
            # Display result
            QMessageBox.information(
                self, "BMI Calculation Result",
                f"Your BMI: {bmi_value:.2f}\nHealth Category: {health_category}"
            )
            
            # Refresh history display
            self._load_user_history(current_user_id)
            
        except ValueError as error:
            QMessageBox.warning(self, "Calculation Error", str(error))
    
    def _load_user_history(self, user_id):
        """Load and display user's BMI history."""
        history_records = self.data_store.fetch_user_history(user_id)
        self.trends_panel.update_data(history_records)
    
    def _clear_user_history(self):
        """Clear all history for the current user."""
        current_user_id = self.entry_panel.user_dropdown.currentData()
        if current_user_id is None:
            return
        
        confirmation = QMessageBox.question(
            self, 'Confirm Deletion',
            "Are you sure you want to delete all BMI history for this user?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            self.data_store.remove_user_history(current_user_id)
            self._load_user_history(current_user_id)
            QMessageBox.information(
                self, "History Cleared",
                "All BMI history has been deleted successfully."
            )
    
    def _delete_user(self, user_id):
        """Delete a user completely from the system."""
        if self.data_store.delete_user(user_id):
            QMessageBox.information(
                self, "User Deleted",
                "User and all associated records have been deleted successfully."
            )
            self.entry_panel.refresh_users()
            self.trends_panel.update_data([])
        else:
            QMessageBox.warning(
                self, "Deletion Failed",
                "Failed to delete user. Please try again."
            )
