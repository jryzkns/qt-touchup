from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QPushButton, QWidget, QMessageBox, QRadioButton, QSlider
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter, QPen, QBrush, QColor
import qt_touchup_lib

from PIL import Image
import numpy as np

class QtTouchupApp(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setFixedSize(QSize(894, 651))
        self.setWindowTitle(" ")
        self.render = None

        self.imglabel = QLabel(self)
        self.imglabel.setText("No image Loaded!")
        self.imglabel.setGeometry(QRect(175, 15, 300, 40))

        self.loadimgbutton = QPushButton("Load Image", self)
        self.loadimgbutton.clicked.connect(self.on_confirm_loadimg_click)
        self.loadimgbutton.setGeometry(QRect(15, 15, 150, 40))

        self.saveimgbutton = QPushButton("Save Image", self)
        self.saveimgbutton.clicked.connect(self.on_confirm_saveimg_click)
        self.saveimgbutton.setGeometry(QRect(15, 65, 150, 40))

        self.clearbutton = QPushButton("Clear", self)
        self.clearbutton.clicked.connect(self.on_confirm_clear_click)
        self.clearbutton.setGeometry(QRect(15, 115, 150, 40))
        self.clearbutton.setEnabled(False)

        self.touchupbutton = QPushButton("Touch-Up", self)
        self.touchupbutton.clicked.connect(self.on_confirm_touchup_click)
        self.touchupbutton.setGeometry(QRect(175, 115, 150, 40))
        self.touchupbutton.setEnabled(False)

        self.touchup_mode = qt_touchup_lib.INPAINT_TELEA

        self.moderadbutton1 = QRadioButton("TELEA", self)
        self.moderadbutton1.setGeometry(QRect(15, 165, 150, 20))
        self.moderadbutton1.setChecked(True)
        self.moderadbutton1.toggled.connect(
            lambda : self.set_touchup_mode(qt_touchup_lib.INPAINT_TELEA))

        self.moderadbutton2 = QRadioButton("NS", self)
        self.moderadbutton2.setGeometry(QRect(15, 185, 150, 20))
        self.moderadbutton2.setChecked(False)
        self.moderadbutton2.toggled.connect(
            lambda : self.set_touchup_mode(qt_touchup_lib.INPAINT_NS))

        self.moderadbutton3 = QRadioButton("CUSTOM", self)
        self.moderadbutton3.setGeometry(QRect(15, 205, 150, 20))
        self.moderadbutton3.setChecked(False)
        self.moderadbutton3.toggled.connect(
            lambda : self.set_touchup_mode(qt_touchup_lib.INPAINT_CUSTOM))

        self.touch_up_radius = 5
        self.touch_up_slider = QSlider(Qt.Horizontal, self)
        self.touch_up_slider.setGeometry(QRect(15, 235, 75, 20))
        self.touch_up_slider.setMinimum(2)
        self.touch_up_slider.setMaximum(10)
        self.touch_up_slider.setSingleStep(1)
        self.touch_up_slider.setValue(self.touch_up_radius)
        self.touch_up_slider.valueChanged.connect(self.on_slider_update_value)

    def on_slider_update_value(self):
        self.touch_up_radius = self.touch_up_slider.value()
        if self.render is not None:
            self.render.r = self.touch_up_radius

    def set_touchup_mode(self, mode):
        self.touchup_mode = mode

    def on_confirm_touchup_click(self):
                      
        subsampled_mask = qt_touchup_lib.subsample2x(self.render.mask)
        mask_locs = qt_touchup_lib.get_mask_locs(subsampled_mask)

        min_dist_th = 2

        group_bounds = []
        while len(mask_locs) > 0:
            group = [mask_locs.pop()]

            while True:

                min_dists = [qt_touchup_lib.g_pt_mindist(group, pt)
                                for pt in mask_locs]

                if len(min_dists) == 0: break
                if min(min_dists) > min_dist_th: break

                remains = []
                for i, pt in enumerate(mask_locs):
                    if min_dists[i] <= min_dist_th:
                        group.append(pt)
                    else:
                        remains.append(pt)

                mask_locs = remains

            group_bounds.append(
                qt_touchup_lib.reupscaled_group_bounds(group, self.w, self.h))


        for bounds in group_bounds:
            xmi, xma, ymi, yma = bounds
            img_slice  = self.img_raw[xmi : xma, ymi : yma, :]
            mask_slice = self.render.mask[xmi : xma, ymi : yma]
            touched_up_slice = qt_touchup_lib.touch_up( img_slice,
                                                        mask_slice,
                                                        self.touch_up_radius,
                                                        self.touchup_mode)
    
            self.img_raw[xmi : xma, ymi : yma, :] = touched_up_slice

        self.render.img = qt_touchup_lib.raws2qimg(self.img_raw)
        self.render.reset_mask()
        self.render.update()

    def on_confirm_clear_click(self):
        self.render.reset_mask()

    def on_confirm_saveimg_click(self):
        # TODO: add default image file options and default save fn
        self.savepath = QFileDialog.getSaveFileName(self)[0]
        outimg = Image.fromarray(np.transpose(self.img_raw, (1,0,2)))
        outimg.save(self.savepath)

    def on_finish_editing(self):

        self.loadimgbutton.setEnabled(True)
        self.clearbutton.setEnabled(False)
        self.touchupbutton.setEnabled(False)
        self.imglabel.setText("")

        self.render = None

    def on_confirm_loadimg_click(self):

        self.imgpath = QFileDialog.getOpenFileName(self)[0]
        
        if self.imgpath != '': # continue only when a file has been chosen

            try:
       
                self.img_raw, self.w, self.h = qt_touchup_lib.load_img(self.imgpath)
                self.imglabel.setText(self.imgpath.split("/")[-1])

                # activate UI
                self.loadimgbutton.setEnabled(False)
                self.clearbutton.setEnabled(True)
                self.touchupbutton.setEnabled(True)

                # setup render window
                self.render = RenderWin(QRect(0, 0, self.w, self.h),
                                    qt_touchup_lib.raws2qimg(self.img_raw),
                                    self.w, self.h, self.touch_up_radius, self)
                self.render.show()
                self.render.update()

            except:

                self.raise_invalid_file_err()

    def raise_invalid_file_err(self):

        e = QMessageBox()
        e.setIcon(QMessageBox.Critical)
        e.setText("Invalid file encountered!")
        e.setStandardButtons(QMessageBox.Ok)
        e.exec_()

class RenderWin(QMainWindow):

    def __init__(self, loc, img, w, h, r, parent=None):
        super(RenderWin, self).__init__(parent)
        self.parent = parent
        
        # window properties
        self.setWindowTitle(" ")
        self.setGeometry(loc)
        self.setFixedSize(w, h)
        self.move(  parent.x() + parent.width()/2, 
                    parent.y() + parent.height()/2)

        # window data and mask
        self.img, self.w, self.h, self.r = img, w, h, r
        self.reset_mask()
        self.clip_w = lambda x: qt_touchup_lib.clip(x, 0, self.w - 1)
        self.clip_h = lambda x: qt_touchup_lib.clip(x, 0, self.h - 1)

    def reset_mask(self):

        self.mask = np.zeros((  qt_touchup_lib.pad_to_even(self.w), 
                                qt_touchup_lib.pad_to_even(self.h))
                                ).astype(np.uint8)
        self.mask_display = qt_touchup_lib.get_trans_qimg(self.w, self.h)
        self.update()
        
    def paintEvent(self, event):

        painter = QPainter(self)
        painter.drawImage(QPoint(0,0), self.img)
        painter.drawImage(QPoint(0,0), self.mask_display)

    def mouseMoveEvent(self, event):
        
        if Qt.LeftButton and self.is_clicked:

            painter = QPainter(self.mask_display)
            painter.setPen(QPen(Qt.gray, self.r, Qt.SolidLine))
            painter.drawLine(self.prev_point, event.pos())

            self.prev_point = event.pos()
            self.update()

            self.fill_mask_radius(event.pos().x(), event.pos().y())

    def fill_mask_radius(self, x, y):
        for i in range(self.clip_w(x - self.r), self.clip_w(x + self.r - 1)):
            for j in range(self.clip_h(y - self.r), self.clip_h(y + self.r - 1)):
                if ((i - x)**2 + (j - y)**2) <= self.r**2:
                    self.mask[i, j] = 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked, self.prev_point = True, event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked = False

    def closeEvent(self, event):
        self.parent.on_finish_editing()
        self.reset_mask()
        event.accept(); self.destroy()
        