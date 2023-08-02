from PyQt6.QtWidgets import  QDialog
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
