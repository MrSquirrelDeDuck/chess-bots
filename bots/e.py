import typing
import chess
import random
import os

import base

class E(base.ChessBot):
    name = "e"
    creator = "Duck"
    description = "e"
    color = 0x271828

    def __init__(
            self: typing.Self,
            database_data: dict
        ) -> None:
        try:
            with open(os.path.join("data", "100k_pi.txt"), "r") as file_read:
                self.digits = file_read.read()
        except FileNotFoundError:
            self.digits = None

        super().__init__(database_data)
    
    def load(
            self: typing.Self,
            data: dict
        ) -> None:
        if self.digits is None:
            self.digit_position = None
        else:
            self.initial = data.get("initial", random.randint(50, 50_000))
            self.digit_position = data.get("digit_position", self.initial)
    
    def save(self: typing.Self) -> dict | None:
        return {
            "digit_position": self.digit_position,
            "initial": self.initial
        }
    
    def increment(self: typing.Self) -> None:
        if self.initial < 25_000:
            self.digit_position += 1
        else:
            self.digit_position -= 1
    
    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        while True:
            if self.digits is None:
                return random.choice(list(board.legal_moves))
            
            digits = int(self.digits[self.digit_position * 2:self.digit_position * 2 + 2])

            all_pieces = []
            for j in range(6):
                pieces = board.pieces(chess.PIECE_TYPES[j], board.turn)

                for tile in pieces:
                    all_pieces.append((board.piece_at(tile), tile))

            piece_count = len(all_pieces)
            
            cutoff = (100 // piece_count) * piece_count

            if digits >= cutoff:
                while digits >= cutoff:
                    self.increment()
                    digits = int(self.digits[self.digit_position * 2:self.digit_position * 2 + 2])

            chosen_piece, chosen_tile = all_pieces[int(digits / cutoff * piece_count)]
            
            all_moves = board.legal_moves

            possible_moves = []
            for move in all_moves:
                if move.from_square == chosen_tile:
                    possible_moves.append(move)
            
            ###########################################
            self.increment()
            digits = int(self.digits[self.digit_position * 2:self.digit_position * 2 + 2])
            ###########################################

            possible_move_count = len(possible_moves)

            if possible_move_count == 0:
                self.increment()
                continue
            
            cutoff = (100 // possible_move_count) * possible_move_count

            if digits >= cutoff:
                while digits >= cutoff:
                    self.increment()
                    digits = int(self.digits[self.digit_position * 2:self.digit_position * 2 + 2])
        
            return possible_moves[int(digits / cutoff * possible_move_count)]