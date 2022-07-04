import pygame
from sudoku import Sudoku

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Sudoku by PB20111689")
    screen = pygame.display.set_mode((480, 640))
    clock = pygame.time.Clock()
    sudoku = Sudoku(screen)
    while True:
        sudoku.play()
        sudoku.draw_background(screen)
        sudoku.draw_choose(screen)
        sudoku.output(screen)
        if sudoku.win():
            break
        sudoku.music.draw_buttons()

        current_time = sudoku.music.get_music_time()
        sudoku.music.draw_song_name()
        sudoku.music.draw_music_progress(current_time)
        sudoku.music.draw_volume_progress(sudoku.music.volume)
        sudoku.music.new_song(current_time)
        pygame.display.flip()
