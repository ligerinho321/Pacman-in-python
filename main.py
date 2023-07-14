import pygame
from settings import*
from game import*
from Ui import Ui

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption('Pacman')

        self.clock = pygame.time.Clock()

        self.ui = Ui()
        self.game = Game(self.ui,fase_2)
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    
            self.screen.fill('black')
            self.screen.blit(self.game.display_game,(0,0))
            self.game.update()
            self.ui.draw()
            pygame.display.update()
            self.clock.tick(fps)

if __name__ == '__main__':
    main = Main()
    main.run()