def print_draft_status(draft_state):
    print("=========== Draft Status ===========")
    print("Blue Bans:  ", ', '.join(draft_state.get_name(hero_id) for hero_id in draft_state.blue_actions[0]))
    print("Blue Picks: ", ', '.join(draft_state.get_name(hero_id) for hero_id in draft_state.blue_actions[1]))
    print("Blue roles: {}".format(draft_state.blue_pick_roles))
    print("")
    print("Red Bans:   ", ', '.join(draft_state.get_name(hero_id) for hero_id in draft_state.red_actions[0]))
    print("Red Picks:  ", ', '.join(draft_state.get_name(hero_id) for hero_id in draft_state.red_actions[1]))
    print("Red roles: {}".format(draft_state.red_pick_roles))
    print("====================================\n\n")

def print_final_draft(draft_state):
    print("Final draft:")
    print("Blue Team: ", ', '.join(draft_state.get_name(hero_id) for hero_id in draft_state.blue_actions[1]))
    print("Red Team:  ", ', '.join(draft_state.get_name(hero_id) for hero_id in draft_state.red_actions[1]))
