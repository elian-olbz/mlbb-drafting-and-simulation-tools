from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os
from ui.rsc_rc import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class OpenQuickDraft(QDialog):
       def __init__(self):
        super(OpenQuickDraft, self).__init__()

        ui_path = os.path.join(script_dir,  "open_quick_draft.ui")

        uic.loadUi(ui_path, self)
