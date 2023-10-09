from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os
from ui.rsc_rc import *
from ui.misc.dialog_nav import*

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class ExitDialog(QDialog):
       def __init__(self):
              super(ExitDialog, self).__init__()

              ui_path = os.path.join(script_dir,  "exit_page.ui")

              uic.loadUi(ui_path, self)
              self.title_bar = DialogBar(self)
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
              self.title_bar.DialogAttrs(self)

       def mousePressEvent(self, event):
              self.dragPos = event.globalPosition().toPoint()
#######################################################################
