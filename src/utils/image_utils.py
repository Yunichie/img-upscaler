#!/usr/bin/env python
from io import BytesIO
from PyQt5.QtGui import QImage, QPixmap

def pil_to_pixmap(pil_image):
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    buffer.seek(0)
    qimage = QImage()
    qimage.loadFromData(buffer.read())
    return QPixmap.fromImage(qimage)