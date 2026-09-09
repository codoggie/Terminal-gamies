import random, math, storage

WIDTH, HEIGHT = 46, 20
DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

class GameEngine:
    def __init__(self, username):
        self.username = username
        self.cheats_active = True
        mods = storage.load_cheat_modifiers()
        self.exp_factor = mods.get("saved_exp_factor", 1.0)
        self.combo_factor = mods.get("saved_combo_factor", 1.0)
        self.super_food_active = False
        self.is_super_food = False
        self.ghost_mode = False
        self.freeze_timers = False
        self.bearing_dir = "◆"
        self.reset()

    def reset(self):
        self.snake = [[WIDTH//2, HEIGHT//2], [WIDTH//2 - 1, HEIGHT//2], [WIDTH//2 - 2, HEIGHT//2]]
        self.direction = self.next_direction = DIR_RIGHT
        self.score, self.level, self.items_eaten = 0, 1, 0
        self.sprint_cooldown = self.sprint_duration = 0
        self.is_sprinting = False
        self.combo_multiplier, self.combo_timer = 1, 0
        self.experience = 0
        self.food = None; self.spawn_food()
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
