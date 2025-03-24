import typing
import chess
import random

import base

class RobertoBot(base.ChessBot):
	name = "roberto_bot"
	description = """A python version of my Roberto bot (https://github.com/lythd/Robertoct.ChessBot) that placed 293/624 in Sebastians competition. Don't look at my code there please its genuinely embarassing."""
	creator = "Booby"

	HP = 1.2
	ATK = 4.0
	DEF = 1.0
	SPD = 0.4
	DEX = 0.3

	def turn(
			self: typing.Self,
			board: chess.Board,
			depth = 2
		) -> chess.Move:
		
		best_move = None
		best_value = -float('inf') if board.turn else float('inf')

		for move in board.legal_moves:
			board.push(move)
			board_value = self.search(board, depth, -float('inf'), float('inf'), not board.turn)
			board.pop()

			if board.turn and board_value > best_value:
				best_value = board_value
				best_move = move
			elif not board.turn and board_value < best_value:
				best_value = board_value
				best_move = move

		return best_move
		
		
	def evaluate_board(self, board):
		if board.is_checkmate():
			if board.turn:
				return -9999
			else:
				return 9999
		elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
			return 0

		return self.base_eval(board, board.turn) + self.base_eval(board, not board.turn) # one would be negative from being black so we do want to add them here
		#material = sum([self.piece_value(piece) for piece in board.piece_map().values()])
		#return material

	#def piece_value(self, piece):
	#	values = {
	#	chess.PAWN: 100,
	#	chess.KNIGHT: 320,
	#	chess.BISHOP: 330,
	#	chess.ROOK: 500,
	#	chess.QUEEN: 900,
	#	chess.KING: 20000
	#	}
	#	return values[piece.piece_type] if piece.color == chess.WHITE else -values[piece.piece_type]

	def search(self, board, depth, alpha, beta, maximizing_player):
		if depth == 0 or board.is_game_over():
			return self.evaluate_board(board)

		legal_moves = list(board.legal_moves)
		
		if maximizing_player:
			max_eval = -float('inf')
			for move in legal_moves:
				board.push(move)
				eval = self.search(board, depth - 1, alpha, beta, False)
				board.pop()
				max_eval = max(max_eval, eval)
				alpha = max(alpha, eval)
				if beta <= alpha:
					break
			return max_eval
		else:
			min_eval = float('inf')
			for move in legal_moves:
				board.push(move)
				eval = self.search(board, depth - 1, alpha, beta, True)
				board.pop()
				min_eval = min(min_eval, eval)
				beta = min(beta, eval)
				if beta <= alpha:
					break
		return min_eval
	
	def base_eval(self, board, white):
		"""
		 * Eval Explained
		 * 
		 * Pretty much everyone is going to have the same minimax searching and stuff, so in order to win I need to focus on the
		 * eval. You can just do the trivial thing of using the known average material values, but that is kind of lame, and also
		 * just ignores a lot of things that can make positions better or worse. You can do what you did and have like tables of
		 * good squares and such. But I thought this skips the most obvious thing, why not just see how good the pieces are for
		 * myself? So yeah I'm not putting on any of my values for pieces, here we will just see how valuable they are. Also
		 * with some slight modifications I imagine this will let you calculate how good pieces are in a game which is cool.
		 * 
		 * Anyways so on to what I ended up doing. I calculated 5 stats, hp is the amount of pieces you have, honestly not really
		 * important I just thought it fit the theme and its short enough to add, attack is the amount of squares you attack
		 * (this includes squares you attack multiple times), defense is the amount of squares you defend, speed is the amount
		 * of squares you can move without capture to (useful for seeing squares you control, or have the potential to capture on),
		 * and finally dexterity is the amount of squares you could move to if there were no other pieces on the board (useful
		 * to see if it's a useful piece, and if it's in a useful spot).
		 * 
		 * Then I just did a bit of trial and error to find the best weights for combining them. And then well combined them.
		 * Also you will see when I use this function I calculate both black and white and subtract them. As a move might give you
		 * a good position but your opponent an even better one. And just a general note this isn't normalised, so the eval this
		 * gives is not directly comparable to a typical eval, I guess you'd have to take the average eval difference of a bunch
		 * of positions with and without a random pawn and use that to scale it.
		 *
		 * Yes I just copied this message I am not even gonna bother reading this message again.
		 * 
		"""
		
		boardturn = board.turn # not sure if it clones or not but just resetting just incase, and not sure if this even matters but idcccc i just want this to work
		board.turn = white
		
		hp = 0
		attack = 0
		defense = 0
		speed = 0
		dexterity = 0

		friendly_squares = board.occupied_co[white]
		#print("friendly_squares:", bin(friendly_squares)[2:])
		enemy_squares = board.occupied_co[not white]
		#print("enemy_squares:", bin(enemy_squares)[2:])

		pieces = {
			chess.PAWN: list(board.pieces(chess.PAWN, white)),
			chess.KNIGHT: list(board.pieces(chess.KNIGHT, white)),
			chess.BISHOP: list(board.pieces(chess.BISHOP, white)),
			chess.ROOK: list(board.pieces(chess.ROOK, white)),
			chess.QUEEN: list(board.pieces(chess.QUEEN, white)),
			chess.KING: list(board.pieces(chess.KING, white))[0]
		}


		hp = (len(pieces[chess.PAWN]) +
			  3 * len(pieces[chess.KNIGHT]) +
			  3 * len(pieces[chess.BISHOP]) +
			  5 * len(pieces[chess.ROOK]) +
			  9 * len(pieces[chess.QUEEN]))

		for square in pieces[chess.PAWN]:
			pawn_attacks = board.attacks(square)
			#print(f"pawn, attack: {bin(pawn_attacks & enemy_squares).count('1')}, defense: {bin(pawn_attacks & friendly_squares).count('1')}, speed: {bin(pawn_attacks & ~enemy_squares & ~friendly_squares).count('1')}, dexterity: {bin(pawn_attacks).count('1')}")
			attack += bin(pawn_attacks & enemy_squares).count('1')
			defense += bin(pawn_attacks & friendly_squares).count('1')
			speed += bin(pawn_attacks & ~enemy_squares & ~friendly_squares).count('1')
			dexterity += bin(pawn_attacks).count('1')

		for square in pieces[chess.KNIGHT]:
			knight_attacks = board.attacks(square)
			#print(f"knight, attack: {bin(knight_attacks & enemy_squares).count('1')}, defense: {bin(knight_attacks & friendly_squares).count('1')}, speed: {bin(knight_attacks & ~enemy_squares & ~friendly_squares).count('1')}, dexterity: {bin(knight_attacks).count('1')}")
			attack += bin(knight_attacks & enemy_squares).count('1')
			defense += bin(knight_attacks & friendly_squares).count('1')
			speed += bin(knight_attacks & ~enemy_squares & ~friendly_squares).count('1')
			dexterity += bin(knight_attacks).count('1')

		for square in pieces[chess.BISHOP]:
			bishop_attacks = board.attacks(square)
			#print(f"bishop, attack: {bin(bishop_attacks & enemy_squares).count('1')}, defense: {bin(bishop_attacks & friendly_squares).count('1')}, speed: {bin(bishop_attacks & ~enemy_squares & ~friendly_squares).count('1')}, dexterity: {bin(bishop_attacks).count('1')}")
			attack += bin(bishop_attacks & enemy_squares).count('1')
			defense += bin(bishop_attacks & friendly_squares).count('1')
			speed += bin(bishop_attacks & ~enemy_squares & ~friendly_squares).count('1')
			dexterity += bin(bishop_attacks).count('1')

		for square in pieces[chess.ROOK]:
			rook_attacks = board.attacks(square)
			#print(f"rook, attack: {bin(rook_attacks & enemy_squares).count('1')}, defense: {bin(rook_attacks & friendly_squares).count('1')}, speed: {bin(rook_attacks & ~enemy_squares & ~friendly_squares).count('1')}, dexterity: {bin(rook_attacks).count('1')}")
			attack += bin(rook_attacks & enemy_squares).count('1')
			defense += bin(rook_attacks & friendly_squares).count('1')
			speed += bin(rook_attacks & ~enemy_squares & ~friendly_squares).count('1')
			dexterity += bin(rook_attacks).count('1')

		for square in pieces[chess.QUEEN]:
			queen_attacks = board.attacks(square)
			#print(f"queen, attack: {bin(queen_attacks & enemy_squares).count('1')}, defense: {bin(queen_attacks & friendly_squares).count('1')}, speed: {bin(queen_attacks & ~enemy_squares & ~friendly_squares).count('1')}, dexterity: {bin(queen_attacks).count('1')}")
			attack += bin(queen_attacks & enemy_squares).count('1')
			defense += bin(queen_attacks & friendly_squares).count('1')
			speed += bin(queen_attacks & ~enemy_squares & ~friendly_squares).count('1')
			dexterity += bin(queen_attacks).count('1')

		king_square = pieces[chess.KING]
		king_attacks = board.attacks(king_square)
		#print(f"king, attack: {bin(king_attacks & enemy_squares).count('1')}, defense: {bin(king_attacks & friendly_squares).count('1')}, speed: {bin(king_attacks & ~enemy_squares & ~friendly_squares).count('1')}, dexterity: {bin(king_attacks).count('1')}")
		attack += bin(king_attacks & enemy_squares).count('1')
		defense += bin(king_attacks & friendly_squares).count('1')
		speed += bin(king_attacks & ~enemy_squares & ~friendly_squares).count('1')
		dexterity += bin(king_attacks).count('1')

		eval_score = (hp * RobertoBot.HP +
					  attack * RobertoBot.ATK +
					  defense * RobertoBot.DEF +
					  speed * RobertoBot.SPD +
					  dexterity * RobertoBot.DEX)

		#print(f"hp: {hp*RobertoBot.HP}, attack: {attack*RobertoBot.ATK}, defense: {defense*RobertoBot.DEF}, speed: {speed*RobertoBot.SPD}, dexterity: {dexterity*RobertoBot.DEX}")

		if board.fullmove_number < 5:
			eval_score *= random.uniform(0.95, 1.05)  # for opening spice

		board.turn = boardturn

		return eval_score * (1.0 if white else -1.0)