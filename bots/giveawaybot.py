import typing
import chess
import random

import base

class GiveawayBot(base.ChessBot):
    name = "giveaway"
    description = """This bot is convinced it's playing giveaway/antichess, and will attempt to abide by the variant's rules as best it can."""
    creator = "Duck"
    color = 0xd369ae

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        if board.ply() == 0:
            return chess.Move(chess.E2,chess.E3)
        elif board.ply() == 1:
            return chess.Move(chess.E7,chess.E6)

        move_data = {}

        for move in board.legal_moves:
            move_data[move] = self.rate_move(board, move, True)
        
        highest = move_data[max(move_data, key=move_data.get)]

        return random.choice([move for move, value in move_data.items() if value == highest])

    
    def rate_move(
            self: typing.Self,
            board: chess.Board,
            move: chess.Move,
            search: bool = True
        ) -> int:
        if board.is_capture(move):
            return 3
        
        if search:
            board.push(move)

            for search in board.legal_moves:
                ranking = self.rate_move(board, search, False)

                if ranking == 3:
                    board.pop()

                    return 2
            
            board.pop()

        rank = move.to_square // 8 + 1

        if board.turn:
            # White.
            return rank / 8 + 1
        else:
            # Black.
            return (8 - rank) / 8 + 1