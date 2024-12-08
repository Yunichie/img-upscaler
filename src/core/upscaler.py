#!/usr/bin/env python
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image
from realesrgan_ncnn_py import Realesrgan
import ffmpeg
import os
import tempfile

class UpscaleThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, input_path, model, scale):
        super().__init__()
        self.input_path = input_path
        self.model = model
        self.scale = scale

    def run(self):
        if self.is_video(self.input_path):
            output_path = self.upscale_video()
        else:
            output_path = self.upscale_image()
        self.finished.emit(output_path)

    def is_video(self, path):
        return os.path.splitext(path)[1].lower() in ['.mp4', '.avi', '.mov', '.mkv']

    def upscale_image(self):
        realesrgan = Realesrgan(gpuid=0, model=self.model)
        pil_image = Image.open(self.input_path)
        upscaled_image = realesrgan.process_pil(pil_image)
        output_path = self.get_output_path(self.input_path)
        upscaled_image.save(output_path)
        return output_path

    def upscale_video(self):
        temp_dir = tempfile.mkdtemp()
        (
            ffmpeg
            .input(self.input_path)
            .output(f'{temp_dir}/frame_%08d.png')
            .run()
        )

        realesrgan = Realesrgan(gpuid=0, model=self.model)
        frame_files = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])
        for frame_file in frame_files:
            frame_path = os.path.join(temp_dir, frame_file)
            pil_image = Image.open(frame_path)
            upscaled_image = realesrgan.process_pil(pil_image)
            upscaled_image.save(frame_path)

        output_path = self.get_output_path(self.input_path)
        (
            ffmpeg
            .input(f'{temp_dir}/frame_%08d.png', framerate=24)
            .output(output_path)
            .run()
        )

        for frame_file in frame_files:
            os.remove(os.path.join(temp_dir, frame_file))
        os.rmdir(temp_dir)

        return output_path

    def get_output_path(self, input_path):
        base, ext = os.path.splitext(input_path)
        return f"{base}_upscaled{ext}"