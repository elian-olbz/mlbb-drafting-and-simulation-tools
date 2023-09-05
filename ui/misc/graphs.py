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

        self.subjects = ['Objectives', 'Early\nGame', 'Late\nGame', 'Team Fight', 'Map\nControl', 'Sustain']

        self.team_data = [0, 0, 0, 0, 0, 0]

        self.angles = np.linspace(0, 2 * np.pi, len(self.subjects), endpoint=False)
        self.angles = np.concatenate((self.angles, [self.angles[0]]))

        self.subjects.append(self.subjects[0])
        self.team_data.append(self.team_data[0])

        # Create a polar subplot for the radar chart
        ax = fig.add_subplot(1, 2, pos_x, polar=True)
        
        ax.set_ylim(0, 10)  # Adjust the limits according to your data range

        self.team_line, = ax.plot([], [], 'o--', color=team_color, label=team_label, markersize=3)
        
        self.team_line.set_data(self.angles, self.team_data)

        self.team_line.set_markerfacecolor(team_color)

        ax.fill(self.angles, self.team_data, alpha=0.25, color=team_color)

        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects)
    
        ax.grid(True)
        ax.tick_params(left=False)
    
    def update_graph(self, new_team_data, team_color, team_label):
        self.team_data = new_team_data

        self.team_data.append(self.team_data[0])

        ax = self.team_line.axes
        ax.clear()  # Clear the axes

        self.team_line, = ax.plot([], [], 'o--', color=team_color, label=team_label, markersize=3)

        self.team_line.set_data(self.angles, self.team_data)

        self.team_line.set_markerfacecolor(team_color)

        ax.fill(self.angles, self.team_data, alpha=0.25, color=team_color)

        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects)
        ax.set_ylim(0, 10)
        ax.grid(True)
        ax.tick_params(left=False)

class HeadToHeadAttr:
    def __init__(self, ax, blue_values, red_values):
        self.blue_values = [-value for value in blue_values]  # Multiply blue team values by -1
        self.red_values = red_values
        labels = ['Burst', 'DPS', 'Scaling', 'Neutrals', 'Push', 'Clear', 'CC', 'Sustain', 'Vision', 'Mobility']

        ax.set_xlim(min(min(self.blue_values), min(self.red_values)), max(max(self.blue_values), max(self.red_values)))
        x_ticks = np.arange(-10, 11, 1)  # Create an array of x-tick positions
        bars_blue = ax.barh(y=range(len(labels)), width=self.blue_values, color='blue')
        bars_red = ax.barh(y=range(len(labels)), width=red_values, color='red')

        for edge in ['top', 'right', 'bottom', 'left']:
            ax.spines[edge].set_visible(False)

        ax.tick_params(left=False, bottom=True)
        ax.get_xaxis().set_visible(True)
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([str(abs(value)) for value in x_ticks])

        #ax.legend([bars_blue, bars_red], ['Blue Team', 'Red Team'])
        ax.set_title('Head-to-Head Attributes', size=16, weight='bold')

        # Set y-axis tick labels and values
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)

class SingleHeroAttr(): # H_Chart reflecting single hero attributes
    def __init__(self, ax, hero_data):
        self.hero_data = hero_data
        self.ax = ax
        self.labels = ['Burst', 'DPS', 'Scaling', 'Neutrals', 'Push', 'Clear', 'CC', 'Sustain', 'Vision', 'Mobility']

        initial_data = [0] * len(self.labels)

        self.ax.set_xlim(0, 10)  # x-axis limits
        self.ax.barh(y=range(1, len(initial_data) + 1), width=initial_data, color='blue')

        for edge in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[edge].set_visible(False)

        self.ax.tick_params(left=False)
        #ax.get_xaxis().set_visible(False)

        self.ax.set_yticks(range(1, len(initial_data) + 1))
        self.ax.set_yticklabels([label for label in self.labels])

        self.ax.set_title(f'Hero Attributes of Hero X', size=16)

    def update_graph(self, hero_id, team_color):
        if hero_id != 0:
            self.hero_id = hero_id -1
        self.ax.set_xlim(0, 10)  # x-axis limits
        self.ax.barh(y=range(1, len(self.hero_data[self.hero_id]) + 1), width=self.hero_data[self.hero_id], color=team_color)

        for edge in ['top', 'right', 'bottom', 'left']:
            self.ax.spines[edge].set_visible(False)

        self.ax.tick_params(left=False)
        #ax.get_xaxis().set_visible(False)

        self.ax.set_yticks(range(1, len(self.hero_data[self.hero_id]) + 1))
        self.ax.set_yticklabels([label for label in self.labels])

        self.ax.set_title(f'Hero Attributes of Hero X', size=16)

class SingleHeroStats:
    def __init__(self, ax, hero_stats):
        self.ax = ax
        self.hero_stats = hero_stats

        self.value = 0.0  # Initial value
        self.hero_id = 0  # Initial hero ID
        self.index = 0    # Initial index

        # Create a donut chart with a single wedge
        self.wedge, _ = self.ax.pie([1], colors=['white'], radius=1.0, wedgeprops={'linewidth': 2, 'edgecolor': 'gray'})
        self.center_circle = plt.Circle((0, 0), 0.7, color='white', fc='white', lw=1.0)
        self.ax.add_artist(self.center_circle)

        # Add a text label to display self.value in the center
        self.value_text = self.ax.text(0, 0, str(self.value), va='center', ha='center', fontsize=10)

        # Set axis limits and remove axis labels
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.axis('off')

    def update_graph(self, hero_id, index):
        if hero_id != 0:
            self.hero_id = hero_id - 1
        
        win_rate = self.hero_stats[self.hero_id][index] # Get the Win Rate

        # Update the donut chart wedge with the win rate
        self.wedge[0].set_theta1(180 - win_rate * 3.6)
        self.wedge[0].set_theta2(180)
        self.wedge[0].set_facecolor('blue')

        # Update the text label with the win rate
        self.value_text.set_text(f'{win_rate}%')


class LineUpWinrate(): # H_Chart reflecting the winrates of a selected hero against or with each hero on the line up
    def __init__(self, ax):
        self.ax = ax  # Pass the ax object to store it for plotting later
        self.selected_hero = 'Hero 1'
        self.hero_names = ['Hero 2', 'Hero 3', 'Hero 4', 'Hero 5', 'Hero 6', 'Hero 7', 'Hero 8', 'Hero 9', 'Hero 10']

        # Random win rates for illustration (excluding the selected hero)
        self.win_rates_allies = [0, 0, 0, 0]
        self.win_rates_enemies = [0, 0, 0, 0, 0]

        # Concatenate the win rates for both allies and enemies
        self.win_rates = np.concatenate([self.win_rates_allies, self.win_rates_enemies])

        # Create colors for allies (lightblue) and enemies (lightcoral)
        self.colors = ['blue'] * len(self.win_rates_allies) + ['red'] * len(self.win_rates_enemies)

        # Create the horizontal bar chart within the constructor
        self.ax.barh(self.hero_names, self.win_rates, color=self.colors)

        # Set the title
        self.ax.set_title(f'Win Rates for {self.selected_hero} (Allies vs. Enemies)')
        self.ax.tick_params(left=False)
        self.ax.set_xlim(0, 100)

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()

    def update_graph(self, new_ally_winrate, new_enemy_winrate, selected_hero):
        # Clear the existing bar chart
        self.ax.clear()

        # Update the win rates and colors
        self.win_rates = np.concatenate([new_ally_winrate, new_enemy_winrate])
        self.colors = ['blue'] * len(self.win_rates_allies) + ['red'] * len(self.win_rates_enemies)

        # Create the updated horizontal bar chart
        self.ax.barh(self.hero_names, self.win_rates, color=self.colors)

        # Set the y-axis label
        # self.ax.set_xlabel('Win Rate')

        # Set the title
        self.ax.set_title(f'Win Rates for {selected_hero} (Allies vs. Enemies)')
        self.ax.tick_params(left=False)
        self.ax.set_xlim(0, 100)

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()
    