""" 
--⪢ Main file responsible for handling user input and display current GameState.
"""


import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"                   # Hide pygame support information 

import glob
import ChessEngine
import numpy as np
import pygame as pg




# Information regarding the game window
WIDTH = HEIGHT = 512                
DIMENSION = 8                       # a chess board is 8 X 8 cells
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15                        # for animation
IMAGES = {}

base_path = os.path.dirname(os.path.abspath(__file__))

# Load all the images of each individual chess piece to be displayed

for file in glob.glob(os.path.join(base_path, os.path.join("images", "*"))):            # find all the file in the images directory regardless of extension
    piece_name = os.path.split(file)[1].split('.')[0]                                   # find the piece name for the particular image
    IMAGES[piece_name] = pg.image.load(file)






def draw_board(screen):
    """ Draw the squares on the board """

    colors  = [ pg.Color("white"), pg.Color("grey") ]                                               # colors of the board
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c)%2)]                                                             # find the color based on even or odd position
            pg.draw.rect(screen, color, pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE) )           # draw the rectangle shape in the row and column



def draw_pieces(screen, board):
    """ Draw the pieces on the board using the current game state """

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]                                                                     # get the piece from the board
            if piece != "--":                                                                       # if empty piece go to the next piece
                screen.blit( IMAGES[piece], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))        # draw piece in the row and column



def draw_GameState(screen, gs):
    """ Responsible for all the graphics within a game state """

    draw_board(screen)                  # draw squares on the board
                                        # add in piece highlighting and move suggestion (later)
    draw_pieces(screen, gs.board)       # draw pieces on top of the board






def main():
    """ Main function that handles user input and graphics """

    # PyGame initialization
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_icon(IMAGES['logo'])                # add icon to the pg window
    screen = pg.display.set_caption(' Chess')                   # add title to the pg window
    screen = pg.display.set_mode((WIDTH, HEIGHT))               # set size of the pg window
    screen.fill(pg.Color("black"))                              # add background color to the pg window


    # GameEngine initialization
    gs = ChessEngine.GameState()
    running = True
    sq_selected = ()             # store last click of the user
    player_click = []            # store clicks up to two clicks 
    
    valid_moves = gs.get_all_valid_moves()
    move_made = False


    # infinite loop
    while running:

        for e in pg.event.get():                        # for each event in event queue

            if e.type == pg.QUIT:                       # trigger for ending infinite loop
                running = False
            
            elif e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()           # (x, y) location fot the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE


                # storing player clicks
                if sq_selected == (row, col):            # in case the click is same as previous click, reset player clicks
                    sq_selected = ()
                    player_click.clear()

                else:                                   # else update the new click position
                    sq_selected = (row, col)
                    player_click.append(sq_selected)

                
                if len(player_click) == 2:              # when 2 unique clicks have been identified
                    move = ChessEngine.Move( player_click[0], player_click[1], gs.board )
                    
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            print(valid_moves[i].get_chess_notation())
                            gs.make_move(valid_moves[i])

                            player = 'White' if gs.white_to_move else 'Black'
                            # print(np.matrix(gs.board))
                            print(f"\n{player} turn to move: ", end="")

                            move_made = True

                            # reset input
                            sq_selected = ()
                            player_click.clear()
                            break
                        
                    else:
                        player_click = [sq_selected]


            elif e.type == pg.KEYDOWN and e.key == pg.K_z:    # trigger for undoing a move
                gs.undo_move()
                move_made = True


        if move_made:
            valid_moves = gs.get_all_valid_moves()
            move_made = False

        draw_GameState(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()




    

if __name__ == "__main__":
    print("White turn to move: ", end="")
    main()