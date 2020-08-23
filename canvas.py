from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPoint

import qt_touchup_lib as qtl

class Canvas(QWidget):
    def __init__(self, img, w, h, r, parent=None):
        super(Canvas, self).__init__(parent)
        self.parent = parent
        self.setFixedSize(w, h)

        self.img, self.w, self.h, self.r = img, w, h, r
        self.reset_mask()
        self.clip_w = lambda x: qtl.clip(x, 0, self.w - 1)
        self.clip_h = lambda x: qtl.clip(x, 0, self.h - 1)

    def reset_mask(self):
        self.mask = qtl.get_blank_mask(self.w, self.h)
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
