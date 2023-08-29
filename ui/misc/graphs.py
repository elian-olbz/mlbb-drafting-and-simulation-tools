import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class RadarChart():
    def __init__(self, ax, pos_x, fig):
        plt.style.use('ggplot')

        self.subjects = ['Team\nFight', 'Objectives', 'Early\nGame', 'Late\nGame', 'Laning', 'Mobility']

        self.alice = [1.3, 5.7, 6.2, 7.2, 1.3, 7.4]
        self.bob = [5.3, 3.2, 2.5, 7.1, 3.3, 6.2]

        self.angles = np.linspace(0, 2 * np.pi, len(self.subjects), endpoint=False)
        self.angles = np.concatenate((self.angles, [self.angles[0]]))

        self.subjects.append(self.subjects[0])
        self.alice.append(self.alice[0])
        self.bob.append(self.bob[0])

        # Create a polar subplot for the radar chart
        ax = fig.add_subplot(2, 3, pos_x, polar=True)

        ax.plot(self.angles, self.alice, 'o--', color='g', label='Alice')
        ax.fill(self.angles, self.alice, alpha=0.25, color='g')

        ax.plot(self.angles, self.bob, 'o--', color='orange', label='Bob')
        ax.fill(self.angles, self.bob, alpha=0.25, color='orange')

        ax.set_thetagrids(self.angles * 180 / np.pi, self.subjects)
    
        ax.grid(True)
        ax.legend(loc='upper right')

class DonutChart():
    def __init__(self, ax):        
        ax.set_title('Donut Chart')
        # Sample data as percentages
        self.categories = ['Category A', 'Category B']
        self.percentages = [25, 40]
        self.colors = ['#ff9999', '#66b3ff']
        self.explode = (0.01, 0.01)  # Explode slices slightly

        # Create a donut chart with customizations
        ax.pie(self.percentages, labels=self.categories, autopct='%1.1f%%', startangle=75, colors=self.colors, pctdistance=0.5, explode=self.explode)

        # Draw a white circle in the center to create a hole (donut)
        center_circle = plt.Circle((0, 0), 0.60, fc='white')
        ax.add_artist(center_circle)

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        # Add a title with a shadow effect
        ax.set_title('Fancy Donut Chart', fontsize=16, fontweight='bold', loc='center', pad=20, color='navy', backgroundcolor='lightgrey')

        # Add a legend with custom colors
        ax.legend(self.categories, title="Categories", loc="upper right", bbox_to_anchor=(1.3, 1))

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