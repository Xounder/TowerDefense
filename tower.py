import pygame
from guns import Gun, Missile
from settings import tower_gun_pos
from timerizer import Timer
from support import *
from settings import *
from enemy import Enemy

class Tower:
    def __init__(self, screen:pygame.display) -> None:
        self.display_surf = screen
        self.background = [pygame.image.load('img/back_tower.png').convert(), pygame.image.load('img/back_tower_spike.png').convert()]
        self.image = self.background[0]
        self.ply_gun = Gun(self.display_surf, 'Estilingue', ply=True)
        # gold
        self.gold_img = pygame.image.load('img/gold.png').convert()
        self.gold_rect = self.gold_img.get_rect(topleft= (screen_width - 200, 10))
        # tower collision
        self.tower_surf = pygame.Surface((10, 500))
        self.tower_rect = self.tower_surf.get_rect(bottomleft= (tower_pos))
        # barricades
        self.bars_frames = import_frames('img/defenses/barricade')
        self.bars_surf = [self.bars_frames[0] for i in range(2)]
        self.bars_rect = [self.bars_surf[i].get_rect(bottomright= (bar_pos[i][0] + 15, bar_pos[i][1])) for i in range(2)] 
        # baits
            # sky
        self.bait_sky_frames = import_frames('img/defenses/poison')
        self.bait_sky_atualframe = 0
        self.bait_sky_surf = self.bait_sky_frames[self.bait_sky_atualframe]
        self.bait_sky_rect = self.bait_sky_surf.get_rect(bottomleft= (bait_pos[1]))
            # solo
        self.bait_solo = pygame.Surface((135, 75))
        self.bait_solo_rect = self.bait_solo.get_rect(bottomleft= (bait_pos[0]))
        #Invul_Effect
        self.invul_frames = import_frames('img/Invul_Effect')
        self.invul_frames = [pygame.transform.scale(self.invul_frames[i], (self.invul_frames[i].get_width()*2, self.invul_frames[i].get_height()*2)) for i in range(len(self.invul_frames))]
        self.invul_image = self.invul_frames[0]
        self.invul_rect = self.invul_image.get_rect(bottomright= (tower_pos[0], screen_height))
        self.invul_frameid = 0
        #icons
        self.icon_size = 16
        self.life_icon = pygame.transform.scale(pygame.image.load('img/icons/Life.png'), (self.icon_size, self.icon_size))
        self.shield100_icon = pygame.transform.scale(pygame.image.load('img/icons/Shield100.png'), (self.icon_size, self.icon_size))
        self.shield200_icon = pygame.transform.scale(pygame.image.load('img/icons/Shield200.png'), (self.icon_size, self.icon_size))
        self.shield_atk_icon = pygame.transform.scale(pygame.image.load('img/icons/Barrier_Atk.png'), (self.icon_size, self.icon_size))
        self.brkn_shield_icon = pygame.transform.scale(pygame.image.load('img/icons/Brkn_Shield.png'), (self.icon_size, self.icon_size))
        self.heal_invul_icon = pygame.image.load('img/icons/Heal_Invul.png')
        self.missiles_icon = pygame.image.load('img/icons/Missiles.png')
        #sounds
        self.decrease_gold_sound = pygame.mixer.Sound('sound/Decrease_money.ogg')
        self.increase_gold_sound = pygame.mixer.Sound('sound/Increase_money.ogg')
        self.decrease_gold_sound.set_volume(0.1)
        self.increase_gold_sound.set_volume(0.5)
        self.dmg_sound = [pygame.mixer.Sound('sound/smash.ogg'), pygame.mixer.Sound('sound/Shield_smash.ogg')]
        self.dmg_sound[0].set_volume(0.05)
        self.dmg_sound[1].set_volume(0.05)
        self.channel1 = pygame.mixer.Channel(1)
        self.channel2 = pygame.mixer.Channel(2)
        # font
        self.font_40 = pygame.font.Font('font/Pixeltype.ttf', 40)
        self.font_25 = pygame.font.Font('font/Pixeltype.ttf', 25)
        # timer
        self.timer_healthbar = [Timer(3.5), Timer(3.5), Timer(3.5)]
        self.redflag_cons_timer = [Timer(0.7), Timer(0.7)]
        self.invul_timer = Timer(10)
        self.timer = Timer(0.7)
        # initial state
        self.initial_atrib()

    def initial_atrib(self) -> None:
        self.life = 100
        self.shield = 0    # 0/200
        self.gold = 0
        self.amount_gold = 0
        self.amount_opacity = 0
        self.amount_pos = []
        self.set_amount_pos = False
        self.more_gold = False
        self.barricades = [False, False]
        self.bar_life = [0, 0]
        self.baits = [False, False]
        self.guns_name = ['', '', 'Estilingue']
        self.tower_guns = ['', '']
        self.invulnerable = False
        self.consumables = [0, 0]   # Q(Missile)/E(Heal+Invunerability)
        self.used_consumables = [0, 0]
        self.missiles = []
        self.ply_gun.wait_timer.active()

    def get_used_consumables(self) -> list[int]:
        return self.used_consumables

    def set_consumables(self, cons:int, id:int=-1) -> None:
        if id != -1:
            self.consumables[id] = cons
        else:
            self.consumables = cons
    
    def get_consumables(self) -> list[int]:
        return self.consumables

    def increase_consumable(self, id:int) -> None:
        self.consumables[id] += 1

    def get_all_collisions(self) -> list:
        col =  [self.tower_rect, [' ', ' '], [' ', ' ']]
        if self.barricades[0]:
            col[1][0] = self.bars_rect[0]
        if self.barricades[1]:
            col[1][1] = self.bars_rect[1]
        if self.baits[0]:
            col[2][0] = self.bait_solo_rect
        if self.baits[1]:
            col[2][1] = self.bait_sky_rect
        return col

    def get_guns_name(self, id:int=-1) -> list[str]:
        return self.guns_name if id == -1 else self.guns_name[id]
    
    def set_guns_name(self, guns_name:str, id:int) -> None:
        self.guns_name[id] = guns_name

    def change_guns(self, id:int) -> None:
        if id == 2:
            self.ply_gun.change_gun(self.guns_name[id])
        else:
            if self.tower_guns[id] != '':
                self.tower_guns[id].change_gun(self.guns_name[id], tower_gun_pos[id])
            else:
                self.tower_guns[id] = Gun(self.display_surf, self.guns_name[id], tower_gun_pos[id], ply=False, tower=id)
    
    def get_gold(self) -> int:
        return self.gold
    
    def set_gold(self, gold:int) -> None:
        self.gold = gold

    def increase_gold(self, gold:int) -> None:
        self.amount_gold = gold
        self.amount_opacity = 100
        self.set_amount_pos = True
        self.more_gold = True
        self.gold += gold
        self.channel2.play(self.increase_gold_sound)

    def decrease_gold(self, gold:int) -> None:
        self.amount_gold = gold
        self.amount_opacity = 100
        self.set_amount_pos = True
        self.more_gold = False
        self.gold -= gold
        self.channel2.play(self.decrease_gold_sound)

    def is_last_gun(self, id:int) -> bool:
        return True if self.guns_name[id] == 'Laser' else False

    def get_life(self) -> int:
        return self.life

    def set_life(self, life:int) -> None:
        self.life = life
    
    def heal_life(self, heal:int) -> None:
        self.life += heal
    
    def is_max_life(self) -> bool:
        return True if self.life == 100 else False
    
    def set_shield(self, shield:int) -> None:
        self.shield = shield

    def get_shield(self) -> int:
        return self.shield
    
    def repair_shield(self, shield:int) -> None:
        self.shield += shield

    def is_max_shield(self) -> bool:
        return True if self.shield == 200 else False
    
    def is_bar(self, id:int) -> bool:
        return self.barricades[id]
    
    def is_max_lifebar(self, id:int) -> bool:
        return True if self.bar_life[id] == 200 else False
    
    def get_lifebar(self, id:int) -> int:
        return self.bar_life[id]
    
    def bar_receive_dmg(self, dmg:int, id:int) -> None:
        self.bar_life[id] -= dmg 
        if self.bar_life[id] <= 0:
            self.bar_life[id] = 0
            self.barricades[id] = False
        self.play_sound()
        self.timer_healthbar[id].active()

    def active_bar(self, id:int) -> None:
        self.barricades[id] = True
        self.bar_life[id] = 200 

    def is_bait(self, id:int) -> bool:
        return self.baits[id]
    
    def set_bait(self, bait:bool, id:int) -> None:
        self.baits[id] = bait

    def active_bait(self, id:int) -> None:
        self.baits[id] = True
    
    def deactive_baits(self) -> None:
        self.baits = [False, False]

    def is_max_consumable(self, id:int) -> bool:
        m = [5, 2]
        return True if self.consumables[id] == m[id] else False

    def receive_dmg(self, dmg:int) -> None:
        if not self.invulnerable:
            if self.shield > 0:
                self.shield -= dmg
            else:
                self.life -= dmg
            self.play_sound()
            self.timer_healthbar[2].active()

    def set_do_once(self) -> None:
        # ao entrar na BuyPhase ativar para poder recarregar a arma e mover as balas
        if self.tower_guns[0] != '':
            self.tower_guns[0].set_do_once(True)
        if self.tower_guns[1] != '':
            self.tower_guns[1].set_do_once(True)
        self.ply_gun.set_do_once(True)

    def play_sound(self) -> None:
        if self.timer_healthbar[2].run and self.shield == 0:
            self.channel1.play(self.dmg_sound[0])
        else:
            self.channel1.play(self.dmg_sound[1])

    def draw(self, run_game:bool) -> None:
        self.change_background()
        self.display_surf.blit(self.image, (0, 0))
        if run_game:
            self.draw_gold()
            self.draw_invulnerable()
            self.draw_consumables()
            self.draw_barricades()
            self.draw_sky_bait()
            self.draw_missiles()
            self.draw_guns()
            self.draw_all_health_bars()
    
    def draw_guns(self) -> None:
        for twr_gun in self.tower_guns:
            if twr_gun != '':
                twr_gun.draw()
        self.ply_gun.draw()

    def draw_all_health_bars(self) -> None:
        for i, t_healthbar in enumerate(self.timer_healthbar):
            if t_healthbar.run:
                self.draw_health_bars(i)

    def draw_gold(self) -> None:
        x_size = 100 + 12*len(str(self.gold))
        pos_x = screen_width - x_size
        self.gold_rect.topleft = [pos_x, 10]
        pygame.draw.rect(self.display_surf, 'gray', (pos_x - 10, 5, x_size, 42))
        pygame.draw.rect(self.display_surf, 'black', (pos_x - 10, 5, x_size, 42), 3)
        self.display_surf.blit(self.gold_img, self.gold_rect)
        blit_text_shadow(self.display_surf, f'${self.gold}', 'black', [pos_x + 45, 15], self.font_40, back_color='green')
        if self.amount_opacity > 0:
            if self.set_amount_pos:
                self.amount_pos = [pos_x + 45, 15]
                if self.more_gold:
                    self.amount_pos[1] += 60
                self.set_amount_pos = False
            self.draw_amount()

    def draw_amount(self) -> None:
        # qnd ganhar ou gastar dinheiro
        b_color = 'green' if self.more_gold else 'red'
        text = f'${self.amount_gold}' if self.more_gold else f'-${self.amount_gold}'
        blit_text_shadow(self.display_surf, text, 'black', self.amount_pos, self.font_40, back_color=b_color, alpha=self.amount_opacity)
        self.animation_amount()

    def draw_health_bars(self, defense_atacked:int=-1, show_buy:bool=False) -> None:
        size = [90, 15]
        # life e shield
        if defense_atacked == 2 or show_buy:
            self.draw_tower_hbar_icon(size)          
        # barricadas
        if defense_atacked == 1 or show_buy:
            self.draw_barricade_hbar_icon(size, id=1)           
        if defense_atacked == 0 or show_buy:
            self.draw_barricade_hbar_icon(size, id=0)

    def draw_tower_hbar_icon(self, size:tuple[int, int]) -> None:
        pos = [230, 270]
        icon = self.shield_atk_icon
        hbar = []
        c = ''
        if self.shield == 0 and self.life < 100:
            icon = self.life_icon
            hbar = self.life
            c = 'red'
        else:
            if 0 < self.shield <= 100:
                icon = self.shield100_icon
                hbar = self.shield
                c = '#00aaff'
            elif 100 < self.shield < 200:
                icon = self.shield200_icon
                hbar = self.shield - 100
                c = '#0000df'
        if icon != self.shield_atk_icon:
            self.draw_hbar_icon(icon, pos, size, hbar, c)

    def draw_barricade_hbar_icon(self, size:tuple[int, int], id:int) -> None:
        pos = [bar_pos[id][0] - 120, bar_pos[id][1] + 10]
        icon = self.life_icon
        hbar = 0
        c = ''
        if 0 < self.bar_life[id] <= 100:
            icon = self.brkn_shield_icon
            hbar = self.bar_life[1]
            c = '#00aaff'
        elif 100 < self.bar_life[id] < 200:
            icon = self.shield_atk_icon
            hbar = self.bar_life[id] - 100
            c = '#0000df'
        if icon != self.life_icon:
            self.draw_hbar_icon(icon, pos, size, hbar, c)

    def draw_hbar_icon(self, icon:pygame.image, pos:tuple[int, int], size:tuple[int, int], hbar:list[int], c:str) -> None:
        draw_health_bar(self.display_surf, hbar, 100, c, pos, size)
        draw_icon(self.display_surf, icon, [(pos[0] + size[0] + 2), (pos[1]-4)], self.icon_size)
    
    def draw_barricades(self) -> None:
        self.change_frame_and_draw(id=0)
        self.change_frame_and_draw(id=1)

    def change_frame_and_draw(self, id:int) -> None:
        if self.barricades[id]:
            if self.bar_life[id] > 100:
                self.bars_surf[id] = self.bars_frames[1]
            else:
                self.bars_surf[id] = self.bars_frames[0]
            self.display_surf.blit(self.bars_surf[id], self.bars_rect[id])
    
    def draw_sky_bait(self) -> None:
        if self.baits[1]: 
            self.display_surf.blit(self.bait_sky_surf, self.bait_sky_rect)
            self.animation_sky_bait()
    
    def draw_missiles(self) -> None:
        if self.missiles:
            for m in self.missiles:
                m.draw()

    def draw_invulnerable(self) -> None:
        if self.invulnerable:
            self.display_surf.blit(self.invul_image, self.invul_rect)
            self.animation_invul_tower()

    def draw_consumables(self) -> None:
        size = 48
        pos = [[5, (screen_height - 65)], [(size + 30), (screen_height - 65)]]
        c = 'red' if self.redflag_cons_timer[0].run else 'black'
        draw_icon(self.display_surf, self.missiles_icon, pos[0], size, color=c)
        blit_text_shadow(self.display_surf, 'Q', 'white', (pos[0][0] + (size + 3), pos[0][1] - 5), self.font_25, back_color='black')
        blit_text_shadow(self.display_surf, f'{self.consumables[0]}x', 'red', (pos[0][0] + (size - 5), pos[0][1] + (size - 5)), self.font_25, back_color='black')
        c = 'red' if self.redflag_cons_timer[1].run else 'black'
        draw_icon(self.display_surf, self.heal_invul_icon, pos[1], size, color=c)
        blit_text_shadow(self.display_surf, 'E', 'white', (pos[1][0] + (size + 3), pos[1][1] - 5), self.font_25, back_color='black')
        blit_text_shadow(self.display_surf, f'{self.consumables[1]}x', 'red', (pos[1][0] + (size - 5), pos[1][1] + (size - 5)), self.font_25, back_color='black')

    def animation_amount(self) -> None:
        if self.more_gold:
            self.amount_pos[1] -= 2
            self.amount_opacity -= 3        
        else:
            self.amount_pos[1] += 2
            self.amount_opacity -= 2

    def animation_invul_tower(self) -> None:
        self.invul_frameid += 0.15
        if self.invul_frameid > (len(self.invul_frames) - 1):
            self.invul_frameid = 0
        self.invul_image = self.invul_frames[int(self.invul_frameid)]
        self.invul_image.set_alpha(80)

    def animation_sky_bait(self) -> None:
        self.bait_sky_atualframe += 0.1
        if self.bait_sky_atualframe > len(self.bait_sky_frames):
            self.bait_sky_atualframe = 0
        self.bait_sky_surf = self.bait_sky_frames[int(self.bait_sky_atualframe)]
    
    def change_background(self) -> None:
        if self.baits[0]:
            self.image = self.background[1]
        else:
            self.image = self.background[0]

    def update_missiles(self, enemys:list[Enemy]) -> None:
        if self.missiles:
            for i in range((len(self.missiles) - 1), -1, -1):
                self.missiles[i].update(enemys)
                if self.missiles[i].can_destroy():
                    self.missiles.pop(i)

    def update_timers(self) -> None:
        for t_healthbar in self.timer_healthbar:
            if t_healthbar.run:
                t_healthbar.update()
        for rf_cons in self.redflag_cons_timer:
            if rf_cons.run:
                rf_cons.update()
        if self.timer.run:
            self.timer.update()
        if self.invul_timer.run:
            self.invul_timer.update()
        else:
            self.invulnerable = False

    def update(self, enemys:list[Enemy], close_e:list[int], paused:bool) -> None:
        for twr_gun in self.tower_guns:
            if twr_gun != '':
                twr_gun.update(enemys, close_e, paused)
        self.ply_gun.update(enemys, close_e, paused)
        self.update_missiles(enemys)
        if not paused:
            self.input()
            self.update_timers()

    def input(self) -> None:
        if not self.timer.run:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]: # missile
                self.check_use_consumable(id=0)
                self.timer.active()
            elif keys[pygame.K_e]:
                self.check_use_consumable(id = 1)
                self.timer.active()
    
    def check_use_consumable(self, id:int) -> None:
        if self.consumables[id] > 0:
            self.consumables[id] -= 1
            self.consumable_used(id)
        else:
            self.redflag_cons_timer[id].active()

    def consumable_used(self, id:int) -> None:
        if id == 0:
            self.missiles.append(Missile(self.display_surf, [pygame.mouse.get_pos()[0], -100]))
            self.used_consumables[0] += 1
        else:
            self.life = 100
            self.invulnerable = True
            self.used_consumables[1] += 1
            self.invul_timer.active()
