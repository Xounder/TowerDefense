import pygame
from settings import *
from timerizer import Timer
from tower import Tower
from support import *
from typing import Callable

class Button:
    def __init__(self, screen:pygame.display, pos:tuple[int, int], size:tuple[int, int], path:str='', inv:bool=False) -> None:
        self.display_surf = screen
        self.pressed = False
        self.image = pygame.Surface(size) if inv else pygame.transform.scale(pygame.image.load(path), size)
        self.rect = self.image.get_rect(topleft= pos)
    
    def get_pressed(self) -> bool:
        return self.pressed
    
    def set_pressed(self, pressed) -> None:
        self.pressed = pressed

    def draw(self) -> None:
        self.display_surf.blit(self.image, self.rect)

    def update(self, mouse_rect) -> None:
        self.input(mouse_rect)

    def input(self, mouse_rect) -> bool:
        self.pressed = not self.pressed if self.rect.colliderect(mouse_rect) else False


class BuyStand:
    def __init__(self, screen:pygame.display, id:int, tower:Tower, select_show_buttons:Callable) -> None:
        self.display_surf = screen
        self.id = id
        self.tower = tower
        self.image = pygame.image.load('img/buy_stand.png').convert_alpha()
        self.rect = self.image.get_rect(topleft= (buy_stand_pos[self.id]))
        # var's
        pos = (self.rect.midbottom[0] - 10, self.rect.midbottom[1] - 35)
        self.button_buy = Button(self.display_surf, pos, (89, 29), path='img/buy_button.png')
        self.select_show_buttons = select_show_buttons
        self.buy_stand = buy_stand[f'{self.id}']
        self.atual_buy_stand = []
        self.pressed = False
        self.activated = False
        self.buy_item = False
        self.is_repair = False
        # font
        self.font_30 = pygame.font.Font('font/Pixeltype.ttf', 30)

    def active(self) -> None:
        self.activated = True
        self.change_attributes()

    def deactive(self) -> None:
        self.activated = False
        self.pressed = False
        self.buy_item = False
        self.atual_buy_stand = []
        self.is_repair = False

    def verify_barricade(self, is_tbar:bool) -> str:
        # verifica se possui ou não barricada e retorna o caminho da imagem
        if is_tbar:
            self.atual_buy_stand = self.buy_stand['Repair']
            path = f'{self.atual_buy_stand[0]}_repair.png'
            self.is_repair = True
        else:
            self.atual_buy_stand = self.buy_stand['Build']
            path = f'{self.atual_buy_stand[0]}_build.png'
        return path

    def change_attributes(self) -> None:
        # modifica imagem e [nome, qnt, valor] dos itens disponiveis
        self.atual_buy_stand = self.buy_stand
        path = f'img/buy_stand/'
        if self.id < 3:
            name = self.tower.get_guns_name(self.id)
            self.atual_buy_stand = self.buy_stand[name]
            gun_name = all_guns[all_guns.index(name) + 1]
            path = f'img/guns/{gun_name}/{gun_name}.png'
        else:
            if 5 <= self.id <= 6:
                path += self.verify_barricade(self.tower.is_bar(0) if self.id == 5 else self.tower.is_bar(1))
            else:
                if 7 <= self.id <= 8:
                    path += f'{self.atual_buy_stand[0]}1.png' if self.id == 7 else f'{self.atual_buy_stand[0]}2.png'
                else:
                    path += f'{self.atual_buy_stand[0]}.png'
                    
        self.item_img = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (48, 48))
        self.item_rect = self.item_img.get_rect(topleft=(self.rect.topleft[0] + 11, self.rect.topleft[1] + 11))
        
    def draw(self, b_buy:bool) -> None:
        if self.activated:
            self.display_surf.blit(self.image, self.rect)
            self.display_surf.blit(self.item_img, self.item_rect)
            self.draw_item_info(b_buy)
            if b_buy:
                self.button_buy.draw()

    def draw_item_info(self, b_buy:bool) -> None:
        gold = self.tower.get_gold() if b_buy else 2000
        qnt, value = self.calc_half(gold) if (3 <= self.id <= 4) else self.atual_buy_stand[1:3]
        blit_text_shadow(self.display_surf, f'{qnt}x', 'black', [self.rect.midbottom[0] - 30, self.rect.midbottom[1] - 20], self.font_30, back_color='white', right=True)
        blit_text_shadow(self.display_surf, f'${value}', 'black', [self.rect.midbottom[0] + 35, self.rect.midbottom[1] - 53], self.font_30, back_color='green', center=True)

    def update(self, mouse_rect:pygame.rect, b_buy:bool) -> None:
        if self.activated and b_buy:
            self.input(mouse_rect)
            self.check_buy_item()

    def input(self, mouse_rect:pygame.rect) -> None:
        self.button_buy.update(mouse_rect)
        if self.button_buy.get_pressed():
            self.pressed = True
            self.button_buy.set_pressed(False)

    def check_buy_item(self) -> None:
        if self.pressed:
            self.buy_full() if (self.id != 3 and self.id != 4) else self.buy_half()
            self.select_show_buttons()
            self.deactive()
    
    def buy_full(self) -> None:
        # compra completo, somente
        gold = self.tower.get_gold()
        if gold >= self.atual_buy_stand[2]:
            if self.id < 3:
                self.tower.set_guns_name(self.atual_buy_stand[0], self.id)
                self.tower.change_guns(self.id)
            elif 5 <= self.id <= 6:
                self.tower.active_bar((self.id - 5))
            else:
                if 7 <= self.id <= 8:
                    self.tower.active_bait((self.id - 7))
                else:
                    self.tower.increase_consumable((self.id - 9))
            self.tower.decrease_gold(self.atual_buy_stand[2])

    def buy_half(self) -> None:
        # restaura parcialmente ou completamente
        gold = self.tower.get_gold()
        restore, exp_gold = self.calc_half(gold)
        self.tower.decrease_gold(exp_gold)
        self.tower.heal_life(restore) if self.id == 3 else self.tower.repair_shield(restore)
    
    def calc_half(self, gold) -> tuple[int, int]:
        # verifica se é possivel encher a vida/shield com a grana, caso não, enche somente o necessário
        restore = (100 - self.tower.get_life()) if self.id == 3 else (200 - self.tower.get_shield())
        exp_gold = (int(restore/self.atual_buy_stand[1]) * self.atual_buy_stand[2])
        if gold < exp_gold:
            restore = int(gold/self.atual_buy_stand[2])
            exp_gold = (int(restore/self.atual_buy_stand[1]) * self.atual_buy_stand[2])
        return restore, exp_gold

class BuyPhase:
    def __init__(self, screen:pygame.display, tower:Tower) -> None:
        self.display_surf = screen
        self.tower = tower
        # buy_buttons img
        self.qnt_itens = 11
        self.buy_buttons = [Button(self.display_surf, sum_buttons_pos[i], (24, 24), path='img/buy.png') for i in range(self.qnt_itens)]
        self.buy_stand = [BuyStand(self.display_surf, i, self.tower, self.select_show_buttons) for i in range(self.qnt_itens)]
        # next_wave window
        self.next_wave = pygame.image.load('img/next_wave.png').convert()
        self.next_wave_rect = self.next_wave.get_rect(topleft= (screen_width - 240, (screen_height/2) - 80))
        self.next_wave_button = Button(self.display_surf, (screen_width - 180, (screen_height/2) - 40), [95, 30], inv=True)
        # var's
        self.activated = False
        self.atual_buy_button = -1
        self.show_all_buystand = False
        # font
        self.font_40 = pygame.font.Font('font/Pixeltype.ttf', 40)
        # mouse
        self.mouse_timer = Timer(0.6)
        self.keyboard_timer = Timer(0.6)
        self.mouse_surf = pygame.Surface((5, 5))
        self.mouse_rect = self.mouse_surf.get_rect(center= (0, 0))

    def is_active(self) -> None:
        return self.activated

    def active(self) -> None:
        self.activated = True
        self.select_show_buttons()
    
    def select_show_buttons(self) -> None:
        # verificador de quais botões serão mostrados
        self.show_buttons = [i for i in range(self.qnt_itens) if self.not_cancel_buy_button(i)]

    def deactive(self) -> None:
        self.activated = False
        self.buy_buttons[self.atual_buy_button].set_pressed(False)
        self.deactive_atual_buystand()
        self.atual_buy_button = -1
        self.show_all_buystand = False

    def deactive_atual_buystand(self) -> None:
        self.buy_stand[self.atual_buy_button].deactive()

    def can_buy(self, price:int) -> bool:
        return self.tower.get_gold() >= price
    
    def can_buy_nextgun(self, id:int) -> bool:
        # verifica se é possivel comprar a proxima arma com o gold que possui
        atual_gun = self.tower.get_guns_name(id)
        price_nextgun = buy_stand[str(id)][atual_gun][2]
        return self.can_buy(price_nextgun)

    def not_cancel_buy_button(self, i:int) -> bool:
        # verificações
        if not self.show_all_buystand:
            if 0 <= i <= 2:
                return (not self.tower.is_last_gun(i) and self.can_buy_nextgun(i))
            elif i == 3:
                return (not self.tower.is_max_life() and self.can_buy(buy_stand[str(i)][2]))
            elif i == 4:
                return (not self.tower.is_max_shield() and self.can_buy(buy_stand[str(i)][2]))
            elif 5 <= i <= 6:
                if not self.tower.is_bar((i - 5)):
                    return self.can_buy(buy_stand[str(i)]['Build'][2])
                else:
                    return (not self.tower.is_max_lifebar((i - 5)) and self.can_buy(buy_stand[str(i)]['Repair'][2]))
            elif 7 <= i <= 8:
                return (not self.tower.is_bait((i - 7)) and self.can_buy(buy_stand[str(i)][2]))
            else:
                return (not self.tower.is_max_consumable((i - 9)) and self.can_buy(buy_stand[str(i)][2]))
        else:
            if 0 <= i <= 2:
                return not self.tower.is_last_gun(i)
            elif i == 3:
                return not self.tower.is_max_life()
            elif i == 4:
                return not self.tower.is_max_shield()
            elif 5 <= i <= 6:
                if not self.tower.is_bar((i - 5)):
                    return True
                else:
                    return not self.tower.is_max_lifebar((i - 5))
            elif 7 <= i <= 8:
                return not self.tower.is_bait((i - 7))
            else:
                return not self.tower.is_max_consumable((i - 9))

    def draw(self) -> None:
        self.tower.draw_health_bars(show_buy=True)
        self.draw_buy_buttons()
        self.draw_atual_buy_stand()
        self.display_surf.blit(self.next_wave, self.next_wave_rect)

    def draw_atual_buy_stand(self) -> None:
        if self.atual_buy_button != -1:
            self.buy_stand[self.atual_buy_button].draw(b_buy=(not self.show_all_buystand))

    def draw_buy_buttons(self) -> None:
        for i in range(len(self.buy_buttons)):
            if self.show_buttons.count(i) == 1:
                self.buy_buttons[i].draw()

    def update_timers(self) -> None:
        if self.mouse_timer.run:
            self.mouse_timer.update()
        if self.keyboard_timer.run:
            self.keyboard_timer.update()

    def update(self) -> None:
        self.update_timers()
        self.input()

    def update_atual_buy_stand(self) -> None:
        if self.atual_buy_button > -1:
            self.buy_stand[self.atual_buy_button].update(self.mouse_rect, b_buy=(not self.show_all_buystand))

    def input(self) -> None:
        self.mouse_input()
        self.keyboard_input()

    def keyboard_input(self) -> None:
        if not self.keyboard_timer.run:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_TAB]:
                if self.show_all_buystand:
                    self.show_all_buystand = False
                else:
                    self.show_all_buystand = True
                self.deactive_atual_buystand()
                self.select_show_buttons()
                self.keyboard_timer.active()

    def mouse_input(self) -> None:
        if not self.mouse_timer.run:
            if pygame.mouse.get_pressed()[0]:
                self.mouse_rect.center = pygame.mouse.get_pos()
                self.check_wave_button()
                self.check_buy_button_pressed()
                self.update_atual_buy_stand()
                self.mouse_timer.active() 

    def check_buy_button_pressed(self) -> None:
        for i, button in enumerate(self.buy_buttons):
            if self.show_buttons.count(i) == 1:
                button.update(self.mouse_rect)
                if button.get_pressed():
                    if i != self.atual_buy_button:
                        self.buy_buttons[self.atual_buy_button].set_pressed(False)
                        self.deactive_atual_buystand()
                    self.atual_buy_button = i
                    self.buy_stand[self.atual_buy_button].active()
                    break
    
    def check_wave_button(self) -> None:
        self.next_wave_button.update(self.mouse_rect)
        if self.next_wave_button.get_pressed():
            self.deactive()
