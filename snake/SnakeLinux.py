#!/usr/bin/env python3
import curses, time, random

def draw_apple(stdscr, y, x, color_pair):
    try: stdscr.addstr(y, x, "⌺", color_pair | curses.A_BOLD)
    except curses.error: pass

def main_menu(stdscr, last_score=None, last_time=None):
    stdscr.clear(); curses.curs_set(0); stdscr.keypad(True); stdscr.nodelay(False)
    curses.start_color(); curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    g_term = curses.color_pair(1)
    stdscr.addstr(2, 4, " ▄████████  ███▄▄▄▄      ▄████████    ▄█   ▄█▄    ▄████████ ", g_term | curses.A_BOLD)
    stdscr.addstr(3, 4, "███    ███  ███▀▀▀██▄   ███    ███   ███ ▄███▀   ███    ███ ", g_term | curses.A_BOLD)
    stdscr.addstr(4, 4, "███    █▀   ███   ███   ███    ███   ███▐███▀    ███    █▀  ", g_term | curses.A_BOLD)
    stdscr.addstr(5, 4, "███         ███   ███   ███    ███  ▄█████▀      ███▄▄▄▄▄   ", g_term | curses.A_BOLD)
    stdscr.addstr(6, 4, "▀█████████▄ ███   ███ ▀███████████ ▀▀█████▄     ▀▀███▀▀▀▀   ", g_term | curses.A_BOLD)
    stdscr.addstr(7, 4, "         ██ ███   ███   ███    ███   ███▐███▄    ███    █▄  ", g_term | curses.A_BOLD)
    stdscr.addstr(8, 4, "   ▄█    ██ ███   ███   ███    ███   ███ ▀███▄   ███    ███ ", g_term | curses.A_BOLD)
    stdscr.addstr(9, 4, " ▄████████▀  ▀█   █▀    ███    █▀    ███   ▀█▄   ██████████ ", g_term | curses.A_BOLD)
    stdscr.addstr(10, 4, " ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀ ", curses.A_DIM)
    stdscr.addstr(11, 4, " [vitals.sys // terminal-compiled pipeline interface]", curses.A_DIM)
    if last_score is not None and last_time is not None:
        stdscr.addstr(13, 4, " ┌────────────────────────────────────────────────────────┐", g_term)
        stdscr.addstr(14, 4, f"  │  [⚡] RECOVERED SCORE : {last_score:02d} BLOCKS                        │", curses.A_BOLD)
        stdscr.addstr(15, 4, f"  │  [⏳] ELAPSED TIME    : {last_time:03d} SECONDS                     │", curses.A_BOLD)
        stdscr.addstr(16, 4, " └────────────────────────────────────────────────────────┘", g_term)
    stdscr.addstr(19, 6, " » Press [ ENTER ] to play game", g_term | curses.A_BOLD)
    stdscr.addstr(20, 6, " » Press [ Q ] to exit terminal", curses.A_DIM)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [10, 13, curses.KEY_ENTER]: return True
        elif key in [ord('q'), ord('Q')]: return False

def pause_menu(stdscr, g_term):
    stdscr.nodelay(False); p_y, p_x = 11, 14
    stdscr.addstr(p_y,     p_x, " ┌──────────────────────────────────────────┐ ", g_term | curses.A_BOLD)
    stdscr.addstr(p_y + 1, p_x, "  │               GAME PAUSED                │ ", curses.A_REVERSE)
    stdscr.addstr(p_y + 2, p_x, "  │                                         │ ", g_term)
    stdscr.addstr(p_y + 3, p_x, "  │  -> Press [ESC] to resume gameplay      │ ", curses.A_BOLD)
    stdscr.addstr(p_y + 4, p_x, "  │  -> Press [Q] to quit to main menu      │ ", curses.A_DIM)
    stdscr.addstr(p_y + 5, p_x, " └──────────────────────────────────────────┘ ", g_term | curses.A_BOLD)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == 27: stdscr.nodelay(True); return "RESUME"
        elif key in [ord('q'), ord('Q')]: return "QUIT"

def game_loop(stdscr):
    curses.curs_set(0); stdscr.nodelay(True); stdscr.keypad(True); stdscr.timeout(40)
    g_term = curses.color_pair(1)
    start_time, paused_duration, tick_counter = time.time(), 0, 0
    box_top, box_bottom, box_left, box_right = 6, 23, 2, 65
    snake = [[box_top + 5, box_left + 7], [box_top + 5, box_left + 6], [box_top + 5, box_left + 5]]
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT = 0, 1, 2, 3
    current_dir, next_dir = DIR_RIGHT, DIR_RIGHT
    food = [box_top + 7, box_left + 15]
    while True:
        elapsed_seconds = int((time.time() - start_time) - paused_duration)
        snake_size = len(snake); stdscr.clear()
        stdscr.addstr(1, 2, "  ___  _  _   _   _  __ ___ ", g_term | curses.A_BOLD)
        stdscr.addstr(2, 2, " / __|| \\| | /_\\ | |/ /| __|", g_term | curses.A_BOLD)
        stdscr.addstr(3, 2, " \\__ \\| .` |/ _ \\| ' < | _| ", g_term | curses.A_BOLD)
        stdscr.addstr(4, 2, " |___/|_|\\_/_/ \\_\\_|\\_\\|___|", g_term | curses.A_BOLD)
        stdscr.addstr(1, 34, f"SCORE: {snake_size:02d} BLOCKS", g_term | curses.A_BOLD)
        stdscr.addstr(2, 34, f"TIME : {elapsed_seconds:03d} SECONDS", g_term | curses.A_BOLD)
        stdscr.addstr(3, 34, "PAUSE: Press [ESC]", curses.A_DIM)
        for x in range(box_left + 1, box_right): stdscr.addch(box_top, x, '─'); stdscr.addch(box_bottom, x, '─')
        for y in range(box_top + 1, box_bottom): stdscr.addch(y, box_left, '│'); stdscr.addch(y, box_right, '│')
        stdscr.addch(box_top, box_left, '┌'); stdscr.addch(box_top, box_right, '┐')
        stdscr.addch(box_bottom, box_left, '└'); stdscr.addch(box_bottom, box_right, '┘')
        
        if food: draw_apple(stdscr, food[0], food[1], g_term)
        
        for idx, segment in enumerate(snake):
            seg_y, seg_x = segment[0], segment[1]
            if idx == 0:
                if current_dir == DIR_UP: head_char = "▲"
                elif current_dir == DIR_DOWN: head_char = "▼"
                elif current_dir == DIR_LEFT: head_char = "◀"
                else: head_char = "▶"
                stdscr.addstr(seg_y, seg_x, head_char, g_term | curses.A_BOLD)
            else: 
                stdscr.addstr(seg_y, seg_x, "■", g_term)
                
        stdscr.refresh(); key = stdscr.getch()
        if key == 27:
            pause_start = time.time()
            if pause_menu(stdscr, g_term) == "QUIT": return snake_size, elapsed_seconds
            paused_duration += (time.time() - pause_start); stdscr.timeout(40); continue
        if key in [curses.KEY_UP, ord('w'), ord('W')] and current_dir != DIR_DOWN: next_dir = DIR_UP
        elif key in [curses.KEY_DOWN, ord('s'), ord('S')] and current_dir != DIR_UP: next_dir = DIR_DOWN
        elif key in [curses.KEY_LEFT, ord('a'), ord('A')] and current_dir != DIR_RIGHT: next_dir = DIR_LEFT
        elif key in [curses.KEY_RIGHT, ord('d'), ord('D')] and current_dir != DIR_LEFT: next_dir = DIR_RIGHT
        tick_counter += 1
        if next_dir in [DIR_UP, DIR_DOWN] and tick_counter % 2 == 0: continue
        current_dir = next_dir
        
        # FIX: Correctly grab only the first coordinate sub-list element from the head segment
        head = snake[0]
        if current_dir == DIR_UP: new_head = [head[0] - 1, head[1]]
        elif current_dir == DIR_DOWN: new_head = [head[0] + 1, head[1]]
        elif current_dir == DIR_LEFT: new_head = [head[0], head[1] - 1]
        elif current_dir == DIR_RIGHT: new_head = [head[0], head[1] + 1]
        
        near_wall = (new_head[0] <= box_top + 1 or new_head[0] >= box_bottom - 1 or new_head[1] <= box_left + 1 or new_head[1] >= box_right - 1)
        if near_wall: stdscr.timeout(75)
        else: stdscr.timeout(40)
        
        snake.insert(0, new_head)
        if (new_head[0] <= box_top or new_head[0] >= box_bottom or new_head[1] <= box_left or new_head[1] >= box_right):
            time.sleep(0.35); return snake_size, elapsed_seconds
        if new_head in snake[1:]:
            time.sleep(0.35); return snake_size, elapsed_seconds
        if new_head == food:
            food = None
            while food is None:
                new_food = [random.randint(box_top + 3, box_bottom - 3), random.randint(box_left + 3, box_right - 3)]
                if new_food not in snake: food = new_food
        else: snake.pop()

def master_flow(stdscr):
    score, survival_time = None, None
    while True:
        if not main_menu(stdscr, score, survival_time): break
        score, survival_time = game_loop(stdscr)

if __name__ == '__main__':
    curses.wrapper(master_flow)
