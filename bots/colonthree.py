import typing
import chess
import math
import copy
import random

import base

class colon_three(base.ChessBot):
    name = ":3"
    description = """:3"""
    creator = "Duck"
    color = 0xffa8ff

    bot_turn = None
    
    PIECE_TABLE_VARIATION = {
        n: 1 if n < 10 else (
            0 if n > 20 else (
                math.cos((math.pi / 10) * n - math.pi) / 2 + 0.5
            )
        )
        for n in range(33)
    }
    
    # The point at which to award the maximum amount of points for the piece sum.
    # If the piece sum goes above this then it will award a higher than normal amount of points.
    # That should really only occur if it promotes a ton of queens, though.
    MAX_PIECE_SUM = 3940 # Starting position.
    
    DISTANCE_MULTIPLIER = {
        chess.PAWN: 1,
        chess.KNIGHT: 1.5,
        chess.BISHOP: 1.5,
        chess.ROOK: 1.25,
        chess.QUEEN: 1.33,
        chess.KING: 0.2   
    }
    
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 320,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 300
    }
    
    WHITE_PIECE_TABLE_PAWN_START = list(reversed([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]))

    WHITE_PIECE_TABLE_PAWN_END = list(reversed([
        100, 100, 100, 100, 100, 100, 100, 100,
         75,  75,  75,  75,  75,  75,  75,  75,
         50,  50,  50,  50,  50,  50,  50,  50,
         25,  25,  25,  25,  25,  25,  25,  25,
         20,  20,  20,  20,  20,  20,  20,  20,
         10,  10,  10,  10,  10,  10,  10,  10,
          0,   0,   0,   0,   0,   0,   0,   0,
          0,   0,   0,   0,   0,   0,   0,   0
    ]))

    WHITE_PIECE_TABLE_KNIGHT = list(reversed([
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]))

    WHITE_PIECE_TABLE_BISHOP = list(reversed([
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ]))
    
    WHITE_PIECE_TABLE_ROOK = list(reversed([
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]))

    WHITE_PIECE_TABLE_QUEEN = list(reversed([
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        -5,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]))

    WHITE_PIECE_TABLE_KING_START =list(reversed([
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]))

    WHITE_PIECE_TABLE_KING_END = list(reversed([
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]))
    
    # The black piece tables are the white ones but reversed.
    BLACK_PIECE_TABLE_PAWN_START = list(reversed(WHITE_PIECE_TABLE_PAWN_START))
    BLACK_PIECE_TABLE_PAWN_END = list(reversed(WHITE_PIECE_TABLE_PAWN_END))
    BLACK_PIECE_TABLE_KNIGHT = list(reversed(WHITE_PIECE_TABLE_KNIGHT))
    BLACK_PIECE_TABLE_BISHOP = list(reversed(WHITE_PIECE_TABLE_BISHOP))
    BLACK_PIECE_TABLE_ROOK = list(reversed(WHITE_PIECE_TABLE_ROOK))
    BLACK_PIECE_TABLE_QUEEN = list(reversed(WHITE_PIECE_TABLE_QUEEN))
    BLACK_PIECE_TABLE_KING_START = list(reversed(WHITE_PIECE_TABLE_KING_START))
    BLACK_PIECE_TABLE_KING_END = list(reversed(WHITE_PIECE_TABLE_KING_END))

    #######################################################################################################################
    ##### UTILITIES #######################################################################################################
    #######################################################################################################################
    
    def get_attacks(
            self: typing.Self,
            board: chess.Board,
            square: chess.Square
        ) -> chess.Bitboard:
        """Returns a bitboard for the squares that the piece on the given square attacks."""
        return int(board.attacks(square))

    def get_attacked_squares(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color
        ) -> chess.Bitboard:
        """Returns a bitboard of squares attacked by the given side."""
        total = chess.BB_EMPTY

        for square in board.piece_map(mask=self.get_occupied_bitboard(board, side)):
            total |= self.get_attacks(board, square)

        return total
    
    def get_piece_bitboard(
            self: typing.Self,
            board: chess.Board,
            piece: chess.Piece
        ) -> chess.Bitboard:
        """Returns a bitboard of all the squares with the given piece."""
        return board.pieces_mask(piece)

    def get_occupied_bitboard(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color
        ) -> chess.Bitboard:
        """Returns a bitboard of all the squares occupied by the given side."""
        return board.occupied_co[side]
    
    def get_undefended_pieces(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color
        ) -> chess.Bitboard:
        """Returns a bitboard of all the pieces for the given side that are not defended."""
        return self.get_occupied_bitboard(board, side) - (self.get_occupied_bitboard(board, side) & self.get_attacked_squares(board, side))

    def get_hanging_pieces(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color
        ) -> chess.Bitboard:
        """Returns a bitboard of the pieces for the given side that are attacked by the other side but not defended."""
        return self.get_undefended_pieces(board, side) & self.get_attacked_squares(board, not side)
    
    def is_passed_pawn(
            self: typing.Self,
            board: chess.Board,
            square: chess.Square,
            side: chess.Color
        ) -> bool:
        """Returns a boolean for whether the pawn on the given square is a passed pawn."""
        cover_bitboard = 0
        
        pawn_file = chess.square_file(square)
        
        # Get a bitboard covering the file the pawn is on, as well as the files next to it.
        cover_bitboard |= chess.BB_FILES[pawn_file]
        
        if pawn_file != 0:
            cover_bitboard |= chess.BB_FILES[pawn_file - 1]
        if pawn_file != 7:
            cover_bitboard |= chess.BB_FILES[pawn_file + 1]
        
        # Shift the bitboard by 8 per row the pawn is away from the end of the board.
        # If it's a white pawn, shift right, if it's a black pawn, shift left.
        # Add 1 to the shift multiplier to disregard pawns on the same rank as the passed pawn.
        if side == chess.WHITE:
            cover_bitboard <<= 8 * (chess.square_rank(square) + 1)
        else:
            cover_bitboard >>= 8 * (8 - chess.square_rank(square))
        
        # Bitwise and the other side's pieces with the overall pawn bitboard to get the other side's pawns in a bitboard.
        # Then, by bitwise anding that with the cover bitboard any bits that are 1 are opposing pawns that are able to stop this pawn.
        # If that's the case, then this pawn is not a passed pawn, so invert the result to return True for actual passed pawns.
        return not bool(board.pawns & board.occupied_co[not side] & cover_bitboard)

    def find_passed_pawns(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color
        ) -> chess.Bitboard:
        """Returns a bitboard of the passed pawns for the given side."""
        result = 0
        
        for pawn in board.pieces(chess.PAWN, side):
            if self.is_passed_pawn(board, pawn, side):
                result |= chess.BB_SQUARES[pawn]
        
        return result

    def occupied_value(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color,
            value: chess.PieceType,
            condition: typing.Callable[[int, int], bool],
            exclude_king: bool = True
        ) -> chess.Bitboard:
        """Returns a bitboard for every occupied square with a piece value that satisfies the given condition."""
        check_value = self.PIECE_VALUES[value]
        
        out = 0
        
        for piece_type, piece_value in self.PIECE_VALUES.items():
            if not condition(piece_value, check_value):
                continue
            
            if piece_type == chess.KING and exclude_king:
                continue
            
            for piece in board.pieces(piece_type, side):
                out |= chess.BB_SQUARES[piece]
        
        return out

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        self.bot_turn = board.turn
        pre_check_board = board.copy()
        
        moves = []

        for move in board.legal_moves:
            # Push the move to the board and get the ranking of the move.
            board.push(move)

            ranking = self.rate_board_state(
                pre_board = pre_check_board,
                post_board = board,
                move = move
            )
            
            if ranking == math.inf:
                board.pop()
                return move

            # Append the move and its ranking to the list of moves and pop the move from the board.
            moves.append((move, ranking))
            board.pop()
        
        # Get a dictionary with the keys being the ranks
        # and the values being a list of moves with that rank.
        move_brackets = {}
        
        for move, rank in moves:
            if rank not in move_brackets:
                move_brackets[rank] = [move]
            else:
                move_brackets[rank].append(move)
        
        
        sort = sorted(list(move_brackets.items()), key=lambda x: x[0], reverse=True)
        
        for rank, sorted_moves in copy.deepcopy(sort):
            while len(sorted_moves) > 0:
                chosen = random.choice(sorted_moves)
                
                if not self.sanity_check(board, chosen):
                    sorted_moves.remove(chosen)
                    continue
                
                return chosen
            
            # If it gets here then all the moves resulted in the sanity check failing, that's not good.
        
        # If the `for` loop didn't return anything then every single possible move fails the sanity check,
        # in which case we should just return a random one in the highest bracket.
        highest = max(move_brackets.keys())
        
        return random.choice(move_brackets[highest])
    
    def sanity_check(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> bool:
        """Final sanity check for good moves. This makes sure nothing is really wrong with the move.
        Blundering checkmate, for example, would flag this and the move would be ignored.
        
        Returns a boolean for whether the move is okay to play."""
        board.push(move)

        # Check for checkmate.
        # Check the opponent's legal moves to see if they have mate in 1.
        for move_check in board.legal_moves:
            board.push(move_check)
            if board.is_checkmate():
                board.pop()
                board.pop()
                return False
            
            if self.check_mate_in_two(board):
                board.pop()
                board.pop()
                return False
            
            board.pop()
        
        board.pop()
        
        # If nothing else fires, the move is probably okay.
        return True

    def rate_board_state(
            self: typing.Self,
            pre_board: chess.Board,
            post_board: chess.Board,
            move: chess.Move
        ) -> float:
        """Ranks a board state based on the some criteria.""" 
        # If it's checkmate, that's pretty good. Return infinity.
        if post_board.is_checkmate():
            return math.inf
        
        # We want to avoid draws, so if it's a draw, return negative infinity.
        if post_board.is_game_over(claim_draw=True):
            return -math.inf
        
        # Check for mate in 2.
        if self.check_mate_in_two(post_board):
            return 1e200 # Not math.inf in case there's mate in 1 and we haven't checked it yet.

        # Base score of 0.
        out = 0

        # If it's a capture, reward that by adding the value of the captured piece to the score.
        if pre_board.is_capture(move):
            captured_piece = pre_board.piece_at(move.to_square)
            try:
                captured_piece_value = self.PIECE_VALUES[captured_piece.piece_type] * 1.75
            except AttributeError:
                # En passant.
                captured_piece_value = self.PIECE_VALUES[chess.PAWN] * 1.75
            out += captured_piece_value
        
        # If it's a check, reward that by adding 1 to the score.
        if post_board.is_check():
            out += self.check_value(pre_board, post_board, move)
            # out += 100
        
        # For every hanging piece, subtract 5 from the score.
        out -= self.hanging_pieces_penalty(post_board)
        # hanging = self.get_hanging_pieces(post_board, self.bot_turn)
        # out -= hanging.bit_count() * 500
        
        # If this move is moving a passed pawn, we should reward that.
        out += self.moving_passed_pawn(pre_board, move)
        
        # Use the piece square tables to rate the ending location of the played move.
        out += self.rate_ending_location(pre_board, move)
        
        # Apply a bonus based on the average distance of the pieces to the opposing king.
        out += self.average_distance_bonus(post_board, move)
        
        # Apply a bonus based on the sum of piece values for the bot.
        # This really only makes a difference in regards to pawn promotion.
        out += self.piece_sum(post_board)
        
        # Attempt to keep castling rights by applying a 50 point
        # penalty to moves that would lose castling rights.
        out -= self.castling_rights(pre_board, post_board, move)
        
        # Apply a bonus or penalty based on how safe our
        # king is and how safe the opposing king is.
        out += self.rate_king_safety(post_board)
        
        return out
    
    #######################################################################################################################
    ##### RANKING CRITERIA ################################################################################################
    #######################################################################################################################
    
    def check_value(
            self: typing.Self,
            pre_board: chess.Board,
            post_board: chess.Board,
            move: chess.Move
        ) -> int:
        """Gives a rating for a move that puts the opponent in check."""
        
        # By default give checks a bonus of 100 to incentivise them
        out = 100
        
        # Check for forks!
        # If the piece moved is also attacking an undefended piece or a 
        # defended piece of higher value add a larger bonus for the move
        # based on what exactly is the case.
        attacked = self.get_attacks(post_board, move.to_square)
        opposing_undefended = self.get_undefended_pieces(post_board, not self.bot_turn)
        
        # We want to make sure the king isn't in the bitboard of undefended pieces, since that could mess things up.
        opposing_king = chess.BB_SQUARES[post_board.king(not self.bot_turn)]
        if opposing_king & opposing_undefended:
            opposing_undefended -= opposing_king
        
        # If the bitwise AND returns something other than 0 that means we're forking an undefended piece.
        undefended_attacked = attacked & opposing_undefended
        if undefended_attacked:
            # We're assuming we'll capture the highest value piece if there's multiple,
            # so iterate through the bits in the bitboard and find the one with the highest piece value.
            pieces = []
            for forked_square in chess.scan_forward(undefended_attacked):
                forked_piece = post_board.piece_at(forked_square).piece_type
                pieces.append(self.PIECE_VALUES[forked_piece])
            
            out += max(pieces)
        
        # Time to check for defended pieces we're attacking that are worth more than what we're attacking with.
        attacking_value = self.PIECE_VALUES[post_board.piece_at(move.to_square).piece_type]
        defended_squares = self.get_attacked_squares(post_board, not self.bot_turn)
        opposing_pieces = self.get_occupied_bitboard(post_board, not self.bot_turn)
        
        defended_pieces = defended_squares & opposing_pieces
        attacked_pieces = defended_pieces & attacked
        
        if attacked_pieces:
            pieces = []
            for forked_square in chess.scan_forward(undefended_attacked):
                forked_piece_value = self.PIECE_VALUES[post_board.piece_at(forked_square).piece_type]
                
                if forked_piece_value > attacking_value:
                    pieces.append(forked_piece_value)
            
            # An empty list will return False, so this checks if the list has any pieces in it.
            if pieces:
                out += max(pieces) * (2/3)
        
        return out

    def moving_passed_pawn(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> int:
        """Returns a boolean for whether the given move is moving a passed pawn."""
        if board.piece_at(move.from_square).piece_type == chess.PAWN:
            rank_multiplier = chess.square_rank(move.to_square) if self.bot_turn == chess.WHITE else 7 - chess.square_rank(move.to_square)
            
            return self.is_passed_pawn(board, move.from_square, board.turn) * (rank_multiplier * 50)
        
        return 0
    
    def rate_ending_location(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> int:
        piece_type = board.piece_at(move.from_square).piece_type
        
        # Pawns and kings are a bit special since they have two different ones that are interpolated between based on the number of remaining pieces.
        if piece_type == chess.PAWN:
            return self.rate_ending_location_pawn(board, move)
        elif piece_type == chess.KING:
            return self.rate_ending_location_king(board, move)
        
        # Knights.
        elif piece_type == chess.KNIGHT:
            if self.bot_turn == chess.WHITE:
                return self.WHITE_PIECE_TABLE_KNIGHT[move.to_square]
            else:
                return self.BLACK_PIECE_TABLE_KNIGHT[move.to_square]
        
        # Bishops:
        elif piece_type == chess.BISHOP:
            if self.bot_turn == chess.WHITE:
                return self.WHITE_PIECE_TABLE_BISHOP[move.to_square]
            else:
                return self.BLACK_PIECE_TABLE_BISHOP[move.to_square]
        
        # Rooks:
        elif piece_type == chess.ROOK:
            if self.bot_turn == chess.WHITE:
                return self.WHITE_PIECE_TABLE_ROOK[move.to_square]
            else:
                return self.BLACK_PIECE_TABLE_ROOK[move.to_square]
        
        # Queens:
        elif piece_type == chess.QUEEN:
            if self.bot_turn == chess.WHITE:
                return self.WHITE_PIECE_TABLE_QUEEN[move.to_square]
            else:
                return self.BLACK_PIECE_TABLE_QUEEN[move.to_square]

        # This should be unreachable.
        return 0

    def rate_ending_location_pawn(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> int:
        """Gives a score based on the location of a pawn if it's being moved."""
        remaining_pieces = board.occupied.bit_count()
        
        ending_contribution = self.PIECE_TABLE_VARIATION[remaining_pieces]
        
        if self.bot_turn == chess.WHITE:
            start = self.WHITE_PIECE_TABLE_PAWN_START[move.to_square]
            end = self.WHITE_PIECE_TABLE_PAWN_END[move.to_square]
        else:
            start = self.BLACK_PIECE_TABLE_PAWN_START[move.to_square]
            end = self.BLACK_PIECE_TABLE_PAWN_END[move.to_square]
        
        return ending_contribution * (end - start) + start

    def rate_ending_location_king(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> int:
        """Gives a score based on the location of the king if it's being moved."""
        remaining_pieces = board.occupied.bit_count()
        
        ending_contribution = self.PIECE_TABLE_VARIATION[remaining_pieces]
        
        if self.bot_turn == chess.WHITE:
            start = self.WHITE_PIECE_TABLE_KING_START[move.to_square]
            end = self.WHITE_PIECE_TABLE_KING_END[move.to_square]
        else:
            start = self.BLACK_PIECE_TABLE_KING_START[move.to_square]
            end = self.BLACK_PIECE_TABLE_KING_END[move.to_square]
        
        return ending_contribution * (end - start) + start
    
    # Unused, but should still theoretically work.
    def full_hanging_pieces_penalty(
            self: typing.Self,
            post_board: chess.Board
        ) -> int:
        """Applies a negative penalty based on hanging pieces, this only accounts for undefended pieces, however."""
        hanging_pieces = self.get_hanging_pieces(post_board, self.bot_turn)
        
        if not hanging_pieces:
            return 0
        
        out_score = 0
        
        for hanging_square in chess.scan_forward(hanging_pieces):
            # Get the piece on the given square.
            piece_type = post_board.piece_at(hanging_square).piece_type
            out_score -= self.PIECE_VALUES[piece_type]
        
        return out_score
    
    def hanging_pieces_penalty(
            self: typing.Self,
            post_board: chess.Board
        ) -> int:
        """Applies a negative penalty based on hanging pieces, accounting for piece value."""
        self_occupied = self.get_occupied_bitboard(post_board, self.bot_turn)
        self_attacking = self.get_attacked_squares(post_board, self.bot_turn)
        
        penalty_value = 0
        
        for square in chess.scan_forward(self.get_occupied_bitboard(post_board, not self.bot_turn)):
            piece_type = post_board.piece_at(square).piece_type
            
            attacking = self.get_attacks(post_board, square)
            
            for attacked_square in chess.scan_forward(attacking & self_occupied):
                attacked_type = post_board.piece_at(attacked_square).piece_type
                
                attacking_amount = post_board.attackers_mask(not self.bot_turn, attacked_square).bit_count()
                defending_amount = post_board.attackers_mask(self.bot_turn, attacked_square).bit_count()
                
                if attacking_amount > defending_amount:
                    penalty_value += self.PIECE_VALUES[attacked_type] * 1.5
                
                if not chess.BB_SQUARES[attacked_square] & self_attacking:
                    penalty_value += self.PIECE_VALUES[attacked_type] * 1.5
                
                # If it's worth the same assume it's a fair trade.
                elif self.PIECE_VALUES[attacked_type] > self.PIECE_VALUES[piece_type]:
                    penalty_value += self.PIECE_VALUES[attacked_type] / 2
                    
        return penalty_value

    def average_distance_bonus(
            self: typing.Self,
            post_board: chess.Board,
            move: chess.Move
        ) -> int:
        opposing_king = post_board.king(not self.bot_turn)
        opposing_rank = chess.square_rank(opposing_king)
        opposing_file = chess.square_file(opposing_king)
        
        distances = []
        for piece_square in chess.scan_forward(self.get_occupied_bitboard(post_board, self.bot_turn)):
            square_rank = chess.square_rank(piece_square) - opposing_rank
            square_file = chess.square_file(piece_square) - opposing_file
            
            square_rank **= 2
            square_file **= 2
            
            distances.append(square_rank + square_file)
        
        out = int((128 - (sum(distances) / len(distances)) / 128 * 300))
        
        piece_type = post_board.piece_at(move.to_square).piece_type
        out *= self.DISTANCE_MULTIPLIER[piece_type]
        
        return out

    def check_mate_in_two(
            self: typing.Self,
            post_board: chess.Board
        ) -> bool:
        """Attempts to find mate in two. Returns a boolean for whether it found mate in two."""
        
        for opponent_move in post_board.legal_moves:
            post_board.push(opponent_move)

            for self_move in post_board.legal_moves:
                post_board.push(self_move)

                if post_board.is_checkmate():
                    post_board.pop()
                    break

                post_board.pop()
            else:
                post_board.pop()
                break

            post_board.pop()
        else:
            return True

        return False
    
    def piece_sum(
            self: typing.Self,
            board: chess.Board
        ) -> int:
        amount = 0
        
        for piece_type in chess.PIECE_TYPES:
            # Ignore the king.
            if piece_type == chess.KING:
                continue
            
            amount += board.pieces_mask(piece_type, self.bot_turn).bit_count() * self.PIECE_VALUES[piece_type]
        
        return amount / self.MAX_PIECE_SUM * 100
    
    def castling_rights(
            self: typing.Self,
            pre_board: chess.Board,
            post_board: chess.Board,
            move: chess.Move
        ) -> int:
        if pre_board.is_castling(move):
            return -75 # Apply a bonus to castling.
        
        if pre_board.has_castling_rights(self.bot_turn) and not post_board.has_castling_rights(self.bot_turn):
            return 100

        return 0
    
    def rate_king_safety(
            self: typing.Self,
            post_board: chess.Board
        ) -> int:
        """Rates the position based on the king safety of both sides."""
        self_safety = self.king_safety_single(post_board, self.bot_turn)
        opposing_safety = self.king_safety_single(post_board, not self.bot_turn)
        
        return self_safety - opposing_safety
    
    def king_safety_single(
            self: typing.Self,
            board: chess.Board,
            side: chess.Color
        ) -> int:
        """Rates king safety for the given side."""
        king = board.king(side)
        
        check = chess.BB_KING_ATTACKS[king]
        
        if board.turn == side:
            moves = list(board.generate_legal_moves(chess.BB_SQUARES[king]))
        else:
            board.push(chess.Move.null())
            moves = list(board.generate_legal_moves(chess.BB_SQUARES[king]))
            board.pop()
        
        return 300 - (check & self.get_attacks(board, not side)).bit_count() * 33 - len(moves) * 50