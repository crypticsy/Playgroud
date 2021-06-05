""" 
--⪢ Engine file responsible for storing all the information about the current state of chess game. 
    Also responsible for validating moves.  
"""

class GameState():
    
    def __init__(self):
        # 2D list containing the pieces of the board, where each element has 2 characters.
        # The first character is the color ('b' or 'w') and the second character is the type of the piece ('K', 'Q', ...).
        # '--' represents an empty space with no piece.

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wK", "wQ", "wB", "wN", "wR"] 
        ]

        self.move_functions = { 'P' : self.get_pawn_moves, 
                                'R' : self.get_rook_moves, 
                                'N' : self.get_night_moves, 
                                'B' : self.get_bishop_moves,
                                'Q' : self.get_queen_moves,
                                'K' : self.get_king_moves}

        self.white_to_move = True
        self.move_log = []

        self.white_king = (7, 3)            # start position of white king
        self.black_king = (0, 4)            # start position of black king
        
        self.in_check = False
        self.check_mate = False
        self.stale_mate = False
        
        self.pins = []
        self.checks = []






    def make_move(self, move):
        """ Takes a move parameter and executes it """

        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move         # swap player

        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)



    def undo_move(self):
        """ Undo last move """

        if self.move_log:                                   # ensure a previous move exists
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move     # switch turns back

            # Handle undo king move
            if move.piece_moved == "wK":
                self.white_king = (move.start_row, move.start_col)

            elif move.piece_moved == "bK":
                self.black_king = (move.start_row, move.start_col)






    def get_all_valid_moves(self):
        """ All moves considering checks """

        moves = []
        self.in_check, self.pins,  self.checks =self.check_for_pins_and_check()
        kingRow, kingCol = self.white_king if self.white_to_move else self.black_king

        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()

                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = set()               # squares that pieces can move to

                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    valid_squares = set((check_row, check_col))
                
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3]*i)            # check[2] and check[3] are the check directions
                        valid_squares.add(validSquare)
                        if validSquare[0] == check_row and validSquare[1] == check_col:
                            break
                
                # get rid of moves that don't block check or move king
                for i in range(len(moves)-1,-1,-1):                 # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != 'K':              # move doesn't move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:          # move doesn't block or capture piece
                            moves.remove(moves[i])
            
            else:           # not in check - all moves are fine
                self.get_king_moves(kingRow, kingCol, moves)
        
        else:
            moves = self.get_all_possible_moves()
        
        return moves






    def get_all_possible_moves(self):
        """ All moves without considering checks """

        moves = []
        for r in range(8):
            for c in range(8):
                turn  = self.board[r][c][0]

                if (turn == 'w' and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
                    
        return moves







    def check_for_pins_and_check(self):
        """ All possible pins and check """

        pins, checks, in_check = [], [], False
        enemy_color, ally_color = ("b","w") if self.white_to_move else ("w","b")
        start_row, start_col = self.white_king if self.white_to_move else self.black_king

        # check outwards from king for pins and checks, keep track of pins
        for j, dir in enumerate([(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]):            # for all possible directions
            possible_pin = ()    # reset possible pins

            for i in range(1, 8):
                end_row, end_col = start_row + dir[0] * i, start_col + dir[1] * i 

                if 0 <= end_row < 8 and 0 <= end_col < 8:               # ensure valid move
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":          # if the piece is ally and not phantom king
                        if possible_pin == ():                          # first allied piece could be pinned
                            possible_pin = (end_row, end_col, dir[0], dir[1])
                        else:                                           # second allied piece - no check or pin from this direction
                            break
                    
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        
                        # Five possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if  (0 <= j <=3 and piece_type=='R') or \
                            (4 <= j <=7  and piece_type=='B') or \
                            (i == 1 and piece_type=='P' and ((enemy_color=='w' and 6 <= j <= 7) or (enemy_color=='b' and 4 <= j <= 5))) or \
                            (piece_type == 'Q') or\
                            (i ==1 and piece_type =='K'):
                            
                            if possible_pin == ():      # when no piece is blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, dir[0], dir[1]))
                                break

                            else:                       # when piece is blocking, so it's a pin
                                pins.append(possible_pin)
                                break
                        else:                           # when no piece is blocking, so check
                            break
                else:
                    break
        
        # check for knight checks
        for dir in  [(-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2)]:           # for all possible knight moves
            end_row, end_col = start_row + dir[0], start_col + dir[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:                       # ensure the move is valid
                end_piece = self.board[end_row][end_col]

                if end_piece[0] == enemy_color and end_piece[1] == "N":     # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, dir[0], dir[1]))
            
        return in_check, pins, checks





        
    def get_pawn_moves(self, r, c, moves):
        """ All moves for pawn pieces """

        pieces_pinned = False
        pin_direction = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pieces_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break 

        enemy_color = "b" if self.white_to_move else "w"
        dir, start = (-1,6) if self.white_to_move else (1,1) 

        # Check if the piece is not pinned and can move 1 square ahead
        if (not pieces_pinned or pin_direction == (dir,0)) and  0 <= r+dir < 8 and self.board[r+dir][c] == "--":
            moves.append(Move((r,c), (r+dir,c), self.board))

            # Check if the piece is at start and can move 2 square ahead
            if r==start and self.board[r+dir*2][c] == "--":
                moves.append(Move((r,c), (r+dir*2,c), self.board))

        for i in [-1, 1]:           # Check if the pawn can capture an enemy piece
            if 0 <= r+dir < 8 and 0 <= c+i < 8:
                if (not pieces_pinned or pin_direction == (dir,i)) and self.board[r+dir][c+i][0] == enemy_color:
                    moves.append(Move((r,c), (r+dir,c+i), self.board))






    def get_rook_moves(self, r, c, moves):
        """ All moves for rook pieces """

        pieces_pinned = False
        pin_direction = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pieces_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])

                if self.board[r][c][1] != "Q":                      # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break 

        enemy_color = "b" if self.white_to_move else "w"
        for dir in [(-1,0),(0,-1),(1,0),(0,1)]:                     # for each possible direction (up, left, down, right) for rook piece
            for i in range(1, 8):

                end_row, end_col = r + dir[0] * i, c + dir[1] * i
                if 0 <= end_row < 8 and  0 <= end_col < 8:
                    if not pieces_pinned or pin_direction == dir or pin_direction == (-dir[0], -dir[1]):
                        end_piece = self.board[end_row][end_col]

                        if end_piece == "--":                       # add empty square
                            moves.append(Move((r,c), (end_row, end_col), self.board))

                        elif end_piece[0] == enemy_color:           # capture enemy piece
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break

                        else:                                       # friendly piece
                            break

                else:                                               # outside the board boundary
                    break






    def get_night_moves(self, r, c, moves):
        """ All moves for night pieces """

        pieces_pinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pieces_pinned = True
                self.pins.remove(self.pins[i])
                break 

        ally_color = "w" if self.white_to_move else "b"
        for dir in [(-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2)]:   # for each possible move for knight piece
            end_row, end_col = r + dir[0], c + dir[1]

            if 0 <= end_row < 8 and  0 <= end_col < 8 and not pieces_pinned:    # ensure valid move
                end_piece = self.board[end_row][end_col]
                
                if end_piece[0] != ally_color:                                  # capture enemy piece or empty square
                    moves.append(Move((r,c), (end_row, end_col), self.board))






    def get_bishop_moves(self, r, c, moves):
        """ All moves for bishop pieces """

        pieces_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pieces_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break 

        enemy_color = "b" if self.white_to_move else "w"
        for dir in [(-1,-1),(-1,1),(1,1),(1,-1)]:                       # for each possible direction (diagonal) for bishop piece
            for i in range(1, 8):
                end_row, end_col = r + dir[0] * i, c + dir[1] * i
                
                if 0 <= end_row < 8 and  0 <= end_col < 8:
                    if not pieces_pinned or pin_direction == dir or pin_direction == (-dir[0], -dir[1]):
                        end_piece = self.board[end_row][end_col]
                        
                        if end_piece == "--":                           # add empty square
                            moves.append(Move((r,c), (end_row, end_col), self.board))

                        elif end_piece[0] == enemy_color:               # capture enemy piece
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break

                        else:                                           # friendly piece
                            break

                else:                                                   # outside the board boundary
                    break






    def get_queen_moves(self, r, c, moves):
        """ All moves for queen piece """

        self.get_rook_moves(r, c, moves)            # queen piece can move like a rook
        self.get_bishop_moves(r,c, moves)           # queen piece can move like a bishop





    def get_king_moves(self, r, c, moves):
        """ All moves for king piece """

        ally_color = "w" if self.white_to_move else "b"
        for dir in [(-1,-1),(-1,1),(1,1),(1,-1),(-1,0),(0,-1),(1,0),(0,1)]:     # for each possible move for king piece
            end_row, end_col = r + dir[0], c + dir[1]

            if 0 <= end_row < 8 and  0 <= end_col < 8:                          # ensure valid move
                end_piece = self.board[end_row][end_col]
                
                if end_piece[0] != ally_color:                                  # capture enemy piece or empty square
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.white_king = (end_row, end_col)
                    else:
                        self.black_king = (end_row, end_col)

                    in_check, pins, checks =  self.check_for_pins_and_check()
                    if not in_check:
                        moves.append(Move((r,c), (end_row, end_col), self.board))

                    # place king back on original location
                    if ally_color == "w":
                        self.white_king = (r, c)
                    else:
                        self.black_king = (r, c)

            










class Move():

    # map keys to vallues
    rank_to_row = { str(x) : 8 - x  for x in range(1,9) }
    row_to_rank = { v : k for k, v in rank_to_row.items() }
    files_to_cols = { chr(97+x) : x  for x in range(8)}
    cols_to_files = { v : k for k, v in files_to_cols.items() }


    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col] 

        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col


    # Overriding the equal method
    def __eq__(self, other):
        if isinstance(other, Move):                         # ensure the board is an instance of Move Class
            return self.move_ID == other.move_ID            # check if the move id is not the same as current move

        return False
            
    
    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + " " + self.get_rank_file(self.end_row, self.end_col)


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.row_to_rank[r]
