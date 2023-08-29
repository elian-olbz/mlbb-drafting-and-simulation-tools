from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource, QEvent
from PyQt6 import uic
import sys
import os
import pandas as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from run_draft_logic.utils import load_theme
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import*
from ui.dialogs.hero_selector_tab import *
from ui.misc.graphs import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

class QuickDraftWindow(QMainWindow):
    def __init__(self):
        super(QuickDraftWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.menu_width = 55
        self.qlabel_to_update = None
        self.obj_name = None
        self.blue_heroes = {"blue_roam":"", "blue_mid":"", "blue_exp":"", "blue_jungle":"", "blue_gold":""}
        self.red_heroes = {"red_gold":"", "red_jungle":"", "red_exp":"", "red_mid":"", "red_roam":""}
        self.prev_qlabel = None

        self.title_bar = TitleBar(self)
        self.hero_dialog = HeroSelectorDialog()
        ui_path = os.path.join(script_dir,  "quick_draft.ui")

        uic.loadUi(ui_path, self)

        self.hero_dialog.select_btn.clicked.connect(self.select_button_click)

        self.labels = {}

        self.label_names = list(self.blue_heroes.keys()) + list(self.red_heroes.keys())

        # Find the child qlabels to properly connect an event filter
        for name in self.label_names:
            label = self.findChild(QLabel, name)
            if label:
                self.labels[name] = label
                label.installEventFilter(self)
        
        # Canvas for the graphs
        self.fig = Figure(figsize=(10,10))
        self.canvas = FigureCanvas(self.fig)
        self.graph_layout.addWidget(self.canvas)

        self.axs = self.fig.subplots(2,3)

        self.fig.patch.set_visible(False)

        # Create instances of the graphs and pass the subplots
        radar_blue = RadarChart(self.axs[0, 0], pos_x=1, fig=self.fig)
        diverging_team = DivergingChart(self.axs[0,1])
        radar_red = RadarChart(self.axs[0, 2], pos_x=3, fig=self.fig)

        horizotal_indiv = HorizontalChart(self.axs[1, 0])
        diverging_indiv = DivergingChart(self.axs[1, 1])
        donut_indiv = DonutChart(self.axs[1, 2])

        for i, ax in enumerate(self.axs.flatten()):
            ax.set_frame_on(False)
            if i in [0, 2]:
                ax.set_yticklabels([])
                ax.set_xticklabels([])
                ax.set_yticks([])
                ax.set_xticks([])
        
        self.fig.tight_layout()
        
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

                self.obj_name = obj.objectName()
                self.qlabel_to_update = obj
                self.set_highlight(20)
                if self.obj_name in self.labels:
                    self.show_dial()

        self.prev_qlabel = self.qlabel_to_update    
        return super().eventFilter(obj, event)
    
    def show_dial(self):
        self.hero_dialog.show()
    
    # when "Select" button from the selector is clicked
    def select_button_click(self):
        if self.hero_dialog.selector.selected_id is not None and self.qlabel_to_update is not None:
            self.qlabel_to_update.setStyleSheet("")
            #self.hero_dialog.hide()
            self.hero_dialog.selector.disp_selected_image(self.hero_dialog.selector.selected_id, self.qlabel_to_update)
            self.hero_dialog.selector.current_clicked_label.setStyleSheet("")

            if str(self.obj_name).startswith("blue"):
                if self.blue_heroes[self.obj_name] == "":
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                else:
                    self.hero_dialog.selector.unavailable_hero_ids.remove(self.blue_heroes[self.obj_name])
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
            else:
                if self.red_heroes[self.obj_name] == "":
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                else:
                    self.hero_dialog.selector.unavailable_hero_ids.remove(self.red_heroes[self.obj_name])
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id

            print("Unavailable Heroes: {}".format(self.hero_dialog.selector.unavailable_hero_ids))
            print("blue heroes: {}\t\tred heroes: {}\n".format(list(self.blue_heroes.values()), list(self.red_heroes.values())))
            self.qlabel_to_update = None
            self.hero_dialog.selector.selected_id = None

    def get_index(self, name):
        if isinstance(name, str):
            indexx = self.label_names.index(name)

            if indexx > 4:
                return indexx - 5
            return indexx
        
    def set_highlight(self, radius):
        if self.prev_qlabel is not None and self.qlabel_to_update != self.prev_qlabel:
            self.prev_qlabel.setStyleSheet("image: url(:/icons/icons/plus-circle.svg);")

        highlight_color = QColor(69, 202, 255)  # Replace with the desired highlight color
        highlight_radius = radius / 2  # Adjust the radius as needed

        circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
        self.qlabel_to_update.setStyleSheet(circular_style + "image: url(:/icons/icons/plus-circle.svg);")