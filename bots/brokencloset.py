import typing
import chess
import math
import random
import copy

import base

class BrokenCloset(base.ChessBot):
    name = "brokencloset"
    description = """Tries to put its king as close as possible to his boyfriend: The enemy king."""
    creator = "ph03n1x"
    color = 0x078d70

    BC_DIST_CAP = 0 # Adjust this if the bot seems to prioritize getting to the enemy king *too* much.

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:

        # Uncomment this to see the board before every move.
        # print(board)
        # print()

        if board.ply() == 0:
            return chess.Move(chess.E2,chess.E4)
        elif board.ply() == 1:
            return chess.Move(chess.E7,chess.E5)
        
        board_copy = copy.deepcopy(board)
        moveDict = {}

        for move in board.legal_moves:
            board_copy.push(move) 
            moveDict[move] = self.rateDistFromKing(board_copy, board.turn)
            board_copy.pop()

        lowValMove = min(moveDict, key=moveDict.get)
        board_copy.push(lowValMove) 
        lowVal = self.rateDistFromKing(board_copy, board.turn)
        board_copy.pop()
        return random.choice([k for k, v in moveDict.items() if v == lowVal])

    # Functions for use in turn().

    def helper_numToSquare(self, boardNum): # Must input an integer.
        if boardNum < 0 or boardNum >= 64:
            # print("Illegal input made.")
            return None       
        return [(boardNum // 8)+1,boardNum % 8+1]
    
    def helper_squareToNum(self, boardNum): # Must input a list.
        if type(boardNum) != list:
            # print("Illegal input made.")
            return None       
        return (boardNum[0]-1)*8+(boardNum[1]-1)

    def rateDistFromKing(self, thisBoard, color):
        # For now, all pieces' distance from the king will be judged.
        # It should be fairly easy to adjust this so that a piece type is ignored later.

        thisBoard.turn = color
        if thisBoard.king(thisBoard.turn) == None or thisBoard.king(not thisBoard.turn) == None:
            # print("A king is missing.")
            return 0
        pieceDist = math.dist(self.helper_numToSquare(thisBoard.king(thisBoard.turn)),self.helper_numToSquare(thisBoard.king(not thisBoard.turn)))
        if pieceDist < (self.BC_DIST_CAP): # Replace 13**0.5 with the highest distance you want to matter.
            return self.BC_DIST_CAP
        else:
            return pieceDist