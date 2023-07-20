from player import HumanPlayer, AIPlayer
from utils import print_draft_status, print_final_draft
import threading

# Define the indices for blue and red turns
blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]
red_turn = [1, 3, 5, 7, 8, 11, 12, 14, 16, 19]

# Define the indices for picks and bans
pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
ban_indices = [0, 1, 2, 3, 4, 5, 12, 13, 14, 15]

def run_human_vs_human(draft_state):
    blue_player = HumanPlayer("Blue")
    red_player = HumanPlayer("Red")

    for i in range(20):
        if i in blue_turn:
            player = blue_player
        else:
            player = red_player

        if i in pick_indices:
            player.pick(draft_state)
        else:
            player.ban(draft_state)

        print_draft_status(draft_state)

    print_final_draft(draft_state)

def run_human_vs_ai(draft_state, model_path):
    blue_player = HumanPlayer("Blue")
    red_player = AIPlayer("Red", model_path)

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


def run_ai_vs_human(draft_state, model_path):
    blue_player = AIPlayer("Blue", model_path)
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




