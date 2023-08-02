from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import uic
import sys
import os
from ui.rsc_rc import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class OpenQuickDraft(QDialog):
       def __init__(self):
        super(OpenQuickDraft, self).__init__()

        ui_path = os.path.join(script_dir,  "open_quick_draft.ui")

        uic.loadUi(ui_path, self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = OpenQuickDraft()
    window.show()

    sys.exit(app.exec())