import random
import numpy as np
import time
from run_draft_logic.utils import load_hero_roles, get_name, get_role

class DraftState:
    def __init__(self, hero_roles_path):
        self.hero_roles = {}
        self.hero_names = []
        self.hero_icons = []
        self.hero_types = {}
        self.draft_sequence = []
        self.final_sequence = []
        self.blue_actions = [[], []]  # blue ban is [0], blue picks is [1]
        self.red_actions = [[], []]  # red ban is [0], red picks is [1]
        self.blue_pick_roles = []
        self.red_pick_roles = []
        self.blue_level = None
        self.red_level = None
        
        self.hero_roles, self.hero_names, self.hero_icons, self.hero_types = load_hero_roles(hero_roles_path)

    def add_pick(self, team_color, hero_id):
        if team_color == "Blue":
            self.blue_actions[1].append(hero_id)
            pick_role = self.filter_pick_roles(hero_id, self.blue_pick_roles)
            if pick_role is not None:
                self.blue_pick_roles.append(pick_role)
        else:
            self.red_actions[1].append(hero_id)
            pick_role = self.filter_pick_roles(hero_id, self.red_pick_roles)
            if pick_role is not None:
                self.red_pick_roles.append(pick_role)

    def add_ban(self, team_color, hero_id):
        if team_color == "Blue":
            self.blue_actions[0].append(hero_id)
        else:
            self.red_actions[0].append(hero_id)

    def filter_pick_roles(self, hero_id, team_pick_roles):
        # Deciding what role to get if hero has 2 roles
        hero_role = get_role(hero_id, self.hero_roles)
        if len(hero_role) == 1:
            if hero_role[0] not in team_pick_roles:
                return hero_role[0]
        elif len(hero_role) == 2:
            if hero_role[0] not in team_pick_roles:
                return hero_role[0]
            elif hero_role[0] in team_pick_roles and hero_role[1] not in team_pick_roles:
                return hero_role[1]
        return None

    def filter_predictions(self, valid_heroes, valid_predictions, team_pick_roles, enemy_pick_roles, is_picking, level):
        if is_picking:
            valid_predictions_filtered = []
            for hero_id, prediction in zip(valid_heroes, valid_predictions):
                if len(team_pick_roles) == 2: # added to avoid returning None for mirrored drafting on phase 1
                    if self.filter_pick_roles(hero_id, enemy_pick_roles) is not None and self.filter_pick_roles(hero_id, team_pick_roles) is not None:
                        valid_predictions_filtered.append(prediction)

                else:
                    if self.filter_pick_roles(hero_id, team_pick_roles) is not None:
                        valid_predictions_filtered.append(prediction)

            if not valid_predictions_filtered:
                next_hero_id = random.choice(valid_heroes)
                print("Random selection:", next_hero_id)
            else:
                # Obtain the indices of the top predictions
                top_prediction_indices = np.argsort(valid_predictions_filtered)[level:]
                # Select a random prediction among the top predictions
                random_prediction_idx = random.choice(top_prediction_indices)

                next_hero_id = valid_heroes[valid_predictions.index(valid_predictions_filtered[random_prediction_idx])]
                prediction_probability = valid_predictions_filtered[random_prediction_idx]
                print("Model prediction:", get_name(next_hero_id, self.hero_names), "| Probability -", prediction_probability)

        else:
            valid_predictions_filtered = []
            for hero_id, prediction in zip(valid_heroes, valid_predictions):
                if len(team_pick_roles) < 3:
                    if self.filter_pick_roles(hero_id, enemy_pick_roles)  is not None:
                            valid_predictions_filtered.append(prediction)
                else:
                    if self.filter_pick_roles(hero_id, enemy_pick_roles)  is not None and self.filter_pick_roles(hero_id, enemy_pick_roles) in team_pick_roles:
                            valid_predictions_filtered.append(prediction)


            if not valid_predictions_filtered:
                next_hero_id = random.choice(valid_heroes)
                print("Random selection:", next_hero_id)
            else:
                # Obtain the indices of the top predictions
                top_prediction_indices = np.argsort(valid_predictions_filtered)[level:]
                # Select a random prediction among the top predictions
                random_prediction_idx = random.choice(top_prediction_indices)

                next_hero_id = valid_heroes[valid_predictions.index(valid_predictions_filtered[random_prediction_idx])]
                prediction_probability = valid_predictions_filtered[random_prediction_idx]
                print("Model prediction:", get_name(next_hero_id, self.hero_names), "| Probability -", prediction_probability)

        return next_hero_id
