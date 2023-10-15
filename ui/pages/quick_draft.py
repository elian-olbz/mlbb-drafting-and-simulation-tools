from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource, QEvent
from PyQt6 import uic
import os
import pandas as pd
import ast
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from run_draft_logic.utils import get_name, get_icon
from functools import partial
from ui.rsc_rc import *
from ui.misc.titlebar import*
from ui.dialogs.hero_selector_tab import *
from ui.dialogs.reset_heroes import*
from ui.misc.graphs import *

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

PICKER_QSS = "QPushButton{text-align:center; border-radius: 23px; padding: 5px, 5px;} QPushButton:hover { background-color: #23272e;}\
                QPushButton:pressed {background-color: rgb(62, 69, 82); color: rgb(255, 255, 255);}"
MINUS_QSS = "QPushButton{text-align:center; border-radius: 5px; padding: 5px, 5px;} QPushButton:hover { background-color: #23272e;}\
                 QPushButton:pressed {background-color: rgb(62, 69, 82); color: rgb(255, 255, 255);}"
BLUE_COLOR = "#2e6eea"
RED_COLOR = "#ed0d3a"


EMPTY_HERO_QSS = "image: url(:/icons/icons/plus-circle.svg);"

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

        self.qlabel_to_clear = None # Used when minus button is active
        self.is_minus_btn_active = False

        self.hero_names = None
        self.hero_roles = None
        self.df = None
        self.hero_data = None
        
        self.selected_hero = None
        self.is_blue = True
        self.picker_button_active = False

        self.title_bar = TitleBar(self)
        self.hero_dialog = HeroSelectorDialog()
        ui_path = os.path.join(script_dir,  "quick_draft.ui")

        uic.loadUi(ui_path, self)

        self.hero_dialog.select_btn.clicked.connect(self.select_button_click)
        self.hero_dialog.exit_button.clicked.connect(self.on_dialog_exit)
        self.picker_btn.clicked.connect(self.picker_button_clicked)
        self.minus_btn.clicked.connect(self.minus_btn_clicked)

        self.labels = {}

        self.label_names = list(self.blue_heroes.keys()) + list(self.red_heroes.keys())

        # Find the child qlabels to properly connect an event filter
        for name in self.label_names:
            label = self.findChild(QLabel, name)
            if label:
                self.labels[name] = label
                label.installEventFilter(self)

        self.reset_dialog = ResetDialog()
        self.reset_btn.clicked.connect(self.show_reset_dialog)
        self.reset_dialog.okay_btn.clicked.connect(self.reset_all)
        self.reset_dialog.cancel_btn.clicked.connect(self.close_reset_dialog)

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
            self.qlabel_to_update.setStyleSheet(EMPTY_HERO_QSS)


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
                        if self.obj_name.startswith("blue"):
                            self.is_blue = True
                        else:
                            self.is_blue = False
                        self.update_single_hero()
                        self.set_highlight(25)
                elif self.is_minus_btn_active:
                    if self.combined_hero_dict[self.obj_name] != 0:
                        self.qlabel_to_clear = obj
                        self.remove_single_hero()
                else:
                    if self.obj_name in self.labels:
                        self.set_highlight(25)
                        self.show_dial()
        self.prev_selected_qlbel = self.curr_selected_qlabel
        self.prev_qlabel = self.qlabel_to_update    
        return super().eventFilter(obj, event)
    
    def show_reset_dialog(self):
        if len(self.hero_dialog.selector.unavailable_hero_ids) > 0:
            self.reset_dialog.show()
        else:
            return
    def close_reset_dialog(self):
        self.reset_dialog.close()

    def show_dial(self):
        self.hero_dialog.show()  

    def on_dialog_exit(self):
        if self.picker_button_active == False and self.qlabel_to_update is not None:
            self.qlabel_to_update.setStyleSheet(EMPTY_HERO_QSS)

    def merge_heroes_dict(self, dict1, dict2):
        res = {**dict1, **dict2}
        return res
    
    # when "Select" button from the selector is clicked
    def select_button_click(self):
        if self.hero_dialog.selector.selected_id is not None and self.qlabel_to_update is not None:
            self.qlabel_to_update.setStyleSheet("")
            self.hero_dialog.hide()
            self.hero_dialog.selector.disp_selected_image(self.hero_dialog.selector.selected_id, self.qlabel_to_update)
            if self.hero_dialog.selector.current_clicked_label is not None:
                self.hero_dialog.selector.current_clicked_label.setStyleSheet("")

            if str(self.obj_name).startswith("blue"):
                if self.blue_heroes[self.obj_name] == 0:
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                    self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.hero_dialog.selector.selected_id, False) 
                else:
                    if self.blue_heroes[self.obj_name] in self.hero_dialog.selector.unavailable_hero_ids:
                        self.hero_dialog.selector.unavailable_hero_ids.remove(self.blue_heroes[self.obj_name])
                        self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.blue_heroes[self.obj_name], True)
                        self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
            else:
                if self.red_heroes[self.obj_name] == 0:
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                    self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.hero_dialog.selector.selected_id, False)
                else:
                    if self.red_heroes[self.obj_name] in self.hero_dialog.selector.unavailable_hero_ids:
                        self.hero_dialog.selector.unavailable_hero_ids.remove(self.red_heroes[self.obj_name])
                        self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, self.red_heroes[self.obj_name], True)
                        self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id

            self.qlabel_to_update = None
            self.update_left_charts_data()

            self.hero_dialog.selector.selected_id = None
            self.qlabel_to_update = None

        else:
            return
        self.revalidate_selected_hero()
     
    def revalidate_selected_hero(self): 
        if self.selected_hero is not None:
            if self.selected_hero in self.blue_heroes.values() or self.selected_hero in self.red_heroes.values():
                self.update_wr_data()
            else:
                self.clear_right_charts()
                self.reset_hero_info()
                self.selected_hero = None
            self.h_charts_canvas.draw()
        else:
            return
        
    def update_left_charts_data(self):
        # update the radar chart
        new_blue_win_attr = self.set_radar_data(self.blue_heroes)
        new_red_win_attr = self.set_radar_data(self.red_heroes)
        self.blue_win_attr.update_graph(new_blue_win_attr)
        self.red_win_attr.update_graph(new_red_win_attr)
        self.radar_canvas.draw()

        # update diverging h_chart
        new_blue_data = self.set_diverging_data(self.blue_heroes)
        new_red_data = self.set_diverging_data(self.red_heroes)
        self.head_to_head_attr.update_graph(new_blue_data, new_red_data)
        self.diverging_canvas.draw()

    def update_wr_data(self):  # this is for the H_chart wr not the pie
        if self.is_blue:
            ally_wr, enemy_wr, ally_tg, enemy_tg, ally_names, enemy_names  = self.set_winrate_data(self.selected_hero, self.blue_heroes, self.red_heroes)
            self.wr_chart.update_graph(ally_wr, enemy_wr, ally_tg, enemy_tg, ally_names, enemy_names, get_name(self.selected_hero, self.hero_names), side='blue')
        else:
            ally_wr, enemy_wr, ally_tg, enemy_tg, ally_names, enemy_names = self.set_winrate_data(self.selected_hero, self.red_heroes, self.blue_heroes)
            self.wr_chart.update_graph(ally_wr, enemy_wr, ally_tg, enemy_tg, ally_names, enemy_names, get_name(self.selected_hero, self.hero_names), side='red')

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
                self.prev_qlabel.setStyleSheet(EMPTY_HERO_QSS) # return to plus icon when clicking other qlabel
            self.qlabel_to_update.setStyleSheet(circular_style + EMPTY_HERO_QSS)
    
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

        icon_style = "border-radius: 30px; border: 2px solid; border-color:rgb(255, 255, 255);"

        if self.is_blue:
            self.hero_icon.setStyleSheet(icon_style)
            # update and set the color for the pie chart
            self.hero_wr.update_graph(self.selected_hero, 0, 3,BLUE_COLOR)
            self.hero_pr.update_graph(self.selected_hero, 1, 4, BLUE_COLOR)
            self.hero_br.update_graph(self.selected_hero, 2, 5, BLUE_COLOR)
            self.single_hero_attr.update_graph(self.selected_hero, get_name(self.selected_hero, self.hero_names), team_color=BLUE_COLOR)

            # update the hero name
            self.hero_name.setText(get_name(self.selected_hero, self.hero_names)) # Set the name on the qlabel
            self.hero_name.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {BLUE_COLOR};")
        else:
            self.hero_icon.setStyleSheet(icon_style)
            # update and set the color for the pie chart
            self.hero_wr.update_graph(self.selected_hero, 0, 3, RED_COLOR)
            self.hero_pr.update_graph(self.selected_hero, 1, 4, RED_COLOR)
            self.hero_br.update_graph(self.selected_hero, 2, 5, RED_COLOR)
            self.single_hero_attr.update_graph(self.selected_hero, get_name(self.selected_hero, self.hero_names), team_color=RED_COLOR)

            # update the hero name
            self.hero_name.setText(get_name(self.selected_hero, self.hero_names)) # Set the name on the qlabel
            self.hero_name.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {RED_COLOR};")

        #update win rate chart (h_chart)
        if self.selected_hero is not None:
            self.update_wr_data()
            self.h_charts_canvas.draw()
            self.pie_canvas.draw()
        else:
            return

    def create_all_charts(self):
        self.radar_canvas, self.blue_win_attr, self.red_win_attr = self.crete_radar_chart()
        self.h_charts_canvas, self.single_hero_attr, self.wr_chart = self.create_horizontal_stats()

        self.diverging_canvas, self.head_to_head_attr = self.create_diverging_stats()

        self.pie_canvas, self.hero_wr, self.hero_pr, self.hero_br = self.create_single_hero_stats(self.extract_stats(self.hero_data))

    def crete_radar_chart(self):  # radar chart
        # Canvas for the graphs
        fig = Figure(figsize=(5, 5))
        canvas = FigureCanvas(fig)
        self.radar_layout.addWidget(canvas)
        fig.subplots_adjust(top=0.89, bottom=0.2, left=0.8, right=0.9)

        axs = fig.subplots(1, 2)
        fig.patch.set_visible(False)

        # Create instances of the graphs and pass the subplots
        blue_win_attr = TeamWinAttr(axs[0], pos_x=1, fig=fig, team_color=BLUE_COLOR, team_label='Blue Team')
        red_win_attr = TeamWinAttr(axs[1], pos_x=2, fig=fig, team_color=RED_COLOR, team_label='Team Red')
        
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
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7))
        fig.patch.set_visible(False)
        canvas = FigureCanvas(fig)
        self.attr_layout.addWidget(canvas)

        # Adjust the subplots' position and spacing
        fig.subplots_adjust(left=0.235, right=0.9, hspace=0.4)  # adjust values

        # Create instances of SingleHeroAttr and LineUpWinrate, passing the axes
        wr_chart = LineUpWinrate(ax1)

        single_hero_attr = SingleHeroAttr(ax2, self.extract_attr(self.hero_data))

        return canvas, single_hero_attr, wr_chart


    def create_diverging_stats(self):  # head to head attr
        fig, ax = plt.subplots(figsize=(6, 8))
        fig.patch.set_visible(False)
        canvas = FigureCanvas(fig)
        self.diverging_layout.addWidget(canvas)
        fig.subplots_adjust(top=0.9, bottom=0.2, left=0.15, right=0.89)

        # Create an instance of HeadToHeadAttr, passing the Matplotlib axes
        head_to_head_attr = HeadToHeadAttr(ax)

        return canvas, head_to_head_attr
    
    def create_single_hero_stats(self, hero_stats): # pie charts
        # Create a Matplotlib figure and canvas for the three donut charts
        fig = Figure(figsize=(7,7))
        axs = fig.subplots(1, 3)
        fig.patch.set_visible(False)
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
    
    def extract_attr(self, hero_data):
        hero_stats = []
        for row in hero_data:
            values = row[6:13]
            hero_stats.append(values)
        return hero_stats
    
    def extract_stats(self, hero_data):
        hero_stats = []
        for row in hero_data:
            last_six_values = row[13:19]
            rounded_values = [round(value * 100, 2) if isinstance(value, float) else value for value in last_six_values]
            hero_stats.append(rounded_values)
        return hero_stats
    
    def set_radar_data(self, hero_dict):
        em, tf,  b, lg, i, ds   =  0, 1, 2, 3, 4, 5
        early_to_mid, team_fight, burst,  late_game, iso, dot_sutain = [], [], [], [], [], []

        len_count = 5
        team_data = []
        if isinstance(hero_dict, dict):
            for val in hero_dict.values():
                if val != 0:
                    hero_id = int(val) - 1
                    early_to_mid.append(self.hero_data[hero_id][em])
                    team_fight.append(self.hero_data[hero_id][tf])
                    burst.append(self.hero_data[hero_id][b])
                    late_game.append(self.hero_data[hero_id][lg])
                    iso.append(self.hero_data[hero_id][i])
                    dot_sutain.append(self.hero_data[hero_id][ds])

            team_data = [self.get_average(early_to_mid, len_count), self.get_average(team_fight, len_count), 
                         self.get_average(burst, len_count), self.get_average(late_game, len_count), 
                         self.get_average(iso, len_count), self.get_average(dot_sutain, len_count)]
        return team_data
    
    def set_diverging_data(self, hero_dict):
        wc, hd, v, cc, o, p, u = 6, 7, 8, 9, 10, 11, 12
        wave_clear, hero_dps, vision, crowd_control, objective, push, utility = [], [], [], [], [], [], []

        team_data = []
        len_count = 5

        if isinstance(hero_dict, dict):
            for val in hero_dict.values():
                if val != 0:
                    hero_id = int(val) - 1
                    wave_clear.append(self.hero_data[hero_id][wc])
                    hero_dps.append(self.hero_data[hero_id][hd])
                    vision.append(self.hero_data[hero_id][v])
                    crowd_control.append(self.hero_data[hero_id][cc])
                    objective.append(self.hero_data[hero_id][o])
                    push.append(self.hero_data[hero_id][p])
                    utility.append(self.hero_data[hero_id][u])
        
        team_data = [self.get_average(wave_clear, len_count), self.get_average(hero_dps, len_count), 
                     self.get_average(vision, len_count), self.get_average(crowd_control, len_count), 
                     self.get_average(objective, len_count), self.get_average(push, len_count), 
                     self.get_average(utility, len_count)]
        
        return team_data

    def get_winrate(self, current_hero, hero_dict, is_ally):  # get winrate for each ally and enemy (H_chart)
        team_wr = []
        total_games = []
        for hero in list(hero_dict.values()):
                if hero == 0:
                    team_wr.append(0)
                    total_games.append(0)
                else:
                    if int(hero) != current_hero:
                        cell_str = self.df.loc[current_hero, str(hero)]
                        cell_list = ast.literal_eval(cell_str)
                        if is_ally:
                            if cell_list[0] != 0 or cell_list[1] != 0:
                                team_wr.append((cell_list[0] / (cell_list[0] + cell_list[1]) * 100))
                                total_games.append(cell_list[0] + cell_list[1])
                            else:
                                team_wr.append(0)
                                total_games.append(0)
                        else:
                            if cell_list[2] != 0 or cell_list[3] != 0:
                                team_wr.append((cell_list[2] / (cell_list[2] + cell_list[3]) * 100))
                                total_games.append(cell_list[2] + cell_list[3])
                            else:
                                team_wr.append(0)
                                total_games.append(0)
        return team_wr, total_games

    def set_winrate_data(self, curr_hero, team_dict, enemy_dict):  # for h_chart / line up winrate not for pie chart
        ally_wr = []
        enemy_wr = []

        ally_names = []
        enemy_names = []

        ally_total_games = []
        enemy_total_games = []

        if curr_hero != 0:
            ally_wr, ally_total_games = self.get_winrate(curr_hero, team_dict, True)
            enemy_wr, enemy_total_games = self.get_winrate(curr_hero, enemy_dict, False)
        else:
            ally_wr = [0] * 4
            enemy_wr = [0] * 5

            ally_total_games = [0] * 4
            enemy_total_games = [0] * 5
        
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
        return ally_wr, enemy_wr, ally_total_games, enemy_total_games, ally_names, enemy_names
    
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

    def picker_button_clicked(self):
        if any(self.combined_hero_dict.values()) != 0:
            self.clear_minus_styles()
            self.clear_recent_qlabels()

            if self.picker_button_active == False:
                self.picker_button_active = True

                highlight_color = QColor(85, 255, 127)
                highlight_radius = 23 
                self.picker_btn.setFixedSize(46, 46)
                circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
                self.picker_btn.setStyleSheet(circular_style + PICKER_QSS)

                # Remove recent highlight from the hero selector dialog if there is any
                if self.qlabel_to_update is not None:  # check if there is a previously higlighted empty qlabel to update
                    key = self.qlabel_to_update.objectName()
                    if self.combined_hero_dict[key] != 0:
                        self.qlabel_to_update.setStyleSheet("") # Remove the highlight if highligted qlabel has an image
                    else:
                        self.qlabel_to_update.setStyleSheet(EMPTY_HERO_QSS) # Remove the highlight if highligted qlabel has no image and return the plus icon
            else:
                self.picker_btn.setFixedSize(46, 46)
                self.picker_btn.setStyleSheet(PICKER_QSS)
                self.picker_button_active = False
                if self.curr_selected_qlabel is not None:
                    self.curr_selected_qlabel.setStyleSheet("")
        else:
            return
        
    def minus_btn_clicked(self):
        if any(self.combined_hero_dict.values()) != 0:
            self.clear_picker_styles()

            if self.is_minus_btn_active == False:
                self.is_minus_btn_active = True

                highlight_color = QColor(85, 255, 127)
                highlight_radius = 5
                self.minus_btn.setFixedSize(30, 30)
                circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
                self.minus_btn.setStyleSheet(circular_style + MINUS_QSS)
            
            else:
                self.minus_btn.setFixedSize(30, 30)
                self.minus_btn.setStyleSheet(MINUS_QSS)
                self.is_minus_btn_active = False
        else:
            return

    def remove_single_hero(self):
        if self.combined_hero_dict[self.obj_name] != 0:
            hero_id = self.combined_hero_dict[self.obj_name]

            if hero_id in self.hero_dialog.selector.unavailable_hero_ids:
                self.hero_dialog.selector.unavailable_hero_ids.remove(hero_id)

            if len(self.hero_dialog.selector.unavailable_hero_ids) > 0:
                self.update_chart_on_minus()
            else:
                self.clear_all_charts()
                self.reset_hero_info()
                self.minus_btn.setStyleSheet(MINUS_QSS)
                self.is_minus_btn_active = False

            self.combined_hero_dict[self.obj_name] = 0
            if self.obj_name.startswith("blue"):
                self.blue_heroes[self.obj_name] = 0
            elif self.obj_name.startswith("red"):
                self.red_heroes[self.obj_name] = 0

            self.hero_dialog.selector.selected_id = hero_id
            self.hero_dialog.selector.update_labels_in_tabs(self.hero_dialog, hero_id, False)

            # reset the qlabel stylesheet to empty 
            clear_pix = QPixmap(QSize(self.qlabel_to_clear.size()))
            clear_pix.fill(Qt.GlobalColor.transparent)
            self.qlabel_to_clear.setPixmap(clear_pix)
            self.qlabel_to_clear.setStyleSheet(EMPTY_HERO_QSS)
        self.revalidate_selected_hero()
        self.update_left_charts_data()

    def reset_all(self):
        self.clear_recent_qlabels()
        self.clear_picker_styles()
        self.clear_minus_styles()

        for name in self.label_names:
            label = self.findChild(QLabel, name)
            if label:
                clear_pix = QPixmap(QSize(label.size()))
                clear_pix.fill(Qt.GlobalColor.transparent)
                label.setPixmap(clear_pix)
                label.setStyleSheet(EMPTY_HERO_QSS)
        
        for  key in self.blue_heroes.keys():
            self.blue_heroes[key] = 0
        
        for key in self.red_heroes.keys():
            self.red_heroes[key] = 0

        for key in self.combined_hero_dict.keys():
            self.combined_hero_dict[key] = 0

        self.hero_dialog.selector.populate_tabs(self.hero_dialog, 60)
        self.hero_dialog.selector.unavailable_hero_ids = []
        self.hero_dialog.selector.selected_id = None
        self.combined_hero_dict 

        self.is_minus_btn_active = False
        self.picker_button_active = False
        self.close_reset_dialog()
        self.clear_all_charts()
        self.reset_hero_info()

    def reset_hero_info(self):
        empty_hero_icon = "image: url(:/icons/icons/question_mark.png); border-radius: 30px; border: 2px solid; border-color:rgb(255, 255, 255);"
        self.hero_name.setText("Select hero") # Set the name on the qlabel
        self.hero_name.setStyleSheet(f"font-size: 20pt; font-weight: bold; color: {BLUE_COLOR};")

        clear_pix = QPixmap(QSize(self.hero_icon.size()))
        clear_pix.fill(Qt.GlobalColor.transparent)
        self.hero_icon.setPixmap(clear_pix)
        self.hero_icon.setStyleSheet(empty_hero_icon)

        self.role2.setVisible(False)
        p = QPixmap("images/hero_roles/mlbb_icon.png")
        self.role1.setPixmap(p)

    def update_chart_on_minus(self):
        self.update_left_charts_data()
        if self.selected_hero is not None:
            if self.selected_hero in self.blue_heroes.values() or self.selected_hero in self.red_heroes.values():
                self.update_wr_data()
            else:
                self.clear_right_charts()
                self.reset_hero_info()
            self.h_charts_canvas.draw()
        else:
            return

    def clear_all_charts(self):
        self.clear_left_charts()
        self.clear_right_charts()

    def clear_left_charts(self):
        self.blue_win_attr.update_graph([0] * 6)
        self.red_win_attr.update_graph([0]*6)
        self.radar_canvas.draw()

        self.head_to_head_attr.update_graph([0]*7, [0]*7)
        self.diverging_canvas.draw()

    def clear_right_charts(self):
        self.single_hero_attr.init_chart()
        self.wr_chart.init_chart()
        self.h_charts_canvas.draw()

        self.hero_br.init_chart()
        self.hero_wr.init_chart()
        self.hero_pr.init_chart()
        self.pie_canvas.draw()

    def clear_picker_styles(self):
        if self.picker_button_active:
                # Just remove all previous highlight whether it's from when the pciker btn is active or not
                self.picker_btn.setStyleSheet(PICKER_QSS)
                self.picker_button_active = False
                if self.curr_selected_qlabel is not None:
                    self.curr_selected_qlabel.setStyleSheet("")

                # Remove recent highlight from the hero selector dialog if there is any
                if self.qlabel_to_update is not None:  # check if there is a previously higlighted empty qlabel to update
                    key = self.qlabel_to_update.objectName()
                    if self.combined_hero_dict[key] != 0:
                        self.qlabel_to_update.setStyleSheet("") # Remove the highlight if highligted qlabel has an image
                    else:
                        self.qlabel_to_update.setStyleSheet(EMPTY_HERO_QSS) # Remove the highlight if highligted qlabel has no image and return the plus icon

    def clear_recent_qlabels(self):
        if self.qlabel_to_update is not None:
            self.qlabel_to_update.setStyleSheet(EMPTY_HERO_QSS)
            self.qlabel_to_update = None
            
        if self.curr_selected_qlabel is not None:
            self.curr_selected_qlabel.setStyleSheet(EMPTY_HERO_QSS)
            self.curr_selected_qlabel = None

    def clear_minus_styles(self):
        if self.is_minus_btn_active:
                self.minus_btn.setStyleSheet(MINUS_QSS)
                self.is_minus_btn_active = False
                