import sys
import requests
import geocoder
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QMessageBox, QFrame
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QFont

class WeatherModel:

    def __init__(self):
        self.weather_data: Optional[Dict[str, Any]] = None
    
    def parse_weather_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:

        try:
            parsed = {
                'city': json_data.get('name', 'Unknown'),
                'country': json_data.get('sys', {}).get('country', ''),
                'temp_kelvin': json_data.get('main', {}).get('temp', 0),
                'temp_celsius': json_data.get('main', {}).get('temp', 0) - 273.15,
                'temp_fahrenheit': (json_data.get('main', {}).get('temp', 0) - 273.15) * 9/5 + 32,
                'condition': json_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'description': json_data.get('weather', [{}])[0].get('description', '').title(),
                'humidity': json_data.get('main', {}).get('humidity', 0),
                'pressure': json_data.get('main', {}).get('pressure', 0),
                'wind_speed': json_data.get('wind', {}).get('speed', 0),
                'icon_code': json_data.get('weather', [{}])[0].get('icon', '01d')
            }
            self.weather_data = parsed
            return parsed
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Failed to parse weather data: {str(e)}")
    
    def get_icon_url(self, icon_code: str) -> str:
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


class WeatherWorker(QThread):
    """
    QThread worker for handling API requests in background.
    Prevents UI freezing during network operations.
    
    Signals:
        weather_fetched: Emitted when weather data is successfully retrieved
        error_occurred: Emitted when an error occurs during API call
        location_detected: Emitted when user location is successfully detected
    """
    
    weather_fetched = pyqtSignal(dict) 
    error_occurred = pyqtSignal(str)    
    location_detected = pyqtSignal(str) 
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.city: Optional[str] = None
        self.use_coords = False
        self.lat: Optional[float] = None
        self.lon: Optional[float] = None
        self.model = WeatherModel()
    
    def set_city(self, city: str):
        """Set the city to fetch weather for."""
        self.city = city
        self.use_coords = False
    
    def set_coordinates(self, lat: float, lon: float):
        """Set coordinates for location-based weather fetch."""
        self.lat = lat
        self.lon = lon
        self.use_coords = True
    
    def run(self):
        """
        Main thread execution method.
        This runs in a separate thread to avoid blocking the UI.
        """
        try:
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            
            if self.use_coords and self.lat is not None and self.lon is not None:
                url = f"{base_url}?lat={self.lat}&lon={self.lon}&appid={self.api_key}"
            elif self.city:
                url = f"{base_url}?q={self.city}&appid={self.api_key}"
            else:
                self.error_occurred.emit("No city or coordinates provided.")
                return
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 401:
                self.error_occurred.emit("Invalid API Key. Please check your OpenWeatherMap API key.")
                return
            elif response.status_code == 404:
                self.error_occurred.emit(f"City '{self.city}' not found. Please check the spelling.")
                return
            elif response.status_code != 200:
                self.error_occurred.emit(f"API Error: {response.status_code} - {response.text}")
                return
            
            json_data = response.json()
            parsed_data = self.model.parse_weather_data(json_data)
            
            self.weather_fetched.emit(parsed_data)
            
        except requests.exceptions.Timeout:
            self.error_occurred.emit("Request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Connection error. Please check your internet connection.")
        except ValueError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}")


class LocationWorker(QThread):
    """
    Separate thread for detecting user location via IP.
    """
    location_detected = pyqtSignal(float, float, str)  
    error_occurred = pyqtSignal(str)
    
    def run(self):
        """Detect user location using IP-based geolocation."""
        try:
            g = geocoder.ip('me')
            if g.ok and g.latlng:
                lat, lon = g.latlng
                city = g.city or "Unknown Location"
                self.location_detected.emit(lat, lon, city)
            else:
                self.error_occurred.emit("Could not detect location. Please enter city manually.")
        except Exception as e:
            self.error_occurred.emit(f"Location detection failed: {str(e)}")


class MainWindow(QMainWindow):
    """
    Main application window managing UI and user interactions.
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = "abcd_enter_your_api_key" 
        self.current_unit = "celsius"  
        self.weather_data: Optional[Dict[str, Any]] = None
        
        self.init_ui()
        self.apply_dark_theme()
    
    def init_ui(self):
        """Initialize and setup the user interface."""
        self.setWindowTitle("Advanced Weather Application")
        self.setMinimumSize(500, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("🌤️ Weather Dashboard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name...")
        self.city_input.setFont(QFont("Arial", 12))
        self.city_input.setMinimumHeight(40)
        self.city_input.returnPressed.connect(self.fetch_weather)
        
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.search_btn.setMinimumHeight(40)
        self.search_btn.setMinimumWidth(100)
        self.search_btn.clicked.connect(self.fetch_weather)
        
        search_layout.addWidget(self.city_input, 3)
        search_layout.addWidget(self.search_btn, 1)
        main_layout.addLayout(search_layout)
        
        self.location_btn = QPushButton("📍 Use My Location")
        self.location_btn.setFont(QFont("Arial", 11))
        self.location_btn.setMinimumHeight(40)
        self.location_btn.clicked.connect(self.detect_location)
        main_layout.addWidget(self.location_btn)
        
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Temperature Unit:")
        unit_label.setFont(QFont("Arial", 11))
        
        self.celsius_radio = QRadioButton("Celsius (°C)")
        self.fahrenheit_radio = QRadioButton("Fahrenheit (°F)")
        self.celsius_radio.setChecked(True)
        self.celsius_radio.setFont(QFont("Arial", 10))
        self.fahrenheit_radio.setFont(QFont("Arial", 10))
        
        self.unit_group = QButtonGroup()
        self.unit_group.addButton(self.celsius_radio)
        self.unit_group.addButton(self.fahrenheit_radio)
        self.celsius_radio.toggled.connect(self.update_temperature_display)
        
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.celsius_radio)
        unit_layout.addWidget(self.fahrenheit_radio)
        unit_layout.addStretch()
        main_layout.addLayout(unit_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        self.weather_container = QWidget()
        weather_layout = QVBoxLayout(self.weather_container)
        weather_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.city_label = QLabel("---")
        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.city_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        weather_layout.addWidget(self.city_label)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setMinimumSize(100, 100)
        weather_layout.addWidget(self.icon_label)
        
        self.temp_label = QLabel("--°")
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        weather_layout.addWidget(self.temp_label)
        
        self.condition_label = QLabel("---")
        self.condition_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.condition_label.setFont(QFont("Arial", 16))
        weather_layout.addWidget(self.condition_label)
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(10)
        
        self.humidity_label = QLabel("💧 Humidity: --%")
        self.wind_label = QLabel("💨 Wind Speed: -- m/s")
        self.pressure_label = QLabel("🌡️ Pressure: -- hPa")
        
        for label in [self.humidity_label, self.wind_label, self.pressure_label]:
            label.setFont(QFont("Arial", 12))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            details_layout.addWidget(label)
        
        weather_layout.addLayout(details_layout)
        
        main_layout.addWidget(self.weather_container)
        main_layout.addStretch()
        
        self.weather_container.hide()
    
    def apply_dark_theme(self):
        """Apply modern dark mode styling using QSS."""
        dark_stylesheet = """
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLineEdit {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 8px;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
            QRadioButton {
                color: #cdd6f4;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #45475a;
                border-radius: 9px;
                background-color: #313244;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #89b4fa;
                border-radius: 9px;
                background-color: #89b4fa;
            }
            QFrame {
                color: #45475a;
            }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def fetch_weather(self):
        """Initiate weather data fetch for entered city."""
        city = self.city_input.text().strip()
        
        if not city:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            return
        
        self.set_ui_enabled(False)
        
        self.worker = WeatherWorker(self.api_key)
        self.worker.set_city(city)
        
        self.worker.weather_fetched.connect(self.display_weather)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished.connect(lambda: self.set_ui_enabled(True))
        self.worker.start()
    
    def detect_location(self):
        """Detect user location and fetch weather data."""
        self.set_ui_enabled(False)
        
        self.location_worker = LocationWorker()
        
        self.location_worker.location_detected.connect(self.on_location_detected)
        self.location_worker.error_occurred.connect(self.handle_error)
        self.location_worker.finished.connect(lambda: self.set_ui_enabled(True))
        
        self.location_worker.start()
    
    def on_location_detected(self, lat: float, lon: float, city: str):
        """Handle successful location detection."""
        self.city_input.setText(city)
        
        self.worker = WeatherWorker(self.api_key)
        self.worker.set_coordinates(lat, lon)
        
        self.worker.weather_fetched.connect(self.display_weather)
        self.worker.error_occurred.connect(self.handle_error)
        
        self.worker.start()
    
    def display_weather(self, data: Dict[str, Any]):
        """
        Display weather data in the UI.
        This method is called via signal when weather data is ready.
        """
        self.weather_data = data
        
        self.city_label.setText(f"{data['city']}, {data['country']}")
        
        self.update_temperature_display()
        
        self.condition_label.setText(data['description'])
        
        self.humidity_label.setText(f"💧 Humidity: {data['humidity']}%")
        self.wind_label.setText(f"💨 Wind Speed: {data['wind_speed']:.1f} m/s")
        self.pressure_label.setText(f"🌡️ Pressure: {data['pressure']} hPa")
        
        self.load_weather_icon(data['icon_code'])
        
        self.weather_container.show()
    
    def update_temperature_display(self):
        """Update temperature display based on selected unit."""
        if not self.weather_data:
            return
        
        if self.celsius_radio.isChecked():
            temp = self.weather_data['temp_celsius']
            unit = "°C"
            self.current_unit = "celsius"
        else:
            temp = self.weather_data['temp_fahrenheit']
            unit = "°F"
            self.current_unit = "fahrenheit"
        
        self.temp_label.setText(f"{temp:.1f}{unit}")
    
    def load_weather_icon(self, icon_code: str):
        """Load weather icon from OpenWeatherMap."""
        try:
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            response = requests.get(icon_url, timeout=5)
            
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.icon_label.setPixmap(pixmap.scaled(
                    100, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
        except Exception as e:
            print(f"Failed to load icon: {e}")
            self.icon_label.setText("🌤️")
            self.icon_label.setFont(QFont("Arial", 48))
    
    def handle_error(self, error_message: str):
        """Display error message to user."""
        QMessageBox.critical(self, "Error", error_message)
        self.set_ui_enabled(True)
    
    def set_ui_enabled(self, enabled: bool):
        """Enable or disable UI elements during operations."""
        self.city_input.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)
        self.location_btn.setEnabled(enabled)
        self.celsius_radio.setEnabled(enabled)
        self.fahrenheit_radio.setEnabled(enabled)


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced Weather App")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()