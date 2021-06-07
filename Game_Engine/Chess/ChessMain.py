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
BOARD_WIDTH = BOARD_HEIGHT = 512      
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8                       # a chess board is 8 X 8 cells
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15                        # for animation
IMAGES = {}

base_path = os.path.dirname(os.path.abspath(__file__))

# Load all the images of each individual chess piece to be displayed

for file in glob.glob(os.path.join(base_path, os.path.join("images", "*"))):            # find all the file in the images directory regardless of extension
    piece_name = os.path.split(file)[1].split('.')[0]                                   # find the piece name for the particular image
    IMAGES[piece_name] = pg.image.load(file)






def draw_board(screen):
    """ Draw the squares on the board """

    global colors
    colors  = [ pg.Color("white"), pg.Color("grey") ]                                               # colors of the board
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c)%2)]                                                             # find the color based on even or odd position
            pg.draw.rect(screen, color, pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE) )           # draw the rectangle shape in the row and column


def highlight_squares(screen, game_state, valid_moves, square_selected):
    """ Highlight square selected and moves for the particular piece. """

    if len(game_state.move_log) > 0:
        last_move = game_state.move_log[-1]
        s = pg.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pg.Color('green'))
        screen.blit(s, (last_move.end_col * SQ_SIZE, last_move.end_row * SQ_SIZE))

    if square_selected != ():
        row, col = square_selected

        if game_state.board[row][col][0] == ('w' if game_state.white_to_move else 'b'):             # square_selected is a piece that can be moved
            
            # highlight selected square
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(220)                                                                        # transparency value 0 -> transparent, 255 -> opaque
            s.fill(pg.Color('#1768ac'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

            s.set_alpha(90)  
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    hightlight_color = '#0098f1' if move.piece_captured == "--" else '#ff0000'
                    s.fill(pg.Color(hightlight_color))                                              # highlight moves from that square
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))



def draw_pieces(screen, board):
    """ Draw the pieces on the board using the current game state """

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]                                                                     # get the piece from the board
            if piece != "--":                                                                       # if empty piece go to the next piece
                screen.blit( IMAGES[piece], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))        # draw piece in the row and column



def draw_move_log(screen, game_state, font):
    """ Draw the move log at the right side of the screen """

    move_log_rect = pg.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pg.draw.rect(screen, pg.Color('black'), move_log_rect)

    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):                                                                   # make sure black made a move
            move_string += str(move_log[i + 1]) + "   "
        move_texts.append(move_string)

    # Styling values
    moves_per_row = 3
    padding = 10
    line_spacing = 5
    text_y = padding

    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, pg.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing



def draw_GameState(screen, game_state, valid_moves, square_selected, move_log_font):
    """ Responsible for all the graphics within a game state """

    draw_board(screen)                                                              # draw squares on the board
    highlight_squares(screen, game_state, valid_moves, square_selected )            # add in piece highlighting and move suggestion (later)
    draw_pieces(screen, game_state.board)                                           # draw pieces on top of the board
    draw_move_log(screen, game_state, move_log_font)                                # draw the move log






def animate_move(move, screen, board, clock):
    """ Animating a move """

    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col

    frames_per_square = 10                                                          # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square

    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        
        draw_board(screen)
        draw_pieces(screen, board)
        
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pg.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pg.draw.rect(screen, color, end_square)
        
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = pg.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)

        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        
        clock.tick(180)



def draw_end_game_text(screen, text):
    """ Draw the end text. """

    font = pg.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, pg.Color("gray"))

    # Center the font by using font BOARD_WIDTH and BOARD_HEIGHT 
    text_location = pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_BOARD_WIDTH() / 2, BOARD_HEIGHT / 2 - text_object.get_BOARD_HEIGHT() / 2)

    screen.blit(text_object, text_location)
    text_object = font.render(text, False, pg.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))












def main():
    """ Main function that handles user input and graphics """

    # PyGame initialization
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_icon(IMAGES['logo'])                # add icon to the pg window
    screen = pg.display.set_caption(' Chess')                   # add title to the pg window
    screen = pg.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))               # set size of the pg window
    screen.fill(pg.Color("black"))                              # add background color to the pg window

    move_log_font = pg.font.SysFont("Arial", 13, True, False)


    # GameEngine initialization
    game_state = ChessEngine.GameState()
    running = True
    sq_selected = ()             # store last click of the user
    player_click = []            # store clicks up to two clicks 
    
    valid_moves = game_state.get_all_valid_moves()
    move_made = False           # flag variable for when a move is made
    animate = False             # flag variable for when a move needs to be animated
    game_over = False           # flag variable for when game is over



    # infinite loop
    while running:

        for e in pg.event.get():                            # for each event in event queue

            if e.type == pg.QUIT:                           # trigger for ending infinite loop
                running = False
            
            elif not game_over and e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()               # (x, y) location fot the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE


                # storing player clicks
                if sq_selected == (row, col) or col >= 8:   # in case the click is same as previous click, reset player clicks
                    sq_selected = ()
                    player_click.clear()

                else:                                       # else update the new click position
                    sq_selected = (row, col)
                    player_click.append(sq_selected)

                
                if len(player_click) == 2:              # when 2 unique clicks have been identified
                    move = ChessEngine.Move( player_click[0], player_click[1], game_state.board )
                    
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            game_state.make_move(valid_moves[i])

                            move_made = True
                            animate = True

                            # reset input
                            sq_selected = ()
                            player_click.clear()
                            break
                        
                    else:
                        player_click = [sq_selected]


            elif e.type == pg.KEYDOWN and e.key == pg.K_z:      # trigger for undoing a move
                game_state.undo_move()
                move_made = True
                animate = False
            
            elif e.type == pg.KEYDOWN and e.key == pg.K_z:      # trigger for resetting the board
                game_state = ChessEngine.GameState()
                valid_moves = game_state.get_all_valid_moves()
                sq_selected = ()
                player_click.clear()
                move_made = False
                animate = False


        if move_made:
            if animate : animate_move(game_state.move_log[-1], screen, game_state.board, clock )             # animate the move made by the user
            valid_moves = game_state.get_all_valid_moves()
            move_made = False
            animate = False
            
        if not game_over:
            draw_GameState(screen, game_state, valid_moves, sq_selected, move_log_font)
        
        if game_state.check_mate or game_state.stale_mate: 
            game_over = True
            win_txt = 'Stalemate' if game_state.stale_mate else 'Black win by checkmate.' if game_state.white_to_move else 'White  win by checkmate.'
            draw_end_game_text(screen, win_txt)


        clock.tick(MAX_FPS)
        pg.display.flip()




    

if __name__ == "__main__":
    main()