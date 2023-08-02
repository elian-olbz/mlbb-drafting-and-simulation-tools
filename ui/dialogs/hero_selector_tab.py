from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout
from PyQt6.QtGui import QPixmap, QColor, QShortcut
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class HeroSelector(QDialog):
       def __init__(self):
        super(HeroSelector, self).__init__()

        ui_path = os.path.join(script_dir,  "hero_selector_tab.ui")

        uic.loadUi(ui_path, self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = HeroSelector()
    window.show()

    sys.exit(app.exec())