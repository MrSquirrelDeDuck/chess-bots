import typing
import chess
import math

import base

class AlphaMove(base.ChessBot):
    name = "alphamove"
    creator = "Randall Munroe"
    description = "Sorts the legal moves alphabetically, and plays the middle one."
    color = 0x7f7f7f

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        moves = list(board.legal_moves)

        sorted_moves = sorted(moves, key=lambda move: board.san(move))
        
        return sorted_moves[math.ceil(len(sorted_moves)) - 1]