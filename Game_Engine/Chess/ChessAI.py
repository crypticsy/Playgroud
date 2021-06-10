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



def score_board(game_state):
    """ Score the board. A positive score is good for white, a negative score is good for black. """
    
    if game_state.check_mate:
        return -CHECKMATE if game_state.white_to_move else CHECKMATE                  # win condition reached

    elif game_state.stale_mate:
        return STALEMATE

    score = 0

    for row, pieces in enumerate(game_state.board):                            
        for col, piece in enumerate(pieces):  
            if piece == "--": continue
            piece_position_score = 0 if piece[1] == "K" else piece_position_scores[piece][row][col]             # add heuristic based on piece position

            if piece[0] == "w":
                score += piece_score[piece[1]] + piece_position_score
            elif piece[0] == "b":
                score -= piece_score[piece[1]] + piece_position_score

    return score









def find_random_move(valid_moves):
    """ Picks and returns a random valid move. """
    return random.choice(valid_moves)



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
 


def find_move_min_max(game_state, valid_moves, depth, white_to_move):
    """ The best move based on min max algorithm alone """
    
    global next_move
    
    if depth == 0: return score_board(game_state)                   # base case to stop infinite recursion

    if white_to_move:

        max_score = -CHECKMATE
        for move in valid_moves:

            game_state.make_move(move)
            next_moves = game_state.get_all_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth-1, False)

            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move

            game_state.undo_move()

        return max_score

    else:

        min_score = CHECKMATE
        for move in valid_moves:

            game_state.make_move(move)
            next_moves = game_state.get_all_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth-1, True)

            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move

            game_state.undo_move()
    
        return min_score
 


def find_move_nega_max(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """ The best move based on nega max algorithm """
    
    global next_move
    
    if depth == 0: return turn_multiplier * score_board(game_state)                   # base case to stop infinite recursion

    max_score = -CHECKMATE
    for move in valid_moves:
        
        game_state.make_move(move)
        next_moves = game_state.get_all_valid_moves()
        score = -find_move_nega_max(game_state, next_moves, depth-1,  -beta, -alpha, -turn_multiplier)

        if score > max_score:
            max_score = score
            if depth == DEPTH: next_move = move

        game_state.undo_move()
        
        if max_score > alpha: alpha = max_score         # pruning happens
        if alpha >= beta: break

    return max_score



def find_best_move(game_state, valid_moves, return_queue):
    """  Helper method to make the first recursive call based on the min max algorithm """
    
    global next_move
    next_move = None
    random.shuffle(valid_moves)

    # find_move_min_max(game_state, valid_moves, DEPTH, game_state.white_to_move)                                                   # only min max implementation
    find_move_nega_max(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.white_to_move else -1)               # nega max with alpha beta pruning

    # return_queue.put(next_move)
    return next_move
