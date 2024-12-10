# Zenith - AI Image Upscaler

A user-friendly GUI application for upscaling images using Real-ESRGAN AI models.
## Features

- Upscale images up to 4x using various AI models
- Side-by-side comparison view
- Multiple AI model options:
    - realesr-animevideov3 (x2, x3, x4)
    - realesrgan-x4plus-anime
    - realesrgan-x4plus
- Supports multiple output formats (PNG, JPEG, WEBP)
- Real-time resolution preview

## Installation

# Clone the repository

```
git clone https://github.com/yunichie/zenith.git
cd zenith
```


# Install dependencies

```
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python main.py
```

2. Click "🖼 Change image" to select an input image
3. Choose upscaling options:
    - Select upscaling mode (x2, x3, x4)
    - Choose output format
    - Select AI model
4. Click "✨ Upscale" to process the image
5. Use "💾 Save Upscaled Image" to save the result

## Requirements

- Python 3.6+
- PyQt5
- Pillow
- realesrgan-ncnn-py

## Building

To create a standalone executable:

```bash
pyinstaller main.spec
```

The executable will be created in the `dist` directory.

## License

[BSD 3-Clause License](https://spdx.org/licenses/BSD-3-Clause-Clear.html)

Copyright (c) 2024, Alfarel Sandriano Subektiansyah, Muhammad Rasya Alghifari

## Acknowledgments

This project uses [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) for image upscaling.