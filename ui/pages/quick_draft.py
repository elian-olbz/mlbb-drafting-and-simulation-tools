from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class QuickDraftWindow(QMainWindow):
       def __init__(self, parent):
        super(QuickDraftWindow, self).__init__(parent)

        ui_path = os.path.join(script_dir,  "quick_draft.ui")

        uic.loadUi(ui_path, self)
        self.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuickDraftWindow()
    window.show()

    sys.exit(app.exec())