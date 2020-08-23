from PyQt5.QtWidgets import QMainWindow, QScrollArea, QStyle, QStyleOptionSlider
from PyQt5.QtCore import QSize

from canvas import Canvas
from qt_touchup_lib import clip

class RenderWin(QMainWindow):

    def __init__(self, loc, img, w, h, r, parent=None):
        super(RenderWin, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle(" ")
        self.setGeometry(loc)

        self.move(  parent.x() + parent.width()/2,
                    parent.y() + parent.height()/2)

        self.canvas = Canvas(img, w, h, r, self)

        self.scrollview = QScrollArea(self)
        bar_w = self.scrollview.style().subControlRect(
                    QStyle.CC_ScrollBar, QStyleOptionSlider(),
                    QStyle.SC_ScrollBarGroove, self).x()
        self.scrollview.setWidget(self.canvas)
        self.setCentralWidget(self.scrollview)

        default_max_w, default_max_h = 300, 300
        self.setFixedSize(QSize(clip(w + bar_w, 0, default_max_w),
                                clip(h + bar_w, 0, default_max_h)))
        self.setMaximumSize(QSize(w + bar_w, h + bar_w))
        self.canvas.update()

    def closeEvent(self, event):
        self.parent.on_finish_editing()
        self.canvas.reset_mask()
        event.accept(); self.destroy()
