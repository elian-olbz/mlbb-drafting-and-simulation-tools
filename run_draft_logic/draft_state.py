import csv
import random
from tensorflow.lite.python.interpreter import Interpreter
import numpy as np
import time

num_heroes = 122

class DraftState:
    def __init__(self, model_path, hero_roles_path):
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.hero_roles = {}
        self.hero_names = []
        self.draft_sequence = []
        self.final_sequence = []
        self.blue_actions = [[], []]  # blue ban is [0], blue picks is [1]
        self.red_actions = [[], []]  # red ban is [0], red picks is [1]
        self.blue_pick_roles = []
        self.red_pick_roles = []
        self.load_hero_roles(hero_roles_path)

    def load_hero_roles(self, hero_roles_path):
        with open(hero_roles_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hero_id = int(row['HeroID'])
                roles = [role.strip() for role in row['Role'].split('/')]
                self.hero_roles[hero_id] = roles
                hero_name = row['Name']
                self.hero_names.append(hero_name)

    def get_name(self, hero_id):
        return self.hero_names[hero_id - 1]

    def get_role(self, hero_id):
        return self.hero_roles.get(hero_id, [])

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
        hero_role = self.get_role(hero_id)
        if len(hero_role) == 1:
            if hero_role[0] not in team_pick_roles:
                return hero_role[0]
        elif len(hero_role) == 2:
            if hero_role[0] not in team_pick_roles:
                return hero_role[0]
            elif hero_role[0] in team_pick_roles and hero_role[1] not in team_pick_roles:
                return hero_role[1]
        return None

    def filter_predictions(self, valid_heroes, valid_predictions, team_pick_roles, enemy_pick_roles, is_picking):
        if is_picking:
            valid_predictions_filtered = []
            for hero_id, prediction in zip(valid_heroes, valid_predictions):
                if self.filter_pick_roles(hero_id, team_pick_roles) is not None:
                    valid_predictions_filtered.append(prediction)

            if not valid_predictions_filtered:
                next_hero_id = random.choice(valid_heroes)
                print("Random selection:", next_hero_id)
            else:
                # Obtain the indices of the top predictions
                top_prediction_indices = np.argsort(valid_predictions_filtered)[-1:]
                # Select a random prediction among the top predictions
                random_prediction_idx = random.choice(top_prediction_indices)

                next_hero_id = valid_heroes[valid_predictions.index(valid_predictions_filtered[random_prediction_idx])]
                prediction_probability = valid_predictions_filtered[random_prediction_idx]
                print("Model prediction:", self.get_name(next_hero_id), "| Probability -", prediction_probability)

        else:
            valid_predictions_filtered = []
            for hero_id, prediction in zip(valid_heroes, valid_predictions):
                if self.filter_pick_roles(hero_id, enemy_pick_roles)  is not None:
                        valid_predictions_filtered.append(prediction)

            if not valid_predictions_filtered:
                next_hero_id = random.choice(valid_heroes)
                print("Random selection:", next_hero_id)
            else:
                # Obtain the indices of the top predictions
                top_prediction_indices = np.argsort(valid_predictions_filtered)[-3:]
                # Select a random prediction among the top predictions
                random_prediction_idx = random.choice(top_prediction_indices)

                next_hero_id = valid_heroes[valid_predictions.index(valid_predictions_filtered[random_prediction_idx])]
                prediction_probability = valid_predictions_filtered[random_prediction_idx]
                print("Model prediction:", self.get_name(next_hero_id), "| Probability -", prediction_probability)

        return next_hero_id

    def generate_draft_sequence(self, padded_sequence, team_color, is_picking):
        time.sleep(1)  # Delay for x seconds
        
        input_data = np.array(padded_sequence, dtype=np.float32)
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Set input tensor
        self.interpreter.set_tensor(input_details[0]['index'], input_data)

        # Run inference
        self.interpreter.invoke()

        # Get output tensor
        output_data = self.interpreter.get_tensor(output_details[0]['index'])

        predictions = output_data[0]
        
        valid_heroes = [hero_id for hero_id in range(num_heroes - 1) if hero_id not in self.draft_sequence]
        valid_predictions = [predictions[hero_id] for hero_id in valid_heroes]

        if not valid_predictions:
            next_hero_id = random.choice(valid_heroes)
            print("Random selection:", next_hero_id)
        else:
            if team_color == 'Blue':
                next_hero_id = self.filter_predictions(valid_heroes, valid_predictions, self.blue_pick_roles, self.red_pick_roles, is_picking)
            elif team_color == 'Red':
                next_hero_id = self.filter_predictions(valid_heroes, valid_predictions, self.red_pick_roles, self.blue_pick_roles, is_picking)

        return next_hero_id
