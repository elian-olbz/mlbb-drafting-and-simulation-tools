from draft_state import DraftState
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import numpy as np

max_sequence_length = 19

class HumanPlayer:
    def __init__(self, team_color):
        self.team_color = team_color

    def pick(self, draft_state):
        while True:
            pick_id = int(input(f"{self.team_color} pick: "))
            if pick_id not in draft_state.draft_sequence:
                break
            print("Invalid Move!")
        draft_state.draft_sequence.append(pick_id)
        draft_state.final_sequence.append(pick_id)
        draft_state.add_pick(self.team_color, pick_id)

    def ban(self, draft_state):
        while True:
            ban_id = int(input(f"{self.team_color} ban: "))
            if ban_id not in draft_state.draft_sequence:
                break
            print("Invalid Move!")
        draft_state.draft_sequence.append(ban_id)
        draft_state.final_sequence.append(ban_id)
        draft_state.add_ban(self.team_color, ban_id)


class AIPlayer:
    def __init__(self, team_color, model_path):
        self.team_color = team_color
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
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
