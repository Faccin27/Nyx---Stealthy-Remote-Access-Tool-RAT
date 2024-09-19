from PIL import ImageGrab
from io import BytesIO
import os

def Sprint():
    return ImageGrab.grab()

def save_image(image, path):
    image.save(path, format='PNG')

def get_image_bytes(image):
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
