#Configuraçôes

fase_1 = {
    'inimigos': 'layout/fase_1/fase_1_inimigos.csv',
    'pacman': 'layout/fase_1/fase_1_pacman.csv',
    'paredes': 'layout/fase_1/fase_1_paredes.csv',
    'pontos': 'layout/fase_1/fase_1_pontos.csv'
}

fase_2 = {
    'inimigos': 'layout/fase_2/fase_2_inimigos.csv',
    'pacman': 'layout/fase_2/fase_2_pacman.csv',
    'paredes': 'layout/fase_2/fase_2_paredes.csv',
    'pontos': 'layout/fase_2/fase_2_pontos.csv'
}

fase_1_width = 28
fase_1_height = 31

fase_2_width = 37
fase_2_height = 21

tile_size = 30

game_size = (fase_2_width*tile_size,fase_2_height*tile_size)

screen_size = (game_size[0],game_size[1])

fps = 60

ready_cooldown = 4200
vuneravel_cooldown = 8000
eat_ghost_cooldown = 500

entidade_speed = 2
entidade_speed_min = 1
entidade_speed_max = 10