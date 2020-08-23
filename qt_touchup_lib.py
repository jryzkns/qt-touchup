from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QImage, QColor
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

def render_qimage(pixdata, w, h):
    img = QImage(w, h, QImage.Format_RGB888)
    for i, pixelrgb in enumerate(pixdata):
        img.setPixel(i % w, i // w, qRgb(*pixelrgb))
    return img

def get_trans_qimage(w, h):
    return QImage(w,h, QImage.Format_ARGB32)

def get_blank_mask(w, h):
    return np.zeros((pad_to_even(w), pad_to_even(h))).astype(np.uint8)

def clip(x,lo,hi):
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

def c_pt_mindist( cluster, pt,
    # 2D chebyshev/chessboard distance
    norm = lambda a,b,c,d: max(abs(a-c),abs(b-d))):
    min_dist = norm(*pt, *cluster[0])
    for pt_ in cluster[1:]:
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

def reupscaled_cluster_bounds(g, w, h, padding = 20):
    xs, ys = zip(*g)
    return  clip((min(xs) << 1) - padding, 0, w), \
            clip((max(xs) << 1) + padding, 0, w), \
            clip((min(ys) << 1) - padding, 0, h), \
            clip((max(ys) << 1) + padding, 0, h)

def generate_mask_windows(m, th = 4):

    subsampled_m = subsample2x(m) # subsample mask to save time
    locs, mask_windows = get_mask_locs(subsampled_m), []
    while len(locs) > 0:
        # initialize a cluster by extracting a point from locs
        cluster = [locs.pop()]
        while True:
            # generate a list of minimum distances from 
            # points to current cluster, init remainder list
            mi_dists = [c_pt_mindist(cluster, pt) for pt in locs]

            # stop searching for this cluster if no more points left 
            # or no more close points to cluster
            if len(mi_dists) == 0 or min(mi_dists) > th:
                break

            cluster += [pt for i, pt in enumerate(locs) if mi_dists[i] <= th]
            locs     = [pt for i, pt in enumerate(locs) if mi_dists[i] > th]
        mask_windows.append(reupscaled_cluster_bounds(cluster, *m.shape))
    return mask_windows
