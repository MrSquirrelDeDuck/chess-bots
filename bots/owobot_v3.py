import typing
import chess
import random
import math

import base

class OwObot_v3(base.ChessBot):
    name = "owobot_v3"
    description = """Duck's failed attempt at dethroning NyaaBot, but the third version."""
    creator = "Duck"
    color = 0x0a6564

    PIECE_VALUE = {
        chess.KING: 3,
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.2,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    PIECE_VALUE_ITEMS = list(PIECE_VALUE.items())

    # King move rankings.

    KING_MOVE_RANKINGS_START = {
        0: -1,
        1: 1,
        2: 0.5,
        3: 0,
        4: -0.25,
        5: -0.5,
        6: -0.5,
        7: -0.5,
        8: -0.5,
        9: -0.5
    }

    KING_MOVE_RANKINGS_END = {
        0: -4,
        1: -3,
        2: -2,
        3: -1,
        4: 0,
        5: 1,
        6: 2,
        7: 3,
        8: 4,
        9: 5
    }

    # Piece tables.

    PIECE_TABLE_PAWN_START = list(reversed([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]))

    PIECE_TABLE_PAWN_END = list(reversed([
        100, 100, 100, 100, 100, 100, 100, 100,
         75,  75,  75,  75,  75,  75,  75,  75,
         50,  50,  50,  50,  50,  50,  50,  50,
         25,  25,  25,  25,  25,  25,  25,  25,
         20,  20,  20,  20,  20,  20,  20,  20,
         10,  10,  10,  10,  10,  10,  10,  10,
          0,   0,   0,   0,   0,   0,   0,   0,
          0,   0,   0,   0,   0,   0,   0,   0
    ]))

    PIECE_TABLE_KNIGHT = list(reversed([
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]))

    PIECE_TABLE_BISHOP = list(reversed([
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ]))
    
    PIECE_TABLE_ROOK = list(reversed([
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]))

    PIECE_TABLE_QUEEN = list(reversed([
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]))

    PIECE_TABLE_KING_START =list(reversed([
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]))

    PIECE_TABLE_KING_END = list(reversed([
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]))

    # Utility methods.

    def iterate_through_bitboard(
            self: typing.Self,
            bitboard: chess.Bitboard
        ) -> typing.Generator[int, None, None]:
        while bitboard:
            b = bitboard & (~bitboard + 1)
            yield int(math.log2(b))
            bitboard ^= b
    
    def get_attacks(
            self: typing.Self,
            board: chess.Board,
            square: chess.Square
        ) -> chess.Bitboard:
        """Returns a bitboard for the squares that the piece on the given square attacks."""
        return int(board.attacks(square))
    
    def get_attacks_filtered(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color,
            square: chess.Square
        ) -> chess.Bitboard:
        """Same as .get_attacks, but removes the tiles that the given color's pieces are on."""
        attacks = self.get_attacks(board, square)

        return attacks - (attacks & self.get_all_pieces(board, color))
    
    def get_defense(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color,
            square: chess.Square
        ) -> chess.Bitboard:
        """Gives a bitboard of squares defended by the given square that the given color has a piece on."""
        attacks = self.get_attacks(board, square)

        return attacks & self.get_all_pieces(board, color)
    
    def get_defended_squares(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Gives a bitboard of every square the given color has a piece on which is defended."""
        total = chess.BB_EMPTY

        for square in board.piece_map(mask=self.get_all_pieces(board, color)):
            total |= self.get_defense(board, color, square)
        
        return total
    
    def get_attacked_squares(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Gives a bitboard of every square the given color attacks."""
        total = chess.BB_EMPTY

        for square in board.piece_map(mask=self.get_all_pieces(board, color)):
            total |= self.get_attacks(board, square)
        
        return total
    
    def get_attacked_squares_no_king(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Gives a bitboard of every square the given color attacks, not including the king."""
        total = chess.BB_EMPTY

        for square in board.piece_map(mask=self.get_all_pieces(board, color)):
            if board.piece_at(square).piece_type == chess.KING:
                continue

            total |= self.get_attacks(board, square)
        
        return total
    
    def get_squares_attacked_by_king(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        return self.get_attacks(board, board.king(color))
    
    def get_all_pieces(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Gives a bitboard of every square the given color occupies."""
        return board.occupied_co[color]

    def get_all_other_than_panws(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Same as get_all_pieces, but removes pawns."""
        return self.get_all_pieces(board, color) - board.pieces_mask(chess.PAWN, color)

    def get_undefended_pieces(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Gives a bitboard of every square that has a piece of the given color which that color does not defend."""
        return self.get_all_pieces(board, color) - self.get_defended_squares(board, color)

    def get_square_attackers(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color,
            square: chess.Square
        ) -> chess.Bitboard:
        """Gives a bitboard of each square that the given color occupies that attacks the given square."""
        shift = 1 << square
        total = chess.BB_EMPTY

        for piece_square in board.piece_map(mask=self.get_all_pieces(board, color)):
            if shift & self.get_attacks(board, piece_square):
                total |= 1 << piece_square
        
        return total

    def get_attacked_pieces(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Gives a bitboard for every piece of the given color that is attacked by the opposing side."""
        return self.get_all_pieces(board, color) & self.get_attacked_squares(board, not color)
    
    def get_piece_value_from_square(
            self: typing.Self,
            board: chess.Board,
            square: chess.Square
        ) -> int:
        return self.PIECE_VALUE.get(board.piece_type_at(square), 0)

    def convert_square_index(
            self: typing.Self,
            square: chess.Square
        ) -> tuple[int, int]:
        return (square % 8, square // 8)

    def find_hanging_pieces(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        """Finds hanging pieces that `not color` has."""
        output = 0

        color_pieces = self.get_all_pieces(board, color)
        opposite_pieces = self.get_all_pieces(board, not color)

        for piece_square in self.iterate_through_bitboard(color_pieces):
            piece_value = self.get_piece_value_from_square(board, piece_square)

            attacks = self.get_attacks_filtered(board, color, piece_square)

            for attack_square in self.iterate_through_bitboard(attacks & opposite_pieces):
                attack_value = self.get_piece_value_from_square(board, attack_square)

                if attack_value > piece_value:
                    output |= 1 << attack_square
        
        return output
                

    ###################################################################################

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        self.side = board.turn


        move_rankings = {}

        for move in board.legal_moves:

            score = 0

            ################################
            # Check for checks.
            if board.gives_check(move):
                score += self.check_value(board, move)

                # Check if it's checkmate...
                board.push(move)
                if board.is_checkmate():
                    board.pop()
                    return move
                board.pop()

            ################################
            # Check for captures.
            if board.is_capture(move):
                score += self.capture_value(board, move)
            
            ################################
            # Check for piece blunders.
            if self.move_blunders_piece(board, move):
                score -= 10

            ################################
            # Check for piece hangs.
            score += self.move_hangs_any_piece(board, move) * -7.5
                
            ################################
            # Account for king safety.
            score += self.king_safety(board, move)

            ################################
            # Account for distance to enemy king.
            score += self.rate_distance(board, move)

            ################################
            # Account for the number of enemy king moves.
            score += self.enemy_king_moves(board, move)

            ################################
            # Account for the piece table scores.
            score += self.rank_ending_piece_location(board, move)

            ################################
            # Account for attacking vulnerable squares
            score += self.vulnerable_squares(board, move)

            ################################
            # Check for trapped pieces.
            score += self.check_trapped_pieces(board, move)

            move_rankings[move] = score
        
        initial_move = self.get_move(move_rankings)
        move = initial_move

        while not self.final_check(board, move, move_rankings.get(move)):            
            move_rankings.pop(move)

            # If the length of move_rankings is 0 that means that
            # every possible move fails the final check, which
            # means we're screwed. In that case, just return 
            # whatever was the first move chosen.
            if len(move_rankings) == 0:
                return initial_move
            
            move = self.get_move(move_rankings)

        return move
    
    def get_move(
            self: typing.Self,
            rankings: dict[chess.Move, float]
        ) -> chess.Move:
        highest_score = max(rankings.values())

        try:
            return random.choice([m for m, v in rankings.items() if v == highest_score])
        except:
            return max(rankings, key=rankings.get)
    
    ##### RANKING CRITERIA #####

    def final_check(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move,
            ranking: float
        ) -> bool:
        """Final check, if the best move fails this it is thrown out."""
        board.push(move)

        for opponent_move in board.legal_moves:
            if board.gives_check(opponent_move):
                board.push(opponent_move)
                if board.is_checkmate():
                    board.pop()
                    board.pop()
                    return False
                board.pop()
        
        if board.outcome(claim_draw=True) and not board.is_checkmate():
            board.pop()
            return False
        
        board.pop()

        #########################

        return True
    
    def move_blunders_piece(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> bool:
        """If any attacked piece is left undefended after the move is complete.
        This has the exception for if the move is a capture and the captured piece is of equal or higher value than what is doing the capturing."""
        if board.is_capture(move):
            if self.get_piece_value_from_square(board, move.from_square) <= self.get_piece_value_from_square(board, move.to_square):
                return False

        board.push(move)

        undefended_pieces = self.get_undefended_pieces(board, self.side)
        attacked = self.get_attacked_squares(board, not self.side)

        attacked_pieces = undefended_pieces & attacked

        board.pop()

        return attacked_pieces > 0
    
    def move_hangs_moved_piece(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> bool:
        """If the piece being moved will be hanging after being moved."""

        board.push(move)

        attacks = self.get_square_attackers(board, board.turn, move.to_square)
        piece_value = self.get_piece_value_from_square(board, move.to_square)

        for piece_type, value in self.PIECE_VALUE_ITEMS:
            if value == piece_value:
                break

            mask = board.pieces_mask(piece_type, board.turn)

            if mask & attacks > 0:
                board.pop()
                return True

        board.pop()

        return False
    
    def move_hangs_any_piece(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> bool:
        board.push(move)

        attacked_pieces = self.get_attacked_pieces(board, self.side)

        if attacked_pieces == 0:
            board.pop()
            return False
        
        hanging = self.find_hanging_pieces(board, not self.side)
        if hanging:
            board.pop()
            return hanging.bit_count() 
        
        # for hang_square in self.iterate_through_bitboard(attacked_pieces):
        #     # hang_square = int(math.log2(hang_square_raw))
        #     hang_value = self.get_piece_value_from_square(board, hang_square)

        #     attackers = self.get_square_attackers(board, not self.side, hang_square)
        #     for attack_square in self.iterate_through_bitboard(attackers):
        #         # attack_square = int(math.log2(attack_square_raw))
        #         attack_value = self.get_piece_value_from_square(board, attack_square)

        #         if attack_value < hang_value:
        #             board.pop()
        #             if board.fullmove_number == 47 and move.from_square == chess.C4:
        #                 # print(att)
        #                 print(board.san(move), hang_square, hang_value, attack_square, attack_value)
        #             return True
        
        board.pop()
        return False

    
    def capture_value(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        """Assigns a score to a capture."""
        if board.is_capture(move):
            opponent_attackers = self.get_square_attackers(board, not self.side, move.to_square)
            defenders = self.get_square_attackers(board, self.side, move.to_square)
            
            captured_value = self.get_piece_value_from_square(board, move.to_square)
            capturing_value = self.get_piece_value_from_square(board, move.from_square)

            if captured_value > capturing_value:
                return (2 + max((captured_value - capturing_value), 0)) * 3
            elif capturing_value == captured_value:
                if opponent_attackers <= defenders:
                    return 2
                
            if opponent_attackers >= defenders:
                return -2

        return 1
    
    def rate_distance(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        """Rates the updated distance to the enemy king."""
        board.push(move)
        king = board.king(not self.side)

        distance_sum = []

        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, self.side):
                if board.piece_type_at(square) == chess.KING:
                    continue

                distance = math.dist(
                    self.convert_square_index(square),
                    self.convert_square_index(king)
                )
                distance_sum.append(distance)
        
        board.pop()

        if len(distance_sum) == 0:
            return -1
        
        return 10 - (sum(distance_sum) / len(distance_sum))
    
    def enemy_king_moves(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        """Rates the number of moves the enemy king has."""
        board.push(move)
        king_mask = board.pieces_mask(chess.KING, not self.side)
        king_moves = len(list(board.generate_legal_moves(from_mask=king_mask)))

        remaining_pieces = (self.get_all_pieces(board, True) | self.get_all_pieces(board, False)).bit_count() - 2 # Subtract the 2 kings. Max is now 30.

        board.pop()
        ranking = max(min((25 - remaining_pieces), 25), 0) * ((9 - king_moves) / math.pi)

        return ranking

    
    def king_safety(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        board.push(move)
        board.push(chess.Move.null())

        king_mask = board.pieces_mask(chess.KING, self.side)
        
        king_moves = len(list(board.generate_legal_moves(from_mask=king_mask)))

        rank_start = self.KING_MOVE_RANKINGS_START[king_moves]
        rank_end = self.KING_MOVE_RANKINGS_END[king_moves]

        remaining_pieces = (self.get_all_pieces(board, True) | self.get_all_pieces(board, False)).bit_count() - 2 # Subtract the 2 kings. Max is now 30.

        rank_start_apply = (remaining_pieces / 30) * rank_start
        rank_end_apply = ((30 - remaining_pieces) / 30) * rank_end

        ranking = rank_start_apply + rank_end_apply
    
        board.pop()
        board.pop()

        return ranking
    
    def rank_ending_piece_location(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        piece = board.piece_at(move.from_square)

        score = 0

        if piece.piece_type == chess.PAWN:
            remaining_pieces = (self.get_all_other_than_panws(board, True) | self.get_all_other_than_panws(board, False)).bit_count() - 2 # Subtract the 2 kings. Max is now 14.

            score_start = (remaining_pieces / 14) * self.PIECE_TABLE_PAWN_START[move.to_square]
            score_end = ((14 - remaining_pieces) / 14) * self.PIECE_TABLE_PAWN_START[move.to_square]

            score = score_start + score_end
        elif piece.piece_type == chess.KING:
            remaining_pieces = (self.get_all_other_than_panws(board, True) | self.get_all_other_than_panws(board, False)).bit_count() - 2 # Subtract the 2 kings. Max is now 14.

            score_start = (remaining_pieces / 14) * self.PIECE_TABLE_KING_START[move.to_square]
            score_end = ((14 - remaining_pieces) / 14) * self.PIECE_TABLE_KING_START[move.to_square]

            score = score_start + score_end
        elif piece.piece_type == chess.BISHOP:
            score = self.PIECE_TABLE_BISHOP[move.to_square]
        elif piece.piece_type == chess.KNIGHT:
            score = self.PIECE_TABLE_KNIGHT[move.to_square]
        elif piece.piece_type == chess.ROOK:
            score = self.PIECE_TABLE_ROOK[move.to_square]
        elif piece.piece_type == chess.QUEEN:
            score = self.PIECE_TABLE_QUEEN[move.to_square]
        
        return score / 10

    def vulnerable_squares(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        king = self.get_squares_attacked_by_king(board, not self.side)
        attacked = self.get_attacked_squares_no_king(board, not self.side)

        king_vulernable = king - (king & attacked)

        board.push(move)

        self_attacking = self.get_attacks(board, move.to_square)

        board.pop()

        if king_vulernable & self_attacking:
            # Attacking a vulnerable square!
            return 1.5

        return 0

    def check_value(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        value = 1

        fork_pre = self.find_hanging_pieces(board, self.side)

        board.push(move)

        ### Number of king moves. ###

        king_mask = board.pieces_mask(chess.KING, not self.side)
        king_moves = len(list(board.generate_legal_moves(from_mask=king_mask)))
        value += (9 - king_moves) / 3

        ### Potential forks. ###
        
        fork_post = self.find_hanging_pieces(board, self.side)
        post_count = fork_post.bit_count()

        if post_count > fork_pre.bit_count():
            value += post_count * 7.5

        ########################        

        board.pop()

        return value
    
    def check_trapped_pieces(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> float:
        board.push(move)

        attack_pieces = self.get_attacked_pieces(board, not self.side)

        if not attack_pieces:
            board.pop()
            return 0
        
        out = 0
        
        all_attacks = self.get_attacked_squares(board, self.side)

        for square in self.iterate_through_bitboard(attack_pieces):
            square_attacks = self.get_attacks_filtered(board, not self.side, square)

            if square_attacks & all_attacks == square_attacks:
                attacked = self.get_piece_value_from_square(board, square)
                attackers = self.get_square_attackers(board, self.side, square)

                for potential in self.iterate_through_bitboard(attackers):
                    if self.get_piece_value_from_square(board, potential) < attacked:
                        out += 10
                        break

        board.pop()

        return out