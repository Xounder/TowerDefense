import pygame
from timerizer import Timer
from enemy import Enemy
from tower import Tower
from settings import *
from random import randint, choice, random
from time import time
from support import blit_text_shadow
from typing import Callable

class Control:
    def __init__(self, screen:pygame.display, tower:Tower, buy_phase_active:Callable, level_deactive:Callable) -> None:
        self.display_surf = screen
        self.tower = tower
        self.buy_phase_active = buy_phase_active
        self.level_deactive = level_deactive
        # game_over window
        self.game_over_surf = pygame.image.load('img/game_over.png').convert()
        self.game_over_rect = self.game_over_surf.get_rect(center= (screen_width/2, screen_height/2))
        self.gover_button = pygame.Surface((225, 70))
        self.gover_button_rect = self.gover_button.get_rect(center= (screen_width/2, screen_height/2 + 185))
        # pause window
        self.pause_surf = pygame.image.load('img/pause_game.png').convert()
        self.pause_rect = self.pause_surf.get_rect(center= (screen_width/2, screen_height/2))
        self.pause_button = pygame.Surface((95, 30))
        self.pause_button_rect = self.pause_button.get_rect(center= (screen_width/2, screen_height/2 + 18))
        # sound
        self.game_over_sound = pygame.mixer.Sound('sound/Lose.ogg')
        self.game_over_sound.set_volume(0.1)
        self.channel = pygame.mixer.Channel(3)
        # font
        self.font_38 = pygame.font.Font('font/Pixeltype.ttf', 38)
        self.font_50 = pygame.font.Font('font/Pixeltype.ttf', 50)
        self.font_25 = pygame.font.Font('font/Pixeltype.ttf', 25)
        # mouse
        self.mouse_surf = pygame.Surface((5, 5))
        self.mouse_rect = self.mouse_surf.get_rect(center=(0, 0))
        #timer
        self.timer_sort = Timer(0.4)
        self.timer = Timer(0.6)
        self.enemy_timer = Timer(1) 
        #initial state
        self.set_initial_atrib()

    def set_initial_atrib(self) -> None:
        self.start_time_plyed = time()
        self.time_plyd = 0
        self.enemys = []
        self.enemys_close = []
        self.chance_spawn_fly = 0
        self.wave = 1
        self.max_enemy_wave = 5
        self.added_enemys = 0
        self.removed_enemys = 0
        self.closests_enemys = []
        self.enemys_defeated = [0, 0] # normal / boss
        self.switch = False
        self.game_over = False
        self.paused = False

    def is_game_over(self) -> bool:
        return self.game_over
    
    def is_paused(self) -> bool:
        return self.paused

    def get_enemys(self) -> list[Enemy]:
        return self.enemys
    
    def get_closests_enemys(self) -> list[int]:
        return self.closests_enemys

    def draw(self) -> None:
        self.draw_wave_info()
        self.draw_enemys()
        self.draw_game_over()
        self.draw_pause()

    def draw_enemys(self) -> None:
        for e in self.enemys:
            e.draw()

    def draw_game_over(self) -> None:
        if self.game_over:
            used_cons = self.tower.get_used_consumables()
            self.display_surf.blit(self.game_over_surf, self.game_over_rect)               
            blit_text_shadow(self.display_surf, f'{self.wave} Waves', 'red', [screen_width/2 + 20, screen_height/2 - 130], self.font_50, back_color='black')     
            blit_text_shadow(self.display_surf, f'{self.time_plyd}', 'red', [screen_width/2 - 60, screen_height/2 - 55], self.font_50, back_color='black')     
            blit_text_shadow(self.display_surf, f'N[{self.enemys_defeated[0]}] - B[{self.enemys_defeated[1]}]', 'red', [screen_width/2 - 40, screen_height/2 + 12], self.font_38, back_color='black')     
            blit_text_shadow(self.display_surf, f'{used_cons[0]}/{used_cons[1]}', 'red', [screen_width/2 + 80, screen_height/2 + 90], self.font_38, back_color='black')     

    def draw_pause(self) -> None:
        if self.paused:
            self.display_surf.blit(self.pause_surf, self.pause_rect)
            blit_text_shadow(self.display_surf, f'{self.wave}', '#ca0000', [screen_width/2 + 30, screen_height/2 - 33], self.font_25, back_color='white')

    def draw_wave_info(self) -> None:
        wave = self.wave 
        blit_text_shadow(self.display_surf, f'WAVE: {wave}', '#ca0000', [5, screen_height/2 - 15], self.font_38, back_color='white')
        blit_text_shadow(self.display_surf, f'{self.removed_enemys}/{self.max_enemy_wave}', 'red', [screen_width/2 - 180, screen_height - 30], self.font_25, back_color='black', center= True)

    def update_timers(self) -> None:
        if self.enemy_timer.run:
            self.enemy_timer.update()
        if self.timer_sort.run:
            self.timer_sort.update()
        if self.timer.run:
            self.timer.update()

    def update(self) -> None:
        self.update_timers()
        self.input()
        if not self.paused and not self.game_over:
            self.check_end_wave()
            self.check_end_game()
            self.add_enemy()
            self.remove_enemy()
            self.update_enemys()
            self.sort_enemys()

    def input(self) -> None:
        if not self.timer.run:
            if self.game_over:
                self.check_gover_button()
            else:
                if not self.paused:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_p] or keys[pygame.K_ESCAPE]:
                        self.paused = True
                        self.timer.active()
                else:
                    self.check_pause_button()

    def check_gover_button(self) -> None:
        self.mouse_rect.center = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and self.gover_button_rect.colliderect(self.mouse_rect):
            self.set_initial_atrib()
            self.level_deactive()

    def check_pause_button(self) -> None:
        self.mouse_rect.center = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and self.pause_button_rect.colliderect(self.mouse_rect):
            self.paused = False

    def get_enemy_size(self) -> str:
        #retorna o tamanho do inimigo
        e_size = ''
        if self.wave % 25 == 0:
            if (self.added_enemys + 1) == self.max_enemy_wave:
                if self.wave % 50 == 0:    # wave 50/100/150...
                    e_size = 'Boss'
                elif self.wave % 25 == 0:  # wave 25/75/125...
                    e_size = 'MiniBoss'
        else:
            if self.wave <= 10:
                e_size = 'Mid' 
            else:
                if 10 <= self.wave <= 13:
                    e_size = ['Small', 'Mid', 'Mid', 'Mid', 'Mid']
                elif 13 < self.wave <= 15:
                    e_size = ['Small', 'Mid', 'Small', 'Mid', 'Mid']
                elif 15 < self.wave < 20:
                    e_size = ['Small', 'Mid', 'Small', 'Mid', 'Small']
                else:
                    if 20 <= self.wave <= 45:
                        e_size = ['Small', 'Mid', 'Big', 'Small', 'Mid', 'Small', 'Mid', 'Mid', 'Small', 'Mid']
                    elif 45 < self.wave <= 70:
                        e_size = ['Small', 'Mid', 'Big', 'Small', 'Mid', 'Small', 'Mid', 'Big', 'Small', 'Mid']
                    else:
                        e_size = ['Small', 'Mid', 'Big', 'Small', 'Big', 'Small', 'Mid', 'Big', 'Small', 'Mid']
                e_size = choice(e_size)
        return e_size

    def get_enemy_atrib(self, e_size) -> tuple[int, int, int]:
        #retorna a velocidade e a vida maxima do inimigo
        if e_size == 'Small': # aparece wave 10
            spd_lim, life_lim = 22, 25 # limites de velocidade e vida
            spd, m_life, dmg = 14, 6, 1
        else:
            if e_size == 'Mid':
                spd_lim, life_lim = 4, 45 
                spd, m_life, dmg = 3, 8, 1
            else: 
                if e_size == 'Big': #aparece wave 20
                    spd_lim, life_lim = 3, 70 
                    spd, m_life, dmg = 2, 30, 2
                else:
                    if e_size == 'MiniBoss':
                        spd_lim, life_lim = 3, 650 
                        spd, m_life, dmg = 1, 450, 4
                    else:
                        spd_lim, life_lim = 2, 900 
                        spd, m_life, dmg = 1, 550, 7

        spd += self.wave//50
        if spd > spd_lim:
            spd = spd_lim
        m_life += 3 * (self.wave//5)
        if m_life > life_lim:
            m_life = life_lim

        return spd, m_life, dmg

    def add_enemy(self) -> None:
        if not self.enemy_timer.run and self.added_enemys < self.max_enemy_wave:
            self.enemy_timer.change_max_time(round(randint(0, 2) + random(), 2))
            e_size = self.get_enemy_size()
            speed, max_life, dmg = self.get_enemy_atrib(e_size)
            col_tower = self.tower.get_all_collisions()
            if e_size != 'MiniBoss' and e_size != 'Boss':
                e_type = 'Ground' if randint(1, 100) > self.chance_spawn_fly else 'Fly'
                valued_gold = 40 + int(0.8*self.wave//5) + (1 if e_type == 'Ground' else 2)
            else:
                valued_gold += 1000 + (25 * self.wave//25) if e_size == 'Mini Boss' else 2500 + (50 * self.wave//50) 
                e_type = e_size
            
            self.enemys.append(Enemy(self.display_surf, col_tower, [[e_size, e_type], speed, max_life, dmg, valued_gold]))
            self.added_enemys += 1
            self.enemy_timer.active()

    def remove_enemy(self) -> None:
        for i in range(len(self.enemys)-1, -1, -1):
            if self.enemys[i].is_dead() and self.enemys[i].can_remove():
                self.tower.increase_gold(self.enemys[i].get_valued_gold())
                self.removed_enemys += 1
                if self.enemys[i].get_type() != 'Boss' and self.enemys[i].get_type() != 'MiniBoss':
                    self.enemys_defeated[0] += 1
                else:
                    self.enemys_defeated[1] += 1
                self.enemys.pop(i)

    def update_enemys(self) -> None:
        for e in self.enemys:
            e.update([self.tower.get_lifebar(id=0), self.tower.get_lifebar(id=1)])
            self.check_enemy_attack(e)

    def check_enemy_attack(self, e) -> None:
        # verifica se o inimigo atacou alguma barricada ou a torre
        attack_bar = e.get_attack_bar()
        if attack_bar[0]:
            self.tower.bar_receive_dmg(e.dmg, id=0)
            e.set_attack_bar(False, id=0)
        else:
            if attack_bar[1]:
                self.tower.bar_receive_dmg(e.dmg, id=1)
                e.set_attack_bar(False, id=1)
            else:
                if e.get_attack_tower():
                    self.tower.receive_dmg(e.dmg)
                    e.set_attack_tower(False)

    def check_end_wave(self) -> None:
        # verifica se acabou os inimigos e passa pro buy_phase
        if len(self.enemys) == 0 and self.added_enemys == self.max_enemy_wave:
            self.wave += 1
            self.max_enemy_wave += 2
            self.added_enemys = 0
            self.removed_enemys = 0
            if self.wave % 5 == 0:
                self.max_enemy_wave += 5 if not self.switch else 10
                self.switch = not self.switch
            if self.wave == 5:
                self.chance_spawn_fly = 30
            else:
                if self.wave % 50 == 0 and self.wave <= 200:
                    self.chance_spawn_fly += 5 # limite de 50% chance 'fly'

            self.tower.increase_gold(25 + int((2.5 * self.wave//5)))
            self.tower.deactive_baits()
            self.buy_phase_active()
    
    def check_end_game(self) -> None:
        if self.tower.get_life() <= 0:
            self.game_over = True
            self.time_plyd = round(time() - self.start_time_plyed)
            # transformando o tempo(s) em hora, minuto e segundo
            t = [3600, 60, 1]
            v = 0
            for i in range(3):
                v = self.time_plyd//t[i]
                if v != 0:
                    self.time_plyd -= t[i]*v
                    t[i] = v
                else:
                    t[i] = 0 
            self.time_plyd = (f'{t[0]}H  ' if t[0] > 0 else '') + (f'{t[1]}m  ' if t[1] > 0 else '') + (f'{t[1]}s' if t[2] > 0 else '')
            self.channel.play(self.game_over_sound)
    
    def sort_enemys(self) -> None:
        # organizar o array de inimigos para armazenar info dos inimigos mais proximos para as tower_guns
        if not self.timer_sort.run and self.enemys:
            p = [] 
            p_new = []
            e_pos = []
            new_pos = []
            # adicionando as posições dos inimigos
            for i, e in enumerate(self.enemys):
                s = str(e.get_rect()[0])
                if len(s) != 4:
                    s = '0'*(4 - len(s)) + s
                e_pos.append(s)
                p.append(i)
            new_pos = e_pos[:]
            p_new = p[:]
            # radix sort para pegar lista dos indexes mais proximos da torre
            for i in range(len(e_pos[0])-1, -1, -1): 
                c_num = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                ini_pos = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                pos = 0
                for j in range(len(e_pos)):
                    n = int(e_pos[j][i])
                    c_num[n] += 1
                
                for j in range(len(ini_pos)):
                    n = c_num[j]
                    if n > 0:
                        ini_pos[j] = pos
                        pos += n
                for j in range(len(e_pos)):
                    n = int(e_pos[j][i])
                    new_pos[ini_pos[n]] = e_pos[j]
                    p_new[ini_pos[n]] = p[j]
                    #new_e[ini_pos[n]] = enemys[j]
                    ini_pos[n] += 1
                p = p_new[:]
                e_pos = new_pos[:]
            self.closests_enemys = p
            self.timer_sort.active()
