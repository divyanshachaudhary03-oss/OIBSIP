APP_STYLESHEET = """
QMainWindow {
    border-image: url("background.png") 0 0 0 0 stretch stretch;
}

QFrame#Card {
    background-color: rgba(25, 28, 42, 0.90);
    border: 2px solid rgba(138, 180, 248, 0.15);
    border-radius: 16px;
    padding: 5px;
}

QLabel {
    color: #e0e6f0;
    font-family: 'Arial', 'Helvetica', sans-serif;
    font-size: 13px;
    background: transparent;
}

QLabel#Title {
    font-size: 32px;
    font-weight: 700;
    color: #7dd3fc;
    margin-bottom: 15px;
    letter-spacing: 1px;
}

QLabel#PasswordDisplay {
    background-color: rgba(30, 35, 50, 0.75);
    border: 2px solid #4a5568;
    border-radius: 10px;
    color: #6ee7b7;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 18px;
    padding: 18px;
    selection-background-color: #4b5563;
}

QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7dd3fc, stop:1 #3b82f6);
    color: #0f172a;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #2563eb);
}

QPushButton:pressed {
    background-color: #0ea5e9;
    padding-top: 14px;
    padding-bottom: 10px;
}

QPushButton#CopyButton {
    background-color: rgba(55, 65, 81, 0.85);
    color: #e0e6f0;
    border: 1px solid #6b7280;
}

QPushButton#CopyButton:hover {
    background-color: rgba(75, 85, 99, 0.95);
    border-color: #9ca3af;
}

QCheckBox {
    color: #e0e6f0;
    font-size: 13px;
    spacing: 8px;
    background: transparent;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #4a5568;
    background-color: rgba(30, 35, 50, 0.7);
}

QCheckBox::indicator:checked {
    background-color: #7dd3fc;
    border-color: #7dd3fc;
}

QCheckBox::indicator:hover {
    border-color: #60a5fa;
}

QSlider::groove:horizontal {
    border: 1px solid #4a5568;
    height: 6px;
    background: rgba(30, 35, 50, 0.7);
    margin: 3px 0;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7dd3fc, stop:1 #3b82f6);
    border: 2px solid #1e293b;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #38bdf8;
}

QSpinBox {
    background-color: rgba(30, 35, 50, 0.7);
    border: 2px solid #4a5568;
    border-radius: 6px;
    color: #e0e6f0;
    padding: 8px;
    font-size: 13px;
    font-weight: 500;
}

QSpinBox:focus {
    border-color: #7dd3fc;
}

QLineEdit {
    background-color: rgba(30, 35, 50, 0.7);
    border: 2px solid #4a5568;
    border-radius: 6px;
    color: #e0e6f0;
    padding: 8px;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #7dd3fc;
}
"""
