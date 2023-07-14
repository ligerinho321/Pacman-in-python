import pygame
from settings import *
from support import*
from classes import*
from pygame.math import Vector2
from time import sleep


class Game:
    def __init__(self,ui,layout):

        self.display_game = pygame.Surface(game_size)

        self.ui = ui

        self.parede_layout = import_csv_folder(layout['paredes'])
        self.parede_sprites = self.render_layout(self.parede_layout,'parede')

        self.pacman_layout = import_csv_folder(layout['pacman'])
        self.pacman_sprite = self.render_layout(self.pacman_layout,'pacman')
        self.player = self.pacman_sprite.sprite

        self.inimigo_layout = import_csv_folder(layout['inimigos'])
        self.inimigo_sprites = self.render_layout(self.inimigo_layout,'inimigo')

        self.ponto_layout = import_csv_folder(layout['pontos'])
        self.ponto_sprites = self.render_layout(self.ponto_layout,'ponto')

        self.score = 0
        self.life = 2

        self.ready = True
        self.ready_time = pygame.time.get_ticks()
        self.power_pellet = False
        self.power_pellet_time = None
        self.eat_ghost_time = 0
        self.eat_ghost = False
        self.eat_ghost_pos = None

        self.ready_sound = pygame.mixer.Sound('sounds/pacman_beginning.wav')
        self.power_pellet_sound = pygame.mixer.Sound('sounds/power_pellet.wav')
        self.pacman_chomp_sound = pygame.mixer.Sound('sounds/munch_1.wav')
        self.eat_ghost_sound = pygame.mixer.Sound('sounds/eat_ghost.wav')
        self.siren = pygame.mixer.Sound('sounds/siren_1.wav')

        self.pacman_chomp_sound.set_volume(0.3)
        self.ready_sound.set_volume(0.6)
        self.siren.set_volume(0.6)
        self.power_pellet_sound.set_volume(0.6)

        self.ready_sound.play()

    def render_layout(self,layout,type):
        sprites = pygame.sprite.Group()

        for index_l, linha in enumerate(layout):
            for index_c, coluna in enumerate(linha):
                if coluna != '-1':
                    x = index_c * tile_size
                    y = index_l * tile_size

                    if type == 'parede':
                        if coluna == '44':
                            tipo = 'especial'
                        else:
                            tipo = 'comum'

                        image = import_cut_graphic('graphics/paredes.png',8)
                        Tile((x,y),sprites,tipo,image[int(coluna)])
                    
                    if type == 'ponto':
                        image = import_cut_graphic('graphics/pontos.png',8)
                        if coluna == '2':
                            tipo = 'ponto_grande'
                            AnimatedTile((x,y),sprites,tipo,image)
                        else:
                            tipo = 'ponto_pequeno'
                            Tile((x,y),sprites,tipo,image[int(coluna)])
                    
                    if type == 'inimigo':
                        frames = import_folder(f'graphics/fantasma/fantasma_{coluna}')
                        recuando = import_folder('graphics/fantasma/recuando')
                        grid = import_matrix(self.parede_layout)
                        Inimigo((x,y),
                                frames,recuando,
                                grid[0],grid[1],grid[2],
                                self.parede_sprites,
                                self.display_game,
                                self.player,
                                self.reposicionar,
                                sprites)
                    
                    if type == 'porta':
                        Tile((x,y),sprites,type)
                    
                    if type == 'pacman':
                        sprite =  pygame.sprite.GroupSingle()
                        Pacman((x,y),self.display_game,self.parede_sprites,self.reposicionar,sprite)

                        return sprite
        return sprites

    def update_score(self):
        if self.ponto_sprites:
            for ponto in self.ponto_sprites.sprites():
                if ponto.rect.collidepoint(self.player.rect.center):
                    if ponto.tipo == 'ponto_pequeno':
                        self.score += 10
                    elif ponto.tipo == 'ponto_grande':
                        self.score += 100
                        self.set_vuneravel()
                    if self.pacman_chomp_sound.get_num_channels() == 0:
                        self.pacman_chomp_sound.play()
                    ponto.kill()
    
    def set_vuneravel(self):
        time = pygame.time.get_ticks()
        for inimigo in self.inimigo_sprites.sprites():
            if not inimigo.recuando:
                inimigo.vuneravel = True
                inimigo.state = 'vuneravel'
                inimigo.vuneravel_time = time
        self.siren.stop()
        self.power_pellet_sound.stop()
        self.power_pellet_sound.play(-1)
        self.power_pellet = True
        self.power_pellet_time = time
        
    def check_collision(self):
        for inimigo in self.inimigo_sprites.sprites():
            if inimigo.rect.colliderect(self.player.rect):
                if inimigo.vuneravel and not inimigo.recuando:
                    self.score += 200
                    self.eat_ghost_time = pygame.time.get_ticks()
                    self.eat_ghost = True
                    self.eat_ghost_pos = inimigo.rect.center
                    self.eat_ghost_sound.play()
                    inimigo.recuar()
    
    def reposicionar(self):
        self.life -= 1
        if self.life == 0:
             self.ponto_sprites = self.render_layout(self.ponto_layout,'ponto')

             self.score = 0
             self.life = 2
             self.power_pellet = False
             self.power_pellet_time = None
             self.eat_ghost_time = 0
             self.eat_ghost = False
             self.eat_ghost_pos = None

        self.pacman_sprite = self.render_layout(self.pacman_layout,'pacman')
        self.player = self.pacman_sprite.sprite

        self.inimigo_sprites = self.render_layout(self.inimigo_layout,'inimigo')

        self.ready = True
        self.ready_time = pygame.time.get_ticks()
        self.ready_sound.play()
    
    def cooldowns(self):
        current = pygame.time.get_ticks()

        if self.ready:
            if current - self.ready_time >= ready_cooldown:
                self.ready = False
                if self.siren.get_num_channels() == 0:
                    self.siren.play(-1)
        if self.power_pellet:
            if current - self.power_pellet_time >= vuneravel_cooldown:
                self.power_pellet = False
                self.power_pellet_sound.stop()
                if self.siren.get_num_channels() == 0:
                    self.siren.play(-1)
        if self.eat_ghost:
            if current - self.eat_ghost_time >= eat_ghost_cooldown:
                self.eat_ghost = False

    def update(self):
        self.display_game.fill('black')

        self.cooldowns()

        self.ui.update(self.score,self.life)

        self.ponto_sprites.update()
        self.ponto_sprites.draw(self.display_game)

        self.parede_sprites.draw(self.display_game)

        if self.eat_ghost:
            self.ui.draw_eat_ponto(self.eat_ghost_pos)

        if not self.ready:
            self.update_score()
            self.check_collision()

            if self.player.state != 'death':
                self.inimigo_sprites.update()
                self.inimigo_sprites.draw(self.display_game)

            self.pacman_sprite.update()
        else:
            self.ui.draw_ready()

        self.pacman_sprite.draw(self.display_game)

