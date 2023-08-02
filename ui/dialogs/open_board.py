from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import uic
import sys
import os
from ui.rsc_rc import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class OpenBoard(QDialog):
       def __init__(self):
        super(OpenBoard, self).__init__()

        ui_path = os.path.join(script_dir,  "open_board.ui")

        uic.loadUi(ui_path, self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OpenBoard()
    window.show()

    sys.exit(app.exec())