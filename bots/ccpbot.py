import typing
import chess
import copy
import random
import math

import base

class CCPBot(base.ChessBot):
    name = "ccpbot"
    description = """BORN TO BLUNDER / TOURNAMENT IS A FUCK / 將死 Capture Em All 1989 / I am martin / 410,757,864,530 HUNG QUEENS"""
    creator = "ph03n1x"
    color = 0xde2810

    CCP_DIST_CAP = 5**0.5 # Adjust this to ensure pieces don't get TOO close.
    CCP_PIECE_VALUES = [1,3,3,9,5,5]
    CCP_FORCED_EP = True
    # CCP_PIECE_VALUES = [1,3,3,10,0.25,5]

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:

        # Uncomment this to see the board before every move.
        # print(board)
        # print()

        # This bot has the following priorities:
        # Priority 1: Checkmate
        # Priority 2: Deliver a check
        # Priority 3: Capture a piece
        # Priority 4: Push a piece closer to the king.

        # First, classify all the moves, and while doing so:
        # Step 1: If you find a checkmate, play it immediately.

        if board.has_legal_en_passant() and self.CCP_FORCED_EP:
            for move in board.legal_moves:
                if chess.Board.is_en_passant(board, move):
                    return move

        check_moves = []
        cap_moves = []

        board_copy = copy.deepcopy(board)
        for move in board.legal_moves:
            if board.gives_check(move): # Is it a check?
                check_moves.append(move) # If so, note the move as a check, then scan for mate.
                board_copy.push(move) 
                if board_copy.is_checkmate(): # If it is mate, then play it now.
                    return move
                board_copy.pop()
            if board.is_capture(move): # If it is not check, check if it is a capture.
                cap_moves.append(move) # Note any captures.            

        # Step 2: If no mate exists, Check the king

        # Step 3: ...and if that can't happen, Capture a piece

        if len(cap_moves) != 0:
            return random.choice(cap_moves)
        
        if len(check_moves) != 0:
            return random.choice(check_moves)

        # Step 4: ...and if that can't happen, Push a piece closer to the enemy king.

        # All potential future boards will be assigned a "rating" value for average
        # distance from the enemy1 king with dist(). Lower is better.
        
        # return random.choice(list(board.legal_moves))

        moveDict = {}

        for move in board.legal_moves:
            board_copy.push(move) 
            moveDict[move] = self.rateDistFromKing(board_copy, board.turn)
            board_copy.pop()

        return min(moveDict, key=moveDict.get)
            


    # Functions for use in turn().

    def helper_numToSquare(self, boardNum): # Must input an integer.
        if boardNum < 0 or boardNum >= 64:
            return None       
        return [(boardNum // 8)+1,boardNum % 8+1]

    def rateDistFromKing(self, thisBoard, color):
        # For now, all pieces' distance from the king will be judged.
        # It should be fairly easy to adjust this so that a piece type is ignored later.

        thisBoard.turn = color
        sumDist = 0
        totalPieces = 0
        for piece in chess.PIECE_TYPES:
            # if piece == chess.KING:
                # continue
            listPieces = list(thisBoard.pieces(piece, thisBoard.turn))
            for item in listPieces:
                rawDist = math.dist(self.helper_numToSquare(item),self.helper_numToSquare(thisBoard.king(not thisBoard.turn)))
                if rawDist <= self.CCP_DIST_CAP:
                    sumDist += (self.CCP_DIST_CAP) * self.getPieceValue(thisBoard, item)
                else:
                    sumDist += rawDist * self.getPieceValue(thisBoard, item)
                totalPieces += 1 * self.getPieceValue(thisBoard, item)
        if totalPieces == 0:
            # Should only fire if the king is the only piece.
            return 0
        return sumDist/totalPieces
    
    def getPieceValue(self, thisBoard, square):
        if chess.Board.piece_type_at(thisBoard, square) == chess.PAWN:
            return self.CCP_PIECE_VALUES[0]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.KNIGHT:
            return self.CCP_PIECE_VALUES[1]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.BISHOP:
            return self.CCP_PIECE_VALUES[2]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.ROOK:
            return self.CCP_PIECE_VALUES[3]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.QUEEN:
            return self.CCP_PIECE_VALUES[4]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.KING:
            return self.CCP_PIECE_VALUES[5]
        else:
            return 0