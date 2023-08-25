from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource, QEvent
from PyQt6 import uic
import sys
import os
from run_draft_logic.utils import load_theme
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import*
from ui.dialogs.hero_selector_tab import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class QuickDraftWindow(QMainWindow):
    def __init__(self):
        super(QuickDraftWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.menu_width = 55
        self.qlabel_to_update = None

        self.title_bar = TitleBar(self)
        self.hero_dialog = HeroSelectorDialog()
        ui_path = os.path.join(script_dir,  "quick_draft.ui")

        uic.loadUi(ui_path, self)

        #self.logo_btn.clicked.connect(self.show_dial)

        self.hero_dialog.select_btn.clicked.connect(self.select_button_click)

        self.labels = {}

        label_names = ["blue_roam", "blue_mid", "blue_exp", "blue_jungle", "blue_gold", "red_roam", "red_mid", "red_exp", "red_jungle", "red_gold"]

        for name in label_names:
            label = self.findChild(QLabel, name)
            if label:
                self.labels[name] = label
                label.installEventFilter(self)
        
#############################################################       
        # MOVE WINDOW
        def moveWindow(event):
            # RESTORE BEFORE MOVE
            if self.title_bar.returnStatus() == True:
                self.title_bar.maximize_restore(self)

            # IF LEFT CLICK MOVE WINDOW
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

        # SET TITLE BAR
        #-----------------
        self.header_container.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        self.title_bar.uiDefinitions(self)
        #self.showMaximized()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

#######################################################################     
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                object_name = obj.objectName()
                self.qlabel_to_update = obj
                if object_name in self.labels:
                    self.show_dial()
                    
        return super().eventFilter(obj, event)
    
    def show_dial(self):
        self.hero_dialog.show()
    
    # when "Select" button from the selector is clicked
    def select_button_click(self, qlabel):
              if self.hero_dialog.selector.selected_id is not None and self.qlabel_to_update is not None:
                     self.hero_dialog.hide()
                     self.hero_dialog.selector.disp_selected_image(self.hero_dialog.selector.selected_id, self.qlabel_to_update)
                     self.hero_dialog.selector.current_clicked_label.setStyleSheet("")

                     self.qlabel_to_update.setStyleSheet("")
                     self.qlabel_to_update = None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuickDraftWindow()
    window.show()

    sys.exit(app.exec())