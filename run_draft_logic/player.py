from run_draft_logic.utils import get_name
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import time
import random

max_sequence_length = 19
num_heroes = 122

class HumanPlayer:
    def __init__(self, team_color):
        self.team_color = team_color
        
    def pick(self, draft_state, hero_id):
        if hero_id is not None and hero_id not in draft_state.draft_sequence:
            draft_state.draft_sequence.append(hero_id)
            draft_state.final_sequence.append(hero_id)
            draft_state.add_pick(self.team_color, hero_id)
        else:
            return

    def ban(self, draft_state, hero_id):
        if hero_id is not None and hero_id not in draft_state.draft_sequence:
            draft_state.draft_sequence.append(hero_id)
            draft_state.final_sequence.append(hero_id)
            draft_state.add_ban(self.team_color, hero_id)
        else:
            return
            

class AIPlayer:
    def __init__(self, team_color):
        self.team_color = team_color
        self.interpreter = None

    def pick(self, draft_state):
        while True:
            padded_sequence = pad_sequences([draft_state.draft_sequence], maxlen=max_sequence_length, padding='post')
            next_hero_id = self.generate_predictions(draft_state, padded_sequence, self.team_color, True)
            if next_hero_id not in draft_state.draft_sequence:
                break
        draft_state.draft_sequence.append(next_hero_id)
        draft_state.final_sequence.append(next_hero_id)
        draft_state.add_pick(self.team_color, next_hero_id)
        #print(f"{self.team_color} Pick:", get_name(next_hero_id, draft_state.hero_names))
        return next_hero_id

    def ban(self, draft_state):
        while True:
            padded_sequence = pad_sequences([draft_state.draft_sequence], maxlen=max_sequence_length, padding='post')
            next_ban_id = self.generate_predictions(draft_state, padded_sequence, self.team_color, False)
            if next_ban_id not in draft_state.draft_sequence:
                break
        draft_state.draft_sequence.append(next_ban_id)
        draft_state.final_sequence.append(next_ban_id)
        draft_state.add_ban(self.team_color, next_ban_id)
        #print(f"{self.team_color} Ban:", get_name(next_ban_id, draft_state.hero_names))
        return next_ban_id


    def generate_predictions(self, draft_state, padded_sequence, team_color, is_picking):
        if self.interpreter is not None:
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
            
            valid_heroes = [hero_id for hero_id in range(num_heroes - 1) if hero_id not in draft_state.draft_sequence]
            valid_predictions = [predictions[hero_id] for hero_id in valid_heroes]

            if not valid_predictions:
                next_hero_id = random.choice(valid_heroes)
                #print("Random selection:", next_hero_id)
            else:
                if team_color == 'Blue':
                    next_hero_id = draft_state.filter_predictions(valid_heroes, valid_predictions, draft_state.blue_pick_roles, draft_state.red_pick_roles, is_picking, draft_state.ai_level)
                elif team_color == 'Red':
                    next_hero_id = draft_state.filter_predictions(valid_heroes, valid_predictions, draft_state.red_pick_roles, draft_state.blue_pick_roles, is_picking, draft_state.ai_level)

        return next_hero_id
