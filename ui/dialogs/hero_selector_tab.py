from PyQt6.QtWidgets import  QDialog
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *
from ui.misc.dialog_nav import*
from run_draft_logic.setup_selector import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class HeroSelectorDialog(QDialog):
       def __init__(self):
              super(HeroSelectorDialog, self).__init__()

              ui_path = os.path.join(script_dir,  "hero_selector_tab.ui")
              uic.loadUi(ui_path, self)
              self.t_bar = DialogBar(self) 

              self.selector = SetupHeroDialog(self)

              self.selector.populate_tabs(self)

#############################################################       
              # MOVE WINDOW
              def moveWindow(event):
                     # IF LEFT CLICK MOVE WINDOW
                     if event.buttons() == Qt.MouseButton.LeftButton:
                            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                            self.dragPos = event.globalPosition().toPoint()
                            event.accept()

              # SET TITLE BAR
              #-----------------
              self.exit_frame.mouseMoveEvent = moveWindow

              ## ==> SET UI DEFINITIONS
              self.t_bar.DialogAttrs(self)

       def mousePressEvent(self, event):
              self.dragPos = event.globalPosition().toPoint()
#######################################################################

              
                     
       
