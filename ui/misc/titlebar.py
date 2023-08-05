from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QSizeGrip
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic

WINDOW_MAXED = True

class UIFunctions(QMainWindow):

    ## ==> MAXIMIZE RESTORE FUNCTION
    def maximize_restore(self):
        global WINDOW_MAXED
        status = WINDOW_MAXED

        # IF NOT MAXIMIZED
        if status == False:
            self.showMaximized()

            # SET GLOBAL TO 1
            WINDOW_MAXED = True

            # IF MAXIMIZED REMOVE MARGINS AND BORDER RADIUS
            self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(42, 44, 111, 255), stop:0.521368 rgba(28, 29, 73, 255)); border-radius: 0px;")
            self.btn_max.setToolTip("Restore")
        else:
            WINDOW_MAXED = False
            self.showNormal()
            self.resize(self.width()+1, self.height()+1)

            #--------------
            self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
            self.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(42, 44, 111, 255), stop:0.521368 rgba(28, 29, 73, 255)); border-radius: 10px;")
            self.btn_max.setToolTip("Maximize")
            #--------------

    ## ==> UI DEFINITIONS
    def uiDefinitions(self):

        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.drop_shadow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(42, 44, 111, 255), stop:0.521368 rgba(28, 29, 73, 255)); border-radius: 0px;")
        self.btn_max.setToolTip("Restore")
        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # SET DROPSHADOW WINDOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 100))

        # APPLY DROPSHADOW TO FRAME
        #------------
        self.drop_shadow.setGraphicsEffect(self.shadow)

        # MAXIMIZE / RESTORE
        self.btn_max.clicked.connect(lambda: UIFunctions.maximize_restore(self))

        # MINIMIZE
        self.btn_min.clicked.connect(lambda: self.showMinimized())

        # CLOSE
        self.btn_close.clicked.connect(lambda: self.close())
        #----------------------

        ## ==> CREATE SIZE GRIP TO RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.frame_grip)
        self.sizegrip.setStyleSheet("QSizeGrip { width: 10px; height: 10px; margin: 5px } QSizeGrip:hover { background-color: rgb(50, 42, 94) }")
        self.sizegrip.setToolTip("Resize Window")



    ## RETURN STATUS IF WINDOWS IS MAXIMIZE OR RESTAURED
    def returnStatus():
        return WINDOW_MAXED
