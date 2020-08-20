from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QPushButton, QWidget, QMessageBox
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
        self.img_render = None

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

        self.imglabel = QLabel(self)
        self.imglabel.setText("No image Loaded!")
        self.imglabel.setGeometry(QRect(175, 15, 300, 40))

    def on_confirm_clear_click(self):
        self.img_render.reset_mask()

    def on_confirm_saveimg_click(self):
        # TODO: add default image file options and default save fn
        self.savepath = QFileDialog.getSaveFileName(self)[0]
        print(self.savepath)

    def on_finish_editing(self):
        self.loadimgbutton.setEnabled(True)
        self.img_render = None

    def on_confirm_loadimg_click(self):

        if self.img_render is not None:
            return

        self.imgpath = QFileDialog.getOpenFileName(self)[0]
        
        if self.imgpath != '':

            try:
                im = Image.open(self.imgpath)
                self.imgdata, self.img_w, self.img_h = im.getdata(), *im.size

                self.disp_qimg = qt_touchup_lib.render_qimage(
                                self.imgdata, 
                                self.img_w, self.img_h)
                
                self.imglabel.setText(self.imgpath.split("/")[-1])

                self.img_render = RenderWin(    QRect(0,0, self.img_w, self.img_h),
                                                self.disp_qimg.copy(),
                                                self.img_w, self.img_h, self)
                
                self.loadimgbutton.setEnabled(False)
                self.clearbutton.setEnabled(True)
                self.img_render.show()
            except:
                self.raise_invalid_file_err()

    def raise_invalid_file_err(self):
        e = QMessageBox()
        e.setIcon(QMessageBox.Critical)
        e.setText("Invalid file encountered!")
        e.setStandardButtons(QMessageBox.Ok)
        e.exec_()

class RenderWin(QMainWindow):

    def __init__(self, loc, img, w,h, parent=None):
        super(RenderWin, self).__init__(parent)
        self.parent = parent
        
        # window properties
        self.setWindowTitle(" ")
        self.setGeometry(loc)
        self.setFixedSize(w, h)
        self.move(  parent.x() + parent.width()/2, 
                    parent.y() + parent.height()/2)

        # window data and mask
        self.img, self.w, self.h = img, w, h
        self.reset_mask()
        self.clip_w = lambda x: qt_touchup_lib.clip(x, 0, self.w - 1)
        self.clip_h = lambda x: qt_touchup_lib.clip(x, 0, self.h - 1)

    def reset_mask(self):
        self.mask = np.zeros((self.w, self.h))
        self.mask_display = qt_touchup_lib.get_trans_qimage(self.w, self.h)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(0,0), self.img)
        painter.drawImage(QPoint(0,0), self.mask_display)

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.is_clicked:
            painter = QPainter(self.mask_display)
            painter.setPen(QPen(Qt.gray, 2, Qt.SolidLine))
            painter.drawLine(self.prev_point, event.pos())
            self.prev_point = event.pos()
            self.update()

            self.mask[  self.clip_w(event.pos().x()-1), 
                        self.clip_h(event.pos().y()-1)] = 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked = True
            self.prev_point = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked = False

    def closeEvent(self, event):
        self.parent.on_finish_editing()
        event.accept()
        self.destroy()