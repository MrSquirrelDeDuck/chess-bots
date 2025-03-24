import typing
import chess
import copy
import random

import base

class RandomCheckmate(base.ChessBot):
    name = "random_checkmate"
    description = """The same as `random`, but if it has mate in 1 it will play it."""
    creator = "Duck"
    color = 0x43cc2e

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        # First, create a copy of the board, so we're not messing with the passed board.
        board_copy = copy.deepcopy(board)

        # Go through each move, play it on the board, check if it's checkmate.
        # If the move is checkmate, just return it. If it's not checkmate, use board.pop() to unplay it.
        for move in board_copy.legal_moves:
            board_copy.push(move)
            
            if board_copy.is_checkmate():
                board_copy.pop()
                return move
            
            board_copy.pop()
        
        # If a checkmate in 1 was not found, resort to the regular random bot.
        
        piece_moves = {}
        
        # Go through all the legal moves the bot has, and mark down each move with the square it start from.
        # Moves by the same piece will start on the same square, so this gets the moves each piece has.
        for move in board.legal_moves:
            from_square = move.from_square
            
            # If the square is in the dictionary, append the move to the list there,
            # if it isn't, add the move to the dictionary with a new list containing the move.
            if from_square in piece_moves:
                piece_moves[from_square].append(move)
            else:
                piece_moves[from_square] = [move]
        
        # The values of the dictionary are the lists of moves, so by choosing a random one
        # it's choosing a random piece to move. `dict.values()` returns a `dict_values` object,
        # so convert it to a list so random.choice can work.
        move_options = random.choice(list(piece_moves.values()))
        
        # move_options is a list of the available moves by the chosen piece, so
        # choosing a random one from it will be choosing a random move by that piece.
        return random.choice(move_options)
