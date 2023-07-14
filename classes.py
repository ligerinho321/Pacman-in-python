import pygame
from settings import*
from support import*
from pygame.math import Vector2
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from random import choice

class Entidade(pygame.sprite.Sprite):
    def __init__(self,group,tipo):
        super().__init__(group)

        self.tipo = tipo
    
    def collision(self):
        for parede in self.parede_sprites.sprites():
            if parede.rect.colliderect(self.rect):
                if parede.tipo == 'comum':
                    if self.direction.x > 0:
                        self.rect.right = parede.rect.left
                    if self.direction.x < 0:
                        self.rect.left = parede.rect.right
                    if self.direction.y > 0:
                        self.rect.bottom = parede.rect.top
                    if self.direction.y < -0:
                        self.rect.top = parede.rect.bottom
                    self.direction = Vector2(0,0)
        
        if self.rect.left < 0:
            self.rect.right = game_size[0]
        elif self.rect.right > game_size[0]:
            self.rect.left = 0
        elif self.rect.top < 0:
            self.rect.bottom = game_size[1]
        elif self.rect.bottom > game_size[1]:
            self.rect.top = 0
    
    def check_direction(self,rect):
        for parede in self.parede_sprites.sprites():
                if parede.rect.colliderect(rect):
                    return False
        return True


class Inimigo(Entidade):
    def __init__(self,pos,frames,recuando,matrix,caminhos,caminhos_especiais,parede_sprites,surface,pacman,reposicionar,group):

        super().__init__(group,'inimigo')

        self.surface = surface
        self.frames = frames
        self.frames_recuando = recuando
        self.state = 'right'
        self.frame_index = 0
        self.frame_speed = 0.10
        self.origin_pos = pos
        self.pacman = pacman

        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        self.grid = Grid(matrix = matrix)
        self.path = []
        self.rect_collision = []
        self.caminhos = caminhos
        self.caminhos_especiais = caminhos_especiais

        self.direction = Vector2(0,0)
        self.speed = entidade_speed
        self.parede_sprites = parede_sprites
        self.reposicionar = reposicionar

        self.vuneravel_time = None

        self.create_caminho()

        self.vuneravel = False
        self.perseguindo = False
        self.recuando = False
        self.procurar_caminho = False

        self.recuando_sound = pygame.mixer.Sound('sounds/retreating.wav')
    
    def create_caminho(self):
        while True:
            caminho = choice(self.caminhos)
            if caminho not in self.caminhos_especiais:
                self.create_pathfinding(caminho)
                break
    
    def animate(self):
        if not self.recuando:
            self.frame_index += self.frame_speed
            if self.frame_index > len(self.frames[self.state]):
                self.frame_index = 0
            
            self.image = self.frames[self.state][int(self.frame_index)]
        else:
            self.image = self.frames_recuando[self.state][0]
    
    def get_state(self):
        if not self.vuneravel:
            if self.direction.x > 0:
                self.state = 'right'
            elif self.direction.x < 0:
                self.state = 'left'
            elif self.direction.y > 0:
                self.state = 'down'
            elif self.direction.y < 0:
                self.state = 'top'
        
        if self.recuando:
            self.speed = entidade_speed_max
        elif self.vuneravel:
            self.speed = entidade_speed_min
        else:
            self.speed = entidade_speed

    def create_pathfinding(self,pos):

        mx,my = pos[0]//tile_size,pos[1]//tile_size

        x = self.rect.centerx // tile_size
        y = self.rect.centery // tile_size

        start = self.grid.node(x,y)
        end = self.grid.node(mx,my)

        finder = AStarFinder()
        self.path,_ = finder.find_path(start,end,self.grid)

        self.create_rect_collision()

        self.grid.cleanup()
    
    def draw_path(self):
        if self.path:
            points = []
            for point in self.path:
                x = (point[0] * tile_size) + tile_size//2
                y = (point[1] * tile_size) + tile_size//2
                points.append((x,y))
            pygame.draw.lines(self.surface,'green',False,points,1)

    def create_rect_collision(self):
        if self.path:
            self.rect_collision = []
            for point in self.path:
                x = (point[0] * tile_size) + tile_size//2
                y = (point[1] * tile_size) + tile_size//2
                rect = pygame.Rect(x-2,y-2,4,4)
                self.rect_collision.append(rect)

    def set_direction(self):
        if self.rect_collision:
            start = Vector2(self.rect.center)
            end = Vector2(self.rect_collision[0].center)
            distanci = (end - start).magnitude()

            if distanci < self.speed:
                del self.rect_collision[0]
                self.set_direction()
            else:
                direction = (end - start).normalize()
                if direction.x > 0.9:
                    self.direction = Vector2(1,0)
                elif direction.x < -0.9:
                    self.direction = Vector2(-1,0)
                elif direction.y > 0.9:
                    self.direction = Vector2(0,1)
                elif direction.y < -0.9:
                    self.direction = Vector2(0,-1)
        else:
            if self.recuando:
                self.recuando = False
                self.recuando_sound.stop()
            self.direction = Vector2(0,0)
            self.perseguindo = False
            self.procurar_caminho = True
            self.path = []
            pos = self.rect.centerx//tile_size,self.rect.centery//tile_size
            self.rect.topleft = Vector2(pos) * tile_size

    def check_collision(self):
        if self.rect.colliderect(self.pacman.rect) and not self.vuneravel and not self.recuando:
            self.pacman.morte()

        if self.rect_collision:
            for rect in self.rect_collision:
                if rect.collidepoint(self.rect.center):
                    del self.rect_collision[0]
                    self.set_direction()
    
    def move(self):
        
        if self.procurar_caminho and not self.recuando:
            end = Vector2(self.pacman.rect.center)
            start = Vector2(self.rect.center)
            distanci = (end - start).magnitude()

            if distanci < 160 and not self.vuneravel:
                self.create_pathfinding(self.pacman.rect.center)
            else:
                self.create_caminho()

            self.procurar_caminho = False
        
        self.rect.topleft += self.direction * self.speed
    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.vuneravel:
            if current_time - self.vuneravel_time > vuneravel_cooldown:
                self.vuneravel = False
    
    def recuar(self):
        self.recuando = True
        self.vuneravel = False
        self.create_pathfinding(self.origin_pos)
        self.recuando_sound.play(-1)

    def update(self):
        self.get_state()
        self.set_direction()
        self.move()
        self.check_collision()
        self.animate()
        self.cooldowns()
        #self.draw_path()

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,group,tipo,image=pygame.Surface((tile_size,tile_size))):
        super().__init__(group)

        self.tipo = tipo
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)

class AnimatedTile(pygame.sprite.Sprite):
    def __init__(self,pos,group,tipo,frames):
        super().__init__(group)

        self.tipo = tipo
        self.frame_index = 0
        self.frame_speed = 0.05
        self.frames = frames

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
    
    def animate(self):
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        
        self.image = self.frames[int(self.frame_index)]
    
    def update(self):
        self.animate()

class Pacman(Entidade):
    def __init__(self,pos,display_game,parede_sprites,reposicionar,group):

        super().__init__(group,'pacman')

        self.surface = display_game

        self.frames = {'horizontal': import_cut_graphic('graphics/pacman_horizontal.png',13),
                        'vertical': import_cut_graphic('graphics/pacman_vertical.png',13),
                        'death': import_cut_graphic('graphics/pacman_death.png',15)}
        
        self.state = 'horizontal'
        self.frame_index = 0
        self.frame_speed = 0.15

        self.image = self.frames[self.state][self.frame_index]

        self.rect = self.image.get_rect(topleft = pos)

        self.direction = Vector2(0,0)
        self.speed = entidade_speed

        self.parede_sprites = parede_sprites
        self.reposicionar = reposicionar

        self.facing = 'right'

        self.death_sound = pygame.mixer.Sound('sounds/pacman_death.wav')
    
    def input(self):
        key = pygame.key.get_pressed()

        new_direction = None
        if self.state != 'death':
            if key[pygame.K_d]:
                new_direction = Vector2(1,0)
                new_facing = 'right'
                new_state = 'horizontal'
            elif key[pygame.K_a]:
                new_direction = Vector2(-1,0)
                new_facing = 'left'
                new_state = 'horizontal'
            elif key[pygame.K_s]:
                new_direction = Vector2(0,1)
                new_facing = 'down'
                new_state = 'vertical'
            elif key[pygame.K_w]:
                new_direction = Vector2(0,-1)
                new_facing = 'top'
                new_state = 'vertical'

        if new_direction != None:
            next_pos = self.rect.topleft + new_direction * tile_size
            rect = pygame.Rect(next_pos.x,next_pos.y,tile_size,tile_size)

            if self.check_direction(rect):
                self.direction = new_direction
                self.facing = new_facing
                self.state = new_state

    def animate(self):
        self.frame_index += self.frame_speed

        if self.frame_index > len(self.frames[self.state]):
            self.frame_index = 0
        
        imagem = self.frames[self.state][int(self.frame_index)]

        if self.facing == 'left':
            imagem = pygame.transform.flip(imagem,True,False)
        elif self.facing == 'down':
            imagem = pygame.transform.flip(imagem,False,True)
        
        self.image = imagem
    
    def morte(self):
        self.frame_speed = 0.10
        self.frame_index = 0
        self.state = 'death'
        self.direction = Vector2(0,0)
        pygame.mixer.stop()
        self.death_sound.play()

    def update(self):
        if self.state == 'death':
            if self.death_sound.get_num_channels() == 0:
                self.reposicionar()
                
        self.input()

        self.rect.topleft += self.direction * self.speed

        self.collision()
        self.animate()