import chess
import typing
import random

import base

class RandomSimple(base.ChessBot):
    name = "random_simple"
    description = """Gets a list of all possible moves, and chooses a random one."""
    creator = "Duck"
    color = 0x2eccb7

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        return random.choice(list(board.legal_moves))