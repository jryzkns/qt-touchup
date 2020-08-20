from PyQt5.QtWidgets import QApplication
from qt_touchup_app import QtTouchupApp
import sys

if __name__ == '__main__':
    m = QApplication(sys.argv)
    app = QtTouchupApp()
    app.show()
    sys.exit(m.exec_())