import os, sys, time, json, random, math
from datetime import datetime

LEADERBOARD_FILE = "snake_vitals_data.json"
GLOBAL_CLOUD_API = "https://kvdb.io"

try:
    import urllib.request
    HAS_NETWORK = True
except ImportError:
    HAS_NETWORK = False

def init_storage():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump({"global_leaderboard": [], "session_runs_log": [], "developer_profiles": {"saved_exp_factor": 1.0, "saved_combo_factor": 1.0}}, f, indent=4)

def load_data():
    init_storage()
    local_data = {"global_leaderboard": [], "session_runs_log": [], "developer_profiles": {"saved_exp_factor": 1.0, "saved_combo_factor": 1.0}}
    try:
        with open(LEADERBOARD_FILE, 'r') as f: local_data = json.load(f)
    except: pass
    if HAS_NETWORK:
        try:
            req = urllib.request.Request(GLOBAL_CLOUD_API, method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as response:
                cloud_board = json.loads(response.read().decode('utf-8'))
                if isinstance(cloud_board, list):
                    local_data["global_leaderboard"] = cloud_board
        except: pass
    return local_data

def save_data(data):
    try:
        with open(LEADERBOARD_FILE, 'w') as f: json.dump(data, f, indent=4)
    except: pass

    if HAS_NETWORK and "global_leaderboard" in data:
        try:
            req = urllib.request.Request(
                GLOBAL_CLOUD_API,
                data=json.dumps(data["global_leaderboard"]).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as response: pass
        except: pass

def register_run(username, score, max_level, execution_time):
    data = load_data()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["session_runs_log"].append({"username": username, "score": score, "level": max_level, "seconds": execution_time, "date": timestamp})
    leaderboard = data["global_leaderboard"]
    p_rec = next((i for i in leaderboard if i["username"].lower() == username.lower()), None)
    if p_rec:
        if score > p_rec["high_score"]:
            p_rec["high_score"], p_rec["max_level"], p_rec["last_updated"] = score, max_level, timestamp
    else:
        leaderboard.append({"username": username, "high_score": score, "max_level": max_level, "last_updated": timestamp})
    data["global_leaderboard"] = sorted(leaderboard, key=lambda x: x["high_score"], reverse=True)[:10]
    save_data(data)

def get_top_scores(limit=8): return load_data()["global_leaderboard"][:limit]
def load_cheat_modifiers(): return load_data().get("developer_profiles", {"saved_exp_factor": 1.0, "saved_combo_factor": 1.0})
def save_cheat_modifiers(exp_f, combo_f):
    data = load_data()
    data["developer_profiles"] = {"saved_exp_factor": exp_f, "saved_combo_factor": combo_f}
    save_data(data)

DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

class GameEngine:
    def __init__(self, username):
        self.username = username
        self.cheats_active = True
        mods = load_cheat_modifiers()
        self.exp_factor = mods.get("saved_exp_factor", 1.0)
        self.combo_factor = mods.get("saved_combo_factor", 1.0)
        self.super_food_active = False
        self.is_super_food = False
        self.ghost_mode = False
        self.freeze_timers = False
        self.reset()

    def reset(self):
        self.snake = [[WIDTH//2, HEIGHT//2], [WIDTH//2 - 1, HEIGHT//2], [WIDTH//2 - 2, HEIGHT//2]]
        self.direction = self.next_direction = DIR_RIGHT
        self.score, self.level, self.items_eaten = 0, 1, 0
        self.sprint_cooldown = self.sprint_duration = 0
        self.is_sprinting = False
        self.combo_multiplier, self.combo_timer = 1, 0
        self.experience = 0
        self.food = None; self.bearing_dir = "◆"; self.spawn_food()
        self.radar_distance = 0; self.update_radar()

    @property
    def experience_required(self): return int(200 * self.level * 1.5)

    def change_direction(self, act):
        if act == 'UP' and self.direction != DIR_DOWN: self.next_direction = DIR_UP
        elif act == 'DOWN' and self.direction != DIR_UP: self.next_direction = DIR_DOWN
        elif act == 'LEFT' and self.direction != DIR_RIGHT: self.next_direction = DIR_LEFT
        elif act == 'RIGHT' and self.direction != DIR_LEFT: self.next_direction = DIR_RIGHT

    def trigger_sprint(self):
        if self.sprint_cooldown == 0 and not self.is_sprinting:
            self.is_sprinting, self.sprint_duration, self.sprint_cooldown = True, max(4, 12 - (self.level // 2)), 40

    def update_radar(self):
        h = self.snake[0]
        f = self.food if self.food else [WIDTH//2, HEIGHT//2]
        dx, dy = f[0] - h[0], f[1] - h[1]
        self.radar_distance = int(math.sqrt(dx**2 + dy**2))
        if abs(dx) > abs(dy):
            self.bearing_dir = "▶" if dx > 0 else "◀"
        elif abs(dy) > abs(dx):
            self.bearing_dir = "▼" if dy > 0 else "▲"
        else:
            self.bearing_dir = "◆"

    def update_timers(self):
        if not self.freeze_timers:
            if self.combo_timer > 0:
                self.combo_timer -= 1
                if self.combo_timer == 0: self.combo_multiplier = 1
        if self.is_sprinting:
            self.sprint_duration -= 1
            if self.sprint_duration == 0: self.is_sprinting = False
        if self.sprint_cooldown > 0: self.sprint_cooldown -= 1

    def spawn_food(self):
        while True:
            rx, ry = random.randint(2, WIDTH - 1), random.randint(4, HEIGHT + 1)
            if [rx, ry] not in self.snake:
                self.food = [rx, ry]
                self.is_super_food = self.super_food_active
                self.super_food_active = False
                break

    def validate_vitals(self):
        while self.experience >= self.experience_required and self.level < 10:
            self.experience -= self.experience_required
            self.level += 1

    def execute_extended_cheat(self, action, val_str):
        if not self.cheats_active: return "[DENIED]: Dev cheats currently set to false."
        try:
            val = int(val_str)
            if action == "ghostmode":
                self.ghost_mode = (val == 1)
                return f"[SUCCESS]: Ghost collision bypass toggled to {val}"
            elif action == "freezetimers":
                self.freeze_timers = (val == 1)
                return f"[SUCCESS]: Timers frozen: {val}"
            elif action == "warpsize":
                while len(self.snake) < val: self.snake.append(list(self.snake[-1]))
                while len(self.snake) > val and len(self.snake) > 2: self.snake.pop()
                return f"[SUCCESS]: Tail restructured to length {val}"
        except: pass
        return "[ERROR]: Syntax verification failure."

    def step(self):
        self.direction = self.next_direction
        h = self.snake[0]
        nx, ny = h[0] + self.direction[0], h[1] + self.direction[1]
        if nx <= 1: nx = WIDTH
        elif nx > WIDTH: nx = 2
        if ny <= 3: ny = HEIGHT + 2
        elif ny > HEIGHT + 2: ny = 4
        nh = [nx, ny]
        if nh in self.snake and not self.ghost_mode: return False
        self.snake.insert(0, nh)
        if nh == self.food:
            food_multiplier = 3 if self.is_super_food else 1
            self.score += int((10 * self.combo_multiplier) * self.combo_factor * food_multiplier)
            self.items_eaten += 1
            base_exp = 20
            combo_exp_mult = 0.25 if self.combo_multiplier <= 2 else (0.5 * self.combo_multiplier)
            calculated_exp = int(base_exp * (1.0 + (self.level * 0.25)) * combo_exp_mult * self.exp_factor * food_multiplier)
            self.experience += calculated_exp
            if not self.freeze_timers:
                self.combo_multiplier = min(10, self.combo_multiplier + 1) if self.combo_timer > 0 else 2
                self.combo_timer = int(45 + (self.level * 1.5))
            self.validate_vitals(); self.spawn_food()
        else: self.snake.pop()
        self.update_timers(); self.update_radar(); return True

    def get_hud_stats(self):
        return {"username": self.username, "score": self.score, "combo": self.combo_multiplier, "combo_time": self.combo_timer, "level": self.level, "sprint_cd": self.sprint_cooldown, "snake_len": len(self.snake), "radar_dist": self.radar_distance, "experience": self.experience, "experience_required": self.experience_required, "exp_factor": self.exp_factor, "combo_factor": self.combo_factor, "is_super_food": self.is_super_food, "bearing_dir": self.bearing_dir}

WIDTH, HEIGHT, SIDEBAR_WIDTH = 46, 20, 34

def move_cursor(y, x): sys.stdout.write(f"\033[{y};{x}H")
def hide_cursor(): sys.stdout.write("\033[?25l"); sys.stdout.flush()
def show_cursor(): sys.stdout.write("\033[?25h"); sys.stdout.flush()
def clear_screen(): sys.stdout.write("\033[2J\033[H"); sys.stdout.flush()

def get_pulsing_color(tick, flavor="SUPER"):
    cycle = (tick // 4) % 2
    if flavor == "SUPER": return "\033[38;5;99m" if cycle == 0 else "\033[38;5;141m"
    return "\033[38;5;46m"

def draw_signature_header(y_offset=2):
    g, r = "\033[38;5;46m\033[1m", "\033[0m"
    lines = [
        " ▄████████  ███▄▄▄▄      ▄████████    ▄█   ▄█▄    ▄████████ ",
        "███    ███  ███▀▀▀██▄   ███    ███   ███ ▄███▀   ███    ███ ",
        "███    █▀   ███   ███   ███    ███   ███▐███▀    ███    █▀  ",
        "███         ███   ███   ███    ███  ▄█████▀      ███▄▄▄▄▄   ",
        "▀█████████▄ ███   ███ ▀███████████ ▀▀█████▄     ▀▀███▀▀▀▀   ",
        "         ██ ███   ███   ███    ███   ███▐███▄    ███    █▄  ",
        "   ▄█    ██ ███   ███   ███    ███   ███ ▀███▄   ███    ███ ",
        " ▄████████▀  ▀█   █▀    ███    █▀    ███   ▀█▄   ██████████ "
    ]
    for i, l in enumerate(lines):
        move_cursor(y_offset + i, 4); sys.stdout.write(f"{g}{l}{r}")

def boot_sequence():
    clear_screen(); hide_cursor(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[90m[vitals.sys // terminal interface]\033[0m")
    logs = [
        "Connecting to core...", "Allocating grid space...",
        "Syncing radar...", "Calibrating EKG graph...",
        "Loading storage database...", "Initialization database global node online."
    ]
    for i, log in enumerate(logs):
        move_cursor(13 + i, 6)
        sys.stdout.write(f"\033[38;5;46m» {log}\033[0m" if i == len(logs)-1 else f"\033[37m» {log}\033[0m")
        sys.stdout.flush(); time.sleep(0.08)

    move_cursor(20, 6); sys.stdout.write("\033[90mLOADING RUNTIME: [░░░░░░░░░░░░░░░░░░░░] 0%\033[0m"); sys.stdout.flush(); time.sleep(0.05)
    for f in range(1, 21):
        move_cursor(20, 6); sys.stdout.write(f"\033[38;5;46mLOADING RUNTIME: [{'█'*f + '░'*(20-f)}] {int((f/20)*100)}%\033[0m"); sys.stdout.flush(); time.sleep(0.01)
    time.sleep(0.1)

def draw_main_menu(sel):
    clear_screen(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[90m[vitals.sys // main menu]\033[0m")
    opts = ["INITIALIZE SNAKE PROTOCOL (PLAY)", "GLOBAL CLOUD LEADERBOARDS", "SHUT DOWN CORE TERMINAL (EXIT)"]
    for i, o in enumerate(opts):
        move_cursor(14 + (i * 2), 8)
        sys.stdout.write(f"\033[38;5;46m\033[1m» {o} \033[0m" if i == sel else f"\033[90m  {o} \033[0m")
    move_cursor(21, 6); sys.stdout.write("\033[37mUse [ W / S ] or [ ARROWS ]. Press [ ENTER ] to confirm.\033[0m"); sys.stdout.flush()

def draw_static_game_frame():
    clear_screen(); hide_cursor()
    move_cursor(1, 2); sys.stdout.write("\033[38;5;46m\033[1mVITALS ENGINE\033[0m \033[90m// TERMINAL FRAMEWORK V3.5\033[0m")
    move_cursor(3, 1); sys.stdout.write("\033[38;5;46m┌" + "─" * WIDTH + "┐\033[0m")
    for y in range(4, 4 + HEIGHT):
        move_cursor(y, 1); sys.stdout.write("\033[38;5;46m│\033[0m")
        move_cursor(y, WIDTH + 2); sys.stdout.write("\033[38;5;46m│\033[0m")
    move_cursor(4 + HEIGHT, 1); sys.stdout.write("\033[38;5;46m└" + "─" * WIDTH + "┘\033[0m")
    sbs = WIDTH + 4
    move_cursor(3, sbs); sys.stdout.write("\033[38;5;46m┌" + "─" * SIDEBAR_WIDTH + "┐\033[0m")
    for y in range(4, 4 + HEIGHT):
        move_cursor(y, sbs); sys.stdout.write("\033[38;5;46m│\033[0m")
        move_cursor(y, sbs + SIDEBAR_WIDTH + 1); sys.stdout.write("\033[38;5;46m│\033[0m")
    move_cursor(4 + HEIGHT, sbs); sys.stdout.write("\033[38;5;46m└" + "─" * SIDEBAR_WIDTH + "┘\033[0m"); sys.stdout.flush()

def draw_compass_radar(y, x, dist, bearing_dir):
    c = "\033[91m" if dist<=3 else "\033[93m" if dist<=6 else "\033[38;5;46m"
    pointer = bearing_dir if bearing_dir else "◆"
    lines = [
        f"     \033[38;5;244m[N]\033[0m     ",
        f"  \033[38;5;244m[W]\033[0m  {c}{pointer}\033[0m  \033[38;5;244m[E]\033[0m  ",
        f"     \033[38;5;244m[S]\033[0m     ",
        f" \033[38;5;248mRANGE: {dist:02d} BLK\033[0m"
    ]
    for i, l in enumerate(lines):
        move_cursor(y + i, x)
        sys.stdout.write(l)

def update_hud_dashboard(stats, tick):
    xc = WIDTH + 5
    u, s, c, ct, l, scd, slen, rdist = stats["username"], stats["score"], stats["combo"], stats["combo_time"], stats["level"], stats["sprint_cd"], stats["snake_len"], stats["radar_dist"]
    exp_curr, exp_req, b_dir = stats["experience"], stats["experience_required"], stats.get("bearing_dir", "◆")
    pct = (exp_curr / exp_req) if exp_req > 0 else 0
    bar_str = "█" * int(pct * 10) + "░" * (10 - int(pct * 10))
    sprint_str = f"\033[93mRECHARGING [{ '░'*(8-int((scd/40)*8)) + '█'*int((scd/40)*8) }]\033[0m" if scd>0 else "\033[38;5;46mREADY [████████]\033[0m"
    combo_str = f"\033[91m{c}X COMBO [{ '█'*min(8, int((ct/45)*8)) + '░'*max(0, 8-int((ct/45)*8)) }]\033[0m" if c>1 else "\033[90mNO COMBO  [░░░░░░░░]\033[0m"
    struct = f"\033[38;5;46m▲\033[0m" + f"\033[32m■\033[0m"*min(6, slen-1) + (f"\033[90m..x{slen}\033[0m" if slen>7 else "")

    move_cursor(5, xc); sys.stdout.write(f"\033[38;5;46mPLAYER     :\033[0m \033[97m[{u[:12]}]\033[0m" + " "*4)
    move_cursor(6, xc); sys.stdout.write(f"\033[38;5;46mSCORE      :\033[0m \033[97m[{s:05d}]\033[0m")
    move_cursor(7, xc); sys.stdout.write(f"\033[38;5;46mLEVEL      :\033[0m \033[97m[{l:02d}]\033[0m")
    move_cursor(9, xc); sys.stdout.write(f"\033[38;5;46mXP METRIC  :\033[0m \033[38;5;33m[{bar_str}] {exp_curr}/{exp_req}\033[0m")
    move_cursor(10, xc); sys.stdout.write(f"\033[38;5;46mCOMBO      :\033[0m {combo_str}")
    move_cursor(11, xc); sys.stdout.write(f"\033[38;5;46mSPRINT     :\033[0m {sprint_str}")
    move_cursor(12, xc); sys.stdout.write(f"\033[38;5;46mSNAKE      :\033[0m {struct}     ")
    move_cursor(16, xc); sys.stdout.write(f"\033[38;5;46mRADAR-NODE :\033[0m ")
    draw_compass_radar(16, xc + 13, rdist, b_dir)
    sys.stdout.flush()

def draw_pause_overlay():
    py, px = 10, (WIDTH // 2) - 15
    g = "\033[38;5;46m"
    move_cursor(py, px); sys.stdout.write(f"{g}┌──────────────────────────────┐\033[0m")
    move_cursor(py+1, px); sys.stdout.write("│         \033[7mSYSTEM PAUSED\033[0m        │")
    move_cursor(py+2, px); sys.stdout.write(f"{g}├──────────────────────────────┤\033[0m")
    move_cursor(py+3, px); sys.stdout.write("│  » [ESC]   Resume Game       │")
    move_cursor(py+4, px); sys.stdout.write("│  » [Q]     Exit to Menu      │")
    move_cursor(py+5, px); sys.stdout.write(f"{g}└──────────────────────────────┘\033[0m"); sys.stdout.flush()

def draw_game_over_screen(s, hs):
    clear_screen(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[91m\033[1mSYSTEM CRASH DETECTED // IMPACT TERMINATION\033[0m")
    move_cursor(13, 8); sys.stdout.write("\033[38;5;46m┌────────────────────────────────────────────────────────┐\033[0m")
    move_cursor(14, 8); sys.stdout.write(f" \033[38;5;46m│\033[0m  \033[97mFINAL SCORE:\033[0m \033[38;5;46m{s:05d} BLOCKS\033[0m                             \033[38;5;46m│\033[0m")
    move_cursor(15, 8); sys.stdout.write(f" \033[38;5;46m│\033[0m  \033[97mHIGH SCORE:\033[0m  \033[93m{hs:05d} BLOCKS\033[0m                             \033[38;5;46m│\033[0m")
    move_cursor(16, 8); sys.stdout.write("\033[38;5;46m└────────────────────────────────────────────────────────┘\033[0m")
    move_cursor(18, 8); sys.stdout.write("\033[38;5;46m» Press [ SPACEBAR ] to play again\033[0m")
    move_cursor(19, 8); sys.stdout.write("\033[90m» Press [ ESC ] to leave framework\033[0m"); sys.stdout.flush()

def draw_leaderboard_screen(scores):
    clear_screen(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[95m\033[1mGLOBAL CLOUD HIGH SCORES\033[0m")
    move_cursor(13, 4); sys.stdout.write("\033[38;5;46m┌──────┬──────────────────┬──────────────┬──────────┐\033[0m")
    move_cursor(14, 4); sys.stdout.write(f"\033[38;5;46m│\033[0m \033[90m{'RANK':<4}\033[0m \033[38;5;46m│\033[0m \033[90m{'CODENAME':<16}\033[0m \033[38;5;46m│\033[0m \033[90m{'HIGH SCORE':<12}\033[0m \033[38;5;46m│\033[0m \033[90m{'MAX LVL':<8}\033[0m \033[38;5;46m│\033[0m")
    move_cursor(15, 4); sys.stdout.write("\033[38;5;46m├──────┼──────────────────┼──────────────┼──────────┤\033[0m")
    for idx, r in enumerate(scores):
        fmt_score = f"{r['high_score']:05d}"
        fmt_level = f"{r['max_level']:02d}"
        move_cursor(16+idx, 4); sys.stdout.write(f"\033[38;5;46m│\033[0m {idx+1:<4} \033[38;5;46m│\033[0m \033[97m{r['username'][:16]:<16}\033[0m \033[38;5;46m│\033[0m \033[38;5;46m{fmt_score:<12}\033[0m \033[38;5;46m│\033[0m \033[38;5;33m{fmt_level:<8}\033[0m \033[38;5;46m│\033[0m")
    move_cursor(16+len(scores), 4); sys.stdout.write("\033[38;5;46m└──────┴──────────────────┴──────────────┴──────────┘\033[0m")
    move_cursor(18+len(scores), 6); sys.stdout.write("\033[90mPress [ ESC ] or [ ENTER ] to return...\033[0m"); sys.stdout.flush()

def draw_dev_console(logs, current_input, help_mode, inst=None):
    clear_screen()
    sys.stdout.write("\033[38;5;46m┌" + "─" * 118 + "┐\033[0m\n")
    sys.stdout.write("\033[38;5;46m│\033[0m  \033[1mVITALS DIAGNOSTIC ENGINE\033[0m \033[90m// INTERNAL DEV-CONSOLE TERMINAL v3.5\033[0m" + " " * 49 + "\033[38;5;46m│\033[0m\n")
    sys.stdout.write("\033[38;5;46m├" + "─" * 48 + "┬" + "─" * 32 + "┬" + "─" * 36 + "┤\033[0m\n")
    sys.stdout.write("\033[38;5;46m│\033[0m \033[38;5;33m[1] INTERNAL PARAMETERS LOGSTREAM\033[0m    \033[38;5;46m│\033[0m \033[38;5;33m[2] LIVE REALTIME SIM\033[0m        \033[38;5;46m│\033[0m \033[38;5;33m[3] PARSED COMMAND INDEX\033[0m        \033[38;5;46m│\033[0m\n")
    sys.stdout.write("\033[38;5;46m├" + "─" * 48 + "┼" + "─" * 32 + "┼" + "─" * 36 + "┤\033[0m\n")

    sim_lines = []
    if inst:
        sim_lines.append("\033[38;5;46m┌" + "─" * 28 + "┐\033[0m")
        s_coords = [tuple(s) for s in inst.snake]
        f_coord = tuple(inst.food) if inst.food else (-1, -1)
        for sy in range(4, 13):
            line_str = "\033[38;5;46m│\033[0m "
            for sx in range(2, 28):
                mx = int(sx * (WIDTH / 28))
                my = int(sy * (HEIGHT / 10))
                if [mx, my] in s_coords: line_str += "\033[38;5;84m■\033[0m"
                elif [mx, my] == f_coord: line_str += "\033[38;5;203m⌺\033[0m"
                else: line_str += " "
            line_str += " \033[38;5;46m│\033[0m"
            sim_lines.append(line_str)
        sim_lines.append("\033[38;5;46m└" + "─" * 28 + "┘\033[0m")
        sim_lines.append(" " * 8 + "\033[38;5;242m[CORE PAUSED]\033[0m" + " " * 10)

    syntax_lines = [
        " \033[38;5;220mNUM  KEY/SYNTAX SPECIFICATION\033[0m",
        "  01. /help", "  02. exit",
        "  03. setcombo=<1-10>", "  04. setlevel=<1-10>",
        "  05. setpoints=<num>", "  06. setexpfactor=<2-6>",
        "  07. setcombofactor=<2-6>", "  08. spawnsuperfood",
        "  09. ghostmode=<0|1>", "  10. freezetimers=<0|1>",
        "  11. warpsize=<num>", "  12. clearlogs"
    ]

    processed_logs = []
    for raw_log in logs:
        if len(raw_log) > 44:
            processed_logs.append(raw_log[:41] + "...")
        else:
            processed_logs.append(raw_log)

    display_logs = processed_logs[-11:]
    while len(display_logs) < 11:
        display_logs.insert(0, "")

    for idx in range(11):
        log_raw = display_logs[idx]
        log_seg = f" {log_raw:<45}"
        sim_seg = f"{sim_lines[idx]:<30}" if idx < len(sim_lines) else " " * 30
        syn_seg = f"{syntax_lines[idx]:<34}" if idx < len(syntax_lines) else " " * 34
        sys.stdout.write(f"\033[38;5;46m│\033[0m\033[97m{log_seg}\033[0m \033[38;5;46m│\033[0m {sim_seg} \033[38;5;46m│\033[0m \033[97m{syn_seg}\033[0m \033[38;5;46m│\033[0m\n")

    sys.stdout.write("\033[38;5;46m├" + "─" * 118 + "┤\033[0m\n")
    sys.stdout.write(f"\033[38;5;46m│\033[0m  \033[38;5;46mCONSOLE INJECTION PROMPT\033[0m >> \033[97m{current_input:<87}\033[0m \033[38;5;46m│\033[0m\n")
    sys.stdout.write("\033[38;5;46m└" + "─" * 118 + "┘\033[0m\n")
    sys.stdout.flush()

def run_leaderboard_protocol():
    top_scores = get_top_scores(8)
    draw_leaderboard_screen(top_scores)
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

if sys.platform == "win32":
    import msvcrt
    def read_raw_keystroke():
        if msvcrt.kbhit():
            try:
                res = msvcrt.getch()
                return res
            except:
                return None
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
        load_data()
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
        if k == b'=': return 'TOGGLE_CON'
        if k in [b'\x00', b'\xe0']:
            if sys.platform == "win32" and msvcrt.kbhit():
                k = msvcrt.getch().lower()
                m = {b'h': 'UP', b'p': 'DOWN', b'k': 'LEFT', b'm': 'RIGHT'}
                if k in m and inst: inst.change_direction(m[k])
            return None
        kl = k.lower()
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
        sel = 0; draw_main_menu(sel)
        while True:
            k = read_raw_keystroke()
            if k:
                kl = k.lower()
                if kl == b'w':
                    sel = (sel - 1) % 3; draw_main_menu(sel)
                elif kl == b's':
                    sel = (sel + 1) % 3; draw_main_menu(sel)
                elif kl in (b'\r', b'\n'): return sel
            time.sleep(0.005)

    def run_pause_protocol(self):
        draw_pause_overlay()
        while True:
            k = read_raw_keystroke()
            if k and k.lower() == b'\x1b': return 'RESUME'
            if k and k.lower() == b'q': return 'QUIT'
            time.sleep(0.005)

    def run_dev_console_loop(self, inst):
        draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)
        while self.dev_mode_active:
            char = read_raw_keystroke()
            if char:
                if char == b'=' or char == b'\x1b':
                    self.dev_mode_active = False
                    draw_static_game_frame(); return
                elif char in (b'\r', b'\n'):
                    cmd_string = self.command_input.strip().lower()
                    if cmd_string == "exit":
                        self.dev_mode_active = False
                        draw_static_game_frame(); return
                    elif cmd_string == "/help":
                        self.help_mode_active = True
                        self.console_logs.append(">> /help")
                    elif cmd_string == "clearlogs":
                        self.console_logs = ["[SYSTEM]: Logs Cleared."]
                    elif cmd_string == "setcheats=0":
                        inst.cheats_active = False
                        inst.exp_factor = 1.0; inst.combo_factor = 1.0
                        inst.ghost_mode = False; inst.freeze_timers = False
                        save_cheat_modifiers(1.0, 1.0)
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
                                    self.console_logs.append(f"[SUCCESS]: Level transformed to {val}")
                                elif action == "setpoints" and val >= 0:
                                    inst.experience = val; inst.validate_vitals()
                                    self.console_logs.append(f"[SUCCESS]: Points set to {val}")
                                elif action == "setexpfactor" and 2 <= val <= 6:
                                    inst.exp_factor = float(val); save_cheat_modifiers(inst.exp_factor, inst.combo_factor)
                                    self.console_logs.append(f"[SUCCESS]: Exp multiplier scaled to {val}x")
                                elif action == "setcombofactor" and 2 <= val <= 6:
                                    inst.combo_factor = float(val); save_cheat_modifiers(inst.exp_factor, inst.combo_factor)
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
                    draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)

                elif ord(char) in (8, 127):
                    self.command_input = self.command_input[:-1]
                    draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)
                else:
                    try:
                        decoded = char.decode('utf-8')
                        if len(decoded) == 1 and ord(decoded) >= 32:
                            self.command_input += decoded
                            draw_dev_console(self.console_logs, self.command_input, self.help_mode_active, inst)
                    except: pass
            time.sleep(0.01)

    def run_gameplay_core(self):
        inst = GameEngine(self.username); draw_static_game_frame()
        tick, start, lp = 0, time.time(), set()
        while True:
            input_signal = self.read_keyboard_input(inst)
            if input_signal == 'TOGGLE_CON':
                self.dev_mode_active = True; self.run_dev_console_loop(inst)
                lp.clear(); continue
            if input_signal == 'ESC':
                if self.run_pause_protocol() == 'QUIT': return
                draw_static_game_frame(); lp.clear()
            if not inst.step():
                register_run(self.username, inst.score, inst.level, int(time.time() - start))
                self.run_game_over_protocol(inst.score); return
            cp = set()
            food_color = get_pulsing_color(tick, "SUPER") if inst.is_super_food else "\033[38;5;203m"
            food_char = "★" if inst.is_super_food else "⌺"
            move_cursor(inst.food[1], inst.food[0]); sys.stdout.write(f"{food_color}{food_char}\033[0m")
            cp.add((inst.food[0], inst.food[1]))
            for idx, seg in enumerate(inst.snake):
                move_cursor(seg[1], seg[0])
                if idx == 0:
                    d = inst.direction
                    sys.stdout.write(f"\033[38;5;46m{'▲' if d==(0,-1) else '▼' if d==(0,1) else '◀' if d==(-1,0) else '▶'}\033[0m")
                else: sys.stdout.write("\033[32m■\033[0m")
                cp.add((seg[0], seg[1]))
            for ox, oy in lp:
                if (ox, oy) not in cp: move_cursor(oy, ox); sys.stdout.write(" ")
            lp = cp; update_hud_dashboard(inst.get_hud_stats(), tick); tick += 1
            sp = max(0.02, 0.06 - (inst.level * 0.005))
            time.sleep(sp * 0.4 if inst.is_sprinting else sp)

    def run_game_over_protocol(self, score):
        top = load_data()["global_leaderboard"]
        draw_game_over_screen(score, top[0]["high_score"] if top else score)
        while True:
            k = read_raw_keystroke()
            if k:
                if k.lower() == b' ': self.run_gameplay_core(); return
                if k.lower() == b'\x1b': return
            time.sleep(0.01)

    def master_runtime_loop(self):
        boot_sequence()
        while True:
            route = self.run_menu_protocol()
            if route == 0: self.run_gameplay_core()
            elif route == 1: run_leaderboard_protocol()
            elif route == 2: clear_screen(); show_cursor(); break

if __name__ == '__main__': GameController().master_runtime_loop()
