from draft_state import DraftState
from modes import run_human_vs_human, run_ai_vs_human, run_human_vs_ai, run_ai_vs_ai

# ... (previous code)
model_path1 = 'model/meta_ld_512_x5h.tflite'
model_path2 = 'model/meta_ld_512_x5h.tflite'
hero_roles = 'data/hero_roles.csv'

def main():
    mode = input("Select mode (1: Human vs. Human, 2: AI vs. Human, 3: Human vs. AI, 4: AI vs. AI): ")

    draft_state = DraftState(model_path1, hero_roles)

    if mode == '1':
        run_human_vs_human(draft_state)
    elif mode == '2':
        run_human_vs_ai(draft_state, model_path1)
    elif mode == '3':
        run_ai_vs_human(draft_state, model_path1)
    elif mode == '4':
        run_ai_vs_ai(draft_state, model_path2, model_path1)
    else:
        print("Invalid mode selected.")

if __name__ == "__main__":
    main()
