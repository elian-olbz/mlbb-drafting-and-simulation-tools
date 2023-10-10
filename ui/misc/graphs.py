import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class TeamWinAttr():  # Radar chart reflecting win conditions
    def __init__(self, ax, pos_x, fig, team_color, team_label):
        plt.style.use('ggplot')

        self.subjects = ['       EARLY\n       TO MID', 
                         'TEAM\n FIGHT\n', 
                         'BURST       ', 
                         'LATE       \nGAME       ', 
                         '\nISO', 
                         '       DOT/\n       SUSTAIN']

        self.team_data = [0] * 6

        self.angles = [x / (180 / np.pi)  for x in range(30, 390, 60)]
        self.angles = np.concatenate((self.angles, [self.angles[0]]))

        self.subjects.append(self.subjects[0])
        self.team_data.append(self.team_data[0])

        # Create a polar subplot for the radar chart
        ax = fig.add_subplot(1, 2, pos_x, polar=True)
        
        self.team_line, = ax.plot([], [], 'o--', color=team_color, label=team_label, markersize=3)
        self.team_line.set_data(self.angles, self.team_data)
        self.team_line.set_markerfacecolor(team_color)
        ax.fill(self.angles, self.team_data, alpha=0.5, color=team_color)
        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects, fontsize=9, color="#eaeaea")
        ax.set_ylim(0, 10)  
        ax.grid(True)
        ax.tick_params(left=False)
    
    def update_graph(self, new_team_data):
        self.team_data = new_team_data
        self.team_data.append(self.team_data[0])

        ax = self.team_line.axes
        ax.clear()

        self.team_line, = ax.plot([], [], 'o--', color=self.team_line.get_color(), markersize=3)
        self.team_line.set_data(self.angles, self.team_data)
        self.team_line.set_markerfacecolor(self.team_line.get_color())
        ax.fill(self.angles, self.team_data, alpha=0.5, color=self.team_line.get_color())
        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects, fontsize=9, color="#eaeaea")
        ax.set_ylim(0, 10)
        ax.grid(True)
        ax.tick_params(left=False)

class HeadToHeadAttr: # Diverging chart / Attributes of both team
    def __init__(self, ax):
        self.ax = ax
        self.blue_values = [0]*7
        self.red_values = [0]*7
        self.labels = ['Wave Clear', 'DPS', 'Vision', 'CC', 'Objective', 'Push', 'Utility']

        #self.ax.set_xlim(min(min(self.blue_values), min(self.red_values)), max(max(self.blue_values), max(self.red_values)))
        x_ticks = np.arange(-10, 11, 1)  # Create an array of x-tick positions
        bars_blue = self.ax.barh(y=range(len(self.labels)), width=self.blue_values, color='blue')
        bars_red = self.ax.barh(y=range(len(self.labels)), width=self.red_values, color='red')

        for edge in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[edge].set_visible(False)

        self.ax.tick_params(left=False, bottom=True)
        self.ax.get_xaxis().set_visible(True)
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels([str(abs(value)) for value in x_ticks], color="#eaeaea")

        # Set y-axis tick labels and values
        self.ax.set_yticks(range(len(self.labels)))
        self.ax.set_yticklabels(self.labels, color="#eaeaea")
        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def update_graph(self, blue_values, red_values):
        self.ax.clear()
        self.blue_values = [-value for value in blue_values]  # Multiply blue team values by -1
        self.red_values = red_values

        self.ax.set_xlim(min(min(self.blue_values), min(self.red_values)), max(max(self.blue_values), max(self.red_values)))
        x_ticks = np.arange(-10, 11, 1)  # Create an array of x-tick positions
        bars_blue = self.ax.barh(y=range(len(self.labels)), width=self.blue_values, color='blue')
        bars_red = self.ax.barh(y=range(len(self.labels)), width=red_values, color='red')

        for edge in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[edge].set_visible(False)

        self.ax.tick_params(left=False, bottom=True)
        self.ax.get_xaxis().set_visible(True)
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels([str(abs(value)) for value in x_ticks], color="#eaeaea")

        # Set y-axis tick labels and values
        self.ax.set_yticks(range(len(self.labels)))
        self.ax.set_yticklabels(self.labels, color="#eaeaea")  
        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

class SingleHeroAttr(): # H_Chart reflecting single hero attributes
    def __init__(self, ax, hero_data):
        self.hero_data = hero_data
        self.ax = ax
        self.labels = ['Wave Clear', 'DPS', 'Vision', 'CC', 'Objective', 'Push', 'Utility']

        initial_data = [0] * len(self.labels)

        self.ax.set_xlim(0, 10)  # x-axis limits
        self.ax.barh(y=range(1, len(initial_data) + 1), width=initial_data, color='blue')

        for edge in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[edge].set_visible(False)

        self.ax.tick_params(left=True)

        self.ax.set_yticks(range(1, len(initial_data) + 1))
        self.ax.set_yticklabels([label for label in self.labels], size=9, color="#eaeaea")

        self.ax.set_xticks(self.ax.get_xticks())
        self.ax.set_xticklabels([int(x) for x in self.ax.get_xticks()], size=9, color="#eaeaea")

        self.ax.set_title(f'Hero Attributes', size=11, weight='bold', color="#eaeaea")

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def update_graph(self, hero_id, hero_name, team_color):
        self.ax.clear()
        if hero_id != 0:
            self.hero_id = hero_id -1
        self.ax.set_xlim(0, 10)  # x-axis limits
        self.ax.barh(y=range(1, len(self.hero_data[self.hero_id]) + 1), width=self.hero_data[self.hero_id], color=team_color)

        for edge in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[edge].set_visible(False)

        self.ax.tick_params(left=True)
        #ax.get_xaxis().set_visible(False)

        self.ax.set_yticks(range(1, len(self.hero_data[self.hero_id]) + 1))
        self.ax.set_yticklabels([label for label in self.labels], size=9, color="#eaeaea")

        self.ax.set_xticks(self.ax.get_xticks())
        self.ax.set_xticklabels([int(x) for x in self.ax.get_xticks()], size=9, color="#eaeaea")

        self.ax.set_title(f'{hero_name} Attributes', size=11, weight='bold', color="#eaeaea")
        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

class SingleHeroStats: # pie charts
    def __init__(self, ax, hero_stats, stats_type):
        self.ax = ax
        self.stats_type = stats_type
        self.hero_stats = hero_stats

        self.value = 0.0  # Initial value
        self.hero_id = 0  # Initial hero ID
        self.index = 0    # Initial index

        # Create a blue wedge donut chart (initially hidden)
        self.back_color = (165 / 255, 165 / 255, 255 / 255)
        self.color_wedge, _ = self.ax.pie([1], colors=['blue'], radius=1.0, wedgeprops={'linewidth': 6})
        self.color_wedge[0].set_visible(False)

        # Create a gray ring donut chart
        self.gray_ring, _ = self.ax.pie([1], colors=[self.back_color], radius=1.0, wedgeprops={'linewidth': 6, 'alpha': 0.2})

        self.center_circle = plt.Circle((0, 0), 0.7, color='#31314d', fc='#31314d', lw=1.0)
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
        self.hero_names = [f'Hero {x}' for x in range(1, 10)]
        self.blue = (85 / 255, 170 / 255, 255 / 255)
        self.red = (255 / 255, 68 / 255, 62 / 255)

        # Random win rates for illustration (excluding the selected hero)
        self.win_rates_allies = [0, 0, 0, 0]
        self.win_rates_enemies = [0, 0, 0, 0, 0]

        # Concatenate the win rates for both allies and enemies
        self.win_rates = np.concatenate([self.win_rates_allies, self.win_rates_enemies])

        # Create colors for allies (lightblue) and enemies (lightcoral)
        self.colors = [self.blue] * len(self.win_rates_allies) + [self.red] * len(self.win_rates_enemies)

        # Create the horizontal bar chart within the constructor
        self.ax.barh(self.hero_names, self.win_rates, color=self.colors)

        # Set the title
        self.ax.set_title(f'Hero WR (Ally vs. Enemy)', size=11, weight='bold', color="#eaeaea")
        self.ax.tick_params(left=True)
        self.ax.set_xlim(0, 100)

        self.ax.set_yticks(range(0, len(self.hero_names)))
        self.ax.set_yticklabels([y for y in self.hero_names], size=9, color="#eaeaea")

        self.ax.set_xticks(self.ax.get_xticks())
        self.ax.set_xticklabels([int(x) for x in self.ax.get_xticks()], size=9, color="#eaeaea")

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def update_graph(self, new_ally_winrate, new_enemy_winrate, ally_names, enemy_names, selected_hero_name, side):
        # Clear the existing bar chart
        self.ax.clear()

        # Update the win rates and colors
        self.win_rates = np.concatenate([new_ally_winrate, new_enemy_winrate])
        self.hero_names = ally_names + enemy_names
        
        if side == 'blue':
            self.colors = [self.blue] * len(self.win_rates_allies) + [self.red] * len(self.win_rates_enemies)
        else:
            self.colors = [self.red] * len(self.win_rates_allies) + [self.blue] * len(self.win_rates_enemies)
            
        # Create the updated horizontal bar chart
        self.ax.barh(self.hero_names, self.win_rates, color=self.colors)
        # Set the y-axis label
        # self.ax.set_xlabel('Win Rate')

        # Set the title
        self.ax.set_title(f'{selected_hero_name} WR (Ally vs. Enemy)', size=11, weight='bold', color="#eaeaea")
        self.ax.tick_params(left=True)
        self.ax.set_xlim(0, 100)
        
        self.ax.set_yticks(range(0, len(self.hero_names)))
        self.ax.set_yticklabels([y for y in self.hero_names], size=9, color="#eaeaea")

        self.ax.set_xticks(self.ax.get_xticks())
        self.ax.set_xticklabels([int(x) for x in self.ax.get_xticks()], size=9, color="#eaeaea")

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()
    