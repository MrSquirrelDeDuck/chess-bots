import typing
import chess
import random

import base

class RandomBot(base.ChessBot):
    name = "random"
    description = """Chooses a random piece, and then from there a random move that piece can make.\nThis means each piece has an equal chance of being moved.\nFor a bot that chooses a random move from a giant list of all the possible moves `random_simple` is what you're looking for."""
    creator = "Duck"
    color = 0x2ecc68

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        all_pieces = []

        for piece in chess.PIECE_TYPES:
            pieces = board.pieces(piece, board.turn)

            for tile in pieces:
                all_pieces.append(tile)
        
        for _ in all_pieces:
            chosen_tile = random.choice(all_pieces)
                
            all_moves = board.legal_moves

            possible_moves = []
            for move in all_moves:
                if move.from_square == chosen_tile:
                    possible_moves.append(move)
            
            if len(possible_moves) == 0:
                continue
            
            return random.choice(possible_moves)
        
        # Failsafe, this should never happen, and it might not even help.
        return random.choice(list(board.legal_moves))