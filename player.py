from settings import *
import pygame as pg
import math


class Player:
    def __init__(self, game):
        self.game = game
        self.y, self.x = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        
        # --- מאפייני דמות RPG ---
        self.health = PLAYER_MAX_HEALTH
        self.gold = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100 # צריך 100 XP לרמה 2
        self.attack_damage = PLAYER_ATTACK_DAMAGE # נצטרך להוסיף את זה לקובץ settings
        
        self.rel = 0
        # diagonal movement correction
        self.diag_move_corr = 1 / math.sqrt(2)

    def add_xp(self, xp_amount):
        """פונקציה זו נקראת כשהורגים חיה"""
        self.xp += xp_amount
        print(f"קיבלת {xp_amount} נקודות ניסיון! סך הכל: {self.xp} / {self.xp_to_next_level}")
        # בדוק אם עלינו רמה
        if self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """מעלה את השחקן רמה ומחזק אותו"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        # --- חיזוק הדמות! ---
        # מעלים את כוח ההתקפה שלו
        self.attack_damage += 5 
        # מרפאים אותו לחלוטין
        self.health = PLAYER_MAX_HEALTH 
        
        self.game.sound.level_up.play() # נניח שיש לנו צליל עליית רמה
        
        print("\n" + "="*30)
        print(f"    !!! עלית לרמה {self.level} !!!")
        print(f"    כוח ההתקפה שלך עלה ל-{self.attack_damage}")
        print(f"    הבריאות שלך התחדשה במלואה!")
        print(f"    דרוש {self.xp_to_next_level} ניסיון לרמה הבאה.")
        print("="*30 + "\n")

    def recover_health(self):
        # נטרלנו את זה, אבל משאירים את הפונקציה למקרה שנרצה ריפוי אחר בעתיד
        pass

    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        # לוגיקת הירי נשארת כרגע, בעתיד נחליף אותה בלוגיקת קרב
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    # ... כל שאר הפונקציות (movement, check_wall, mouse_control וכו') נשארות בדיוק אותו הדבר ...
    # (אני מדלג על הדבקתן כאן כדי שההודעה תהיה קצרה, אבל הן צריכות להיות כאן)
    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        num_key_pressed = -1
        if keys[pg.K_w]:
            num_key_pressed += 1
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            num_key_pressed += 1
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            num_key_pressed += 1
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            num_key_pressed += 1
            dx += -speed_sin
            dy += speed_cos
        if num_key_pressed:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr
        self.check_wall_collision(dx, dy)
        self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def draw(self):
        pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100),
                    (self.x * 100 + WIDTH * math.cos(self.angle),
                     self.y * 100 + WIDTH * math. sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)