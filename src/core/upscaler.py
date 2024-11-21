#!/usr/bin/env python
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image
from realesrgan_ncnn_py import Realesrgan


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