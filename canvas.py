from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

import qt_touchup_lib as qtl

class Window():
    def __init__(self, x, y):
        self.top, self.bottom = y, y
        self.left, self.right = x, x
    def update(self, x, y):
        if self.top > y: self.top = y
        elif self.bottom < y: self.bottom = y
        if self.left > x: self.left = x
        elif self.right < x: self.right = x
    def export(self):
        return (self.left, self.top, self.right, self.bottom)

class Canvas(QWidget):
    def __init__(self, img, w, h, r, parent=None):
        super(Canvas, self).__init__(parent)
        self.parent = parent
        self.setFixedSize(w, h)

        self.img, self.w, self.h, self.r = img, w, h, r
        self.reset_mask()
        self.clip_w = lambda x: qtl.clip(x, 0, self.w - 1)
        self.clip_h = lambda x: qtl.clip(x, 0, self.h - 1)

        self.stroke_window = None

    def reset_mask(self):
        self.qmask = qtl.get_trans_qimage(self.w, self.h, QImage.Format_Alpha8)
        self.mask = qtl.get_mask_from_qimg(self.qmask)
        self.mask_display = qtl.get_trans_qimage(self.w, self.h)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), self.img)
        painter.drawImage(QPoint(0, 0), self.mask_display)

    def mouseMoveEvent(self, event):
        if Qt.LeftButton:
            painter = QPainter(self.mask_display)
            painter.setPen(QPen(Qt.gray, self.r, Qt.SolidLine))
            painter.drawLine(self.prev_point, event.pos())

            painter1 = QPainter(self.qmask)
            painter1.setPen(QPen(Qt.gray, self.r, Qt.SolidLine))
            painter1.drawLine(self.prev_point, event.pos())

            self.prev_point = event.pos()
            self.update()

            self.stroke_window.update(  self.clip_w(event.pos().x()), 
                                        self.clip_h(event.pos().y()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_clicked, self.prev_point = True, event.pos()
            self.stroke_window = Window(event.pos().x(), event.pos().y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mask = qtl.get_mask_from_qimg(self.qmask)
            self.parent.parent.add_new_window(self.stroke_window.export())
            self.is_clicked = False