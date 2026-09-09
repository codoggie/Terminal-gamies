import sys
import storage
import display

def run_leaderboard_protocol():
    top_scores = storage.get_top_scores(8)
    display.draw_leaderboard_screen(top_scores)
    while True:
        key = display.time.msvcrt.getch().lower() if hasattr(display.time, 'msvcrt') else None
        if not key:
            import msvcrt
            key = msvcrt.getch().lower()
        if key in [b'\x1b', b'\r', b'\n']:
            return
