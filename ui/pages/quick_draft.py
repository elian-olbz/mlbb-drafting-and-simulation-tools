from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource, QEvent
from PyQt6 import uic
import sys
import os
import pandas as pd
import ast
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from run_draft_logic.utils import load_names, get_name, get_icon, load_hero_roles, get_role
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import*
from ui.dialogs.hero_selector_tab import *
from ui.misc.graphs import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

QSS = "QPushButton{text-align:center; border-radius: 23px; padding: 5px, 5px;} QPushButton:hover { background-color: #23272e;} QPushButton:pressed {background-color: rgb(62, 69, 82); color: rgb(255, 255, 255);}"

class QuickDraftWindow(QMainWindow):
    def __init__(self):
        super(QuickDraftWindow, self).__init__()

        self.WINDOW_MAXED = False
        self.menu_width = 55
        self.obj_name = None
        self.blue_heroes = {"blue_roam":0, "blue_mid":0, "blue_exp":0, "blue_jungle":0, "blue_gold":0}
        self.red_heroes = {"red_gold":0, "red_jungle":0, "red_exp":0, "red_mid":0, "red_roam":0}
        self.combined_hero_dict = {} # used for comparisons of the picked hero
        self.qlabel_to_update = None # Used when picker in picker_button == False
        self.prev_qlabel = None # Used when picker in picker_button == False

        self.curr_selected_qlabel = None # Used when picker in picker_button == True
        self.prev_selected_qlbel = None  # Used when picker in picker_button == True

        self.hero_names = load_names('data/hero_map.csv')
        self.hero_roles, _, _, _ = load_hero_roles('data/hero_roles.csv')
        self.df = pd.read_csv('data/winrate.csv', index_col=0, header=0)
        
        self.hero_data = self.load_attr('data/attr.csv')
        
        self.selected_hero = None
        self.picker_button_active = False

        self.title_bar = TitleBar(self)
        self.hero_dialog = HeroSelectorDialog()
        ui_path = os.path.join(script_dir,  "quick_draft.ui")

        uic.loadUi(ui_path, self)

        self.hero_dialog.select_btn.clicked.connect(self.select_button_click)
        self.hero_dialog.exit_button.clicked.connect(self.on_dialog_exit)
        self.picker_btn.clicked.connect(self.picker_button_clicked)

        self.labels = {}

        self.label_names = list(self.blue_heroes.keys()) + list(self.red_heroes.keys())

        # Find the child qlabels to properly connect an event filter
        for name in self.label_names:
            label = self.findChild(QLabel, name)
            if label:
                self.labels[name] = label
                label.installEventFilter(self)

        self.create_all_charts()
        self.role2.setVisible(False)

        space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self.hero_dialog)
        space_shortcut.activated.connect(self.hero_dialog.select_btn.click)
        
        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self.hero_dialog)
        enter_shortcut.activated.connect(self.hero_dialog.select_btn.click)

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
        self.header_container.mouseMoveEvent = moveWindow

        ## ==> SET UI DEFINITIONS
        self.title_bar.uiDefinitions(self)
        #self.showMaximized()
    #--------------------------------------------
    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def resizeEvent(self, event):
        self.hero_dialog.selector.update_current_tab(self.hero_dialog.hero_tab.currentIndex)
        if self.qlabel_to_update is not None:
            self.qlabel_to_update.setStyleSheet("image: url(:/icons/icons/plus-circle.svg);")


#######################################################################     
    def eventFilter(self, obj, event):
        self.combined_hero_dict = self.merge_heroes_dict(self.blue_heroes, self.red_heroes)
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:

                self.obj_name = obj.objectName()
                self.qlabel_to_update = obj
                
                if self.picker_button_active:
                    if self.combined_hero_dict[self.obj_name] != 0:
                        self.curr_selected_qlabel = obj
                        self.selected_hero = self.combined_hero_dict[self.obj_name]
                        self.update_single_hero()
                        self.set_highlight(25)
                else:
                    if self.obj_name in self.labels:
                        self.set_highlight(25)
                        self.show_dial()
        self.prev_selected_qlbel = self.curr_selected_qlabel
        self.prev_qlabel = self.qlabel_to_update    
        return super().eventFilter(obj, event)
    
    def show_dial(self):
        self.hero_dialog.show()  

    def on_dialog_exit(self):
        if self.picker_button_active == False:
            self.qlabel_to_update.setStyleSheet("image: url(:/icons/icons/plus-circle.svg);")

    def merge_heroes_dict(self, dict1, dict2):
        res = {**dict1, **dict2}
        return res
    
    # when "Select" button from the selector is clicked
    def select_button_click(self):
        if self.hero_dialog.selector.selected_id is not None and self.qlabel_to_update is not None:
            self.qlabel_to_update.setStyleSheet("")
            self.hero_dialog.hide()
            self.hero_dialog.selector.disp_selected_image(self.hero_dialog.selector.selected_id, self.qlabel_to_update)
            self.hero_dialog.selector.current_clicked_label.setStyleSheet("")

            if str(self.obj_name).startswith("blue"):
                if self.blue_heroes[self.obj_name] == 0:
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                    self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.hero_dialog.selector.selected_id, False) 
                else:
                    self.hero_dialog.selector.unavailable_hero_ids.remove(self.blue_heroes[self.obj_name])
                    self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.blue_heroes[self.obj_name], True)
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
            else:
                if self.red_heroes[self.obj_name] == 0:
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                    self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.hero_dialog.selector.selected_id, False)
                else:
                    self.hero_dialog.selector.unavailable_hero_ids.remove(self.red_heroes[self.obj_name])
                    self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.red_heroes[self.obj_name], True)
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
            print(f'unvail: {self.hero_dialog.selector.unavailable_hero_ids}')

            self.qlabel_to_update = None
            # update the radar chart
            new_blue_win_attr = self.set_radar_data(self.blue_heroes)
            new_red_win_attr = self.set_radar_data(self.red_heroes)
            self.blue_win_attr.update_graph(new_blue_win_attr, team_label='Team Blue')
            self.red_win_attr.update_graph(new_red_win_attr, team_label='Team Red')
            self.radar_canvas.draw()

            # update diverging h_chart
            new_blue_data = self.set_diverging_data(self.blue_heroes)
            new_red_data = self.set_diverging_data(self.red_heroes)
            self.head_to_head_attr.update_graph(new_blue_data, new_red_data)
            self.diverging_canvas.draw()

            #update win rate chart (h_chart)
            if self.combined_hero_dict[self.obj_name] != self.selected_hero:
                if self.selected_hero is not None:
                    if self.curr_selected_qlabel.objectName().startswith("blue"):
                        ally_wr, enemy_wr, ally_names, enemy_names = self.set_winrate_data(self.selected_hero, self.blue_heroes, self.red_heroes)
                        self.wr_chart.update_graph(ally_wr, enemy_wr, ally_names, enemy_names, get_name(self.selected_hero, self.hero_names), side='blue')
                    else:
                        ally_wr, enemy_wr, ally_names, enemy_names = self.set_winrate_data(self.selected_hero, self.red_heroes, self.blue_heroes)
                        self.wr_chart.update_graph(ally_wr, enemy_wr, ally_names, enemy_names, get_name(self.selected_hero, self.hero_names), side='red')
                self.h_charts_canvas.draw()

            self.hero_dialog.selector.selected_id = None
            self.qlabel_to_update = None

        else:
            return
            
    def set_highlight(self, radius):
        highlight_color = QColor(85, 255, 127)
        highlight_radius = radius / 2
        circular_style = f"border-radius: {highlight_radius}px; border: 3px solid {highlight_color.name()};"
        if self.picker_button_active:
            if self.selected_hero is not None and self.combined_hero_dict[self.obj_name] != 0:
                if self.prev_selected_qlbel is not None and self.curr_selected_qlabel != self.prev_selected_qlbel:
                    self.prev_selected_qlbel.setStyleSheet("") # If there's a previously selected qlabel, clear
                self.curr_selected_qlabel.setStyleSheet(circular_style)
        else:
            if self.prev_qlabel is not None and self.qlabel_to_update != self.prev_qlabel:
                self.prev_qlabel.setStyleSheet("image: url(:/icons/icons/plus-circle.svg);") # return to plus icon when clicking other qlabel
            self.qlabel_to_update.setStyleSheet(circular_style + "image: url(:/icons/icons/plus-circle.svg);")

    def picker_button_clicked(self):
        if any(self.combined_hero_dict.values()) != 0:
            if self.picker_button_active == False:
                self.picker_button_active = True
                highlight_color = QColor(85, 255, 127)
                highlight_radius = 23 
                self.picker_btn.setFixedSize(46, 46)
                circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
                self.picker_btn.setStyleSheet(circular_style + QSS)
                # Remove recent highlight from the hero selector dialog if there is any
                if self.qlabel_to_update is not None: 
                    key = self.qlabel_to_update.objectName()
                    if self.combined_hero_dict[key] != 0:
                        self.qlabel_to_update.setStyleSheet("") # Remove the highlight if highligted qlabel has an image
                    else:
                        self.qlabel_to_update.setStyleSheet("image: url(:/icons/icons/plus-circle.svg);") # Remove the highlight if highligted qlabel has no image and return the plus icon
            else:
                self.picker_btn.setFixedSize(46, 46)
                self.picker_btn.setStyleSheet(QSS)
                self.picker_button_active = False
                if self.curr_selected_qlabel is not None:
                    self.curr_selected_qlabel.setStyleSheet("")
    
    def update_single_hero(self):
        ###################### update ui elements ###################
        # update the roles icon
        self.update_role_pix(self.selected_hero)
        #update the image on the right
        self.hero_icon.setStyleSheet("")
        image_path = get_icon(self.selected_hero)
        pixmap = QPixmap(image_path)
        round_pix = rounded_pixmap(pixmap, 99, 4)
        # Get the size of the QLabel and scale the pixmap to fit
        label_size = self.hero_icon.size()
        scaled_pixmap = round_pix.scaled(label_size - QtCore.QSize(4, 4) , Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.hero_icon.setPixmap(scaled_pixmap)
        self.hero_icon.setFixedSize(label_size)
        self.hero_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.curr_selected_qlabel.objectName().startswith("blue"):
            self.hero_icon.setStyleSheet("border-radius: 30px; border: 2px solid; border-color:rgb(255, 255, 255);")
            # update and set the color for the pie chart
            blue_rgba = (85 / 255, 170 / 255, 255 / 255)
            self.hero_wr.update_graph(self.selected_hero, 0, 3,blue_rgba)
            self.hero_pr.update_graph(self.selected_hero, 1, 4, blue_rgba)
            self.hero_br.update_graph(self.selected_hero, 2, 5, blue_rgba)
            self.single_hero_attr.update_graph(self.selected_hero, get_name(self.selected_hero, self.hero_names), team_color=blue_rgba)

            # update the hero name
            self.hero_name.setText(get_name(self.selected_hero, self.hero_names)) # Set the name on the qlabel
            self.hero_name.setStyleSheet("font-size: 20pt; font-weight: bold; color: rgb(85, 170, 255);")
        else:
            self.hero_icon.setStyleSheet("border-radius: 30px; border: 2px solid; border-color:rgb(255, 255, 255);")
            # update and set the color for the pie chart
            red_gba = (255 / 255, 68 / 255, 62 / 255)
            self.hero_wr.update_graph(self.selected_hero, 0, 3, red_gba)
            self.hero_pr.update_graph(self.selected_hero, 1, 4, red_gba)
            self.hero_br.update_graph(self.selected_hero, 2, 5, red_gba)
            self.single_hero_attr.update_graph(self.selected_hero, get_name(self.selected_hero, self.hero_names), team_color=red_gba)

            # update the hero name
            self.hero_name.setText(get_name(self.selected_hero, self.hero_names)) # Set the name on the qlabel
            self.hero_name.setStyleSheet("font-size: 20pt; font-weight: bold; color: rgb(255, 68, 62);")

        #update win rate chart (h_chart)
        if self.curr_selected_qlabel.objectName().startswith("blue"):
            ally_wr, enemy_wr, ally_names, enemy_names = self.set_winrate_data(self.selected_hero, self.blue_heroes, self.red_heroes)
            self.wr_chart.update_graph(ally_wr, enemy_wr, ally_names, enemy_names, get_name(self.selected_hero, self.hero_names), side='blue')
        else:
            ally_wr, enemy_wr, ally_names, enemy_names = self.set_winrate_data(self.selected_hero, self.red_heroes, self.blue_heroes)
            self.wr_chart.update_graph(ally_wr, enemy_wr, ally_names, enemy_names, get_name(self.selected_hero, self.hero_names), side='red')

        self.h_charts_canvas.draw()
        self.pie_canvas.draw()

    def create_all_charts(self):
        self.radar_canvas, self.blue_win_attr, self.red_win_attr = self.crete_radar_chart()
        self.h_charts_canvas, self.single_hero_attr, self.wr_chart = self.create_horizontal_stats()

        self.diverging_canvas, self.head_to_head_attr = self.create_diverging_stats()

        self.pie_canvas, self.hero_wr, self.hero_pr, self.hero_br = self.create_single_hero_stats(self.extract_stats(self.hero_data))

    def crete_radar_chart(self):  # radar chart
        # Canvas for the graphs
        fig = Figure(figsize=(4, 4))
        canvas = FigureCanvas(fig)
        self.radar_layout.addWidget(canvas)
        #fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.1, hspace=0.45) 

        axs = fig.subplots(1, 2)
        fig.patch.set_visible(False)

        blue_color = (85 / 255, 170 / 255, 255 / 255)  # Blue
        red_color = (255 / 255, 68 / 255, 62 / 255)     # Red

        # Create instances of the graphs and pass the subplots
        blue_win_attr = TeamWinAttr(axs[0], pos_x=1, fig=fig, team_color=blue_color, team_label='Blue Team')
        red_win_attr = TeamWinAttr(axs[1], pos_x=2, fig=fig, team_color=red_color, team_label='Team Red')
        
        for i, ax in enumerate(axs.flatten()):
            ax.set_frame_on(False)
            if i in [0, 1]:
                ax.set_yticklabels([])
                ax.set_xticklabels([])
                ax.set_yticks([])
                ax.set_xticks([])
        fig.tight_layout()
        return canvas, blue_win_attr, red_win_attr
    
    def create_horizontal_stats(self):  # line up winrate and single hero attr 
        # Create a Matplotlib figure and canvas
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6))
        canvas = FigureCanvas(fig)
        self.attr_layout.addWidget(canvas)

        # Adjust the subplots' position and spacing
        fig.subplots_adjust(left=0.2, right=0.95, hspace=0.4)  # adjust values

        # Create instances of SingleHeroAttr and LineUpWinrate, passing the axes
        wr_chart = LineUpWinrate(ax1)
        single_hero_attr = SingleHeroAttr(ax2, self.extract_attr(self.hero_data))

        return canvas, single_hero_attr, wr_chart


    def create_diverging_stats(self):  # head to head attr
        fig, ax = plt.subplots(figsize=(8, 8))
        canvas = FigureCanvas(fig)
        self.diverging_layout.addWidget(canvas)

        # Create an instance of HeadToHeadAttr, passing the Matplotlib axes
        head_to_head_attr = HeadToHeadAttr(ax)

        return canvas, head_to_head_attr
    
    def create_single_hero_stats(self, hero_stats): # pie charts
        # Create a Matplotlib figure and canvas for the three donut charts
        fig = Figure(figsize=(7,7))
        axs = fig.subplots(1, 3)
        canvas = FigureCanvas(fig)
        self.pie_layout.addWidget(canvas)
        fig.subplots_adjust(top=0.95, bottom=0.3, wspace=0.5 , hspace=0.4)

        fig.patch.set_visible(False)

        # Create instances of SingleHeroStats and pass the subplots and hero_data for each instance
        hero_prx = SingleHeroStats(axs[0], hero_stats, 'pick')
        hero_banx = SingleHeroStats(axs[1], hero_stats, 'ban')
        hero_winx = SingleHeroStats(axs[2], hero_stats, 'win')

        for ax in axs.flatten():
            ax.set_frame_on(False)
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.set_yticks([])
            ax.set_xticks([])
        return canvas, hero_prx, hero_banx, hero_winx

    def get_average(self, list_x, len_x):
        if len(list_x) == 0:
            return 0
        total = sum(x for x in list_x)
        return total/len_x

    def load_attr(self, path):
        hero_data = []
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hero_data.append([int(row['Burst']), int(row['DPS']), int(row['Scaling']), 
                                int(row['Neutrals']), int(row['Push']), int(row['Clear']),
                                int(row['CC']), int(row['Sustain']), int(row['Vision']), int(row['Mobility']), 
                                float(eval(row['Pick Rate'])), float(eval(row['Ban Rate'])), float(eval(row['Win Rate'])), 
                                int(row['Pick']), int(row['Ban']), int(row['Win'])])
        return hero_data
    
    def extract_attr(self, hero_data):
        hero_stats = []
        for row in hero_data:
            first_tean_values = row[:10]
            hero_stats.append(first_tean_values)
        return hero_stats
    
    def extract_stats(self, hero_data):
        hero_stats = []
        for row in hero_data:
            last_six_values = row[10:16]
            rounded_values = [round(value * 100, 2) if isinstance(value, float) else value for value in last_six_values]
            hero_stats.append(rounded_values)
        return hero_stats
    
    def set_radar_data(self, hero_dict):
        hero_burst, hero_dps, hero_scaling, hero_neutrals, hero_push, hero_clear, hero_cc, hero_sustain, hero_vision, hero_mobility = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        objectives, early_game, late_game, team_fight, sustain, map_control = [], [], [], [], [], []

        len_count = 5
        team_data = []
        if isinstance(hero_dict, dict):
            for val in hero_dict.values():
                if val != 0:
                    hero_id = int(val) - 1
                    objectives.append((self.hero_data[hero_id][hero_neutrals] + self.hero_data[hero_id][hero_push]) / 2)
                    late_game.append((self.hero_data[hero_id][hero_scaling] + self.hero_data[hero_id][hero_dps]) / 2)
                    early_game.append((self.hero_data[hero_id][hero_burst] + self.hero_data[hero_id][hero_cc]) / 2)
                    team_fight.append((self.hero_data[hero_id][hero_burst] + self.hero_data[hero_id][hero_cc]) / 2)
                    map_control.append((self.hero_data[hero_id][hero_mobility] + self.hero_data[hero_id][hero_clear]) / 2)
                    sustain.append((self.hero_data[hero_id][hero_sustain]))

            team_data = [self.get_average(objectives, len_count), self.get_average(early_game, len_count), 
                         self.get_average(late_game, len_count), self.get_average(team_fight, len_count), 
                         self.get_average(map_control, len_count), self.get_average(sustain, len_count)]
        return team_data
    
    def set_diverging_data(self, hero_dict):
        hero_burst, hero_dps, hero_scaling, hero_neutrals, hero_push, hero_clear, hero_cc, hero_sustain, hero_vision, hero_mobility = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        team_burst, team_dps, team_scaling, team_neutrals, team_push, team_clear, team_cc, team_sustain, team_vision, team_mobility = [], [], [], [], [], [], [], [], [], []

        team_data = []
        len_count = 5

        if isinstance(hero_dict, dict):
            for val in hero_dict.values():
                if val != 0:
                    hero_id = int(val) - 1
                    team_burst.append(self.hero_data[hero_id][hero_burst])
                    team_dps.append(self.hero_data[hero_id][hero_dps])
                    team_scaling.append(self.hero_data[hero_id][hero_scaling])
                    team_neutrals.append(self.hero_data[hero_id][hero_neutrals])
                    team_push.append(self.hero_data[hero_id][hero_push])
                    team_clear.append(self.hero_data[hero_id][hero_clear])
                    team_cc.append(self.hero_data[hero_id][hero_cc])
                    team_sustain.append(self.hero_data[hero_id][hero_sustain])
                    team_vision.append(self.hero_data[hero_id][hero_vision])
                    team_mobility.append(self.hero_data[hero_id][hero_mobility])

        team_data = [self.get_average(team_burst, len_count), self.get_average(team_dps, len_count), 
                     self.get_average(team_scaling, len_count), self.get_average(team_neutrals, len_count), 
                     self.get_average(team_push, len_count), self.get_average(team_clear, len_count), 
                     self.get_average(team_cc, len_count), self.get_average(team_sustain, len_count), 
                     self.get_average(team_vision, len_count), self.get_average(team_mobility, len_count)]
        
        return team_data

    def get_winrate(self, current_hero, hero_dict, is_ally):  # get winrate for each ally and enemy (H_chart)
        team_wr = []
        for hero in list(hero_dict.values()):
                if hero == 0:
                    team_wr.append(0)
                else:
                    if int(hero) != current_hero:
                        cell_str = self.df.loc[current_hero, str(hero)]
                        cell_list = ast.literal_eval(cell_str)
                        if is_ally:
                            if cell_list[0] != 0 or cell_list[1] != 0:
                                team_wr.append((cell_list[0] / (cell_list[0] + cell_list[1]) * 100))
                            else:
                                team_wr.append(0)
                        else:
                            if cell_list[2] != 0 or cell_list[3] != 0:
                                team_wr.append((cell_list[2] / (cell_list[2] + cell_list[3]) * 100))
                            else:
                                team_wr.append(0)
        return team_wr

    def set_winrate_data(self, curr_hero, team_dict, enemy_dict):  # for h_chart / line up winrate not for pie chart
        ally_wr = []
        enemy_wr = []

        ally_names = []
        enemy_names = []

        if curr_hero != 0:
            ally_wr = self.get_winrate(curr_hero, team_dict, True)
            enemy_wr = self.get_winrate(curr_hero, enemy_dict, False)
        else:
            ally_wr = [0] * 4
            enemy_wr = [0] * 5
        
        if curr_hero != 0:
            for hero in list(team_dict.values()):
                if hero != curr_hero and hero != 0:
                    ally_names.append(get_name(hero, self.hero_names))
                elif hero == 0:
                    ally_names.append(f'Hero {len(ally_names) + 1}')

        if curr_hero != 0:
            for hero in list(enemy_dict.values()):
                if hero != curr_hero and hero != 0:
                    enemy_names.append(get_name(hero, self.hero_names))
                elif hero == 0:
                    enemy_names.append(f'Hero {len(enemy_names) + 5}')
        return ally_wr, enemy_wr, ally_names, enemy_names
    
    def update_role_pix(self, hero_id):
        
        roles = []
        if hero_id != 0:
            roles = list(self.hero_roles.values())[hero_id - 1]

        if len(roles) > 1:
            self.role1.setPixmap(self.get_pix(roles[0]))
            self.role2.setPixmap(self.get_pix(roles[1]))
            self.role2.setVisible(True)
        else:
            self.role2.setVisible(False)
            self.role1.setPixmap(self.get_pix(roles[0]))

    def get_pix(self, role):
            if role == 'Gold':
                pix_map = QPixmap("images/hero_roles/gold_white.png")
            elif role == 'Jungler':
                pix_map = QPixmap("images/hero_roles/jungle_white.png")
            elif role == 'EXP':
                pix_map = QPixmap("images/hero_roles/exp_white.png")
            elif role == 'Mid':
                pix_map = QPixmap("images/hero_roles//mid_white.png")
            elif role == 'Roamer':
                pix_map = QPixmap("images/hero_roles/roam_white.png")   
            return pix_map
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickDraftWindow()
    window.show()

    sys.exit(app.exec())
    