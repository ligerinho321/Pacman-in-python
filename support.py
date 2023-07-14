from csv import reader
import pygame
from settings import*
import os

def import_csv_folder(path):
    lista = []

    with open(path) as map:
        layout = reader(map,delimiter=',')

        for linha in layout:
            lista.append(linha)
            
        return lista

def import_matrix(layout):
    matrix = []
    caminhos = []
    caminhos_especiais = []

    for index_l,linha in enumerate(layout):
        matrix_linha = []
        for index_c,coluna in enumerate(linha):
            x = index_c * tile_size
            y = index_l * tile_size
            if coluna == '44':
                caminhos_especiais.append((x,y))

            if coluna == '-1' or coluna == '44':
                matrix_linha.append(1)
                caminhos.append((x,y))
            else:
                matrix_linha.append(0)
        matrix.append(matrix_linha)
        
    return (matrix,caminhos,caminhos_especiais)


def import_cut_graphic(path,size):
    lista = []
    image = pygame.image.load(path).convert_alpha()

    image_width = image.get_size()[0] // size
    image_height = image.get_size()[1] // size

    for linha in range(image_height):
        for coluna in range(image_width):

            x = coluna * size
            y = linha * size

            new_surface = pygame.Surface((size,size),flags=pygame.SRCALPHA)
            new_surface.blit(image,(0,0),(x,y,size,size))
            lista.append(pygame.transform.scale(new_surface,(tile_size,tile_size)))
    
    return lista

def import_folder(path):
    lista = {}
    for image in os.listdir(path):
        full_path = path + '/' + image
        frame = import_cut_graphic(full_path,14)
        lista[image.split('_')[-1].split('.')[0]] = frame
    
    return lista