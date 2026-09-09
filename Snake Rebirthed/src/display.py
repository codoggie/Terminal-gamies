import os, sys, time

WIDTH, HEIGHT, SIDEBAR_WIDTH = 46, 20, 34
TOTAL_WIDTH = WIDTH + SIDEBAR_WIDTH + 4

def move_cursor(y, x): sys.stdout.write(f"\033[{y};{x}H")
def hide_cursor(): sys.stdout.write("\033[?25l"); sys.stdout.flush()
def show_cursor(): sys.stdout.write("\033[?25h"); sys.stdout.flush()
def clear_screen(): sys.stdout.write("\033[2J\033[H"); sys.stdout.flush()

def get_pulsing_color(tick, flavor="SUPER"):
    cycle = (tick // 4) % 2
    if flavor == "SUPER": return "\033[38;5;99m" if cycle == 0 else "\033[38;5;141m"
    elif flavor == "LIGHT_GREEN": return "\033[38;5;84m" if cycle == 0 else "\033[38;5;120m"
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

def draw_username_prompt():
    clear_screen(); draw_signature_header(2)
    move_cursor(12, 10); sys.stdout.write("\033[38;5;46m┌──────────────────────────────────────────┐\033[0m")
    move_cursor(13, 10); sys.stdout.write("\033[38;5;46m│\033[0m         \033[97mUSER PROFILE REGISTRATION\033[0m        \033[38;5;46m│\033[0m")
    move_cursor(14, 10); sys.stdout.write("\033[38;5;46m├──────────────────────────────────────────┤\033[0m")
    move_cursor(15, 10); sys.stdout.write("\033[38;5;46m│\033[0m \033[97mENTER CODENAME:\033[0m                          \033[38;5;46m│\033[0m")
    move_cursor(16, 10); sys.stdout.write("\033[38;5;46m└──────────────────────────────────────────┘\033[0m")
    move_cursor(15, 28); show_cursor()

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

def draw_hospital_vitals(tick, active):
    w, cycle, wave = 18, tick % 16, ""
    color_code = get_pulsing_color(tick, "LIGHT_GREEN") if active else "\033[38;5;46m"
    for i in range(w):
        t = (cycle + i) % 16
        if active: wave += "▲" if t==2 else "█" if t==3 else "▼" if t==4 else "─"
        else: wave += "▄" if t==3 else "▀" if t==4 else "▄" if t==5 else "─"
    return f"{color_code}{wave}\033[0m"

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
    move_cursor(14, xc); sys.stdout.write(f"\033[38;5;46mPULSE      :\033[0m {draw_hospital_vitals(tick, c>1)}")
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

    # Process and truncate logs to fit into the left column perfectly
    processed_logs = []
    for raw_log in logs:
        if len(raw_log) > 44:
            processed_logs.append(raw_log[:41] + "...")
        else:
            processed_logs.append(raw_log)

    # Strict 11-row line buffer container constraints
    display_logs = processed_logs[-11:]
    while len(display_logs) < 11:
        display_logs.insert(0, "")

    # Clean rendering matrix step
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
