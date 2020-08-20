from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QPushButton, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter, QPen, QBrush, QColor
import imgreaderlib

from PIL import Image

class ImgReaderApp(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setFixedSize(QSize(894, 651))
        self.setWindowTitle(" ")
        self.internal_state = 1

        self.loadimgbutton = QPushButton("Load Image", self)
        self.loadimgbutton.clicked.connect(self.on_confirm_loadimg_click)
        self.loadimgbutton.setGeometry(QRect(15, 15, 150, 40))

        self.saveimgbutton = QPushButton("Save Image", self)
        self.saveimgbutton.clicked.connect(self.on_confirm_saveimg_click)
        self.saveimgbutton.setGeometry(QRect(15, 65, 150, 40))

        self.imglabel = QLabel(self)
        self.imglabel.setText("No image Loaded!")
        self.imglabel.setGeometry(QRect(175, 15, 300, 40))

    def on_confirm_saveimg_click(self):
        # TODO: add default image file options and default save fn
        self.savepath = QFileDialog.getSaveFileName(self)[0]
        print(self.savepath)

    def on_confirm_loadimg_click(self):

        self.imgpath = QFileDialog.getOpenFileName(self)[0]

        if self.imgpath != '':

            try:
                im = Image.open(self.imgpath)
                self.imgdata, self.img_w, self.img_h = im.getdata(), *im.size

                self.disp_qimg = imgreaderlib.render_qimage(
                                self.imgdata, 
                                self.img_w, self.img_h)
                
                self.imglabel.setText(self.imgpath.split("/")[-1])

                self.img_render = RenderWin(QRect(0,0, self.img_w, self.img_h), self)
                self.img_render.img = self.disp_qimg.copy()
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

    def __init__(self, loc, parent=None):
        super(RenderWin, self).__init__(parent)
        self.setGeometry(loc)
        self.setWindowTitle(" ")
        self.img = imgreaderlib.render_qimage([], 0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(0,0),self.img)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing:
            
            painter = QPainter(self.img)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()