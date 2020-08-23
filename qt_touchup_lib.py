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

def get_trans_qimg(w, h):
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

def g_pt_mindist( group, pt,
    # chebyshev distance
    norm = lambda a, b, c, d: max(abs(a - c), abs(b - d))):
    min_dist = norm(*pt, *group[0])
    for pt_ in group[1:]:
        dist = norm(*pt, *pt_)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def pad_to_even(x):
    return x if x % 2 == 0 else (x >> 1) + 1 << 1

def subsample2x(m):
    return m.reshape((m.shape[0] >> 1, 2, m.shape[1] >> 1, 2)).mean(-1).mean(1)

def get_mask_locs(m, th = 0.5):
    return list(np.argwhere(m > th).astype(np.int16))

def reupscaled_group_bounds(g, w, h, padding = 20):
    xs, ys = zip(*g)
    return  clip((min(xs) << 1) - padding, 0, w), \
            clip((max(xs) << 1) + padding, 0, w), \
            clip((min(ys) << 1) - padding, 0, h), \
            clip((max(ys) << 1) + padding, 0, h)