#!/usr/bin/env python
from io import BytesIO
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import os
import tempfile
import ffmpeg
from src.gui.widgets.comparison_widget import ComparisonWidget
from src.core.upscaler import UpscaleThread
from src.gui.widgets.status_widget import StatusWidget


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.upscaled_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Zenith')
        self.setMinimumSize(800, 800)

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
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #4d4d4d;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -8px 0;
                border-radius: 9px;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel('Zenith')
        title_label.setStyleSheet('font-size: 24px; font-family: Serif; margin: 20px 0px;')
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        self.status_widget = StatusWidget()
        self.layout.addWidget(self.status_widget)

        # Create a container for the image
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(10)  # Add spacing between widgets if desired

        # Initialize the comparison widget
        self.comparison_widget = ComparisonWidget()

        # Add widget to the image layout
        image_layout.addWidget(self.comparison_widget, alignment=Qt.AlignCenter)

        # Add the image container to the main layout
        self.layout.addWidget(image_container)

        # Resolution labels
        self.original_res_label = QLabel('Original resolution: -')
        self.output_res_label = QLabel('Output resolution: -')
        self.original_res_label.setAlignment(Qt.AlignCenter)
        self.output_res_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.original_res_label)
        self.layout.addWidget(self.output_res_label)

        # Rest of the UI components (options)
        self.setup_options()

        # Buttons
        self.setup_buttons()

        # Add some padding at the bottom
        self.layout.addSpacing(20)

    def setup_options(self):
        # Upscaling options label
        options_label = QLabel('Upscaling options')
        options_label.setStyleSheet('font-size: 18px; font-family: Serif; margin: 20px 0px 10px 0px;')
        options_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(options_label)

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

        # Model selection
        model_layout = QVBoxLayout()
        model_label = QLabel('Model')
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            '0: realesr-animevideov3-x2',
            '1: realesr-animevideov3-x3',
            '2: realesr-animevideov3-x4',
            '3: realesrgan-x4plus-anime',
            '4: realesrgan-x4plus'
        ])
        self.model_combo.setFixedWidth(200)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)

        options_layout.addLayout(mode_layout)
        options_layout.addSpacing(20)
        options_layout.addLayout(format_layout)
        options_layout.addSpacing(20)
        options_layout.addLayout(model_layout)
        self.layout.addLayout(options_layout)

    def setup_buttons(self):
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Change image button
        change_btn = QPushButton('🖼 Change media')
        change_btn.clicked.connect(self.change_media)
        buttons_layout.addWidget(change_btn)

        # Upscale button
        upscale_btn = QPushButton('✨ Upscale')
        upscale_btn.clicked.connect(self.upscale_media)
        buttons_layout.addWidget(upscale_btn)

        self.layout.addLayout(buttons_layout)

    def change_media(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Image or Video',
            '',
            'Media Files (*.png *.jpg *.jpeg *.webp *.bmp *.mp4 *.avi *.mov *.mkv);;All Files (*.*)'
        )

        if file_path:
            self.status_widget.hide_status()
            self.current_media_path = file_path
            if self.is_video(file_path):
                self.load_and_display_video_thumbnail(file_path)
            else:
                self.load_and_display_image(file_path)
            self.status_widget.clear()

            save_btn = self.findChild(QPushButton, 'save_button')
            if save_btn:
                save_btn.deleteLater()

    def is_video(self, path):
        return os.path.splitext(path)[1].lower() in ['.mp4', '.avi', '.mov', '.mkv']

    def load_and_display_video_thumbnail(self, path):
        temp_dir = tempfile.mkdtemp()
        thumbnail_path = os.path.join(temp_dir, 'thumbnail.png')
        (
            ffmpeg
            .input(path, ss=1)
            .output(thumbnail_path, vframes=1)
            .run(quiet=True)
        )
        self.load_and_display_image(thumbnail_path)
        os.remove(thumbnail_path)
        os.rmdir(temp_dir)

    def load_and_display_image(self, path):
        # Open image with PIL to get dimensions
        pil_image = Image.open(path)
        width, height = pil_image.size

        # Update resolution labels
        self.original_res_label.setText(f'Original resolution: {width}x{height}')

        # Calculate output resolution based on selected mode
        scale = int(self.mode_combo.currentText()[1])
        self.output_res_label.setText(f'Output resolution: {width * scale}x{height * scale}')

        # Load image for display
        pixmap = QPixmap(path)
        self.comparison_widget.setImages(pixmap, pixmap)  # Initially show same image

    def upscale_media(self):
        if not self.current_media_path:
            return

        model_index = self.model_combo.currentIndex()
        scale = int(self.mode_combo.currentText()[1])

        self.status_widget.show_loading()
        self.comparison_widget.setVisible(True)
        self.upscale_thread = UpscaleThread(self.current_media_path, model_index, scale)
        self.upscale_thread.finished.connect(self.show_upscaled_media)
        self.upscale_thread.start()

    def show_upscaled_media(self, output_path):
        self.status_widget.show_success()
        if self.is_video(output_path):
            QMessageBox.information(self, 'Upscaling Complete', f'Upscaled video saved at {output_path}')
        else:
            self.upscaled_image = Image.open(output_path)
            upscaled_pixmap = QPixmap(output_path)
            original_pixmap = QPixmap(self.current_media_path)
            self.comparison_widget.setImages(original_pixmap, upscaled_pixmap, side_by_side=True)

        # Add save button
        save_btn = self.findChild(QPushButton, 'save_button')
        if not save_btn:
            save_btn = QPushButton('💾 Save Upscaled Image')
            save_btn.setObjectName('save_button')
            save_btn.clicked.connect(self.save_upscaled_image)
            self.layout.addWidget(save_btn)

    def save_upscaled_image(self):
        output_format = self.format_combo.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Upscaled Image',
            '',
            f'{output_format.upper()} Files (*.{output_format})'
        )

        if file_path and self.upscaled_image:
            self.upscaled_image.save(file_path)