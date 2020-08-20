from PyQt5.QtGui import QImage, qRgb
from PIL import Image

def render_qimage(pixdata, w, h):
    img = QImage(w, h, QImage.Format_RGB888)
    for i, pixelrgb in enumerate(pixdata):
        img.setPixel(i % w, i // w, qRgb(*pixelrgb))
    return img

def get_trans_qimage(w,h):
    return QImage(w,h, QImage.Format_ARGB32)

def clip(x,lo,hi):
    return lo if x <= lo else (hi if x > hi else x)