import pygame
from settings import*

class Ui:
    def __init__(self):
        self.display = pygame.display.get_surface()

        self.border = pygame.Rect(0,0,screen_size[0],screen_size[1])

        self.font = pygame.font.Font('graphics/joystix.ttf',20)
        self.font_lower = pygame.font.Font('graphics/joystix.ttf',2)

        self.score_title = self.font.render('Pontos ',False,'white')
        self.score_title_rect = self.score_title.get_rect(topleft = (10,10))

        self.live_title = self.font.render('Vidas',False,'white')
        self.live_title_rect = self.live_title.get_rect(topleft = (230,10))

        self.ready_title = self.font.render('Ready!',False,'white')
        self.ready_title_rect = self.ready_title.get_rect(center = (game_size[0]//2,game_size[1]//2))

        self.eat_ponto = self.font.render('200',False,'white')

        image = pygame.image.load('graphics/live.png').convert_alpha()
        self.live_image = pygame.transform.scale(image,(20,20))
    
    def score(self,score):

        score = self.font.render(str(score),False,'white')
        score_rect = score.get_rect(topleft = self.score_title_rect.topright)

        self.display.blit(self.score_title,self.score_title_rect)
        self.display.blit(score,score_rect)
    
    def live(self,lives):
        self.display.blit(self.live_title,self.live_title_rect)

        for live in range(lives):
            self.display.blit(self.live_image,(10+self.live_title_rect.right + (live*tile_size),12))
    
    def update(self,score,lives):
        self.scores = score
        self.lives = lives
    
    def draw_ready(self):
        self.display.blit(self.ready_title,self.ready_title_rect)
    
    def draw_eat_ponto(self,pos):
        self.eat_ponto_rect = self.eat_ponto.get_rect(center = pos)
        self.display.blit(self.eat_ponto,self.eat_ponto_rect)
        
    def draw(self):
        #pygame.draw.rect(self.display,'white',self.border,3)
        #pygame.draw.line(self.display,'white',(0,50),(screen_size[0],50),3)

        self.score(self.scores)
        self.live(self.lives)