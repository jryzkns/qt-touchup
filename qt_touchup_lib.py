from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QImage, QColor
from PIL import Image
import numpy as np

def load_img(in_path):
    im = Image.open(in_path)
    imgdata, w, h, b = im.getdata(), *im.size, len(im.getbands())
    imgdata = np.array(imgdata).reshape((h, w, b))
    imgdata = np.transpose(imgdata, (1,0,2))
    imgdata = imgdata.astype(np.uint8)

    return imgdata, w, h

def render_qimage(pixdata, w, h):
    img = QImage(w, h, QImage.Format_RGB888)
    for i, pixelrgb in enumerate(pixdata):
        img.setPixel(i % w, i // w, qRgb(*pixelrgb))
    return img

def get_trans_qimage(w, h):
    return QImage(w, h, QImage.Format_ARGB32)

def clip(x, lo, hi):
    return lo if x <= lo else (hi if x > hi else x)

def qimg2raws(qimg):
    raws = np.zeros((qimg.width(), qimg.height(),3))
    for i in range(qimg.width()):
        for j in range(qimg.height()):
            pix = qimg.pixelColor(i,j)
            raws[i,j,0] = pix.red()
            raws[i,j,1] = pix.green()
            raws[i,j,2] = pix.blue()
    return raws

def raws2qimg(raws):
    w, h, b = raws.shape
    img = QImage(w, h, QImage.Format_RGB888 
                            if b == 3 else 
                                QImage.Format_ARGB32)
    for i in range(w): 
        for j in range(h):
            qc = QColor(*raws[i, j,:])
            img.setPixelColor(QPoint(i, j), qc)
    return img

import cv2
INPAINT_TELEA = cv2.INPAINT_TELEA
INPAINT_NS = cv2.INPAINT_NS
INPAINT_CUSTOM = -1
def touch_up(orig, mask, rad, mode):

    if mode == INPAINT_CUSTOM:
        res = orig[:,:,:3] # TODO: implement custom inpaint function here
    else:
        res = cv2.inpaint(orig[:,:,:3], mask, rad, mode)

    # restack alpha channel if it exists
    if orig.shape[-1] == 4:
        res = np.dstack((res, np.expand_dims(orig[:,:,3], axis=2)))
    return res