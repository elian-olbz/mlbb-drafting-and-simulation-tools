from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os
from ui.rsc_rc import *
from ui.misc.dialog_nav import*

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class OpenPracticeDraft(QDialog):
    def __init__(self):
        super(OpenPracticeDraft, self).__init__()
        #self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        ui_path = os.path.join(script_dir,  "open_practice_draft.ui")
        uic.loadUi(ui_path, self)
        self.t_bar = DialogBar(self) 

        self.side_combo_box.setDisabled(True)
        self.ai_slider.setDisabled(True)

        self.mode_combo_box.currentIndexChanged.connect(self.mode_index_changed)

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
    def mode_index_changed(self):   
        if self.mode_combo_box.currentIndex() == 1:
            self.ai_slider.setDisabled(False)
            self.side_combo_box.setDisabled(False)
        else:
            self.ai_slider.setDisabled(True)
            self.side_combo_box.setDisabled(True)