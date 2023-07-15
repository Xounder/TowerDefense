import pygame
from os import walk

def blit_text(display_surf:pygame.display, 
              text:str, 
              color:str, 
              pos:list[int], 
              font:pygame.font.Font, 
              right:bool=False, 
              center:bool=False, 
              alpha:int=-1) -> None:
    overlay_txt = font.render(text, False, color)
    if right:
        overlay_txt_rect = overlay_txt.get_rect(topright= (pos))
    elif center:
        overlay_txt_rect = overlay_txt.get_rect(center= (pos))
    else:
        overlay_txt_rect = overlay_txt.get_rect(topleft= (pos))
    
    if alpha != -1:
        overlay_txt.set_alpha(alpha)  
    display_surf.blit(overlay_txt, overlay_txt_rect)

def blit_text_shadow(display_surf:pygame.display, 
                     text:str, 
                     color:str, 
                     pos:tuple[int, int], 
                     font:pygame.font.Font, 
                     back_color:str='black', 
                     right:bool=False, 
                     center:bool=False, 
                     alpha:int=-1) -> None:
    blit_text(display_surf,text, back_color, [pos[0] + 2, pos[1] + 2], font, right, center, alpha)
    blit_text(display_surf,text, color, pos, font, right, center, alpha)

def draw_health_bar(display_surf:pygame.display, 
                    atual_health:float, 
                    max_health:float, 
                    color:str, 
                    pos:tuple[int, int], 
                    size:tuple[int, int]) -> None:
    pygame.draw.rect(display_surf, 'black', (pos[0], pos[1], size[0], size[1]), 3)
    x_size = round(atual_health/max_health * (size[0] - 6), 1)
    pygame.draw.rect(display_surf, color, (pos[0] + 3, pos[1] + 3, x_size, size[1] - 6))

def draw_icon(display_surf:pygame.display, 
              icon:pygame.image, 
              pos:tuple[int, int], 
              size:int, 
              color:str='black') -> None:
    pygame.draw.rect(display_surf, color, (pos[0], pos[1], size + 6, size + 6), 2)
    icon_rect = icon.get_rect(topleft= ([pos[0] + 3, pos[1] + 3]))
    display_surf.blit(icon, icon_rect)

def import_frames(path:str) -> list:
    frames = []
    path = path
    for _, __, info in walk(path):
        for name in info:
            full_path = path + '/' + name
            image_surf = pygame.image.load(full_path).convert_alpha()
            frames.append(image_surf)
    return frames