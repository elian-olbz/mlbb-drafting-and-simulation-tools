from run_draft_logic.draft_state import DraftState
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.lite.python.interpreter import Interpreter
import numpy as np

max_sequence_length = 19

# Define the indices for blue and red turns
blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]
red_turn = [1, 3, 5, 7, 8, 11, 12, 14, 16, 19]

# Define the indices for picks and bans
pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
ban_indices = [0, 1, 2, 3, 4, 5, 12, 13, 14, 15]

class HumanPlayer:
    def __init__(self, team_color):
        self.team_color = team_color
        
    def pick(self, draft_state, hero_id):
        if hero_id is not None:
            while True:
                if hero_id not in draft_state.draft_sequence:
                    break
                print("Invalid Move!")
            draft_state.draft_sequence.append(hero_id)
            draft_state.final_sequence.append(hero_id)
            draft_state.add_pick(self.team_color, hero_id)

    def ban(self, draft_state, hero_id):
        if hero_id is not None:
            while True:
                if hero_id not in draft_state.draft_sequence:
                    break
                print("Invalid Move!")
            draft_state.draft_sequence.append(hero_id)
            draft_state.final_sequence.append(hero_id)
            draft_state.add_ban(self.team_color, hero_id)
            


class AIPlayer:
    def __init__(self, team_color, model_path):
        self.team_color = team_color
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

    def pick(self, draft_state):
        while True:
            padded_sequence = pad_sequences([draft_state.draft_sequence], maxlen=max_sequence_length, padding='post')
            next_hero_id = draft_state.generate_draft_sequence(padded_sequence, self.team_color, True)
            if next_hero_id not in draft_state.draft_sequence:
                break
        draft_state.draft_sequence.append(next_hero_id)
        draft_state.final_sequence.append(next_hero_id)
        draft_state.add_pick(self.team_color, next_hero_id)
        print(f"{self.team_color} Pick:", draft_state.get_name(next_hero_id))

    def ban(self, draft_state):
        while True:
            padded_sequence = pad_sequences([draft_state.draft_sequence], maxlen=max_sequence_length, padding='post')
            next_ban_id = draft_state.generate_draft_sequence(padded_sequence, self.team_color, False)
            if next_ban_id not in draft_state.draft_sequence:
                break
        draft_state.draft_sequence.append(next_ban_id)
        draft_state.final_sequence.append(next_ban_id)
        draft_state.add_ban(self.team_color, next_ban_id)
        print(f"{self.team_color} Ban:", draft_state.get_name(next_ban_id))
