from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
import csv
import os

def rounded_pixmap(pixmap, size, border_thickness=0):
        # Create a transparent mask and painter
        mask = QPixmap(size, size)
        mask.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw a circle on the mask using QPainterPath with an increased border thickness
        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(border_thickness, border_thickness, size - 2 * border_thickness, size - 2 * border_thickness))
        painter.setClipPath(clip_path)

        # Use the mask to draw the pixmap as a rounded shape
        rounded_pixmap = QPixmap(size, size)
        rounded_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(clip_path)  # Set the same clip path for the pixmap
        painter.drawPixmap(0, 0, pixmap)

        return rounded_pixmap

def load_hero_roles(hero_roles_path):
    hero_roles = {}
    hero_types = {}
    hero_names = []
    hero_icons = []
    with open(hero_roles_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            hero_id = int(row['HeroID'])
            roles = [role.strip() for role in row['Role'].split('/')]
            hero_roles[hero_id] = roles
            hero_name = row['Name']
            hero_names.append(hero_name)
            hero_icon = row['Icon']
            hero_icons.append(hero_icon)
            types = [type.strip() for type in row['Type'].split('/')]
            hero_types[hero_id] = types

        return hero_roles, hero_names, hero_icons, hero_types
    
def load_names(path):
    hero_names = []
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
             hero_names.append(row['Name'])
        return hero_names

def get_name(hero_id, hero_names):
    return hero_names[hero_id - 1]

def get_role(hero_id, hero_roles):
    return hero_roles.get(hero_id, [])

def get_icon(hero_id):
    image_filename = 'hero_icon ({})'.format(hero_id) + '.jpg'
    image_path = os.path.join('images/hero_icons/', image_filename)
    return image_path

def get_image(hero_id):
    image_filename = 'hero_image ({})'.format(hero_id) + '.jpg'
    image_path = os.path.join('images/hero_images/', image_filename)
    return image_path

def get_type(hero_id, hero_types):
        return hero_types.get(hero_id, [])


def load_theme(theme_path):
    with open(theme_path, 'r') as file:
        theme = file.read()
    return theme

def get_curr_index(rem_clicks):
        return abs(rem_clicks - 20)

def print_draft_status(draft_state):
    print("=========== Draft Status ===========")
    print("Blue Bans:  ", ', '.join(get_name(hero_id, draft_state.hero_names) for hero_id in draft_state.blue_actions[0]))
    print("Blue Picks: ", ', '.join(get_name(hero_id, draft_state.hero_names) for hero_id in draft_state.blue_actions[1]))
    print("Blue roles: {}".format(draft_state.blue_pick_roles))
    print("")
    print("Red Bans:   ", ', '.join(get_name(hero_id, draft_state.hero_names) for hero_id in draft_state.red_actions[0]))
    print("Red Picks:  ", ', '.join(get_name(hero_id, draft_state.hero_names) for hero_id in draft_state.red_actions[1]))
    print("Red roles: {}".format(draft_state.red_pick_roles))
    print("====================================\n\n")

def print_final_draft(draft_state):
    print("Final draft:")
    print("Blue Team: ", ', '.join(draft_state.get_name(hero_id, draft_state.hero_names) for hero_id in draft_state.blue_actions[1]))
    print("Red Team:  ", ', '.join(draft_state.get_name(hero_id, draft_state.hero_names) for hero_id in draft_state.red_actions[1]))
