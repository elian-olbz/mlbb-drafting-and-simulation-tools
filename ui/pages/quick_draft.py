from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QScrollArea, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QShortcut, QKeySequence, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QResource, QEvent
from PyQt6 import uic
import sys
import os
import pandas as pd
import ast
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from run_draft_logic.utils import load_names, get_name
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
        self.blue_heroes = {"blue_roam":0, "blue_mid":0, "blue_exp":0, "blue_jungle":0, "blue_gold":0}
        self.red_heroes = {"red_gold":0, "red_jungle":0, "red_exp":0, "red_mid":0, "red_roam":0}
        self.prev_qlabel = None

        self.hero_names = load_names('data/hero_map.csv')
        self.df = pd.read_csv('data/winrate.csv', index_col=0, header=0)
        self.hero_burst , self.hero_dps, self.hero_scaling, self.hero_neutrals, self.hero_push, self.hero_clear, self.hero_cc, self.hero_sustain, self.hero_vision, self.hero_mobility = self.load_attr_csv('data/attr.csv')

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
        self.radar_blue = RadarChart(self.axs[0, 0], pos_x=1, fig=self.fig, team_color='blue', team_label='Blue Team')
        self.diverging_team = DivergingChart(self.axs[0,1])
        self.radar_red = RadarChart(self.axs[0, 2], pos_x=3, fig=self.fig, team_color='red', team_label='Team Red')

        self.horizotal_indiv = HorizontalChart(self.axs[1, 0])
        self.diverging_indiv = DivergingChart(self.axs[1, 1])
        self.wr_chart = WinrateChart(self.axs[1, 2])

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
                if self.blue_heroes[self.obj_name] == 0:
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                else:
                    self.hero_dialog.selector.unavailable_hero_ids.remove(self.blue_heroes[self.obj_name])
                    self.blue_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
            else:
                if self.red_heroes[self.obj_name] == 0:
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id
                else:
                    self.hero_dialog.selector.unavailable_hero_ids.remove(self.red_heroes[self.obj_name])
                    self.red_heroes[self.obj_name] = self.hero_dialog.selector.selected_id

            print("Unavailable Heroes: {}".format(self.hero_dialog.selector.unavailable_hero_ids))
            print("blue heroes: {}\t\tred heroes: {}\n".format(list(self.blue_heroes.values()), list(self.red_heroes.values())))
            self.qlabel_to_update = None
            self.hero_dialog.selector.selected_id = None

            # update the radar chart
            self.radar_blue.team_data = self.set_radar_data(self.blue_heroes)
            self.radar_red.team_data = self.set_radar_data(self.red_heroes)
            self.radar_blue.update_graph(self.radar_blue.team_data, team_color='blue', team_label='Team Blue')
            self.radar_red.update_graph(self.radar_red.team_data, team_color='red', team_label='Team Red')

            ally_wr, enemy_wr = self.set_winrate_data(int(self.blue_heroes['blue_roam']), self.blue_heroes, self.red_heroes)
            self.wr_chart.update_graph(ally_wr, enemy_wr, str(self.blue_heroes['blue_roam']))
            self.canvas.draw()

    def set_highlight(self, radius):
        if self.prev_qlabel is not None and self.qlabel_to_update != self.prev_qlabel:
            self.prev_qlabel.setStyleSheet("image: url(:/icons/icons/plus-circle.svg);")

        highlight_color = QColor(69, 202, 255)  # Replace with the desired highlight color
        highlight_radius = radius / 2  # Adjust the radius as needed

        circular_style = f"border-radius: {highlight_radius}px; border: 2px solid {highlight_color.name()};"
        self.qlabel_to_update.setStyleSheet(circular_style + "image: url(:/icons/icons/plus-circle.svg);")

    def get_average(self, list_x, len_x):
        if len(list_x) == 0:
            return 0
        total = sum(x for x in list_x)
        return total/len_x
    
    def load_attr_csv(self, path):
        hero_burst = []
        hero_dps = []
        hero_scaling = []
        hero_neutrals = []
        hero_push = []
        hero_clear = []
        hero_cc = []
        hero_sustain = []
        hero_vision = []
        hero_mobility = []

        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                #hero_id = int(row['HeroID'])
                hero_burst.append(int(row['Burst']))
                hero_dps.append(int(row['DPS']))
                hero_scaling.append(int(row['Scaling']))
                hero_neutrals.append(int(row['Neutrals']))
                hero_push.append(int(row['Push']))
                hero_clear.append(int(row['Clear']))
                hero_cc.append(int(row['CC']))
                hero_sustain.append(int(row['Sustain']))
                hero_vision.append(int(row['Vision']))
                hero_mobility.append(int(row['Mobility']))

        return hero_burst , hero_dps, hero_scaling, hero_neutrals, hero_push, hero_clear, hero_cc, hero_sustain, hero_vision, hero_mobility
     
    def set_radar_data(self, hero_dict):
        len_count = 5
        objectives =[]
        early_game = []
        late_game = []
        team_fight = []
        sustain = []
        map_control = []
        team_data = []

        if isinstance(hero_dict, dict):
            for val in hero_dict.values():
                if val != 0:
                    objectives.append((self.hero_neutrals[int(val) - 1] + self.hero_push[int(val) - 1]) / 2)
                    late_game.append((self.hero_scaling[int(val) - 1] + self.hero_dps[int(val) - 1]) / 2)
                    early_game.append((self.hero_burst[int(val) - 1] + self.hero_cc[int(val) - 1]) / 2)
                    team_fight.append((self.hero_burst[int(val) - 1] + self.hero_cc[int(val) - 1]) / 2)
                    map_control.append((self.hero_mobility[int(val) - 1] + self.hero_clear[int(val) - 1]) / 2)
                    sustain.append((self.hero_sustain[int(val) - 1]))
                    #print(f'ID: {val}\tobj: {objectives}\tearly: {early_game}\tlate: {late_game}\tteamfight: {team_fight}\tmapcontrol: {map_control}')

            team_data = [self.get_average(objectives, len_count), self.get_average(early_game, len_count), 
                         self.get_average(late_game, len_count), self.get_average(team_fight, len_count), 
                         self.get_average(map_control, len_count), self.get_average(sustain, len_count)]
            #print(f'team: {team_data}')
        return team_data

    def set_indiv_hchart_data(self, hero_id, color):
        pass

    def get_winrate(self, current_hero, hero_dict, is_ally):
        team_wr = []
        print(current_hero)
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

    def set_winrate_data(self, curr_hero, team_dict, enemy_dict):
        ally_wr = []
        enemy_wr = []

        ally_wr = self.get_winrate(curr_hero, team_dict, True)
        enemy_wr = self.get_winrate(curr_hero, enemy_dict, False)
        print(f'{ally_wr}\t{enemy_wr}')
        return ally_wr, enemy_wr


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickDraftWindow()
    window.show()

    sys.exit(app.exec())