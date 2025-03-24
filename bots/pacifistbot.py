import typing
import chess
import random
import copy

import base

class PacifistBot(base.ChessBot):
    name = "pacifistbot"
    description = """With the power of friendship I shall win!"""
    creator = "ph03n1x"
    color = 0xdddddd

    PAC_PIECE_VALUES = [1,3,3,5,9,3] # For use in distance calc. P,N,B,R,Q,K

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:

        board_copy = copy.deepcopy(board)
        moveDict = {}

        for move in board.legal_moves:
            moveDict[move] = self.ratePacifism(move, board_copy, board.turn)

        # Uncomment this to see the board before every move.
        # print(board)
        # print()

        highValMove = max(moveDict, key=moveDict.get)
        highVal = self.ratePacifism(highValMove, board_copy, board.turn)
        return random.choice([k for k, v in moveDict.items() if v == highVal])
            
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

    def ratePacifism(self, move, thisBoard, color):
        # For now, all pieces' distance from the king will be judged.
        # It should be fairly easy to adjust this so that a piece type is ignored later.

        thisBoard.turn = color
        sumDist = 0
        totalPieces = 0
        thisBoard.push(move) 
        if chess.Board.is_checkmate(thisBoard):
            thisBoard.pop()
            return -93258468905632490863452
        if chess.Board.is_check(thisBoard):
            checkCount = len(chess.Board.checkers(thisBoard))
            thisBoard.pop()
            return -5000*checkCount
        else:
            thisBoard.pop()
        if chess.Board.is_en_passant(thisBoard, move):
            return -100
        if chess.Board.is_capture(thisBoard, move):
            return -100*self.getPieceValue(thisBoard, move.to_square)
        return 0
        
    def getPieceValue(self, thisBoard, square):
        if chess.Board.piece_type_at(thisBoard, square) == chess.PAWN:
            return self.PAC_PIECE_VALUES[0]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.KNIGHT:
            return self.PAC_PIECE_VALUES[1]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.BISHOP:
            return self.PAC_PIECE_VALUES[2]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.ROOK:
            return self.PAC_PIECE_VALUES[3]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.QUEEN:
            return self.PAC_PIECE_VALUES[4]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.KING:
            return self.PAC_PIECE_VALUES[5]
        else:
            # print("The square is empty.", square)
            return 0