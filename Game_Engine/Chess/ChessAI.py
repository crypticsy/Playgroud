""" 
--⪢ Main file responsible for handling user input and display current GameState.
"""

import random



piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

knight_scores = [[0.0,  0.1,    0.2,    0.2,    0.2,    0.2,    0.1,    0.0],
                 [0.1,  0.3,    0.5,    0.5,    0.5,    0.5,    0.3,    0.1],
                 [0.2,  0.5,    0.6,    0.65,   0.65,   0.6,    0.5,    0.2],
                 [0.2,  0.55,   0.65,   0.7,    0.7,    0.65,   0.55,   0.2],
                 [0.2,  0.5,    0.65,   0.7,    0.7,    0.65,   0.5,    0.2],
                 [0.2,  0.55,   0.6,    0.65,   0.65,   0.6,    0.55,   0.2],
                 [0.1,  0.3,    0.5,    0.55,   0.55,   0.5,    0.3,    0.1],
                 [0.0,  0.1,    0.2,    0.2,    0.2,    0.2,    0.1,    0.0]]

bishop_scores = [[0.0,  0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.0],
                 [0.2,  0.4,    0.4,    0.4,    0.4,    0.4,    0.4,    0.2],
                 [0.2,  0.4,    0.5,    0.6,    0.6,    0.5,    0.4,    0.2],
                 [0.2,  0.5,    0.5,    0.6,    0.6,    0.5,    0.5,    0.2],
                 [0.2,  0.4,    0.6,    0.6,    0.6,    0.6,    0.4,    0.2],
                 [0.2,  0.6,    0.6,    0.6,    0.6,    0.6,    0.6,    0.2],
                 [0.2,  0.5,    0.4,    0.4,    0.4,    0.4,    0.5,    0.2],
                 [0.0,  0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.0]]

rook_scores = [[0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.25],
               [0.5,    0.75,   0.75,   0.75,   0.75,   0.75,   0.75,   0.5],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,  0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.0,    0.25,   0.25,   0.25,   0.25,   0.25,   0.25,   0.0],
               [0.25,   0.25,   0.25,   0.5,    0.5,    0.25,   0.25,   0.25]]

queen_scores = [[0.0,   0.2,    0.2,    0.3,    0.3,    0.2,    0.2,    0.0],
                [0.2,   0.4,    0.4,    0.4,    0.4,    0.4,    0.4,    0.2],
                [0.2,   0.4,    0.5,    0.5,    0.5,    0.5,    0.4,    0.2],
                [0.3,   0.4,    0.5,    0.5,    0.5,    0.5,    0.4,    0.3],
                [0.4,   0.4,    0.5,    0.5,    0.5,    0.5,    0.4,    0.3],
                [0.2,   0.5,    0.5,    0.5,    0.5,    0.5,    0.4,    0.2],
                [0.2,   0.4,    0.5,    0.4,    0.4,    0.4,    0.4,    0.2],
                [0.0,   0.2,    0.2,    0.3,    0.3,    0.2,    0.2,    0.0]]

pawn_scores = [[0.8,    0.8,    0.8,    0.8,    0.8,    0.8,    0.8,    0.8],
               [0.7,    0.7,    0.7,    0.7,    0.7,    0.7,    0.7,    0.7],
               [0.3,    0.3,    0.4,    0.5,    0.5,    0.4,    0.3,    0.3],
               [0.25,   0.25,   0.3,    0.45,   0.45,   0.3,    0.25,   0.25],
               [0.2,    0.2,    0.2,    0.4,    0.4,    0.2,    0.2,    0.2],
               [0.25,   0.15,   0.1,    0.2,    0.2,    0.1,    0.15,   0.25],
               [0.25,   0.3,    0.3,    0.0,    0.0,    0.3,    0.3,    0.25],
               [0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2,    0.2]]

piece_position_scores = {"wN": knight_scores, "bN": knight_scores[::-1],
                         "wB": bishop_scores, "bB": bishop_scores[::-1],
                         "wQ": queen_scores,  "bQ": queen_scores[::-1],
                         "wR": rook_scores,   "bR": rook_scores[::-1],
                         "wP": pawn_scores,   "bP": pawn_scores[::-1]}





def find_random_move(valid_moves):
    """ Picks and returns a random valid move. """
    return random.choice(valid_moves)






def score_board(game_state):
    """ Score the board. A positive score is good for white, a negative score is good for black. """

    score = 0

    for row, pieces in enumerate(game_state.board):                            
        for col, piece in enumerate(pieces):  
            if piece == "--": continue
            piece_position_score = 0 if piece[1] == "K" else piece_position_scores[piece][row][col]

            if piece[0] == "w":
                score += piece_score[piece[1]] + piece_position_score
            elif piece[0] == "b":
                score -= piece_score[piece[1]] + piece_position_score

    return score






def find_best_move_greedy(game_state, valid_moves):
    """ The best move based on greedy algorithm alone """
    
    turn_multiplier = 1 if game_state.white_to_move else -1
    max_score = -CHECKMATE
    best_move = None

    for player_move in valid_moves:
        game_state.make_move(player_move)
        
        if game_state.check_mate:
            score = CHECKMATE
        elif game_state.stale_mate:
            score = 0
        else:
            score = turn_multiplier * score_board(game_state)
        
        if score > max_score:
            max_score = score
            best_move = player_move

        game_state.undo_move()
    
    return best_move
    





