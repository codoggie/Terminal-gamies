import random, math

WIDTH, HEIGHT = 46, 20
DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

class GameEngine:
    def __init__(self, username):
        self.username = username
        self.reset()

    def reset(self):
        self.snake = [[WIDTH//2, HEIGHT//2], [WIDTH//2 - 1, HEIGHT//2], [WIDTH//2 - 2, HEIGHT//2]]
        self.direction = self.next_direction = DIR_RIGHT
        self.score, self.level, self.items_eaten = 0, 1, 0
        self.sprint_cooldown = self.sprint_duration = 0
        self.is_sprinting = False
        self.combo_multiplier, self.combo_timer = 1, 0
        self.food = None; self.spawn_food()
        self.radar_distance = 0; self.update_radar()

    def change_direction(self, act):
        if act == 'UP' and self.direction != DIR_DOWN: self.next_direction = DIR_UP
        elif act == 'DOWN' and self.direction != DIR_UP: self.next_direction = DIR_DOWN
        elif act == 'LEFT' and self.direction != DIR_RIGHT: self.next_direction = DIR_LEFT
        elif act == 'RIGHT' and self.direction != DIR_LEFT: self.next_direction = DIR_RIGHT

    def trigger_sprint(self):
        if self.sprint_cooldown == 0 and not self.is_sprinting:
            self.is_sprinting, self.sprint_duration, self.sprint_cooldown = True, 12, 40

    def update_radar(self):
        h = self.snake[0]
        min_self = 99
        if len(self.snake) > 4:
            for s in self.snake[3:]:
                d = math.sqrt((h[0]-s[0])**2 + (h[1]-s[1])**2)
                if d < min_self: min_self = d
        self.radar_distance = int(min_self) if min_self != 99 else 99

    def update_timers(self):
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
            if [rx, ry] not in self.snake: self.food = [rx, ry]; break

    def step(self):
        self.direction = self.next_direction
        h = self.snake[0]

        nx = h[0] + self.direction[0]
        ny = h[1] + self.direction[1]

        if nx <= 1: nx = WIDTH
        elif nx > WIDTH: nx = 2

        if ny <= 3: ny = HEIGHT + 2
        elif ny > HEIGHT + 2: ny = 4

        nh = [nx, ny]

        if nh in self.snake: return False

        self.snake.insert(0, nh)
        if nh == self.food:
            self.score += 10 * self.combo_multiplier
            self.items_eaten += 1
            self.combo_multiplier = min(4, self.combo_multiplier + 1) if self.combo_timer > 0 else 2
            self.combo_timer = 45
            if self.items_eaten >= (self.level * 3): self.level, self.items_eaten = self.level + 1, 0
            self.spawn_food()
        else: self.snake.pop()
        self.update_timers(); self.update_radar(); return True

    def get_hud_stats(self):
        return {
            "username": self.username, "score": self.score, "combo": self.combo_multiplier,
            "combo_time": self.combo_timer, "level": self.level, "sprint_cd": self.sprint_cooldown,
            "snake_len": len(self.snake), "radar_dist": self.radar_distance
        }
