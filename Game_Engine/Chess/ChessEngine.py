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
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"] 
        ]

        self.move_functions = { 'P' : self.get_pawn_moves, 
                                'R' : self.get_rook_moves, 
                                'N' : self.get_night_moves, 
                                'B' : self.get_bishop_moves,
                                'Q' : self.get_queen_moves,
                                'K' : self.get_king_moves }

        self.white_to_move = True
        self.move_log = []

        self.white_king = (7, 4)            # start position of white king
        self.black_king = (0, 4)            # start position of black king
        
        self.in_check = False
        self.check_mate = False
        self.stale_mate = False
        
        self.pins = []
        self.checks = []
        
        self.enpassant_possible = ()        # coordinates for the square where en-passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        
        self.current_castling_rights = CastleRights( True, True, True, True)
        self.castle_rights_log = [  CastleRights(   self.current_castling_rights.wks, 
                                                    self.current_castling_rights.bks, 
                                                    self.current_castling_rights.wqs, 
                                                    self.current_castling_rights.bqs)]






    def make_move(self, move):
        """ Takes a move parameter and executes it """

        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move             # swap player

        if move.piece_moved == "wK":
            self.white_king = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # enpassant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"     # capturing the pawn
        
        # update enpassant_possible variable
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:              # only on 2 square pawn advance
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()
        
        self.enpassant_possible_log.append(self.enpassant_possible)
        
        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:                                                              # king-side castle move
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]         # moves the rook to its new square
                self.board[move.end_row][move.end_col + 1] = '--'                                               # erase old rook
            else:                                                                                               # queen-side castle move
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]         # moves the rook to its new square
                self.board[move.end_row][move.end_col - 2] = '--'                                               # erase old rook


        # update castling rights - whenever it is a rook or king move
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights( self.current_castling_rights.wks, 
                                                    self.current_castling_rights.bks,
                                                    self.current_castling_rights.wqs, 
                                                    self.current_castling_rights.bqs))
        








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

            # undo en passant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"       # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]
            
            # undo castle rights
            self.castle_rights_log.pop()                                # get rid of the new castle rights from the move we are undoing
            self.current_castling_rights = self.castle_rights_log[-1]   # set the current castle rights to the last one in the list
            
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            self.check_mate = False
            self.stale_mate = False






    def update_castle_rights(self, move):
        """ Update the castle rights for the given move """

        # If rook has been captured
        if move.piece_captured == "wR":
            if move.end_col == 0:                               # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:                             # right rook
                self.current_castling_rights.wks = False

        elif move.piece_captured == "bR":
            if move.end_col == 0:                               # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:                             # right rook
                self.current_castling_rights.bks = False

        # If rook or king has been moved
        if move.piece_moved == 'wK':                            # Remove rights for white king when it is moved
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False

        elif move.piece_moved == 'bK':                          # Remove rights for black king when it is moved
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False

        elif move.piece_moved == 'wR':                          # Remove rights for white rook if it is moved
            if move.start_row == 7:
                if move.start_col == 0:                         # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:                       # right rook
                    self.current_castling_rights.wks = False

        elif move.piece_moved == 'bR':                          # Remove rights for black rook if it is moved
            if move.start_row == 0:
                if move.start_col == 0:                         # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:                       # right rook
                    self.current_castling_rights.bks = False






    def get_all_valid_moves(self):
        """ All moves considering checks """

        temp_castle_rights = CastleRights(  self.current_castling_rights.wks, 
                                            self.current_castling_rights.bks,
                                            self.current_castling_rights.wqs, 
                                            self.current_castling_rights.bqs)

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
            
            king = self.white_king if self.white_to_move else self.black_king
            self.get_Castle_Moves(king[0], king[1], moves)
            
        if len(moves) == 0:
            if self.inCheck():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False

        self.current_castling_rights = temp_castle_rights
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
        king_row, king_col = self.white_king if self.white_to_move else self.black_king

        # Check if the piece is not pinned and can move 1 square ahead
        if (not pieces_pinned or pin_direction == (dir,0)) and  0 <= r+dir < 8 and self.board[r+dir][c] == "--":
            moves.append(Move((r,c), (r+dir,c), self.board))

            # Check if the piece is at start and can move 2 square ahead
            if r==start and self.board[r+dir*2][c] == "--":
                moves.append(Move((r,c), (r+dir*2,c), self.board))

        for n,i in enumerate([1, -1]):           # Check if the pawn can capture an enemy piece
            if 0 <= r+dir < 8 and 0 <= c+i < 8:
                if (not pieces_pinned or pin_direction == (dir,i)):
                    if self.board[r+dir][c+i][0] == enemy_color:                # capture enemy piece
                        moves.append(Move((r,c), (r+dir,c+i), self.board))

                    elif (r+dir, c+i) == self.enpassant_possible:               # capture through enpassant move
                        attacking_piece = blocking_piece = False

                        if king_row == r:
                            if king_col < c:                                    # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                                inside_range = range(king_col + 1, c - n)
                                outside_range = range(c + 2 -n, 8)

                            else:                                                   # king right of the pawn
                                inside_range = range(king_col - 1, c + int((1 +i)*0.5), -1)
                                outside_range = range(c - 2 + int((1 +i)*0.5), -1, -1)

                            for j in inside_range:
                                if self.board[r][j] != "--":                      # some piece beside en-passant pawn blocks
                                    blocking_piece = True

                            for j in outside_range:
                                square = self.board[r][j]
                                if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                    attacking_piece = True

                                elif square != "--":
                                    blocking_piece = True

                        if not attacking_piece or blocking_piece:
                            moves.append(Move((r,c), (r+dir,c+i), self.board, is_enpassant_move=True))

                        






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






    def inCheck(self):
        """ Determine if a current player is in check """

        king = self.white_king if self.white_to_move else self.black_king
        return self.square_under_attack(king[0], king[1])



    def square_under_attack(self, row, col):
        """ Determine if enemy can attack the square row col """

        self.white_to_move = not self.white_to_move             # switch to opponent's point of view
        opponents_moves = self.get_all_possible_moves()

        self.white_to_move = not self.white_to_move             # switch back to your point of view
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:     # square is under attack
                return True
        return False





    def get_Castle_Moves(self, row, col, moves):
        """ Generate all valid castle moves for the king at (row, col) and add them to the list of moves. """
        
        if self.square_under_attack(row, col): return                                  # can't castle while in check

        if  (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            self.get_King_side_Castle_Moves(row, col, moves)

        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_Queen_side_Castle_Moves(row, col, moves)



    def get_King_side_Castle_Moves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--' and \
          not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))



    def get_Queen_side_Castle_Moves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--' and \
          not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
            moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))


            









class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs






class Move():

    # map keys to vallues
    rank_to_row = { str(x) : 8 - x  for x in range(1,9) }
    row_to_rank = { v : k for k, v in rank_to_row.items() }
    files_to_cols = { chr(97+x) : x  for x in range(8)}
    cols_to_files = { v : k for k, v in files_to_cols.items() }


    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col] 

        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or (self.piece_moved == "bP" and self.end_row == 7)
        
        # en passant
        self.is_enpassant_move = is_enpassant_move

        if self.is_enpassant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"

        # castle move
        self.is_castle_move = is_castle_move
        
        self.is_capture = self.piece_captured != "--"
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



    # Overriding the string method
    def __str__(self):
        # Castle Move
        if self.is_castle_move: return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.get_rank_file(self.end_row, self.end_col)

        # Pawn Move
        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture: move_string += "x"
        return move_string + end_square

