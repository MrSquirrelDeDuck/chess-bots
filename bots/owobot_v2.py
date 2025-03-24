import typing
import chess
import random

import base

class OwObot_v2(base.ChessBot):
    name = "owobot_v2"
    description = """Duck's failed attempt at dethroning NyaaBot, but the second version."""
    creator = "Duck"
    color = 0xb200ff

    PIECE_VALUE = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 3
    }
    
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
        attacks = self.get_attacks(board, square)

        return attacks - (attacks & self.get_all_pieces(board, color))
    
    def get_defense(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color,
            square: chess.Square
        ) -> chess.Bitboard:
        attacks = self.get_attacks(board, square)

        return attacks & self.get_all_pieces(board, color)
    
    def get_defended_squares(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        total = chess.BB_EMPTY

        for square in board.piece_map(mask=self.get_all_pieces(board, color)):
            total |= self.get_defense(board, color, square)
        
        return total
    
    def get_attacked_squares(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        total = chess.BB_EMPTY

        for square in board.piece_map(mask=self.get_all_pieces(board, color)):
            total |= self.get_attacks(board, square)
        
        return total
    
    def get_all_pieces(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        return board.occupied_co[color]

    def get_undefended_pieces(
            self: typing.Self,
            board: chess.Board,
            color: chess.Color
        ) -> chess.Bitboard:
        return self.get_all_pieces(board, color) - self.get_defended_squares(board, color)


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
                score += 1

                # Check if it's checkmate...
                board.push(move)
                if board.is_checkmate():
                    board.pop()
                    return move
                board.pop()

            ################################
            # Check for captures.
            if board.is_capture(move):
                score += 1

            ################################
            # Check for piece blunders.
            if self.move_blunders_piece(board, move):
                score -= 10

            move_rankings[move] = score
        
        initial_move = self.get_move(move_rankings)
        move = initial_move

        while True:
            board.push(move)
            if self.final_check(board, move):
                board.pop()
                break
            board.pop()
            
            move_rankings.pop(move)

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
            move: chess.Move
        ) -> bool:

        for opponent_move in board.legal_moves:
            if board.gives_check(opponent_move):
                board.push(opponent_move)
                if board.is_checkmate():
                    board.pop()
                    return False
                board.pop()
        
        if board.outcome(claim_draw=True) and not board.is_checkmate():
            return False

        return True
    
    def move_blunders_piece(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move
        ) -> bool:
        board.push(move)

        undefended_pieces = self.get_undefended_pieces(board, self.side)
        attacked = self.get_attacked_squares(board, not self.side)

        attacked_pieces = undefended_pieces & attacked

        board.pop()

        return attacked_pieces > 0