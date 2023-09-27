from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy,  QButtonGroup, QFontComboBox, QSlider, QColorDialog, QFileDialog
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QAction, QBrush, QPen, QPainter, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource, QSize, QRect, QPoint
from PyQt6 import uic
import sys
import os
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import*
import types

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class DraggableFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.mousePressPosition = None
        self.mouseMoveOffset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressPosition = event.globalPosition()
            self.mouseMoveOffset = self.mousePressPosition.toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.MouseButton.LeftButton:
            globalPos = event.globalPosition()
            self.move(globalPos.toPoint() - self.mouseMoveOffset)

class BoardWindow(QMainWindow):
    def __init__(self):
        super(BoardWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.menu_width = 55
        self.snap_menu_width = 55
        self.title_bar = TitleBar(self)

        ui_path = os.path.join(script_dir,  "board.ui")

        uic.loadUi(ui_path, self)

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

    def setup_drag_item(self, name, locx, locy, image):
        frame1 = DraggableFrame(self)
        frame1.setObjectName(name)
        lay = QVBoxLayout()
        lay.setContentsMargins(8, 8, 8, 8)
        img = QLabel()
        lay.addWidget(img)
        img.setStyleSheet(f"image: url(:/icons/images/hero_roles/{image});")
        frame1.setLayout(lay)
        frame1.setParent(self.map_6)
        frame1.setGeometry(locx, locy, 50, 50)
        frame1.setStyleSheet(f"QFrame #{name}{{background-color: rgba(80, 80, 80, 230);; border-radius: 25px; border:2px solid; border-color:white}}")
    
    def create_drag_items(self):
        self.setup_drag_item("red", 100, 10, "gold_blue.png")
        self.setup_drag_item("blue", 100, 60, "exp_blue.png")
        self.setup_drag_item("red", 100, 110, "mid_blue.png")
        self.setup_drag_item("blue", 100, 160, "roam_blue.png")
        self.setup_drag_item("red", 100, 220, "jungle_blue.png")

        self.setup_drag_item("blue", 300, 10, "exp_red.png")
        self.setup_drag_item("red", 300, 60, "gold_red.png")
        self.setup_drag_item("blue", 300, 110, "roam_red.png")
        self.setup_drag_item("red", 300, 160, "mid_red.png")
        self.setup_drag_item("blue", 300, 220, "jungle_red.png")
#######################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BoardWindow()
    window.show()

    sys.exit(app.exec())