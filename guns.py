import pygame
from timerizer import Timer
from math import atan, pi
from settings import *
from enemy import Enemy
from support import draw_health_bar, import_frames

class Gun(pygame.sprite.Sprite):
    def __init__(self, screen:pygame.display, name:str, pos:tuple[int, int]=[], ply:bool=True, tower:int=-1) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.display_surf = screen
        self.projectiles = []
        self.is_ply = ply
        self.tower = tower
        self.change_gun(name, pos)
    
    def import_assets(self) -> None:
        # importa as imagens do diretorio
        self.gun_states = [pygame.image.load(f'img/guns/{self.name}/{self.name}.png').convert_alpha(), pygame.image.load(f'img/guns/{self.name}/{self.name}_fire.png').convert_alpha()]
        self.reload_frames = import_frames(f'img/guns/{self.name}/reload')

    def change_gun(self, name:str, pos:tuple[int, int]=[]) -> None:
        # modifica a arma utilizada
        self.name = name
        self.import_assets()
        self.image = self.gun_states[0]
        self.view_image = self.image
        self.pos = pos if pos else ply_gun_pos
        self.rect = self.view_image.get_rect(center= (self.pos))
        self.reload_frame_id = 0
        #var's
        self.gun_atrib = guns[self.name]
        self.ammo = self.gun_atrib[2]   # munição
        self.m_pos = [0, 0] # posição do mouse
        self.theta = 0
        self.prev_theta = 0
        self.atual_ammo = self.ammo
        self.wait_once = False
        self.do_once = False
        self.gun_fire = False
        space_reload_frames = round(self.gun_atrib[1]/len(self.reload_frames), 1)
        # sounds
        self.gun_sounds = [pygame.mixer.Sound(f'sound/{self.name}_shot.ogg'), pygame.mixer.Sound(f'sound/{self.name}_reload.ogg')]
        gun_volsound = guns_volsound[self.name]
        self.gun_sounds[0].set_volume(gun_volsound[0])
        self.gun_sounds[1].set_volume(gun_volsound[1])
        if self.is_ply:
            self.channel1 = pygame.mixer.Channel(4)
            self.channel2 = pygame.mixer.Channel(5)
        else:
            if self.tower == 0:
                self.channel1 = pygame.mixer.Channel(6)
                self.channel2 = pygame.mixer.Channel(7)
            else:
                self.channel1 = pygame.mixer.Channel(8)
                self.channel2 = pygame.mixer.Channel(9)
        # timer
        self.wait_timer = Timer(self.gun_atrib[0]) # tempo de espera para soltar outro projetil
        self.reload_timer = Timer(self.gun_atrib[1]) # tempo de recarga das munições
        self.animation_timer = Timer(space_reload_frames)

    def set_do_once(self, do_once:bool) -> None:
        self.do_once = do_once

    def animation_reload(self) -> None:
        # animação do recarregamento da arma
        if self.reload_timer.run:
            if not self.animation_timer.run:
                if self.reload_frame_id < len(self.reload_frames):
                    self.image = self.reload_frames[self.reload_frame_id]
                    self.reload_frame_id += 1
                    self.animation_timer.active()

    def draw(self) -> None:
        self.draw_projectiles()
        self.display_surf.blit(self.view_image, self.rect)
        self.draw_ammo_bar()

    def draw_projectiles(self) -> None:
        for projectile in self.projectiles:
            projectile.draw()

    def draw_ammo_bar(self) -> None:
        color = 'red' if self.atual_ammo < self.ammo/2 else 'green'
        draw_health_bar(self.display_surf, self.atual_ammo, self.ammo, color, [self.rect.midbottom[0] - 15, self.rect.midbottom[1] + 5], [30, 10])

    def update_timers(self) -> None:
        if self.wait_timer.run:
            self.wait_timer.update()
        if self.reload_timer.run:
            self.reload_timer.update()
        if self.animation_timer.run:
            self.animation_timer.update()

    def update_projectiles(self, enemys) -> None:
        for projectile in self.projectiles:
            projectile.update(enemys)

    def update(self, enemys:list[Enemy], close_e:list[int], paused:bool) -> None:
        self.update_timers()
        if not paused:
            if self.is_ply:
                if self.gun_fire and self.name == 'Laser':
                    pass
                else:
                    self.extract_ply_angle()
                    self.rotate()
            else:
                if enemys:
                    self.extract_tower_angle(enemys, close_e)
                    self.rotate()
        else:
            self.reload_gun_buy_phase()

        self.update_projectiles(enemys)
        self.remove_projectiles()
        if self.reload_timer.run:
            self.reload_animation()
        else:
            self.set_to_idle()
            self.verify_shot(enemys, paused)

    def verify_shot(self, enemys:list[Enemy], paused:bool):
        if not paused:
            if self.is_ply:
                self.input()
            else:
                self.auto_fire(enemys)

    def reload_animation(self) -> None:
        self.animation_reload()
        self.gun_fire = False
    
    def set_to_idle(self) -> None:
        if self.wait_once:
            self.image = self.gun_states[0]
            self.wait_once = False
            self.atual_ammo = self.ammo
            self.channel2.stop()
            self.wait_timer.active()

    def remove_projectiles(self) -> None:
        # remove o projetil que colidiu ou que ultrapassou a borda da tela
        for i in range(len(self.projectiles)-1, -1, -1):
            if self.projectiles[i].destroy:
                self.projectiles.pop(i)

    def extract_func(self, p1:list[int], p2:list[int]) -> list[int]: #rect, mpos
        # extrai a função necessária para o calculo da rota do projetil
        try:
            a = (p2[1] - p1[1]) / (p2[0] - p1[0])
            b = p1[1] - (p1[0]*a)
        except ZeroDivisionError as e:
            a = 0
            b = -20
        return [round(a, 4), round(b, 4)]

    def input(self) -> None:
        # player_input
        if not self.wait_timer.run:
            self.check_create_projectile((pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]))

    def auto_fire(self, enemys:list[Enemy]) -> None:
        # tiro das torres
        if not self.wait_timer.run:
            can_fire = self.can_fire(enemys)
            if not can_fire:
                can_fire = self.can_fire(enemys)
            self.check_create_projectile(can_fire)   

    def can_fire(self, enemys:list[Enemy]) -> bool:         
        can_fire = False
        for e in enemys:
            if e.get_pos()[0] <= screen_width:
                tp = e.get_type()
                if self.tower == 1:
                    if tp != 'Fly':
                        can_fire = True
                        break
                else:
                    if tp != 'Ground' and tp != 'MiniBoss':
                        can_fire = True
                        break
        return can_fire

    def check_create_projectile(self, can_fire:bool) -> None:
        #verifica se pode criar o projetil
        if can_fire:
            if self.theta != '':
                if -78 <= self.theta <= 50:
                    self.create_projectile()
                    self.image = self.gun_states[1]
                    self.gun_fire = True
                    self.channel1.play(self.gun_sounds[0])
                    self.wait_timer.active()
        else:
            self.gun_fire = False
            self.image = self.gun_states[0]

    def create_projectile(self) -> None:
        # cria o projetil se houver munição
        if not self.reload_timer.run:
            self.atual_ammo -= 1
            func = self.extract_func(self.rect.center, self.m_pos)
            gun_atrib = [self.name, self.gun_atrib[3], self.gun_atrib[4]]
            self.projectiles.append(Projectile(self.display_surf, gun_atrib, self.rect.center, func, self.theta, self.m_pos, self.is_ply))
            self.reload_gun()

    def reload_gun_buy_phase(self) -> None:
        if self.do_once and self.atual_ammo < self.ammo:
            self.gun_fire = False
            self.do_once = False
            self.atual_ammo = 0
            self.reload_gun()

    def reload_gun(self) -> None:
        if self.atual_ammo == 0:
            self.reload_frame_id = 0
            self.wait_once = True
            self.channel2.play(self.gun_sounds[1])
            self.reload_timer.active()

    def rotate(self) -> None:
        #modifica o angulo da arma
        if self.theta != '':
            self.view_image = pygame.transform.rotate(self.image, self.theta)
            self.prev_theta = self.theta
        else:           
            self.move_to_origin()
            self.view_image = pygame.transform.rotate(self.image, self.prev_theta)
        self.rect = self.view_image.get_rect(center = (self.pos))

    def move_to_origin(self) -> None:
        if self.prev_theta < 0:
            self.prev_theta += 3
            if self.prev_theta >= 0:
                self.prev_theta = 0
        else:
            self.prev_theta -= 3
            if self.prev_theta <= 0:
                self.prev_theta = 0

    def extract_ply_angle(self) -> None:
        # extrai o angulo para a rotação da arma e do projetil do ply
        self.m_pos = pygame.mouse.get_pos()
        width = abs(self.rect.centerx - self.m_pos[0])
        height = abs(self.rect.centery - self.m_pos[1])
        self.extract_angle(width, height)
    
    def extract_angle(self, width:int, height:int) -> None:
        # extrai o angulo para a rotação da arma e do projetil
        if self.rect.centerx > self.m_pos[0]:
            self.theta = ''
        else: 
            try:
                self.theta = atan((height/width))
                self.theta = 180 * self.theta / pi 
                self.theta *= -1 if self.rect.centery < self.m_pos[1] else 1
            except ZeroDivisionError as e:
                self.theta = ''

    def extract_tower_angle(self, enemys:list[Enemy], close_e:list[int]) -> None:
        # extrai o angulo para a rotação da arma e do projetil da torre
        width, height = 0, 0
        for n in close_e:
            try:
                tp = enemys[n].get_type()
                if self.tower == 0:
                    if tp != 'Ground' and tp != 'MiniBoss':
                        self.m_pos = enemys[n].get_pos(center=True)
                        width = abs(self.rect.centerx - self.m_pos[0])
                        height = abs(self.rect.centery - self.m_pos[1])
                        break
                else:
                    if tp != 'Fly':
                        self.m_pos = enemys[n].get_pos(center=True)
                        width = abs(self.rect.centerx - self.m_pos[0])
                        height = abs(self.rect.centery - self.m_pos[1])
                        break
            except IndexError:
                pass
        self.extract_angle(width, height)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, screen:pygame.display, 
                 gun_atrib:list[int], 
                 pos:tuple[int, int], 
                 func:list[int], 
                 theta:float, 
                 end_pos:tuple[int, int], 
                 is_ply:bool) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.display_surf = screen
        self.image = pygame.transform.rotate(pygame.image.load(f'img/guns/projectiles/{projectiles[gun_atrib[0]]}.png').convert_alpha(), theta)
        self.rect = self.image.get_rect(center= (pos))
        # var's
        self.max_vel = gun_atrib[1]
        self.vel = self.max_vel
        self.dmg = gun_atrib[2] if is_ply else round(gun_atrib[2] - (gun_atrib[2] * 0.5), 2)
        self.destroy = False
        self.func = func
        self.diff_pos = [abs(self.rect.centerx - end_pos[0]), abs(self.rect.centery - end_pos[1])]

    def draw(self) -> None:
        self.display_surf.blit(self.image, self.rect)

    def update(self, enemys:list[Enemy]) -> None:
        self.movement()
        self.check_collision(enemys)
        self.check_out_layout()
    
    def movement(self) -> None:
        if self.diff_pos[0] > self.diff_pos[1]: 
            self.vel = self.max_vel
        else:     # para dar um movimento mais smooth qnd atira pra baixo
            self.vel = self.max_vel/2
        self.rect.centerx += self.vel   
        self.rect.centery = self.func[0]*self.rect.centerx + self.func[1]

    def check_collision(self, enemys:list[Enemy]) -> None:
        for e in enemys:
            e_rect = e.get_rect()
            if e_rect.midleft[0] <= screen_width and not e.is_dead(): 
                if self.rect.colliderect(e_rect):
                    e.decrease_life(self.dmg)
                    e.show_life()
                    self.destroy = True
                    break
    
    def check_out_layout(self) -> None:
        if self.rect.midleft[0] > screen_width and self.rect.midleft[1] > screen_height:
            self.destroy = True

class Missile(pygame.sprite.Sprite):
    def __init__(self, screen:pygame.display, pos:tuple[int, int]) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.display_surf = screen
        #var's
        self.dmg = 50
        self.space_x = 150 # area de alcance
        self.destroy = False
        self.show_animation = False
        self.collide = False
        # images
        self.image = pygame.image.load('img/missile/missile.png').convert_alpha()
        self.rect = self.image.get_rect(center=(pos))
        self.col_surf = pygame.Surface((self.space_x, 70))
        self.col_rect = self.col_surf.get_rect(center=(pos))
        # explosion
        self.explosion_frames = import_frames('img/missile/explosion')
        self.exp_image = self.explosion_frames[0]
        self.exp_rect = self.exp_image.get_rect(center=(pos))
        self.exp_frameid = 0
        # sound
        self.missile_sound = pygame.mixer.Sound('sound/Missile.ogg') #########
        self.missile_sound.set_volume(0.2)
        self.channel = pygame.mixer.Channel(10)
        #timer
        self.exp_animation_timer = Timer(0.8)

    def can_destroy(self) -> None:
        return self.destroy

    def draw(self) -> None:
        if not self.show_animation:
            self.display_surf.blit(self.image, self.rect)
        else:
            self.display_surf.blit(self.exp_image, self.exp_rect)

    def update(self, enemys:list[Enemy]) -> None:
        if self.exp_animation_timer.run:
            self.exp_animation_timer.update()
        if not self.show_animation:
            self.rect.centery += 5
            self.col_rect.center = self.rect.center
            self.check_collision(enemys)
        else:
            if not self.exp_animation_timer.run:
                self.destroy = True
            else:
                self.explosion_animation()
    
    def explosion_animation(self) -> None:
        self.exp_frameid += 0.2
        if self.exp_frameid > (len(self.explosion_frames) - 1):
            self.exp_frameid = 0
        self.exp_image = self.explosion_frames[int(self.exp_frameid)]

    def set_explosion(self) -> None:
        self.show_animation = True
        self.exp_rect.center = self.rect.center
        self.channel.play(self.missile_sound)
        self.exp_animation_timer.active()

    def check_collision(self, enemys:list[Enemy]) -> None:
        if not self.collide:
            # verifica se colidiu
            if self.rect.centery > screen_height - 200:
                self.collide = True
            else:
                for e in enemys:
                    e_rect = e.get_rect()
                    if e_rect.midleft[0] <= screen_width and not e.is_dead(): 
                        if self.rect.colliderect(e_rect):
                            self.collide = True
                            break
        else:
            # ao colidir verifica quais inimigos foram afetados pelo raio da explosão
            self.col_rect.center = self.rect.center
            for e in enemys:
                e_rect = e.get_rect()
                if e_rect.midleft[0] <= screen_width and not e.is_dead(): 
                    if self.col_rect.colliderect(e_rect):
                        e.decrease_life(self.dmg)
                        e.show_life()

            self.set_explosion()