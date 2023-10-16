from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QSizeGrip, QFrame
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource
from PyQt6 import uic


class TitleBar(QMainWindow):
    def __init__(self, parent):
        super(TitleBar, self).__init__(parent)
        self.win_maxed = True
        self.shadow_style = "background-color: qlineargradient(\
                                spread: pad, x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 rgba(0, 0, 0, 1), stop: 0.521368 rgba(0, 0, 0, 1));"
        self.main_frame_max = "*{border:none; border-radius: 0px; background-color:transparent; \
                                background:transparent; padding:0; margin:0; color:#fff} \
                                QFrame #main_frame{border:0px solid; border-radius: 0px}"
        self.main_frame_min = "*{border:none; border-radius: 0px; background-color:transparent; \
                                background:transparent; padding:0; margin:0; color:#fff} \
                                QFrame #main_frame{border:1px solid; border-radius: 10px; border-color:rgb(83, 89, 98);}"
        parent.grip_label.setVisible(False)
        
    ## ==> MAXIMIZE RESTORE FUNCTION
    def maximize_restore(self, parent):
        if self.win_maxed == False:    # IF NOT MAXIMIZED
            parent.central_layout.setContentsMargins(0, 0, 0, 0)
            parent.main_frame.setStyleSheet(self.main_frame_max)
            parent.grip_label.setVisible(False)
            parent.showMaximized()
            parent.setStyleSheet("border-radius: 0px;")
            parent.drop_shadow.setStyleSheet(self.shadow_style)
            parent.btn_max.setToolTip("Restore")
            self.win_maxed = True
            
        else:
            parent.main_frame.setStyleSheet(self.main_frame_min)
            parent.central_layout.setContentsMargins(10, 10, 10, 10)
            parent.grip_label.setVisible(True)
            parent.showNormal()
            #parent.resize(parent.width()+1, parent.height()+1)
            parent.setStyleSheet("border-radius: 10px;")
            parent.drop_shadow.setStyleSheet(self.shadow_style)
            parent.btn_max.setToolTip("Maximize")
            self.win_maxed = False

    ## ==> UI DEFINITIONS
    def uiDefinitions(self, parent):

        # REMOVE TITLE BAR
        parent.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        parent.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        #parent.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

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
        parent.sizegrip.setStyleSheet("QSizeGrip { width: 10px; height: 10px; margin: 5px }")
        parent.sizegrip.setToolTip("Resize Window")

    ## RETURN STATUS IF WINDOWS IS MAXIMIZE OR RESTORED
    def returnStatus(self):
        return self.win_maxed
