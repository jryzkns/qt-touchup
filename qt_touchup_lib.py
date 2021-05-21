from PyQt5.QtGui import QImage
from PIL import Image
import numpy as np

def load_img(in_path):
    im = Image.open(in_path)
    imgdata, w, h, b = im.getdata(), *im.size, len(im.getbands())
    imgdata = np.array(imgdata).reshape((h, w, b))
    imgdata = np.transpose(imgdata, (1, 0, 2))
    imgdata = imgdata.astype(np.uint8)

    return imgdata, w, h

def save_img(data, out_path):
    outimg = Image.fromarray(np.transpose(data, (1, 0, 2)))
    outimg.save(out_path)

def get_trans_qimage(w, h, fmt = QImage.Format_ARGB32):
    img = QImage(w, h, fmt)
    img.fill(0)
    return img

def get_mask_from_qimg(qimg):
    ptr = qimg.constBits()
    ptr.setsize(qimg.byteCount())
    return np.array(ptr, copy=True).reshape(qimg.height(), qimg.width()).transpose()

def clip(x,lo,hi):
    return lo if x <= lo else (hi if x > hi else x)

def raws2qimg(raws):
    w, h, b = raws.shape
    img = QImage(np.transpose(raws, (1, 0, 2)).tobytes(),
                    w, h,
                    QImage.Format_RGB888
                        if b == 3 else
                            QImage.Format_ARGB32)
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
