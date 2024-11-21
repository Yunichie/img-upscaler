#!/usr/bin/env python
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer


class StatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.layout.setAlignment(Qt.AlignCenter)

        # Create status label
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('''
            QLabel {
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 4px;
                background-color: rgba(33, 150, 243, 0.1);
                margin: 0px;
            }
        ''')
        self.status_label.hide()

        self.layout.addWidget(self.status_label)

    def show_loading(self):
        """Show loading status"""
        self.status_label.setText('✨ Upscaling...')
        self.status_label.setStyleSheet('''
            QLabel {
                font-size: 16px;
                color: #2196F3;
                padding: 8px 16px;
                border-radius: 4px;
                background-color: rgba(33, 150, 243, 0.1);
            }
        ''')
        self.status_label.show()

    def show_success(self):
        """Show success status"""
        self.status_label.setText('✨ Upscaled successfully!')
        self.status_label.setStyleSheet('''
            QLabel {
                font-size: 16px;
                color: #4CAF50;
                padding: 8px 16px;
                border-radius: 4px;
                background-color: rgba(76, 175, 80, 0.1);
            }
        ''')
        self.status_label.show()
        # Hide after 3 seconds
        QTimer.singleShot(3000, self.status_label.hide)

    def hide_status(self):
        """Hide status label"""
        self.status_label.hide()

    def set_text(self, text):
        """Set custom status text"""
        self.status_label.setText(text)

    def clear(self):
        """Clear status text"""
        self.status_label.setText('')