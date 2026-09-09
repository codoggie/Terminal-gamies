import sys, storage, display

def run_leaderboard_protocol():
    top_scores = storage.get_top_scores(8)
    display.draw_leaderboard_screen(top_scores)
    while True:
        if sys.platform == "win32":
            import msvcrt
            key = msvcrt.getch().lower()
        else:
            import tty, termios, select
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                key = sys.stdin.read(1).encode('utf-8').lower() if rlist else b''
            finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if key in [b'\x1b', b'\r', b'\n']: return
