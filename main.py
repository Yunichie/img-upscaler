#!/usr/bin/env python
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QFileDialog, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPalette, QColor
from PIL import Image


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Zenith')
        self.setMinimumSize(600, 700)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #262626;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #363636;
            }
            QComboBox {
                background-color: #262626;
                color: white;
                border: 1px solid #363636;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QFrame#imageFrame {
                background-color: #262626;
                border-radius: 8px;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel('Zenith')
        title_label.setStyleSheet('font-size: 24px; font-family: Serif; margin: 20px 0px;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Image frame
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")
        self.image_frame.setFixedSize(420, 420)
        image_layout = QVBoxLayout(self.image_frame)

        # Image label
        self.image_label = QLabel('No image selected')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet('color: white;')
        image_layout.addWidget(self.image_label)

        layout.addWidget(self.image_frame, alignment=Qt.AlignCenter)

        # Resolution labels
        self.original_res_label = QLabel('Original resolution: -')
        self.output_res_label = QLabel('Output resolution: -')
        self.original_res_label.setAlignment(Qt.AlignCenter)
        self.output_res_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.original_res_label)
        layout.addWidget(self.output_res_label)

        # Upscaling options label
        options_label = QLabel('Upscaling options')
        options_label.setStyleSheet('font-size: 18px; font-family: Serif; margin: 20px 0px 10px 0px;')
        options_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(options_label)

        # Options layout
        options_layout = QHBoxLayout()
        options_layout.setAlignment(Qt.AlignCenter)

        # Mode selection
        mode_layout = QVBoxLayout()
        mode_label = QLabel('Selected mode')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['x2 (generic)', 'x3 (generic)', 'x4 (generic)'])
        self.mode_combo.setFixedWidth(200)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)

        # Format selection
        format_layout = QVBoxLayout()
        format_label = QLabel('Output format')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PNG', 'JPEG', 'WEBP'])
        self.format_combo.setFixedWidth(200)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)

        options_layout.addLayout(mode_layout)
        options_layout.addSpacing(20)
        options_layout.addLayout(format_layout)
        layout.addLayout(options_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Change image button
        change_btn = QPushButton('🖼 Change image')
        change_btn.clicked.connect(self.change_image)
        buttons_layout.addWidget(change_btn)

        # Upscale button
        upscale_btn = QPushButton('✨ Upscale')
        upscale_btn.clicked.connect(self.upscale_image)
        buttons_layout.addWidget(upscale_btn)

        layout.addLayout(buttons_layout)

        # Add some padding at the bottom
        layout.addSpacing(20)

        self.mode_combo.currentTextChanged.connect(self.update_output_resolution)

    def change_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Image',
            '',
            'Image Files (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*.*)'
        )

        if file_path:
            self.current_image_path = file_path
            self.load_and_display_image(file_path)

    def load_and_display_image(self, path):
        # Open image with PIL to get dimensions
        pil_image = Image.open(path)
        width, height = pil_image.size

        # Update resolution labels
        self.original_res_label.setText(f'Original resolution: {width}x{height}')

        # Calculate output resolution based on selected mode
        scale = int(self.mode_combo.currentText()[1])
        self.output_res_label.setText(f'Output resolution: {width * scale}x{height * scale}')

        # Load and scale image for display
        pixmap = QPixmap(path)
        scaled_pixmap = pixmap.scaled(
            400, 400,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def update_output_resolution(self):
        if self.current_image_path:
            self.load_and_display_image(self.current_image_path)

    def upscale_image(self):
        if not self.current_image_path:
            return

        output_format = self.format_combo.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Upscaled Image',
            '',
            f'{output_format.upper()} Files (*.{output_format})'
        )

        if file_path:
            # Here you would implement the actual upscaling logic
            QMessageBox.information(
                self,
                'Success',
                'Image upscaling would happen here!\nActual upscaling implementation needed.'
            )


def main():
    app = QApplication(sys.argv)

    # Enable High DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    window = App()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()