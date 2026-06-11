import sys
from PyQt6.QtWidgets import QApplication
from gui import PasswordToolWindow

def launch_application():
    """
    Initialize and launch the password generator application.
    """
    try:
        # Create application instance
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("Secure Password Generator")
        app.setOrganizationName("OIBSIP")
        
        # Create and display main window
        main_window = PasswordToolWindow()
        main_window.show()
        
        # Start event loop
        return app.exec()
    
    except Exception as error:
        print(f"Application error: {error}")
        return 1

if __name__ == "__main__":
    exit_code = launch_application()
    sys.exit(exit_code)
