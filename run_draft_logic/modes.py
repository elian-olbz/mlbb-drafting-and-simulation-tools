from run_draft_logic.player import HumanPlayer, AIPlayer
from run_draft_logic.utils import print_draft_status, print_final_draft

# Define the indices for blue and red turns
blue_turn = [0, 2, 4, 6, 9, 10, 13, 15, 17, 18]
red_turn = [1, 3, 5, 7, 8, 11, 12, 14, 16, 19]

# Define the indices for picks and bans
pick_indices = [6, 7, 8, 9, 10, 11, 16, 17, 18, 19]
ban_indices = [0, 1, 2, 3, 4, 5, 12, 13, 14, 15]

def human_vs_human():
    blue_player = HumanPlayer("Blue")
    red_player = HumanPlayer("Red")
    mode = 'HvH'

    return blue_player, red_player, mode

def human_vs_ai():
    blue_player = HumanPlayer("Blue")
    red_player = AIPlayer("Red")
    mode = 'HvA'
    return blue_player, red_player, mode

def ai_vs_human():
    blue_player = AIPlayer("Blue")
    red_player = HumanPlayer("Red")
    mode = 'AvH'
    return blue_player, red_player, mode