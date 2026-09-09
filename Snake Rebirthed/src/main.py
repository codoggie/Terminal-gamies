import sys, time, msvcrt, os
import storage, display, engine, scoreboard

class GameController:
    def __init__(self):
        storage.load_data()
        try: self.username = os.getlogin()
        except: self.username = os.environ.get("USERNAME", os.environ.get("USER", "PLAYER"))
        self.username = self.username.strip()[:14]

    def read_keyboard_input(self, inst=None):
        if msvcrt.kbhit():
            k = msvcrt.getch().lower()
            if k in [b'\x00', b'\xe0']:
                k = msvcrt.getch().lower()
                m = {b'h': 'UP', b'p': 'DOWN', b'k': 'LEFT', b'm': 'RIGHT'}
                if k in m and inst: inst.change_direction(m[k])
                return None
            if k == b'\x1b': return 'ESC'
            if k in [b'\r', b'\n']: return 'ENTER'
            if k == b' ':
                if inst: inst.trigger_sprint()
                return 'SPACE'
            if k == b'q': return 'Q'
            if k == b'w' and inst: inst.change_direction('UP')
            if k == b's' and inst: inst.change_direction('DOWN')
            if k == b'a' and inst: inst.change_direction('LEFT')
            if k == b'd' and inst: inst.change_direction('RIGHT')
        return None

    def run_menu_protocol(self):
        sel = 0; display.draw_main_menu(sel)
        while True:
            k = msvcrt.getch().lower()
            if k in [b'\x00', b'\xe0']:
                k = msvcrt.getch().lower()
                sel = (sel - 1) % 3 if k == b'h' else (sel + 1) % 3 if k == b'p' else sel
                display.draw_main_menu(sel)
            elif k == b'w': sel = (sel - 1) % 3; display.draw_main_menu(sel)
            elif k == b's': sel = (sel + 1) % 3; display.draw_main_menu(sel)
            elif k in [b'\r', b'\n']: return sel

    def run_pause_protocol(self):
        display.draw_pause_overlay()
        while True:
            k = msvcrt.getch().lower()
            if k == b'\x1b': return 'RESUME'
            if k == b'q': return 'QUIT'

    def run_gameplay_core(self):
        inst = engine.GameEngine(self.username); display.draw_static_game_frame()
        tick, start, lp = 0, time.time(), set()
        while True:
            if self.read_keyboard_input(inst) == 'ESC':
                if self.run_pause_protocol() == 'QUIT': return
                display.draw_static_game_frame(); lp.clear()
            if not inst.step():
                storage.register_run(self.username, inst.score, inst.level, int(time.time() - start))
                self.run_game_over_protocol(inst.score); return
            cp = set()
            display.move_cursor(inst.food[1], inst.food[0]); sys.stdout.write("\033[91m⌺\033[0m")
            cp.add((inst.food[0], inst.food[1]))
            for idx, seg in enumerate(inst.snake):
                display.move_cursor(seg[1], seg[0])
                if idx == 0:
                    d = inst.direction
                    sys.stdout.write(f"\033[92m{'▲' if d==engine.DIR_UP else '▼' if d==engine.DIR_DOWN else '◀' if d==engine.DIR_LEFT else '▶'}\033[0m")
                else: sys.stdout.write("\033[32m■\033[0m")
                cp.add((seg[0], seg[1]))
            for ox, oy in lp:
                if (ox, oy) not in cp: display.move_cursor(oy, ox); sys.stdout.write(" ")
            lp = cp; display.update_hud_dashboard(inst.get_hud_stats(), tick); tick += 1
            sp = max(0.03, 0.08 - (inst.level * 0.007))
            time.sleep(sp * 0.4 if inst.is_sprinting else sp)

    def run_game_over_protocol(self, score):
        top = storage.load_data()["global_leaderboard"]
        display.draw_game_over_screen(score, top[0]["high_score"] if top else score)
        while True:
            k = msvcrt.getch().lower()
            if k == b' ': self.run_gameplay_core(); return
            if k == b'\x1b': return

    def master_runtime_loop(self):
        display.boot_sequence()
        while True:
            route = self.run_menu_protocol()
            if route == 0: self.run_gameplay_core()
            elif route == 1: scoreboard.run_leaderboard_protocol()
            elif route == 2: display.clear_screen(); display.show_cursor(); break

if __name__ == '__main__':
    GameController().master_runtime_loop()
