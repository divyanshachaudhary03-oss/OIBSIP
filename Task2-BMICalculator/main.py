import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from bmi_calculator.ui.main_window import BMITrackerWindow

def launch_bmi_tracker():
    """
    Initialize and launch the BMI tracking application.
    """
    try:
        # Create application instance
        application = QApplication(sys.argv)
        
        # Set application metadata
        application.setApplicationName("BMI Health Tracker")
        application.setOrganizationName("OIBSIP")
        
        # Load custom stylesheet
        stylesheet_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        try:
            with open(stylesheet_path, "r") as stylesheet_file:
                application.setStyleSheet(stylesheet_file.read())
        except FileNotFoundError:
            print("Warning: Stylesheet file not found, using default styling")
        
        # Create and display main window
        main_window = BMITrackerWindow()
        main_window.show()
        
        # Start event loop
        return application.exec()
    
    except Exception as error:
        print(f"Application error: {error}")
        return 1

if __name__ == "__main__":
    exit_code = launch_bmi_tracker()
    sys.exit(exit_code)
