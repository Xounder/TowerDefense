import pygame, sys
from settings import screen_width, screen_height
from level import Level

class Game:
    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, -16, 16, 2096)
        pygame.init()
        pygame.mixer.set_num_channels(16)
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Tower The Fancy')
        self.clock = pygame.time.Clock()
        self.level = Level(self.screen)
    
    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.level.draw() 
            self.level.update()

            pygame.display.update()
            self.clock.tick(60)

game = Game()
game.run()