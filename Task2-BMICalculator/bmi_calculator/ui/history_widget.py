from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime

class TrendsDisplayPanel(QWidget):
    """Widget for displaying BMI history and trends."""
    
    def __init__(self):
        super().__init__()
        self._build_ui()
    
    def _build_ui(self):
        """Construct the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_label = QLabel("📈 BMI History & Trends")
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
        layout.addWidget(header_label)
        
        # Chart section
        chart_label = QLabel("📊 BMI Trend Chart")
        chart_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #c77dff;
                padding: 8px;
            }
        """)
        layout.addWidget(chart_label)
        
        self.chart_figure = Figure(figsize=(8, 4))
        self.chart_figure.patch.set_alpha(0.0)
        self.chart_canvas = FigureCanvas(self.chart_figure)
        self.chart_canvas.setStyleSheet("background: transparent;")
        self.chart_canvas.setMinimumHeight(300)
        layout.addWidget(self.chart_canvas)
        
        # Data table section
        table_label = QLabel("📋 Detailed Records")
        table_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #c77dff;
                padding: 8px;
            }
        """)
        layout.addWidget(table_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["📅 Recorded Date", "⚖️ Weight (kg)", "📏 Height (m)", "💯 BMI Value"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setMinimumHeight(200)
        layout.addWidget(self.history_table)
        
        # Clear history button
        self.clear_history_button = QPushButton("🗑️ Delete All History")
        self.clear_history_button.setMinimumHeight(45)
        layout.addWidget(self.clear_history_button)
        
        self.setLayout(layout)
    
    def update_data(self, records):
        """Update the display with new BMI records."""
        # Update table
        self.history_table.setRowCount(len(records))
        date_list = []
        bmi_list = []
        
        for row_index, (weight, height, bmi, timestamp) in enumerate(records):
            # Parse timestamp
            try:
                date_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                date_obj = datetime.datetime.now()
            
            self.history_table.setItem(row_index, 0, QTableWidgetItem(timestamp))
            self.history_table.setItem(row_index, 1, QTableWidgetItem(str(weight)))
            self.history_table.setItem(row_index, 2, QTableWidgetItem(str(height)))
            self.history_table.setItem(row_index, 3, QTableWidgetItem(f"{bmi:.2f}"))
            
            date_list.append(date_obj)
            bmi_list.append(bmi)
        
        # Update chart
        self._render_chart(date_list, bmi_list)
    
    def _render_chart(self, dates, bmi_values):
        """Render the BMI trend chart."""
        self.chart_figure.clear()
        chart_axis = self.chart_figure.add_subplot(111)
        
        # Transparent backgrounds with gradient effect
        self.chart_figure.patch.set_facecolor('none')
        chart_axis.set_facecolor((0.1, 0.0, 0.2, 0.6))  # Deep purple transparent
        
        if dates:
            # Plot with purple-to-pink gradient line and cyan markers
            line_plot, = chart_axis.plot(
                dates, bmi_values,
                marker='o', linestyle='-',
                linewidth=3, markersize=10
            )
            line_plot.set_color('#9d4edd')  # Purple line
            line_plot.set_markerfacecolor('#ff006e')  # Pink markers
            line_plot.set_markeredgecolor('#c77dff')  # Light purple edge
            line_plot.set_markeredgewidth(2)
            
            # Add glow effect with shadow line
            shadow_line, = chart_axis.plot(
                dates, bmi_values,
                linestyle='-', linewidth=6, alpha=0.3
            )
            shadow_line.set_color('#8a2be2')
            
            chart_axis.set_title(
                "BMI Progress Over Time",
                color='#ffffff', fontsize=15, fontweight='bold',
                pad=15
            )
            chart_axis.set_xlabel("Date", color='#c77dff', fontsize=12, fontweight='600')
            chart_axis.set_ylabel("BMI Value", color='#c77dff', fontsize=12, fontweight='600')
            
            # Style ticks and spines
            chart_axis.tick_params(axis='x', colors='#e0aaff', labelsize=10)
            chart_axis.tick_params(axis='y', colors='#e0aaff', labelsize=10)
            
            # Style spines with gradient colors
            chart_axis.spines['bottom'].set_color('#8a2be2')
            chart_axis.spines['left'].set_color('#8a2be2')
            chart_axis.spines['top'].set_color('#9d4edd')
            chart_axis.spines['right'].set_color('#9d4edd')
            chart_axis.spines['bottom'].set_linewidth(2)
            chart_axis.spines['left'].set_linewidth(2)
            
            chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            chart_axis.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.chart_figure.autofmt_xdate()
            
            # Enhanced grid
            chart_axis.grid(True, color='#6a0dad', linestyle='--', alpha=0.4, linewidth=1)
            
            # Add subtle background gradient zones
            chart_axis.axhspan(0, 18.5, alpha=0.05, color='cyan')  # Underweight
            chart_axis.axhspan(18.5, 25, alpha=0.05, color='green')  # Normal
            chart_axis.axhspan(25, 30, alpha=0.05, color='orange')  # Overweight
            chart_axis.axhspan(30, 50, alpha=0.05, color='red')  # Obese
        
        self.chart_canvas.draw()
