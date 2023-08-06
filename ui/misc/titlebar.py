from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QSizeGrip, QFrame
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic


class TitleBar(QMainWindow):
    def __init__(self, parent, window_maxed):
        super(TitleBar, self).__init__(parent)
        self.win_maxed = window_maxed
        

    ## ==> MAXIMIZE RESTORE FUNCTION
    def maximize_restore(self, parent):
        # IF NOT MAXIMIZED
        if self.win_maxed == False:
            parent.showMaximized()

            self.win_maxed = True

            # IF MAXIMIZED REMOVE MARGINS AND BORDER RADIUS
            parent.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            parent.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(35, 39, 46, 1), stop:0.521368 rgba(31, 35, 42, 1)); border-radius: 0px;")
            parent.btn_max.setToolTip("Restore")
        else:
            self.win_maxed = False
            parent.showNormal()
            parent.resize(parent.width()+1, parent.height()+1)

            #--------------
            parent.horizontalLayout.setContentsMargins(10, 10, 10, 10)
            parent.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(35, 39, 46, 1), stop:0.521368 rgba(31, 35, 42, 1));border-radius: 10px;")
            parent.btn_max.setToolTip("Maximize")
            #--------------

    ## ==> UI DEFINITIONS
    def uiDefinitions(self, parent):

        if parent.WINDOW_MAXED == False:
            parent.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            parent.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(35, 39, 46, 1), stop:0.521368 rgba(31, 35, 42, 1)); border-radius: 10px;")
        
            parent.frame_2.setStyleSheet("border-radius: 10px;")
            parent.frame_3.setStyleSheet("border-radius: 10px;")

            parent.btn_max.setToolTip("Restore")
        else:
            parent.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            parent.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(35, 39, 46, 1), stop:0.521368 rgba(31, 35, 42, 1)); border-radius: 0px;")
        
            parent.frame_2.setStyleSheet("border-radius: 10px;")
            parent.frame_3.setStyleSheet("border-radius: 10px;")

            parent.btn_max.setToolTip("Restore")
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

        # MAXIMIZE / RESTORE
        parent.btn_max.clicked.connect(lambda: TitleBar.maximize_restore(self, parent))

        # MINIMIZE
        parent.btn_min.clicked.connect(lambda: parent.showMinimized())

        # CLOSE
        parent.btn_close.clicked.connect(lambda: parent.close())
        #----------------------

        ## ==> CREATE SIZE GRIP TO RESIZE WINDOW
        parent.sizegrip = QSizeGrip(parent.frame_grip)
        parent.sizegrip.setStyleSheet("QSizeGrip { width: 10px; height: 10px; margin: 5px } QSizeGrip:hover { background-color: rgb(50, 42, 94) }")
        parent.sizegrip.setToolTip("Resize Window")



    ## RETURN STATUS IF WINDOWS IS MAXIMIZE OR RESTAURED
    def returnStatus(self):
        return self.win_maxed
