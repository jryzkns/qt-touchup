from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QPushButton, QWidget, QMessageBox, QRadioButton, QSlider
from PyQt5.QtCore import Qt, QSize, QRect

import threading

from renderwin import RenderWin
import qt_touchup_lib as qtl

class QtTouchupApp(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.raw_img_edit_lock = threading.Lock()

        self.setFixedSize(QSize(350, 360))
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
        self.saveimgbutton.setEnabled(False)

        self.clearbutton = QPushButton("Clear", self)
        self.clearbutton.clicked.connect(self.on_confirm_clear_click)
        self.clearbutton.setGeometry(QRect(15, 115, 150, 40))
        self.clearbutton.setEnabled(False)

        self.touchupbutton = QPushButton("Touch-Up", self)
        self.touchupbutton.clicked.connect(self.on_confirm_touchup_click)
        self.touchupbutton.setGeometry(QRect(175, 115, 150, 40))
        self.touchupbutton.setEnabled(False)

        self.touchup_mode = qtl.INPAINT_TELEA

        self.moderadbutton1 = QRadioButton("TELEA", self)
        self.moderadbutton1.setGeometry(QRect(15, 165, 150, 20))
        self.moderadbutton1.setChecked(True)
        self.moderadbutton1.toggled.connect(
            lambda : self.set_touchup_mode(qtl.INPAINT_TELEA))

        self.moderadbutton2 = QRadioButton("NS", self)
        self.moderadbutton2.setGeometry(QRect(15, 185, 150, 20))
        self.moderadbutton2.setChecked(False)
        self.moderadbutton2.toggled.connect(
            lambda : self.set_touchup_mode(qtl.INPAINT_NS))

        self.moderadbutton3 = QRadioButton("CUSTOM", self)
        self.moderadbutton3.setGeometry(QRect(15, 205, 150, 20))
        self.moderadbutton3.setChecked(False)
        self.moderadbutton3.toggled.connect(
            lambda : self.set_touchup_mode(qtl.INPAINT_CUSTOM))

        self.touch_up_radius = 5
        self.touch_up_slider = QSlider(Qt.Horizontal, self)
        self.touch_up_slider.setGeometry(QRect(15, 235, 75, 20))
        self.touch_up_slider.setMinimum(2)
        self.touch_up_slider.setMaximum(10)
        self.touch_up_slider.setSingleStep(1)
        self.touch_up_slider.setValue(self.touch_up_radius)
        self.touch_up_slider.valueChanged.connect(self.on_slider_update_value)

        self.stroke_windows = []

    def add_new_window(self, new_wind):
        new_wind = qtl.rect_expand(*new_wind)
        overlap, complement = [new_wind], []
        while overlap != []:
            new_wind = qtl.merge_all_rects(overlap + [new_wind])
            overlap = []
            for wind in self.stroke_windows:
                if qtl.rect_overlap(*new_wind, *wind):
                    overlap.append(wind)
                else:
                    complement.append(wind)
            self.stroke_windows = complement
        self.stroke_windows = complement + [new_wind]

    def on_slider_update_value(self):
        self.touch_up_radius = self.touch_up_slider.value()
        if self.render is not None:
            self.render.r = self.touch_up_radius

    def set_touchup_mode(self, mode):
        self.touchup_mode = mode

    def on_confirm_touchup_click(self):
        self.touchupbutton.setEnabled(False)
        threading.Thread(daemon=True, target=self.touchup_job).start()

    def touchup_job(self):

        chunk_th_jobs = []
        for bounds in self.stroke_windows:
            chunk_th_jobs.append(
                    threading.Thread(   daemon=True,
                                        target=self.touch_up_region,
                                        args=(bounds)))
            chunk_th_jobs[-1].start()

        map(lambda x: x.join(), chunk_th_jobs)

        self.render.canvas.img = qtl.raws2qimg(self.img_raw)
        self.render.canvas.reset_mask()
        self.render.canvas.update()
        self.touchupbutton.setEnabled(True)

    def touch_up_region(self, xmi, ymi, xma, yma):
        img_slice  = self.img_raw[xmi : xma, ymi : yma, :]
        mask_slice = self.render.canvas.mask[xmi : xma, ymi : yma]
        with self.raw_img_edit_lock:
            self.img_raw[xmi : xma, ymi : yma, :] = qtl.touch_up(
                    img_slice, mask_slice, self.touch_up_radius, self.touchup_mode)

    def on_confirm_clear_click(self):
        self.render.canvas.reset_mask()

    def on_confirm_saveimg_click(self):
        # TODO: add default image file options and default save fn
        self.savepath = QFileDialog.getSaveFileName(self)[0]
        qtl.save_img(self.img_raw,self.savepath)

    def on_finish_editing(self):

        self.loadimgbutton.setEnabled(True)
        self.clearbutton.setEnabled(False)
        self.touchupbutton.setEnabled(False)
        self.imglabel.setText("No image Loaded!")

        self.render = None

    def on_confirm_loadimg_click(self):

        self.imgpath = QFileDialog.getOpenFileName(self)[0]

        # continue only when a file has been chosen
        if self.imgpath != '':
            self.load_img_and_render()

    def load_img_and_render(self):

        try:
            self.img_raw, self.w, self.h = qtl.load_img(self.imgpath)
        except:
            self.raise_invalid_file_err()
            return

        self.render = RenderWin(    QRect(0, 0, self.w, self.h),
                                    qtl.raws2qimg(self.img_raw),
                                    self.w, self.h,
                                    self.touch_up_radius, self)
        self.render.show()

        self.imglabel.setText(self.imgpath.split("/")[-1])
        self.loadimgbutton.setEnabled(False)
        self.saveimgbutton.setEnabled(True)
        self.clearbutton.setEnabled(True)
        self.touchupbutton.setEnabled(True)


    def on_child_destroyed(self):
        self.saveimgbutton.setEnabled(False)

    def raise_invalid_file_err(self):

        e = QMessageBox()
        e.setIcon(QMessageBox.Critical)
        e.setText("Invalid file encountered!")
        e.setStandardButtons(QMessageBox.Ok)
        e.exec_()
