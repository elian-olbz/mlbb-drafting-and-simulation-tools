import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

plt.style.use('ggplot')

FACE_COLOR = "#363655"
EDGE_COLOR= "#d9d9d9"

def remove_grids(ax):
    ax.set_xticks([])  # Remove x ticks
    ax.set_xlabel("")  # Remove x label
    ax.set_xticklabels([])  # Remove x tick labels
    ax.grid(visible=False)

class TeamWinAttr():  # Radar chart reflecting win conditions
    def __init__(self, ax, pos_x, fig, team_color, team_label):
        self.subjects = ['EARLY\nTO MID', 
                         'TEAM\nFIGHT', 
                         'BURST', 
                         'LATE\nGAME', 
                         'ISO', 
                         'DOT/\nSUSTAIN']
        self.pad = 10

        self.team_data = [0] * 6

        self.angles = [x / (180 / np.pi)  for x in range(30, 390, 60)]
        self.angles = np.concatenate((self.angles, [self.angles[0]]))

        self.subjects.append(self.subjects[0])
        self.team_data.append(self.team_data[0])

        # Create a polar subplot for the radar chart
        ax = fig.add_subplot(1, 2, pos_x, polar=True)
        ax.set_facecolor(FACE_COLOR)
        ax.grid(color="#b8b8b8")
        
        self.team_line, = ax.plot([], [], 'o-', color=team_color, label=team_label, markersize=3)
        self.team_line.set_data(self.angles, self.team_data)
        self.team_line.set_markerfacecolor(team_color)
        ax.fill(self.angles, self.team_data, alpha=0.85, color=team_color)
        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects, fontsize=9, color="#eaeaea")
        ax.set_ylim(0, 10)  
        ax.set_yticklabels([])
        ax.tick_params(grid_alpha=0.3, pad=self.pad, left=False)
        ax.grid(True)

    
    def update_graph(self, new_team_data):
        self.team_data = new_team_data
        self.team_data.append(self.team_data[0])
        
        ax = self.team_line.axes
        ax.clear()

        ax.set_facecolor(FACE_COLOR)
        ax.grid(color="#b8b8b8")
        self.team_line, = ax.plot([], [], 'o-', color=self.team_line.get_color(), markersize=3)
        self.team_line.set_data(self.angles, self.team_data)
        self.team_line.set_markerfacecolor(self.team_line.get_color())
        ax.fill(self.angles, self.team_data, alpha=0.85, color=self.team_line.get_color())
        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects, fontsize=9, color="#eaeaea")
        ax.set_ylim(0, 10)
        ax.set_yticklabels([])
        ax.grid(True)
        ax.tick_params(grid_alpha=0.3, pad=self.pad, left=False)

        # Add labels to the points with padding
        label_padding = 1.5  # Adjust this value to control the padding
        bg_box_alpha = 0.9  # Adjust this value to control the background box transparency
        if all(self.team_data) > 0:
            for angle, value in zip(self.angles, self.team_data):
                x = angle
                y = value + label_padding
                ax.annotate(
                    text=str(value),
                    xy=(x, value),
                    xytext=(x, y),
                    fontsize=8,
                    color=EDGE_COLOR,
                    ha='center',
                    va='center',
                    bbox=dict(boxstyle="round, pad=0.3", edgecolor=EDGE_COLOR, facecolor="#292941", alpha=bg_box_alpha)
                )

class HeadToHeadAttr: # Diverging chart / Attributes of both team
    def __init__(self, ax):
        self.ax = ax
        self.blue_values = [0]*7
        self.red_values = [0]*7
        self.labels = ['Wave Clear', 'DPS', 'Vision', 'CC', 'Objective', 'Push', 'Utility']

        #self.ax.set_xlim(min(min(self.blue_values), min(self.red_values)), max(max(self.blue_values), max(self.red_values)))
        x_ticks = np.arange(-10, 11, 1)  # Create an array of x-tick positions
        bars_blue = self.ax.barh(y=range(len(self.labels)), width=self.blue_values, color='#2e6eea')
        bars_red = self.ax.barh(y=range(len(self.labels)), width=self.red_values, color='#ed0d3a')
        self.add_bg_bars(self.labels)
        self.add_bg_bars(self.labels, -10)

        self.ax.set_facecolor(FACE_COLOR)
        self.ax.set_xticks(x_ticks)
        remove_grids(self.ax)

        # Set y-axis tick labels and values
        self.ax.set_yticks(range(len(self.labels)))
        self.ax.set_yticklabels(self.labels, color="#eaeaea")
        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def add_bg_bars(self, hero_data, max_width=10, color="#b8b8b8"):
        self.ax.barh(y=range(len(hero_data)), width=max_width, color=color, edgecolor="#b8b8b8", zorder=0, alpha=0.1)

    def update_graph(self, blue_values, red_values):
        self.ax.clear()
        self.blue_values = [-value for value in blue_values]  # Multiply blue team values by -1
        self.red_values = red_values

        x_ticks = np.arange(-10, 11, 1)  # Create an array of x-tick positions
        bars_blue = self.ax.barh(y=range(len(self.labels)), width=self.blue_values, color='#2e6eea', edgecolor=EDGE_COLOR)
        bars_red = self.ax.barh(y=range(len(self.labels)), width=red_values, color='#ed0d3a', edgecolor=EDGE_COLOR)
        self.add_bg_bars(self.labels)
        self.add_bg_bars(self.labels, -10)

        self.ax.set_facecolor(FACE_COLOR)
        self.ax.set_xticks(x_ticks)
        remove_grids(self.ax)

        # Set y-axis tick labels and values
        self.ax.set_yticks(range(len(self.labels)))
        self.ax.set_yticklabels(self.labels, color="#eaeaea")  
        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

        # Add value text labels on the bars with padding and font size
        for bar, value in zip(bars_blue, self.blue_values):
            if value < 0:
                ha = 'left'
                if value < -0.4:
                    x_position = value
                else:
                    x_position = -0.58
                self.ax.text(x_position, bar.get_y() + bar.get_height() / 2, str(abs(value)), color="#eaeaea", va='center', ha=ha, fontsize=8, bbox=dict(edgecolor=EDGE_COLOR, facecolor="#292941", boxstyle='round'))
        
        for bar, value in zip(bars_red, self.red_values):
            if value > 0:
                ha = 'right'
                if value > 0.4:
                    x_position = value
                else:
                    x_position = 0.58
                self.ax.text(x_position, bar.get_y() + bar.get_height() / 2, str(abs(value)), color='#eaeaea', va='center', ha=ha, fontsize=8, bbox=dict(edgecolor=EDGE_COLOR, facecolor="#292941", boxstyle='round'))

class SingleHeroAttr(): # H_Chart reflecting single hero attributes
    def __init__(self, ax, hero_data):
        self.hero_data = hero_data
        self.ax = ax
        self.labels = ['Wave Clear', 'DPS', 'Vision', 'CC', 'Objective', 'Push', 'Utility']

        self.init_chart()
    
    def init_chart(self):
        self.ax.clear()
        initial_data = [0] * len(self.labels)

        self.ax.set_xlim(0, 10)  # x-axis limits
        self.ax.barh(y=range(1, len(initial_data) + 1), width=initial_data, color='blue', edgecolor=EDGE_COLOR)
        self.add_bg_bars(initial_data, max_width=10)

        self.ax.tick_params(left=True)
        self.ax.set_facecolor(FACE_COLOR)
        self.ax.tick_params(grid_alpha=0.3)

        self.ax.set_yticks(range(1, len(initial_data) + 1))
        self.ax.set_yticklabels([label for label in self.labels], size=9, color="#eaeaea")

        remove_grids(self.ax)
        self.ax.set_title(f'Hero Attributes', size=11, weight='bold', color="#eaeaea")

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def update_graph(self, hero_id, hero_name, team_color):
        self.ax.clear()
        if hero_id != 0:
            self.hero_id = hero_id -1
        self.ax.set_xlim(0, 10)  # x-axis limits
        bars = self.ax.barh(y=range(1, len(self.hero_data[self.hero_id]) + 1), width=self.hero_data[self.hero_id], color=team_color, edgecolor=EDGE_COLOR)
        self.add_bg_bars(self.hero_data[self.hero_id], max_width=10)

        self.ax.tick_params(left=True)
        #ax.get_xaxis().set_visible(False)
        self.ax.set_facecolor(FACE_COLOR)
        self.ax.grid(color="#b8b8b8")
        self.ax.tick_params(grid_alpha=0.3)

        self.ax.set_yticks(range(1, len(self.hero_data[self.hero_id]) + 1))
        self.ax.set_yticklabels([label for label in self.labels], size=9, color="#eaeaea")

        remove_grids(self.ax)

        self.ax.set_title(f'{hero_name} Attributes', size=11, weight='bold', color="#eaeaea")
        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

        for bar, value in zip(bars, self.hero_data[self.hero_id]):
            if value > 0:
                self.ax.text(value, bar.get_y() + bar.get_height() / 2, str(value), color='#eaeaea', va='center', ha='right', fontsize=8, bbox=dict(edgecolor=EDGE_COLOR, facecolor="#292941", boxstyle='round'))

    def add_bg_bars(self, hero_data, max_width=100, color="#b8b8b8"):
        self.ax.barh(y=range(1, len(hero_data) + 1), width=max_width, color=color, edgecolor="#b8b8b8", zorder=0, alpha=0.1)

class SingleHeroStats: # pie charts
    def __init__(self, ax, hero_stats, stats_type):
        self.ax = ax
        self.stats_type = stats_type
        self.hero_stats = hero_stats
        self.value = 0.0  # Initial value
        self.hero_id = 0  # Initial hero ID
        self.index = 0    # Initial index
        self.init_chart()
    
    def init_chart(self):
        self.ax.clear()
        # Create a blue wedge donut chart (initially hidden)
        self.back_color = (165 / 255, 165 / 255, 255 / 255)
        self.color_wedge, _ = self.ax.pie([1], colors=['blue'], radius=1.06, wedgeprops={'linewidth': 7})
        self.color_wedge[0].set_visible(False)

        # Create a gray ring donut chart
        self.gray_ring, _ = self.ax.pie([1], colors=[self.back_color], radius=1.09, wedgeprops={'linewidth': 2, 'alpha': 0.2, 'ec': '#fff'})

        self.center_circle = plt.Circle((0, 0), 0.75, ec='#eaeaea', fc='#31314d', lw=1.0)
        self.ax.add_artist(self.center_circle)

        # Add a text label to display self.value in the center
        self.value_text = self.ax.text(0, 0, f'{self.value:.2f}' + '%', va='center', ha='center', fontsize=9, color="#eaeaea")
        self.anno_text = self.ax.text(0, -1.5, f'0 {self.stats_type}/\n0 game', va='center', ha='center', fontsize=9, color="#eaeaea")

        # Set axis limits and remove axis labels
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.axis('off')

    def update_graph(self, hero_id, wr_index, total_index, team_color):
        if hero_id != 0:
            self.hero_id = hero_id - 1
        
        win_rate = self.hero_stats[self.hero_id][wr_index]  # Get the Win Rate

        # Update the blue wedge donut chart with the win rate
        self.color_wedge[0].set_theta1(180 - win_rate * 3.6)
        self.color_wedge[0].set_theta2(180)  # Use win_rate to determine the angle
        self.color_wedge[0].set_facecolor(team_color)
        self.color_wedge[0].set_visible(True)  # Make the blue wedge visible

        # Update the gray ring donut chart to show the gray ring
        self.gray_ring[0].set_theta1(0)
        self.gray_ring[0].set_theta2(360)  # Full circle
        self.gray_ring[0].set_facecolor(self.back_color)

        # Update the text label with the win rate
        self.value_text.set_text(f'{win_rate:.2f}%')

        matches = self.hero_stats[self.hero_id][total_index]
        if win_rate != 0:
            overall_matches = matches / (win_rate / 100)
        else:
            overall_matches = 0

        if matches <= 1 and overall_matches <= 1: # anti grammar cops
            self.anno_text.set_text(f'{matches} {self.stats_type}/\n{overall_matches:.0f} game')
        elif matches <= 1 and overall_matches > 1:
            self.anno_text.set_text(f'{matches} {self.stats_type}/\n{overall_matches:.0f} games')
        else:
            self.anno_text.set_text(f'{matches} {self.stats_type}s/\n{overall_matches:.0f} games')

class LineUpWinrate(): # H_Chart reflecting the winrates of a selected hero against or with each hero on the line up
    def __init__(self, ax):
        self.ax = ax  # Pass the ax object to store it for plotting later
        self.BLUE_COLOR = "#2e6eea"
        self.RED_COLOR = "#ed0d3a"
        self.tg = []
        self.gid_val = {}
        self.annotation = None
        self.data_bars = []
        self.init_chart()
    
    def init_chart(self):
        self.hero_names = [f'Hero {x}' for x in range(1, 10)]
        # Random win rates for illustration (excluding the selected hero)
        self.win_rates_allies = [0, 0, 0, 0]
        self.win_rates_enemies = [0, 0, 0, 0, 0]
        # Concatenate the win rates for both allies and enemies
        self.win_rates = np.concatenate([self.win_rates_allies, self.win_rates_enemies])

        # Create colors for allies (lightblue) and enemies (lightcoral)
        self.colors = [self.BLUE_COLOR] * len(self.win_rates_allies) + [self.RED_COLOR] * len(self.win_rates_enemies)

        self.ax.clear()
        # Create the horizontal bar chart within the constructor
        self.ax.barh(self.hero_names, self.win_rates, color=self.colors, edgecolor=EDGE_COLOR)
        self.add_bg_bars(self.hero_names)
        # Set the title
        self.ax.set_title(f'Hero Winrate', size=11, weight='bold', color="#eaeaea")
        self.ax.tick_params(left=True)
        self.ax.set_xlim(0, 100)

        self.ax.set_facecolor(FACE_COLOR)

        self.ax.set_yticks(range(0, len(self.hero_names)))
        self.ax.set_yticklabels([y for y in self.hero_names], size=9, color="#eaeaea")

        remove_grids(self.ax)

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def update_graph(self, new_ally_winrate, new_enemy_winrate, new_ally_tg, new_enemy_tg, ally_names, enemy_names, selected_hero_name, side):
        # Clear the existing bar chart
        self.ax.clear()

        # Update the win rates and colors
        self.win_rates = np.concatenate([new_ally_winrate, new_enemy_winrate])
        self.tg = np.concatenate([new_ally_tg + new_enemy_tg])
        self.hero_names = ally_names + enemy_names

        if side == 'blue':
            self.colors = [self.BLUE_COLOR] * len(self.win_rates_allies) + [self.RED_COLOR] * len(self.win_rates_enemies)
        else:
            self.colors = [self.RED_COLOR] * len(self.win_rates_allies) + [self.BLUE_COLOR] * len(self.win_rates_enemies)

        # Create the updated horizontal bar chart
        bars = self.ax.barh(self.hero_names, self.win_rates, color=self.colors, edgecolor=EDGE_COLOR)
        self.add_bg_bars(self.hero_names)

        # Set the title
        self.ax.set_title(f'{selected_hero_name} Winrate', size=11, weight='bold', color="#eaeaea")
        self.ax.tick_params(left=True)
        self.ax.set_xlim(0, 100)

        self.ax.set_facecolor(FACE_COLOR)

        self.ax.set_yticks(range(0, len(self.hero_names)))
        self.ax.set_yticklabels([y for y in self.hero_names], size=9, color="#eaeaea")

        remove_grids(self.ax)

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

        # Create a list to store data bars and their labels
        data_bars = []

        for bar, value, tg, label in zip(bars, self.win_rates, self.tg, self.hero_names):
            if value > 0:
                self.ax.text(round(value), bar.get_y() + bar.get_height() / 2, str(round(value))+"%", color='#eaeaea', va='center', ha='right', fontsize=8, bbox=dict(edgecolor=EDGE_COLOR, facecolor="#292941", boxstyle='round'))
                self.gid_val[label] = tg
                data_bars.append((bar, label))  # Store the data bars and their labels

        self.data_bars = data_bars  # Store the data bars for later reference

        self.ax.figure.canvas.mpl_connect("button_press_event", self.on_click)

    def on_click(self, event):
        if event.inaxes is None:
            return

        for bar, label in self.data_bars:
            if isinstance(bar, Rectangle) and bar.contains(event)[0]:
                val = int(self.gid_val[label])
                if self.gid_val.get(label) is not None:
                    x_pos = (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) / 2
                    y_pos = 10

                    i = i = self.ax.patches.index(bar)
                    g = "game"

                    if int(val) > 1:
                        g = "games"
                    
                    if i < 4:
                        txt = f"Total {g} with {label} : {val}"
                    else:
                        txt = f"Total {g} versus {label} : {val}"

                    # Remove previous text annotation
                    if hasattr(self, "annotation") and self.annotation is not None:
                        self.annotation.remove()

                    # Create a new text annotation
                    self.annotation = self.ax.text(x_pos, y_pos, txt, color='#eaeaea', va='center', ha='center', fontsize=9, weight='bold')

                else:
                    return

        self.ax.get_figure().canvas.draw_idle()

    def add_bg_bars(self, hero_names, max_width=100, color="#b8b8b8"):
        # Create a list of maximum width values for background bars
        max_values = [max_width] * len(hero_names)
        
        # Create the background horizontal bar chart with the specified color
        self.ax.barh(hero_names, max_values, color=color, edgecolor="#b8b8b8", zorder=0, alpha=0.1)
