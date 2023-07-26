from run_draft_logic.player import HumanPlayer, AIPlayer
from run_draft_logic.utils import print_draft_status, print_final_draft
import threading

# Define the indices for blue and red turns
blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]
red_turn = [1, 3, 5, 7, 8, 11, 12, 14, 16, 19]

# Define the indices for picks and bans
pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
ban_indices = [0, 1, 2, 3, 4, 5, 12, 13, 14, 15]

def human_vs_human():
    blue_player = HumanPlayer("Blue")
    red_player = HumanPlayer("Red")

    return blue_player, red_player

def ai_vs_ai():
    blue_player = AIPlayer("Blue", 'model/meta_ld_512_x5h.tflite')
    red_player = AIPlayer("Red", 'model/meta_ld_512_x5h.tflite')

    return blue_player, red_player

def human_vs_ai():
    blue_player = HumanPlayer("Blue")
    red_player = AIPlayer("Red", 'model/meta_ld_512_x5h.tflite')

    return blue_player, red_player


def ai_vs_human(draft_state):
    blue_player = AIPlayer("Blue", draft_state)
    red_player = HumanPlayer("Red")

    for i in range(20):
        if i in blue_turn:
            if i in pick_indices:
                blue_player.pick(draft_state)
            else:
                blue_player.ban(draft_state)
        else:
            if i in pick_indices:
                red_player.pick(draft_state)
            else:
                red_player.ban(draft_state)

        print_draft_status(draft_state)

    print_final_draft(draft_state)


def run_ai_vs_ai(draft_state, model_path1, model_path2):
    blue_player = AIPlayer("Blue", model_path1)
    red_player = AIPlayer("Red", model_path2)

    # Create locks for synchronization
    blue_lock = threading.Lock()
    red_lock = threading.Lock()

    for i in range(20):
        if i in blue_turn:
            if i in pick_indices:
                with blue_lock:
                    blue_player.pick(draft_state)
            else:
                with blue_lock:
                    blue_player.ban(draft_state)
            print_draft_status(draft_state)
        else:
            if i in pick_indices:
                with red_lock:
                    red_player.pick(draft_state)
            else:
                with red_lock:
                    red_player.ban(draft_state)
            print_draft_status(draft_state)

    print_final_draft(draft_state)


"""
def player_pick(self, draft_state, selected_id):
    print("player pick called")
    blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]

    if type(self.blue_player) is HumanPlayer:  # If blue player is human
        if abs(self.remaining_clicks - 20) in blue_turn:
            self.blue_player.pick(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

    else: # If blue player is AI
        if abs(self.remaining_clicks - 20) in blue_turn:
            self.hero_to_disp = self.blue_player.pick(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

    if type(self.red_player) is HumanPlayer:  # If red player is human
        if abs(self.remaining_clicks - 20) not in blue_turn:
            self.red_player.pick(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

    else:  # If red player is AI
        if abs(self.remaining_clicks - 20) not in blue_turn:
            self.hero_to_disp = self.red_player.pick(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

def player_ban(self, draft_state, selected_id):
    print("player ban called")
    blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]

    if type(self.blue_player) is HumanPlayer:  # If blue player is human
        if abs(self.remaining_clicks - 20) in blue_turn:
            self.blue_player.ban(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None
    else: # If blue player is AI
        if abs(self.remaining_clicks - 20) in blue_turn:
            self.hero_to_disp = self.blue_player.ban(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None

    if type(self.red_player) is HumanPlayer:  # If red player is human
        if abs(self.remaining_clicks - 20) not in blue_turn:
            self.red_player.ban(draft_state, selected_id)
            self.hero_to_disp = selected_id
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None
    else:  # If red player is AI
        if abs(self.remaining_clicks - 20) not in blue_turn:
            self.hero_to_disp = self.red_player.ban(draft_state)
            print_draft_status(draft_state)
            self.display_clicked_image(self.hero_to_disp)
            self.hero_to_disp = None
"""


