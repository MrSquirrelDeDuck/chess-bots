import typing
import chess
import copy
import random

import base

class MoveCount(base.ChessBot):
    name = "move_count"
    creator = "Duck"
    description = "Tries to maximize the amount of moves it has."
    color = 0x1e4b70

    def count_moves(
            self: typing.Self,
            board: chess.Board,
            side: bool
        ) -> int:
        if board.turn == side:
            return len(list(board.legal_moves))

        board.push(chess.Move.null())
        amt = len(list(board.legal_moves))
        board.pop()
        return amt

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        try:
            board_copy = copy.deepcopy(board)

            side = board.turn

            amounts = {}

            for move in board.legal_moves:
                board_copy.push(move)
                if board_copy.is_checkmate():
                    return move
                # If the game is over, but it's not checkmate.
                if board_copy.is_game_over():
                    continue
                
                track = []
                
                for depth_move in board_copy.legal_moves:
                    board_copy.push(depth_move)
                    track.append(self.count_moves(board_copy, side))

                    board_copy.pop()

                board_copy.pop()

                if len(track) == 0:
                    track = [0]

                amounts[move] = min(track)
            
            if len(amounts) == 0:
                return random.choice(list(board.legal_moves))

            play = max(amounts, key=amounts.get)
            board.push(play)

            board.pop()
            
            return play
        except AssertionError:
            return random.choice(list(board.legal_moves))