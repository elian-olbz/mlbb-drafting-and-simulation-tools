from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QSizeGrip
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic


class DialogBar(QMainWindow):
    def __init__(self, parent):
        super(DialogBar, self).__init__(parent)

        self.shadow_style = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(26, 26, 43, 255), stop:0.521368 rgba(19, 19, 30, 255));"

    ## ==> UI DEFINITIONS
    def DialogAttrs(self, parent):

        parent.verticalLayout.setContentsMargins(10, 10, 10, 10)
        parent.drop_shadow.setStyleSheet(self.shadow_style)
        
        # REMOVE TITLE BAR
        parent.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        parent.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # SET DROPSHADOW WINDOW
        parent.shadow = QGraphicsDropShadowEffect(parent)
        parent.shadow.setBlurRadius(20)
        parent.shadow.setXOffset(0)
        parent.shadow.setYOffset(0)
        parent.shadow.setColor(QColor(0, 0, 0, 100))

        # APPLY DROPSHADOW TO FRAME
        #------------
        parent.drop_shadow.setGraphicsEffect(parent.shadow)

        # CLOSE
        parent.exit_button.clicked.connect(lambda: parent.close())
        #----------------------

"""
        ## ==> CREATE SIZE GRIP TO RESIZE WINDOW
        parent.sizegrip = QSizeGrip(parent.frame_grip)
        parent.sizegrip.setStyleSheet("QSizeGrip { width: 10px; height: 10px; margin: 5px } QSizeGrip:hover { background-color: rgb(50, 42, 94) }")
        parent.sizegrip.setToolTip("Resize Window")
"""
