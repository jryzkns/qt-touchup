from PyQt5.QtWidgets import QApplication
from imgreaderapp import ImgReaderApp
import sys

if __name__ == '__main__':
    m = QApplication(sys.argv)
    app = ImgReaderApp()
    app.show()
    sys.exit(m.exec_())