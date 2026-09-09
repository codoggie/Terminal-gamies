import sys, time, os
import storage, display, engine, scoreboard

if sys.platform == "win32":
    import msvcrt
    def read_raw_keystroke():
        if msvcrt.kbhit(): return msvcrt.getch()
        return None
else:
    import termios, tty, select
    def read_raw_keystroke():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], 0.005)
            if rlist: return sys.stdin.read(1).encode('utf-8')
            return None
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class GameController:
    def __init__(self):
        storage.load_data()
        try: self.username = os.getlogin()
        except: self.username = os.environ.get("USERNAME", os.environ.get("USER", "PLAYER"))
        self.username = self.username.strip()[:14]
        self.console_logs = ["[SYSTEM]: Dev sub-terminal interface mounted. Enter /help"]
        self.command_input = ""
        self.dev_mode_active = False
        self.help_mode_active = False

    def read_keyboard_input(self, inst=None):
        k = read_raw_keystroke()
        if not k: return None
        if k == b'\x1d': return 'TOGGLE_CON'
        kl = k.lower()
        if kl in [b'\x00', b'\xe0']:
            if sys.platform == "win32":
                import msvcrt
                k = msvcrt.getch().lower()
                m = {b'h': 'UP', b'p': 'DOWN', b'k': 'LEFT', b'm': 'RIGHT'}
                if k in m and inst: inst.change_direction(m[k])
            return None
        if kl == b'\x1b': return 'ESC'
        if kl in (b'\r', b'\n'): return 'ENTER'
        if kl == b' ':
            if inst: inst.trigger_sprint()
            return 'SPACE'
        if kl == b'q': return 'Q'
        if kl == b'w' and inst: inst.change_direction('UP')
        if kl == b's' and inst: inst.change_direction('DOWN')
        if kl == b'a' and inst: inst.change_direction('LEFT')
        if kl == b'd' and inst: inst.change_direction('RIGHT')
        return None

    def run_menu_protocol(self):
        sel = 0; display.draw_main_menu(sel)
        while True:
            k = read_raw_keystroke()
            if k:
                kl = k.lower()
                if kl == b'w':
                    sel = (sel - 1) % 3; display.draw_main_menu(sel)
                elif kl == b's':
                    sel = (sel + 1) % 3; display.draw_main_menu(sel)
                elif kl in (b'\r', b'\n'): return sel
            time.sleep(0.005)

    def run_pause_protocol(self):
        display.draw_pause_overlay()
        while True:
            k = read_raw_keystroke()
            if k and k.lower() == b'\x1b': return 'RESUME'
            if k and k.lower() == b'q': return 'QUIT'
            time.sleep(0.005)

    def run_dev_console_loop(self, inst):
        display.draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)
        while self.dev_mode_active:
            char = read_raw_keystroke()
            if char:
                if char == b'\r' or char == b'\n':
                    cmd_string = self.command_input.strip().lower()
                    if cmd_string == "exit":
                        self.dev_mode_active = False
                        display.draw_static_game_frame(); return
                    elif cmd_string == "/help":
                        self.help_mode_active = True
                        self.console_logs.append(">> /help")
                    elif cmd_string == "clearlogs":
                        self.console_logs = ["[SYSTEM]: Logs Cleared."]
                    elif cmd_string == "setcheats=0":
                        inst.cheats_active = False
                        inst.exp_factor = 1.0; inst.combo_factor = 1.0
                        inst.ghost_mode = False; inst.freeze_timers = False
                        storage.save_cheat_modifiers(1.0, 1.0)
                        self.console_logs.append("[SYSTEM]: All active developer cheats set to false.")

                    elif "=" in cmd_string:
                        if not inst.cheats_active:
                            self.console_logs.append("[DENIED]: Cheats are locked to false.")
                        else:
                            parts = cmd_string.split("=")
                            action, val_str = parts[0].strip(), parts[1].strip()
                            try:
                                val = int(val_str)
                                if action == "setcombo" and 1 <= val <= 10:
                                    inst.combo_multiplier = val
                                    inst.freeze_timers = True
                                    self.console_logs.append(f"[SUCCESS]: Constant combo points set to {val}")
                                elif action == "setlevel" and 1 <= val <= 10:
                                    inst.level = val; inst.items_eaten = 0
                                    self.console_logs.append(f"[SUCCESS]: Active level tier transformed to {val}")
                                elif action == "setpoints" and val >= 0:
                                    inst.experience = val; inst.validate_vitals()
                                    self.console_logs.append(f"[SUCCESS]: Experience points set to {val}")
                                elif action == "setexpfactor" and 2 <= val <= 6:
                                    inst.exp_factor = float(val); storage.save_cheat_modifiers(inst.exp_factor, inst.combo_factor)
                                    self.console_logs.append(f"[SUCCESS]: Exp multiplier scaled to {val}x")
                                elif action == "setcombofactor" and 2 <= val <= 6:
                                    inst.combo_factor = float(val); storage.save_cheat_modifiers(inst.exp_factor, inst.combo_factor)
                                    self.console_logs.append(f"[SUCCESS]: Combo score yield boosted to {val}x")
                                elif action in ("ghostmode", "freezetimers", "warpsize"):
                                    log_msg = inst.execute_extended_cheat(action, val_str)
                                    self.console_logs.append(log_msg)
                            except: self.console_logs.append("[ERROR]: Parameter parsing fault.")
                    elif cmd_string == "spawnsuperfood":
                        if not inst.cheats_active: self.console_logs.append("[DENIED]: Cheats are false.")
                        else:
                            inst.super_food_active = True
                            self.console_logs.append("[SUCCESS]: Next item dropped as super variant.")
                    else:
                        if cmd_string != "": self.console_logs.append(f"[ERROR]: Invalid command token '{cmd_string}'")
                    self.command_input = ""
                    display.draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)

                elif ord(char) in (8, 127):
                    self.command_input = self.command_input[:-1]
                    display.draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)
                elif char != b'\x1d':
                    try:
                        decoded = char.decode('utf-8')
                        if len(decoded) == 1 and ord(decoded) >= 32:
                            self.command_input += decoded
                            display.draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)
                    except: pass
            time.sleep(0.01)

    def run_gameplay_core(self):
        inst = engine.GameEngine(self.username); display.draw_static_game_frame()
        tick, start, lp = 0, time.time(), set()
        while True:
            input_signal = self.read_keyboard_input(inst)
            if input_signal == 'TOGGLE_CON':
                self.dev_mode_active = True; self.run_dev_console_loop(inst)
                lp.clear(); continue
            if input_signal == 'ESC':
                if self.run_pause_protocol() == 'QUIT': return
                display.draw_static_game_frame(); lp.clear()
            if not inst.step():
                storage.register_run(self.username, inst.score, inst.level, int(time.time() - start))
                self.run_game_over_protocol(inst.score); return
            cp = set()
            food_color = display.get_pulsing_color(tick, "SUPER") if inst.is_super_food else "\033[38;5;203m"
            food_char = "★" if inst.is_super_food else "⌺"
            display.move_cursor(inst.food[1], inst.food[0]); sys.stdout.write(f"{food_color}{food_char}\033[0m")
            cp.add((inst.food[0], inst.food[1]))
            for idx, seg in enumerate(inst.snake):
                display.move_cursor(seg[1], seg[0])
                if idx == 0:
                    d = inst.direction
                    sys.stdout.write(f"\033[38;5;46m{'▲' if d==(0,-1) else '▼' if d==(0,1) else '◀' if d==(-1,0) else '▶'}\033[0m")
                else: sys.stdout.write("\033[32m■\033[0m")
                cp.add((seg[0], seg[1]))
            for ox, oy in lp:
                if (ox, oy) not in cp: display.move_cursor(oy, ox); sys.stdout.write(" ")
            lp = cp; display.update_hud_dashboard(inst.get_hud_stats(), tick); tick += 1
            sp = max(0.02, 0.06 - (inst.level * 0.005))
            time.sleep(sp * 0.4 if inst.is_sprinting else sp)

    def run_game_over_protocol(self, score):
        top = storage.load_data()["global_leaderboard"]
        display.draw_game_over_screen(score, top["high_score"] if top else score)
        while True:
            k = read_raw_keystroke()
            if k:
                if k.lower() == b' ': self.run_gameplay_core(); return
                if k.lower() == b'\x1b': return
            time.sleep(0.005)

    def master_runtime_loop(self):
        display.boot_sequence()
        while True:
            route = self.run_menu_protocol()
            if route == 0: self.run_gameplay_core()
            elif route == 1: scoreboard.run_leaderboard_protocol()
            elif route == 2: display.clear_screen(); display.show_cursor(); break

if __name__ == '__main__': GameController().master_runtime_loop()
