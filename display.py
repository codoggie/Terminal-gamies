import os, sys, time

WIDTH, HEIGHT, SIDEBAR_WIDTH = 46, 20, 34
TOTAL_WIDTH = WIDTH + SIDEBAR_WIDTH + 4

def move_cursor(y, x): sys.stdout.write(f"\033[{y};{x}H")
def hide_cursor(): sys.stdout.write("\033[?25l"); sys.stdout.flush()
def show_cursor(): sys.stdout.write("\033[?25h"); sys.stdout.flush()
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

def draw_signature_header(y_offset=2):
    g, r = "\033[92m\033[1m", "\033[0m"
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
        "Loading storage database...", "Initialization dynamic loop operational."
    ]
    for i, log in enumerate(logs):
        move_cursor(13 + i, 6)
        sys.stdout.write(f"\033[92m» {log}\033[0m" if i == len(logs)-1 else f"\033[37m» {log}\033[0m")
        sys.stdout.flush(); time.sleep(0.15)
    move_cursor(20, 6); sys.stdout.write("\033[90mLOADING RUNTIME: [░░░░░░░░░░░░░░░░░░░░] 0%\033[0m"); sys.stdout.flush(); time.sleep(0.1)
    for f in range(1, 21):
        move_cursor(20, 6); sys.stdout.write(f"\033[92mLOADING RUNTIME: [{'█'*f + '░'*(20-f)}] {int((f/20)*100)}%\033[0m"); sys.stdout.flush(); time.sleep(0.02)
    time.sleep(0.2)

def draw_main_menu(sel):
    clear_screen(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[90m[vitals.sys // main menu]\033[0m")
    opts = ["INITIALIZE SNAKE PROTOCOL (PLAY)", "GLOBAL HIGH SCORE LEADERBOARDS", "SHUT DOWN CORE TERMINAL (EXIT)"]
    for i, o in enumerate(opts):
        move_cursor(14 + (i * 2), 8)
        sys.stdout.write(f"\033[92m\033[1m» {o} \033[0m" if i == sel else f"\033[90m  {o} \033[0m")
    move_cursor(21, 6); sys.stdout.write("\033[37mUse [ W / S ] or [ ARROWS ]. Press [ ENTER ] to confirm.\033[0m"); sys.stdout.flush()

def draw_username_prompt():
    clear_screen(); draw_signature_header(2)
    move_cursor(12, 10); sys.stdout.write("┌──────────────────────────────────────────┐")
    move_cursor(13, 10); sys.stdout.write("│         USER PROFILE REGISTRATION        │")
    move_cursor(14, 10); sys.stdout.write("├──────────────────────────────────────────┤")
    move_cursor(15, 10); sys.stdout.write("│ ENTER CODENAME:                          │")
    move_cursor(16, 10); sys.stdout.write("└──────────────────────────────────────────┘")
    move_cursor(15, 28); show_cursor()

def draw_static_game_frame():
    clear_screen(); hide_cursor()
    move_cursor(1, 2); sys.stdout.write("\033[92m\033[1mVITALS ENGINE\033[0m \033[90m// TERMINAL FRAMEWORK V3.5\033[0m")
    move_cursor(3, 1); sys.stdout.write("┌" + "─" * WIDTH + "┐")
    for y in range(4, 4 + HEIGHT):
        move_cursor(y, 1); sys.stdout.write("│")
        move_cursor(y, WIDTH + 2); sys.stdout.write("│")
    move_cursor(4 + HEIGHT, 1); sys.stdout.write("└" + "─" * WIDTH + "┘")
    sbs = WIDTH + 4
    move_cursor(3, sbs); sys.stdout.write("┌" + "─" * SIDEBAR_WIDTH + "┐")
    for y in range(4, 4 + HEIGHT):
        move_cursor(y, sbs); sys.stdout.write("│")
        move_cursor(y, sbs + SIDEBAR_WIDTH + 1); sys.stdout.write("│")
    move_cursor(4 + HEIGHT, sbs); sys.stdout.write("└" + "─" * SIDEBAR_WIDTH + "┘"); sys.stdout.flush()

def draw_hospital_vitals(tick, active):
    w, cycle, wave = 18, tick % 16, ""
    for i in range(w):
        t = (cycle + i) % 16
        if active: wave += "▲" if t==2 else "█" if t==3 else "▼" if t==4 else "─"
        else: wave += "▄" if t==3 else "▀" if t==4 else "▄" if t==5 else "─"
    return f"{'\033[91m' if active else '\033[92m'}{wave}\033[0m"

def draw_circular_radar(y, x, dist):
    c, b = ("\033[91m", "☠") if dist<=2 else ("\033[93m", "×") if dist<=5 else ("\033[32m", "•")
    lines = [f"  {c}▄───▄\033[0m  ", f" {c}│\033[0m   {b}   {c}│\033[0m ", f"  {c}▀───▀\033[0m  "]
    for i, l in enumerate(lines): move_cursor(y + i, x); sys.stdout.write(l)

def update_hud_dashboard(stats, tick):
    xc = WIDTH + 7
    u, s, c, ct, l, scd, slen, rdist = stats["username"], stats["score"], stats["combo"], stats["combo_time"], stats["level"], stats["sprint_cd"], stats["snake_len"], stats["radar_dist"]
    sprint_str = f"\033[93mRECHARGING [{ '░'*(8-int((scd/40)*8)) + '█'*int((scd/40)*8) }]\033[0m" if scd>0 else "\033[92mREADY [████████]\033[0m"
    combo_str = f"\033[91m{c}X COMBO [{ '█'*int((ct/45)*8) + '░'*(8-int((ct/45)*8)) }]\033[0m" if c>1 else "\033[90mNO COMBO  [░░░░░░░░]\033[0m"
    struct = f"\033[92m▲\033[0m" + f"\033[32m■\033[0m"*min(6, slen-1) + (f"\033[90m..x{slen}\033[0m" if slen>7 else "")
    move_cursor(5, xc); sys.stdout.write(f"OPERATOR   : \033[97m{u[:14]}\033[0m" + " "*6)
    move_cursor(6, xc); sys.stdout.write(f"SCORE      : \033[92m{s:05d}\033[0m     LEVEL: \033[96m{l:02d}\033[0m")
    move_cursor(8, xc); sys.stdout.write(f"COMBO      : {combo_str}   ")
    move_cursor(9, xc); sys.stdout.write(f"SPRINT     : {sprint_str}   ")
    move_cursor(10, xc); sys.stdout.write(f"SNAKE      : {struct}      ")
    move_cursor(12, xc); sys.stdout.write(f"EKG PULSE  : {draw_hospital_vitals(tick, c>1)}   ")
    move_cursor(14, xc); sys.stdout.write(f"RADAR      : {rdist:02d} BLOCKS  ")
    draw_circular_radar(14, xc + 18, rdist)
    move_cursor(19, xc); sys.stdout.write("\033[90m[ESC] Pause Game Matrix\033[0m"); sys.stdout.flush()

def draw_pause_overlay():
    py, px = 10, (WIDTH // 2) - 15
    g = "\033[92m"
    move_cursor(py, px); sys.stdout.write(f"{g}┌──────────────────────────────┐\033[0m")
    move_cursor(py+1, px); sys.stdout.write("│         \033[7mSYSTEM PAUSED\033[0m        │")
    move_cursor(py+2, px); sys.stdout.write(f"{g}├──────────────────────────────┤\033[0m")
    move_cursor(py+3, px); sys.stdout.write("│  » [ESC]   Resume Game       │")
    move_cursor(py+4, px); sys.stdout.write("│  » [Q]     Exit to Menu      │")
    move_cursor(py+5, px); sys.stdout.write(f"{g}└──────────────────────────────┘\033[0m"); sys.stdout.flush()

def draw_game_over_screen(s, hs):
    clear_screen(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[91m\033[1mSYSTEM CRASH DETECTED // IMPACT TERMINATION\033[0m")
    move_cursor(13, 8); sys.stdout.write("┌────────────────────────────────────────────────────────┐")
    move_cursor(14, 8); sys.stdout.write(f" │  FINAL SCORE: \033[92m{s:05d} BLOCKS\033[0m                             │")
    move_cursor(15, 8); sys.stdout.write(f" │  HIGH SCORE:  \033[93m{hs:05d} BLOCKS\033[0m                             │")
    move_cursor(16, 8); sys.stdout.write("└────────────────────────────────────────────────────────┘")
    move_cursor(18, 8); sys.stdout.write("\033[92m» Press [ SPACEBAR ] to play again\033[0m")
    move_cursor(19, 8); sys.stdout.write("\033[90m» Press [ ESC ] to leave framework\033[0m"); sys.stdout.flush()

def draw_leaderboard_screen(scores):
    clear_screen(); draw_signature_header(2)
    move_cursor(11, 6); sys.stdout.write("\033[95m\033[1mGLOBAL HIGH SCORES\033[0m")
    move_cursor(13, 4); sys.stdout.write("┌──────┬──────────────────┬──────────────┬──────────┐")
    move_cursor(14, 4); sys.stdout.write(f"\033[90m│ {'RANK':<4} │ {'CODENAME':<16} │ {'HIGH SCORE':<12} │ {'MAX LVL':<8} │\033[0m")
    move_cursor(15, 4); sys.stdout.write("├──────┼──────────────────┼──────────────┼──────────┤")
    for idx, r in enumerate(scores):
        fmt_score = f"{r['high_score']:05d}"
        fmt_level = f"{r['max_level']:02d}"
        move_cursor(16+idx, 4); sys.stdout.write(f"│ {idx+1:<4} │ {r['username'][:16]:<16} │ \033[92m{fmt_score:<12}\033[0m │ \033[96m{fmt_level:<8}\033[0m │")
    move_cursor(16+len(scores), 4); sys.stdout.write("└──────┴──────────────────┴──────────────┴──────────┘")
    move_cursor(18+len(scores), 6); sys.stdout.write("\033[90mPress [ ESC ] or [ ENTER ] to return...\033[0m"); sys.stdout.flush()
