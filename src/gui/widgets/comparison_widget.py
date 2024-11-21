#!/usr/bin/env python
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter


class ComparisonWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = None
        self.upscaled_pixmap = None
        self.setMinimumSize(900, 400)  # Increased width to accommodate spacing
        self.show_side_by_side = False  # Flag to control display mode

    def setImages(self, original_pixmap, upscaled_pixmap, side_by_side=False):
        # Scale images while maintaining aspect ratio
        self.original_pixmap = original_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.upscaled_pixmap = upscaled_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.show_side_by_side = side_by_side
        self.update()

    def paintEvent(self, event):
        if not self.original_pixmap or not self.upscaled_pixmap:
            return

        painter = QPainter(self)

        if self.show_side_by_side:
            # Side by side display (after upscaling)
            spacing = 50  # Space between images
            total_width = self.original_pixmap.width() * 2 + spacing
            start_x = (self.width() - total_width) // 2
            y = (self.height() - self.original_pixmap.height()) // 2

            # Draw original image on the left
            painter.drawPixmap(QPoint(start_x, y), self.original_pixmap)

            # Draw upscaled image on the right
            painter.drawPixmap(QPoint(start_x + self.original_pixmap.width() + spacing, y), self.upscaled_pixmap)

            # TODO: fix "Original" and "Upscaled" texts being overlapped by vertically long images
            # Draw labels
            painter.setPen(Qt.white)
            painter.drawText(start_x, y - 10, "Original")
            painter.drawText(start_x + self.original_pixmap.width() + spacing, y - 10, "Upscaled")
        else:
            # Single image display (before upscaling)
            x = (self.width() - self.original_pixmap.width()) // 2
            y = (self.height() - self.original_pixmap.height()) // 2
            painter.drawPixmap(QPoint(x, y), self.original_pixmap)