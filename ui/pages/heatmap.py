from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic
import sys
import os
from run_draft_logic.utils import load_theme
from functools import partial
from ui.rsc_rc import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class HeatMapWindow(QMainWindow):
    def __init__(self):
        super(HeatMapWindow, self).__init__()

        ui_path = os.path.join(script_dir,  "heatmap.ui")

        uic.loadUi(ui_path, self)
        

        theme_path = "ui/py_dracula_dark.qss"
        theme = load_theme(theme_path)
        self.setStyleSheet(theme)

        self.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = HeatMapWindow()
    window.show()

    sys.exit(app.exec())