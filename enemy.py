import pygame
from settings import *
from random import randint
from timerizer import Timer
from support import draw_health_bar, draw_icon

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen:pygame.display, collisions_tower:list, atribs:list[str, int]):
        pygame.sprite.Sprite.__init__(self)
        self.display_surf = screen
        self.type = atribs[0]
        scale = self.get_scale_size()
        # image
        self.frames = [pygame.transform.scale(pygame.image.load(f'img/enemy/{self.type[1]}/{i}.png').convert_alpha(), scale) for i in range(3)]
        self.frame_id = 0
        self.image = self.frames[self.frame_id]
        y = screen_height - 150 if self.type[1] != 'Fly' else 100
        self.rect = self.image.get_rect(midbottom= (screen_width + randint(75, 300), y))
        # death img
        self.death_frames = [pygame.transform.scale(pygame.image.load('img/death.png').convert(), (scale[0]/2, scale[1]/2)), pygame.transform.scale(pygame.image.load('img/death_poison.png').convert(), (scale[0]/2, scale[1]/2))]
        self.death_surf = self.death_frames[0]
        # icons
        self.icon_size = 16
        self.poison_icon = pygame.transform.scale(pygame.image.load('img/icons/Poison.png'), (self.icon_size, self.icon_size))
        self.spike_icon = pygame.transform.scale(pygame.image.load('img/icons/Spike.png'), (self.icon_size, self.icon_size))
        # var's
        self.all_collisions_tower = collisions_tower #[tower, [bar1, bar2], [bait1, bait2]]
        self.type = self.type[1]
        self.speed = atribs[1]
        self.atual_speed = self.speed
        self.max_life = atribs[2]
        self.life = self.max_life
        self.dmg = atribs[3]
        self.dead = False
        self.attack_tower = False
        self.attack_bar = [False, False]
        self.stop_move = False
        self.poisoned = False
        self.opacity = 255
        self.valued_gold = atribs[4]
        # sounds
        self.take_dmg_sound = pygame.mixer.Sound('sound/Take_dmg.ogg')
        self.take_dmg_sound.set_volume(0.02)
        self.death_sound = pygame.mixer.Sound('sound/Death.ogg')
        self.death_sound.set_volume(0.1)
        self.channel = pygame.mixer.Channel(11)
        # timer
        self.move_timer = Timer(0.4)
        self.attack_timer = Timer(2)
        self.bait_timer = Timer(1)
        self.timer_healthbar = Timer(3.5)

    def get_scale_size(self) -> list[int]:
        if self.type[0] != 'MiniBoss' and self.type[0] != 'Boss':
            scale = (32, 32) if self.type[0] == 'Small' else ((64, 64) if self.type[0] == 'Mid' else (96, 96))
            self.bar_size = [30, 10]
        else:
            if self.type[0] == 'MiniBoss':
                scale = (96, 96)  
                self.bar_size = [60, 15]
            else:
                scale = (128, 500)
                self.bar_size = [100, 20]
        return scale

    def get_rect(self) -> pygame.rect:
        return self.rect

    def can_remove(self) -> bool:
        return True if self.opacity <= 0 else False

    def is_dead(self) -> bool:
        return self.dead

    def get_valued_gold(self) -> int:
        return self.valued_gold

    def get_type(self) -> str:
        return self.type

    def get_pos(self, center:bool=False) -> list[int]:
        return self.rect.midleft if not center else self.rect.center

    def set_life(self, life:int) -> None:
        self.life = life
    
    def decrease_life(self, life:int) -> None:
        self.life = round(self.life - life, 2) 
        self.show_life()
        self.channel.play(self.take_dmg_sound)
    
    def get_life(self) -> None:
        return self.life
    
    def get_attack_bar(self) -> list[bool]:
        return self.attack_bar
    
    def set_attack_bar(self, attack:bool, id:int=-1) -> None:
        if id != -1:
            self.attack_bar[id] = attack
        else:
            self.attack_bar = attack
    
    def get_attack_tower(self) -> bool:
        return self.attack_tower

    def set_attack_tower(self, attack:bool) -> None:
        self.attack_tower = attack

    def show_life(self) -> None:
        self.timer_healthbar.active()

    def draw(self) -> None:
        if not self.dead:
            self.display_surf.blit(self.image, self.rect)
            self.draw_life()
        else:
            self.draw_death()

    def draw_life(self) -> None:
        if self.timer_healthbar.run:
            color = 'red' if self.life < self.max_life/2 else 'green'
            pos = [self.rect.midbottom[0] - self.bar_size[0]/2, self.rect.midbottom[1] + 3]
            draw_health_bar(self.display_surf, self.life, self.max_life, color, pos, self.bar_size)
            if self.poisoned:
                draw_icon(self.display_surf, self.poison_icon, [pos[0] + 32, pos[1] - 4], self.icon_size)
            if self.spike:
                draw_icon(self.display_surf, self.spike_icon, [pos[0] + 32, pos[1] - 4], self.icon_size)

    def draw_death(self) -> None:
        self.display_surf.blit(self.death_surf, self.rect)
        self.animation_death()        

    def update_timers(self) -> None:
        if self.move_timer.run:
            self.move_timer.update()
        if self.attack_timer.run:
            self.attack_timer.update()
        if self.timer_healthbar.run:
            self.timer_healthbar.update()
        if self.bait_timer.run:
            self.bait_timer.update()

    def update(self, bar_lifes:list[int]) -> None:
        self.update_timers()
        self.animation()
        self.movement()
        self.attacking_tower()
        self.verify_attack_bar(bar_lifes)
        self.verify_collide_bait()
        self.check_life()

    def animation(self) -> None:
        self.frame_id += 0.1
        if self.frame_id > len(self.frames):
            self.frame_id = 0
        self.image = self.frames[int(self.frame_id)]

    def animation_death(self) -> None:
        self.rect.centery -= 2
        self.death_surf.set_alpha(self.opacity)
        self.opacity -= 10

    def movement(self) -> None:
        if not self.move_timer.run:
            if not self.stop_move:
                self.rect.x -= self.atual_speed
                self.move_timer.active()

    def attacking_tower(self) -> None:
        if not self.attack_timer.run:
            if self.rect.colliderect(self.all_collisions_tower[0]):
                self.attack_tower = True
                self.stop_move = True
                self.attack_timer.active()

    def verify_attack_bar(self, bar_life:list[int]) -> None:
        # verifica se atacou alguma barreira
        if not self.attack_timer.run:
            if not self.attacking_bar(self.all_collisions_tower[1][0], bar_life[0], id=0):
                if not self.attacking_bar(self.all_collisions_tower[1][1], bar_life[1], id=1):
                    self.stop_move = False

    def attacking_bar(self, collision:list, life:int, id:int) -> bool:
        if collision != ' ':
            if life > 0 and self.rect.colliderect(collision):
                if life > 100:
                    self.decrease_life(5)
                self.attack_bar[id] = True
                self.stop_move = True
                self.attack_timer.active()
                return True
        return False

    def verify_collide_bait(self) -> None:
        # verifica se passou por alguma armadilha
        if not self.bait_timer.run:
            self.spike = self.colide_bait(self.all_collisions_tower[2][0], 3, 2)
            if not self.spike:
                self.poisoned = self.colide_bait(self.all_collisions_tower[2][1], 1, 1.4)

            '''if self.all_collisions_tower[2][0] != ' ' and self.rect.colliderect(self.all_collisions_tower[2][0]):
                self.decrease_life(3)
                self.atual_speed = round(self.atual_speed/2, 2)
                self.spike = True
                self.bait_timer.active()
            else:
                self.spike = False
                self.atual_speed = self.speed
            if self.all_collisions_tower[2][1] != ' ' and self.rect.colliderect(self.all_collisions_tower[2][1]):
                self.decrease_life(1)
                self.atual_speed = round(self.atual_speed/1.4, 2)
                self.poisoned = True
                self.bait_timer.active()
            else:
                self.poisoned = False
                self.atual_speed = self.speed'''

    def colide_bait(self, collision:pygame.rect, dec_life:float, red_spd:float) -> bool:
        if collision != ' ' and self.rect.colliderect(collision):
            self.decrease_life(dec_life)
            self.atual_speed = round(self.atual_speed/red_spd, 2)
            self.bait_timer.active()
            return True
        else:
            self.atual_speed = self.speed
            return False

    def check_life(self) -> None:
        if not self.dead and self.life <= 0:
            self.dead = True
            self.stop_move = True
            if self.poisoned:
                self.death_surf = self.death_frames[1]
            self.channel.play(self.death_sound)
