import pygame
from tower import Tower
from buy_phase import BuyPhase
from control import Control
from settings import screen_height, screen_width, tower_pos
from random import randint
from timerizer import Timer
from support import import_frames

class Level:
    def __init__(self, screen:pygame.display) -> None:
        self.display_surf = screen
        self.tower = Tower(self.display_surf)
        self.buy_phase = BuyPhase(self.display_surf, self.tower)
        self.control_game = Control(self.display_surf, self.tower, self.buy_phase.active, self.deactive)
        # start_game window
        self.start_game_surf = pygame.image.load('img/game_start.png').convert()
        self.start_game_rect = self.start_game_surf.get_rect(center= (screen_width/2, screen_height/2))
        self.stgame_button = pygame.Surface((95, 30))
        self.stgame_button_rect = self.stgame_button.get_rect(center= (screen_width/2, screen_height/2 + 18))
        # wind
        self.wind_surf = pygame.image.load('img/wind.png').convert_alpha()
        self.wind_surf = pygame.transform.scale(self.wind_surf, (self.wind_surf.get_width()/8, self.wind_surf.get_height
        ()/8))
        #girl_rock
        self.girl_rock_frames = import_frames('img/girl_rock')
        self.girl_rock_frames = [pygame.transform.scale(self.girl_rock_frames[i], (self.girl_rock_frames[i].get_width()/2.5, self.girl_rock_frames[i].get_height()/2.5)) for i in range(len(self.girl_rock_frames))]
        # sound
        self.wave_sound = pygame.mixer.Sound('sound/Wave.ogg')
        self.buy_phase_sound = pygame.mixer.Sound('sound/buy_phase.ogg')
        self.start_game_sound = pygame.mixer.Sound('sound/Mamonas Assassinas - Debil Metal.ogg')
        self.wave_sound.set_volume(0.03)
        self.buy_phase_sound.set_volume(0.1)
        self.start_game_sound.set_volume(0.1)
        self.channel = pygame.mixer.Channel(0)
        # mouse
        self.mouse_surf = pygame.Surface((5, 5))
        self.mouse_rect = self.mouse_surf.get_rect(center=(0, 0))
        # timer
        self.wind_timer = Timer(3)
        # initial state
        self.deactive()
        
    def active(self) -> None:
        self.run_game = True
        self.change_music = [True, False, False]
        self.tower.initial_atrib()

    def deactive(self) -> None:
        self.run_game = False
        self.change_music = [False, False, True]
        self.wind_pos = [[screen_width + 200, randint(0, screen_height - 350)], [screen_width + 400, randint(screen_height-450, screen_height - 200)], [screen_width + 700, randint(0, screen_height - 350)], [screen_width + 900, randint(screen_height-450, screen_height - 200)]]
        self.wind_opacity = [255, 255, 255, 255]
        # girl_rock
        self.girl_rock_frameid = 0
        self.girl_rock_image = self.girl_rock_frames[self.girl_rock_frameid]
        self.girl_rock_rect = self.girl_rock_image.get_rect(center = (45, 100))

    def draw(self) -> None:
        self.tower.draw(self.run_game)
        self.draw_girl_rock()
        if self.run_game:
            if self.buy_phase.is_active():
                self.buy_phase.draw()
            else:
                self.control_game.draw()
        else:
            self.draw_wind()
            self.draw_start_game()

    def draw_start_game(self) -> None:
        self.display_surf.blit(self.start_game_surf, self.start_game_rect)  
    
    def update(self) -> None:
        self.update_girl_rock()
        if self.run_game:
            if self.buy_phase.is_active():     
                self.play_music_theme(place=1)  
                self.tower.update(self.control_game.get_enemys(), close_e=[], paused=True)
                self.buy_phase.update()
            else:
                self.play_music_theme(place=0)  
                if not self.control_game.is_game_over() and not self.control_game.is_paused():
                    self.tower.update(self.control_game.get_enemys(), close_e=self.control_game.get_closests_enemys(), paused=False)
                    self.tower.set_do_once()
                self.control_game.update()                
        else:
            self.play_music_theme(place=1)
            self.check_wave_button()
            self.create_wind()
            self.update_winds()
            if self.wind_timer.run:
                self.wind_timer.update()

    def play_music_theme(self, place:int) -> None:
        if place == 0:
            if self.change_music[0]:
                self.channel.stop()
                self.channel.play(self.wave_sound, loops=-1)
                self.change_music[0] = False
                self.change_music[1] = True
        else:  
            if self.change_music[1]:
                self.channel.stop()
                self.channel.play(self.buy_phase_sound, loops=-1)
                self.change_music[1] = False
                self.change_music[0] = True
            else:
                if self.change_music[2]:
                    self.channel.stop()
                    self.channel.play(self.start_game_sound, loops=-1)
                    self.change_music[2] = False

    def check_wave_button(self) -> None:
        self.mouse_rect.center = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and self.stgame_button_rect.colliderect(self.mouse_rect):
            self.active()

    def draw_wind(self) -> None:
        for i in range(len(self.wind_pos)):
            self.wind_surf.set_alpha(self.wind_opacity[i])
            self.display_surf.blit(self.wind_surf, self.wind_pos[i])
    
    def create_wind(self) -> None:
        if not self.wind_timer.run:
            self.wind_pos.append([screen_width + 900, randint(0, screen_height - 350)])
            self.wind_pos.append([screen_width + 1100, randint(screen_height-450, screen_height - 200)])
            self.wind_opacity.append(255)
            self.wind_opacity.append(255)
            self.wind_timer.active()
    
    def update_winds(self) -> None:
        for i in range(len(self.wind_pos)-1, -1, -1):
            self.wind_pos[i][0] -= 2
            if self.wind_pos[i][0] <= tower_pos[0]:
                self.wind_opacity[i] -= 15
            if self.wind_opacity[i] <= 0:
                self.wind_pos.pop(i)
                self.wind_opacity.pop(i)

    def draw_girl_rock(self) -> None:
        if self.girl_rock_rect.right > -50:
            self.display_surf.blit(self.girl_rock_image, self.girl_rock_rect)

    def update_girl_rock(self) -> None:
        if self.girl_rock_rect.right > -50:
            if self.run_game:
                self.girl_rock_rect.centerx -= 3
            else:
                self.animation_girl_rock()
    
    def animation_girl_rock(self) -> None:
        self.girl_rock_frameid += 0.15
        if self.girl_rock_frameid > (len(self.girl_rock_frames) - 1):
            self.girl_rock_frameid = 0
        self.girl_rock_image = self.girl_rock_frames[int(self.girl_rock_frameid)]