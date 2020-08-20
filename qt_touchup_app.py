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

    def on_confirm_touchup_click(self):
        self.img_raw = qt_touchup_lib.touch_up(self.img_raw, self.render.mask)
        self.render.img = qt_touchup_lib.raws2qimg(self.img_raw)
        self.render.reset_mask()

    def on_confirm_clear_click(self):
        self.render.reset_mask()

    def on_confirm_saveimg_click(self):
        # TODO: add default image file options and default save fn
        self.savepath = QFileDialog.getSaveFileName(self)[0]
        outimg = Image.fromarray(np.transpose(self.img_raw, (1,0,2)))
        outimg.save(self.savepath)

    def on_finish_editing(self):

        # Reset UI
        self.loadimgbutton.setEnabled(True)
        self.clearbutton.setEnabled(False)
        self.touchupbutton.setEnabled(False)
        self.imglabel.setText("")

        # Clean up render window resources
        del self.render.img
        del self.render.mask
        del self.render.mask_display
        self.render = None


    def on_confirm_loadimg_click(self):

        # do not allow more than 1 image to load
        if self.render is not None:
            return

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
                self.render = RenderWin(QRect(0,0, self.w, self.h),
                                    qt_touchup_lib.raws2qimg(self.img_raw),
                                    self.w, self.h, self)              
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

        self.mask = np.zeros((self.w, self.h)).astype(np.uint8)
        self.mask_display = qt_touchup_lib.get_trans_qimage(self.w, self.h)
        self.update()
        
    def paintEvent(self, event):

        painter = QPainter(self)
        painter.drawImage(QPoint(0,0), self.img)
        painter.drawImage(QPoint(0,0), self.mask_display)

    def mouseMoveEvent(self, event):
        
        if Qt.LeftButton and self.is_clicked:

            # draw trail on mask_display
            painter = QPainter(self.mask_display)
            painter.setPen(QPen(Qt.gray, 2, Qt.SolidLine))
            painter.drawLine(self.prev_point, event.pos())
            self.prev_point = event.pos()
            self.update()

            # update mask
            self.mask[  self.clip_w(event.pos().x()-1), 
                        self.clip_h(event.pos().y()-1)] = 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked, self.prev_point = True, event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked = False

    def closeEvent(self, event):
        self.parent.on_finish_editing()
        event.accept(); self.destroy()