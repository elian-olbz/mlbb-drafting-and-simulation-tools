from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import*

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class BoardWindow(QMainWindow):
    def __init__(self):
        super(BoardWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.menu_width = 55
        self.snap_menu_width = 55
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir,  "board.ui")

        uic.loadUi(ui_path, self)

        #self.home_btn.clicked.connect(self.toggle_home_menu)
        self.snap_menu_btn.clicked.connect(self.toggle_snap_menu)
    
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


    def toggle_home_menu(self):
        if self.menu_width == 55:
            self.menu_width = 150  # New width when menu is collapsed
        else:
            self.menu_width = 55  # Original width when menu is expanded

        self.left_menu_subcontainer.setFixedWidth(self.menu_width)

    def toggle_snap_menu(self):
        if self.snap_menu_width == 55:
            self.snap_menu_width = 150
        else:
            self.snap_menu_width = 55
        self.right_menu_subcontainer.setFixedWidth(self.snap_menu_width)
#######################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BoardWindow()
    window.show()

    sys.exit(app.exec())