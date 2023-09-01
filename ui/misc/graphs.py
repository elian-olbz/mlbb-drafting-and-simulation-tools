import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class RadarChart():
    def __init__(self, ax, pos_x, fig, team_color, team_label):
        plt.style.use('ggplot')

        self.subjects = ['Objectives', 'Early\nGame', 'Late\nGame', 'Team Fight', 'Map\nControl', 'Sustain']

        self.team_data = [0, 0, 0, 0, 0, 0]

        self.angles = np.linspace(0, 2 * np.pi, len(self.subjects), endpoint=False)
        self.angles = np.concatenate((self.angles, [self.angles[0]]))

        self.subjects.append(self.subjects[0])
        self.team_data.append(self.team_data[0])

        # Create a polar subplot for the radar chart
        ax = fig.add_subplot(2, 3, pos_x, polar=True)
        
        ax.set_ylim(0, 10)  # Adjust the limits according to your data range

        self.team_line, = ax.plot([], [], 'o--', color=team_color, label=team_label)
        
        self.team_line.set_data(self.angles, self.team_data)

        self.team_line.set_markerfacecolor(team_color)

        ax.fill(self.angles, self.team_data, alpha=0.25, color=team_color)

        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects)
    
        ax.grid(True)
        ax.legend(loc='upper right')
    
    def update_graph(self, new_team_data, team_color, team_label):
        self.team_data = new_team_data

        self.team_data.append(self.team_data[0])

        ax = self.team_line.axes
        ax.clear()  # Clear the axes

        self.team_line, = ax.plot([], [], 'o--', color=team_color, label=team_label)

        self.team_line.set_data(self.angles, self.team_data)

        self.team_line.set_markerfacecolor(team_color)

        ax.fill(self.angles, self.team_data, alpha=0.25, color=team_color)

        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects)
        ax.set_ylim(0, 10)
        ax.grid(True)
        ax.legend(loc='upper right')


class DivergingChart():
    def __init__(self, ax):
        file_path = "C:/Users/Marlon/Desktop/graph/data/pop.csv"

        self.df = pd.read_csv(file_path)

        self.df['Age Group'] = self.df['Age Group'].fillna(method='ffill')

        self.df['Males'] = self.df['Males'].str.replace(',','').astype('int')
        self.df['Females'] = self.df['Females'].str.replace(',','').astype('int')
        self.df['Females'] = self.df['Females'] * -1

        ax.set_xlim(-2000_000, 2000_000)
        filtered = self.df[self.df['Year']==self.df['Year'].min()]
        males = ax.barh(y=filtered['Age Group'], width=filtered['Males'], color='red')
        females = ax.barh(y=filtered['Age Group'], width=filtered['Females'], color='blue')

        ax.bar_label(males, padding=3, labels=[f'{round(value, -3):,}' for value in filtered['Males']])
        ax.bar_label(females, padding=3, labels=[f'{-1*round(value, -3):,}' for value in filtered['Females']])

        for edge in ['top', 'right', 'bottom', 'left']:
            ax.spines[edge].set_visible(False)

        ax.tick_params(left=False)
        ax.get_xaxis().set_visible(False)

        ax.legend([males, females], ['Males', 'Females'])
        ax.set_title(f'Population of Canada in {filtered["Year"].values[0]}', size=16, weight='bold')

class HorizontalChart():
    def __init__(self, ax):
        file_path = "C:/Users/Marlon/Desktop/graph/data/pop.csv"

        self.df = pd.read_csv(file_path)

        self.df['Age Group'] = self.df['Age Group'].fillna(method='ffill')

        self.df['Males'] = self.df['Males'].str.replace(',','').astype('int')

        ax.set_xlim(0, 2000_000)
        filtered = self.df[self.df['Year']==self.df['Year'].min()]
        males = ax.barh(y=filtered['Age Group'], width=filtered['Males'], color='red')

        ax.bar_label(males, padding=3, labels=[f'{round(value, -3):,}' for value in filtered['Males']])

        for edge in ['top', 'right', 'bottom', 'left']:
            ax.spines[edge].set_visible(False)

        ax.tick_params(left=False)
        ax.get_xaxis().set_visible(False)

        ax.legend([males], ['Males'])
        ax.set_title(f'Population of Canada in {filtered["Year"].values[0]}', size=16, weight='bold')

class WinrateChart():
    def __init__(self, ax):
        self.ax = ax  # Pass the ax object to store it for plotting later
        self.selected_hero = 'Hero 1'
        self.hero_names = ['Hero 2', 'Hero 3', 'Hero 4', 'Hero 5', 'Hero 6', 'Hero 7', 'Hero 8', 'Hero 9', 'Hero 10']

        # Random win rates for illustration (excluding the selected hero)
        self.win_rates_allies = [12, 45, 56, 100]
        self.win_rates_enemies = [72, 14, 66, 84, 37]

        # Create a list of hero categories (allies and enemies)
        self.categories = ['Allies'] * len(self.win_rates_allies) + ['Enemies'] * len(self.win_rates_enemies)

        # Concatenate the win rates for both allies and enemies
        self.win_rates = np.concatenate([self.win_rates_allies, self.win_rates_enemies])

        # Create colors for allies (lightblue) and enemies (lightcoral)
        self.colors = ['lightblue'] * len(self.win_rates_allies) + ['lightcoral'] * len(self.win_rates_enemies)

        # Create the horizontal bar chart within the constructor
        self.ax.barh(self.hero_names, self.win_rates, color=self.colors)

        # Set the y-axis label
        #self.ax.set_xlabel('Win Rate')

        # Set the title
        self.ax.set_title(f'Win Rates for {self.selected_hero} (Allies vs. Enemies)')

        # Invert the y-axis for better readability
        self.ax.invert_yaxis()
    