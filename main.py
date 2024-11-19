#!/usr/bin/env python
import os
import sys
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QFileDialog, QFrame, QSlider)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PIL import Image
from realesrgan_ncnn_py import Realesrgan


class ProgressCallback:
    def __init__(self, signal):
        self.signal = signal

    def __call__(self, progress):
        self.signal.emit(progress)


class UpscaleThread(QThread):
    finished = pyqtSignal(Image.Image)

    def __init__(self, image_path, model, scale):
        super().__init__()
        self.image_path = image_path
        self.model = model
        self.scale = scale

    def run(self):
        realesrgan = Realesrgan(gpuid=0, model=self.model)
        pil_image = Image.open(self.image_path)
        upscaled_image = realesrgan.process_pil(pil_image)
        self.finished.emit(upscaled_image)


class ComparisonWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = None
        self.upscaled_pixmap = None
        self.slider_position = 0.5
        self.setMinimumSize(400, 400)

    def setImages(self, original_pixmap, upscaled_pixmap):
        # Scale images while maintaining aspect ratio
        self.original_pixmap = original_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.upscaled_pixmap = upscaled_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()

    def setSliderPosition(self, position):
        self.slider_position = position
        self.update()

    def paintEvent(self, event):
        if not self.original_pixmap or not self.upscaled_pixmap:
            return

        painter = QPainter(self)

        # Calculate the split position
        split_x = int(self.width() * self.slider_position)

        # Draw original image on the left side
        painter.drawPixmap(
            QPoint(0, 0),
            self.original_pixmap,
            self.original_pixmap.rect().adjusted(0, 0, split_x - self.original_pixmap.width(), 0)
        )

        # Draw upscaled image on the right side
        painter.drawPixmap(
            QPoint(split_x, 0),
            self.upscaled_pixmap,
            self.upscaled_pixmap.rect().adjusted(split_x, 0, 0, 0)
        )

        # Draw the comparison line
        pen = QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(split_x, 0, split_x, self.height())

    def sizeHint(self):
        if self.original_pixmap:
            return self.original_pixmap.size()
        return super().sizeHint()


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

        # Image display
        self.comparison_widget = ComparisonWidget()
        self.layout.addWidget(self.comparison_widget, alignment=Qt.AlignCenter)

        # Status label
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('font-size: 16px; color: #4CAF50;')  # Green color for status
        self.layout.addWidget(self.status_label)

        # Comparison slider
        slider_container = QWidget()
        slider_layout = QHBoxLayout(slider_container)
        self.comparison_slider = QSlider(Qt.Horizontal)
        self.comparison_slider.setRange(0, 100)
        self.comparison_slider.setValue(50)
        self.comparison_slider.setFixedWidth(400)  # Match image width
        self.comparison_slider.valueChanged.connect(
            lambda value: self.comparison_widget.setSliderPosition(value / 100)
        )
        # Initialize slider as hidden
        self.comparison_slider.setVisible(False)
        slider_layout.addWidget(self.comparison_slider)
        slider_layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(slider_container)

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
        change_btn = QPushButton('🖼 Change image')
        change_btn.clicked.connect(self.change_image)
        buttons_layout.addWidget(change_btn)

        # Upscale button
        upscale_btn = QPushButton('✨ Upscale')
        upscale_btn.clicked.connect(self.upscale_image)
        buttons_layout.addWidget(upscale_btn)

        self.layout.addLayout(buttons_layout)

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
            # Hide the slider when changing image
            self.comparison_slider.setVisible(False)
            # Reset the comparison widget to show only the original image
            pixmap = QPixmap(file_path)
            self.comparison_widget.setImages(pixmap, pixmap)
            self.status_label.setText('')

            # Remove save button if it exists
            save_btn = self.findChild(QPushButton, 'save_button')
            if save_btn:
                save_btn.deleteLater()

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

    def upscale_image(self):
        if not self.current_image_path:
            return

        model_index = self.model_combo.currentIndex()
        scale = int(self.mode_combo.currentText()[1])

        self.status_label.setText('Upscaling...')
        # Hide slider during upscaling
        self.comparison_slider.setVisible(False)
        self.upscale_thread = UpscaleThread(self.current_image_path, model_index, scale)
        self.upscale_thread.finished.connect(self.show_comparison)
        self.upscale_thread.start()

    def show_comparison(self, upscaled_image):
        self.upscaled_image = upscaled_image
        self.status_label.setText('Upscaled!')

        # Convert upscaled PIL image to QPixmap
        buffer = BytesIO()
        upscaled_image.save(buffer, format="PNG")
        buffer.seek(0)
        upscaled_qimage = QImage()
        upscaled_qimage.loadFromData(buffer.read())
        upscaled_pixmap = QPixmap.fromImage(upscaled_qimage)

        # Set images in comparison widget
        original_pixmap = QPixmap(self.current_image_path)
        self.comparison_widget.setImages(original_pixmap, upscaled_pixmap)

        # Show slider only after successful upscaling
        self.comparison_slider.setVisible(True)
        self.comparison_slider.setValue(50)  # Reset to middle

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