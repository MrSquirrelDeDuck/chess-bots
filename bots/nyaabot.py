import typing
import chess
import copy
import random
import math

import base

class NyaaBot(base.ChessBot):
    name = "nyaabot"
    description = """Basic chess skills. Nyaaaaa ^w^"""
    creator = "ph03n1x"
    color = 0xacfffc

    PHO_DIST_CAP = 10**0.5 # If a piece is at least this close to the king, cap the reward gain.
    PHO_FORCED_EP = True # Take en passant if possible.
    PHO_BEST_BY_TEST = True # Premove e4/e5.
    PHO_PIECE_VALUES = [1,3,3,5,9,3] # For use in distance calc. P,N,B,R,Q,K

    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:

        # Uncomment this to see the board before every move.
        # print(board)
        # print()



        if board.ply() == 0 and self.PHO_BEST_BY_TEST == True:
            return chess.Move(chess.E2,chess.E4)
        elif board.ply() == 1 and self.PHO_BEST_BY_TEST == True:
            return chess.Move(chess.E7,chess.E5)
        
        if board.has_legal_en_passant() and self.PHO_FORCED_EP:
            for move in board.legal_moves:
                if chess.Board.is_en_passant(board, move):
                    # print("HOLY HELL!")
                    return move

        check_moves = []
        cap_moves = []

        board_copy = copy.deepcopy(board)
        for move in board.legal_moves:
            if board.gives_check(move) and self.check_SanityCheck(board, move.to_square, move) == True: # Is it a sane check?
                check_moves.append(move) 
                board_copy.push(move) 
                if board_copy.is_checkmate(): # If it is mate, then play it now.
                    return move
                board_copy.pop()
            if board.is_capture(move) and self.capture_SanityCheck(board, move.from_square, move.to_square, move) == True: # If it is not check, check if it is a capture.
                cap_moves.append(move) # Note any captures.            

        # Step 2: If no mate exists, Check the king

        # if len(check_moves) != 0:
        #     return random.choice(check_moves)

        # Step 3: ...and if that can't happen, Capture a piece

        # if len(cap_moves) != 0:
        #     return random.choice(cap_moves)

        moveEvalDict = {}

        # Evaluation time!
        for move in board.legal_moves:
            moveEvalDict[move] = 0
            if move in check_moves:
                moveEvalDict[move] = moveEvalDict[move] + 0
            if move in cap_moves:
                moveEvalDict[move] = moveEvalDict[move] + self.getPieceValue(board, move.to_square)                
            moveEvalDict[move] = moveEvalDict[move] - self.ratePieceDistFromKing(board_copy, board.turn, move)
            moveEvalDict[move] = moveEvalDict[move] + self.attackVulnerableSquares(board_copy, board.turn, move)
            moveEvalDict[move] = moveEvalDict[move] + self.rateKingSafety(board_copy, board.turn, move)
            moveEvalDict[move] = moveEvalDict[move] + (self.pawnAdvancement(board_copy, board.turn, move))*0.5   
            moveEvalDict[move] = moveEvalDict[move] - self.checkYourselfDontWreckYourself(board_copy, board.turn, move)
            if self.move_Draws(board, move):
                moveEvalDict[move] = moveEvalDict[move] - 1000 # Must be stalemate or fivefold repetition.
            if self.move_blundersMate(board, move):
                moveEvalDict[move] = moveEvalDict[move] - 93258468905632490863452

        highValMove = max(moveEvalDict, key=moveEvalDict.get)
        board_copy.push(highValMove) 
        highVal = moveEvalDict.get(highValMove)
        board_copy.pop()
        if len([k for k, v in moveEvalDict.items() if v == highVal]) == 0:
            print("Oh shit!")

        # print(moveEvalDict)
        # print("Cap moves:", cap_moves)
        # print("Check moves:", check_moves)
        # print("The high val move is", highValMove, "with a value of", highVal)
        # print("Possible moves:", [k for k, v in moveEvalDict.items() if v == highVal])
        return random.choice([k for k, v in moveEvalDict.items() if v == highVal])
            


    # Functions for use in turn().

    def helper_numToSquare(self, boardNum: int): # Must input an integer.
        if boardNum < 0 or boardNum >= 64:
            # print("Illegal input made.")
            return None       
        return [(boardNum // 8)+1,boardNum % 8+1]
    
    def helper_squareToNum(self, boardNum: list): # Must input a list.
        if not isinstance(boardNum, list):
            # print("Illegal input made.")
            return None       
        return (boardNum[0]-1)*8+(boardNum[1]-1)

    def ratePieceDistFromKing(self, thisBoard, color, move):
        # For now, all pieces' distance from the king will be judged.
        # It should be fairly easy to adjust this so that a piece type is ignored later.
        chess.Board.push(thisBoard, move)
        thisBoard.turn = color # To fix whose turn it is
        sumDist = 0
        totalPieces = 0
        for piece in chess.PIECE_TYPES:
            listPieces = list(thisBoard.pieces(piece, thisBoard.turn))
            for item in listPieces:
                if chess.Board.piece_type_at(thisBoard, item) == chess.KING or chess.Board.piece_type_at(thisBoard, item) == chess.PAWN:
                    continue # The king should stay away from pieces. Pawns use a more complex system.
                pieceDist = math.dist(self.helper_numToSquare(item),self.helper_numToSquare(thisBoard.king(not thisBoard.turn)))
                # print("Distance of the", chess.square_name(item), chess.Board.piece_type_at(thisBoard, item), "is", pieceDist)
                if pieceDist < (self.PHO_DIST_CAP):
                    sumDist += (self.PHO_DIST_CAP) * self.getPieceValue(thisBoard, item)
                else:
                    sumDist += pieceDist * self.getPieceValue(thisBoard, item)
                totalPieces += 1 * self.getPieceValue(thisBoard, item)
        if totalPieces == 0:
            chess.Board.pop(thisBoard)           
            return 8
        chess.Board.pop(thisBoard)    
        # print(totalPieces)
        # print(sumDist)
        # print()
        return sumDist/totalPieces
    
    def rateKingSafety(self, thisBoard, color, move):
        chess.Board.push(thisBoard, move)
        thisBoard.turn = color # To fix whose turn it is
        sumDist = 0
        totalPieces = 0
        for piece in chess.PIECE_TYPES:
            listPieces = list(thisBoard.pieces(piece, not thisBoard.turn))
            for item in listPieces:
                if chess.Board.piece_type_at(thisBoard, item) == chess.KING or chess.Board.piece_type_at(thisBoard, item) == chess.PAWN:
                    continue # The king should stay away from pieces. Pawns use a more complex system.
                pieceDist = math.dist(self.helper_numToSquare(item),self.helper_numToSquare(thisBoard.king(thisBoard.turn)))
                # print("Distance of the", chess.square_name(item), chess.Board.piece_type_at(thisBoard, item), "is", pieceDist)
                if pieceDist < (self.PHO_DIST_CAP):
                    sumDist += (self.PHO_DIST_CAP) * self.getPieceValue(thisBoard, item)
                else:
                    sumDist += pieceDist * self.getPieceValue(thisBoard, item)
                totalPieces += 1 * self.getPieceValue(thisBoard, item)
        if totalPieces == 0:
            chess.Board.pop(thisBoard)           
            return 8
        chess.Board.pop(thisBoard)    
        # print(totalPieces)
        # print(sumDist)
        # print()
        return sumDist/totalPieces
    
    def pawnAdvancement(self, thisBoard, color, move):
        pushPoints = 0
        if move.promotion != None:
            if move.promotion != chess.QUEEN:
                return 0
            else:
                return 10.5
        chess.Board.push(thisBoard, move)
        thisBoard.turn = color # To fix whose turn it is
        listPieces = list(thisBoard.pieces(chess.PAWN, thisBoard.turn))
        for square in listPieces:
            if thisBoard.turn == chess.WHITE:
                promotionPoints = 0.05*(chess.square_rank(square)**1.5) # 0 to 0.73 points
                kingPenalty = -0.15*math.dist(self.helper_numToSquare(square),self.helper_numToSquare(thisBoard.king(not thisBoard.turn)))
            else: # it's black's move.
                promotionPoints = 0.05*((-chess.square_rank(square)+7)**1.5) # 0 to 0.73 points
                kingPenalty = -0.15*math.dist(self.helper_numToSquare(square),self.helper_numToSquare(thisBoard.king(not thisBoard.turn)))
            promotionPoints *= (-abs(chess.square_file(square)-3.5)+3.5)*0.25+0.5 # Encourage center pawn development
            pushPoints += promotionPoints + kingPenalty
        thisBoard.pop()
        return pushPoints           
    
    def attackVulnerableSquares(self, thisBoard, color, move):
        # print("Considering move", move)
        chess.Board.push(thisBoard, move)
        thisBoard.turn = color # To fix whose turn it is
        listAttacking = list(chess.Board.attacks(thisBoard, thisBoard.king(not thisBoard.turn)))
        listNumAttacking = []
        # print(listAttacking)
        for square in listAttacking:
            if len(chess.Board.attackers(thisBoard, not thisBoard.turn, square)) == 1: # Must only be the king then
                listNumAttacking.append(len(chess.Board.attackers(thisBoard, thisBoard.turn, square)))
                # print("There are", len(chess.Board.attackers(thisBoard, thisBoard.turn, square)), "attackers on square", square)
            else:
                listNumAttacking.append(0)
        thisBoard.pop()
        # print("There are", listNumAttacking, "attackers.")
        # print()
        if max(listNumAttacking) == 0:
            return 0
        elif max(listNumAttacking) == 1:
            return 0.25
        else:
            return (0.5 + max(listNumAttacking) * 0.25)
        
    def check_SanityCheck(self, thisBoard, square, move): # TODO: Convert this to inputting a move.
        # print("Checking if this move is sane:", move)
        if isinstance(square, list):
            opSquare = self.helper_squareToNum(square)
        elif isinstance(square, int):
            opSquare = square
        else:
            # print("Illegal square input.")
            return False
        if self.move_Draws(thisBoard, move):
            return False
        chess.Board.push(thisBoard, move)
        if not(self.pieceIsEndangered(thisBoard, not thisBoard.turn, opSquare)):
            chess.Board.pop(thisBoard)
            return True
        chess.Board.pop(thisBoard)
        if list(chess.Board.attackers(thisBoard, not thisBoard.turn, square)) == [(thisBoard.king(not thisBoard.turn))]:
            if len(chess.Board.attackers(thisBoard, thisBoard.turn, square)) > 1:
                # print(chess.Board.attackers(thisBoard, thisBoard.turn, square))
                return True
        # print("Nope")
        return False
    
    def checkYourselfDontWreckYourself(self, thisBoard, color, move):
        # print("Checking sanity of move", move)
        chess.Board.push(thisBoard, move)
        thisBoard.turn = color # To fix whose turn it is    
        penalty = 0
        for piece in chess.PIECE_TYPES:
            listPieces = list(thisBoard.pieces(piece, thisBoard.turn))
            for square in listPieces:
                if chess.Board.piece_type_at(thisBoard, square) == chess.KING:
                    continue
                else:
                    if self.pieceIsEndangered(thisBoard, thisBoard.turn, square):
                        # print("The piece at", chess.square_name(square), "is endangered.")
                        # For each attacker, perform sanity check.
                        # If at least one can sanely capture, administer penalty.
                        thisBoard.turn = not color
                        for i in chess.Board.attackers(thisBoard, not color, square):
                            if not(chess.Board.is_legal(thisBoard, chess.Move(i, square))):
                                # print(chess.Board.is_legal(thisBoard, chess.Move(i, square)))
                                # print(chess.Move(i, square), "is illegal.")
                                continue
                            # print("Attacker id", i, "trying to take on", square)
                            if self.capture_SanityCheck(thisBoard, i, square, chess.Move(i, square)) or self.move_Draws(thisBoard, chess.Move(i, square)):
                                # print("Penalty applied, as a piece from square name", i, "can take.")
                                penalty = penalty + 0.5 + self.getPieceValue(thisBoard, square)
                                break
                        thisBoard.turn = color
        chess.Board.pop(thisBoard)
        return penalty
    
    def capture_SanityCheck(self, thisBoard, fromSquare, toSquare, move): # TODO: Convert this to inputting a move.
        if isinstance(fromSquare, list):
            opFromSquare = self.helper_squareToNum(fromSquare)
        elif isinstance(fromSquare, int):
            opFromSquare = fromSquare
        else:
            # print("Illegal from square input.")
            return False
        if isinstance(toSquare, list):
            opToSquare = self.helper_squareToNum(toSquare)
        elif isinstance(toSquare, int):
            opToSquare = toSquare
        else:
            # print("Illegal to square input.")
            return False
        if self.move_Draws(thisBoard, move):
            # print("This move is stupid.")
            return False
        chess.Board.push(thisBoard, move)
        if not(self.pieceIsEndangered(thisBoard, not thisBoard.turn, opToSquare)): # TODO: ugh
            # print(opToSquare, "is safe.")
            chess.Board.pop(thisBoard)
            return True
        else:
            chess.Board.pop(thisBoard)
            if self.getPieceValue(thisBoard, opFromSquare) <= self.getPieceValue(thisBoard, opToSquare):
                # print("Attacked > Attacker")
                return True
            else:
                # print("Attacker > Attacked")
                return False
        
    def pieceIsEndangered(self, thisBoard, color, square):
        thisBoard.turn = color # To fix whose turn it is
        # print(square)
        # print(color)
        if not(chess.Board.is_attacked_by(thisBoard, not thisBoard.turn, square)):
            return False
        candidates = list(chess.Board.attackers(thisBoard, not thisBoard.turn, square))
        # print(candidates)
        for i in candidates:
            if chess.Board.is_pinned(thisBoard, not thisBoard.turn, i):
                thisBoard.turn = not color
                if not(chess.Board.is_legal(thisBoard, chess.Move(i, square))):
                    candidates.remove(i)
                thisBoard.turn = color
        if len(candidates) == 0:
            return False
        if candidates == [(thisBoard.king(not thisBoard.turn))]:
            # print("It's the king!")
            if len(chess.Board.attackers(thisBoard, thisBoard.turn, square)) > 0:
                return False
        # print(candidates)
        return True

    def getPieceValue(self, thisBoard, square):
        if chess.Board.piece_type_at(thisBoard, square) == chess.PAWN:
            return self.PHO_PIECE_VALUES[0]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.KNIGHT:
            return self.PHO_PIECE_VALUES[1]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.BISHOP:
            return self.PHO_PIECE_VALUES[2]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.ROOK:
            return self.PHO_PIECE_VALUES[3]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.QUEEN:
            return self.PHO_PIECE_VALUES[4]
        elif chess.Board.piece_type_at(thisBoard, square) == chess.KING:
            return self.PHO_PIECE_VALUES[5]
        else:
            return 0

    def move_Draws(self, thisBoard, move):
        board_copy_HFD = copy.deepcopy(thisBoard)
        chess.Board.push(board_copy_HFD, move)
        if chess.Board.outcome(board_copy_HFD, claim_draw=True) != None and chess.Board.is_checkmate(board_copy_HFD) == False:
            return True
        else:
            return False
        
    def move_blundersMate(self, thisBoard, move):
        board_copy_HFD = copy.deepcopy(thisBoard)
        chess.Board.push(board_copy_HFD, move)
        for i in board_copy_HFD.legal_moves:
            chess.Board.push(board_copy_HFD, i)
            if chess.Board.is_checkmate(board_copy_HFD):
                chess.Board.pop(board_copy_HFD)
                chess.Board.pop(board_copy_HFD)                
                return True
            chess.Board.pop(board_copy_HFD)
        return False