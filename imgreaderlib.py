from PyQt5.QtGui import QImage, qRgb
from PIL import Image

def render_qimage(bmpdata,w,h):
    img = QImage(w, h, QImage.Format_RGB888)
    for i, pixelrgb in enumerate(bmpdata):
        img.setPixel(i % w, i // w, qRgb(*pixelrgb))
    return img