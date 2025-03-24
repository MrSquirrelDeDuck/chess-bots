import chess
import random
import typing
import copy
import abc
import time
import math
import importlib
import os

all_bots = {}
bot_modules = {}
_module_files = {}

try:
    all_games = open("data/Games.txt") # Sourced from https://github.com/SebLague/Chess-Coding-Adventure/blob/Chess-V1-Unity/Assets/Book/Games.txt
    lines = all_games.readlines()
except FileNotFoundError:
    raise FileNotFoundError("The file `data/Games.txt` was not found.")

#############################################################################################################
#############################################################################################################
#############################################################################################################

class ChessBot(abc.ABC):
    """Base class for Chess bots."""
    
    # General information about the bot.
    name = "generic_bot" # The name of the bot, this is what the bot is referred to as. This should be all lowercase.
    description = """Generic Chess bot.""" # The description of the bot. This doesn't necessarily need to describe exactly how the bot works (like in the bot `tau` and `pi`,) but it can if you'd like (like in the bots `alphamove` and `giveaway`.)
    creator = "Biongo" # Whoever created this bot.
    color = 0x888888 # The color of the bot as a hex code. If possible this should be different from the other bots for clarity.

    def __init__(
            self: typing.Self,
            database_data: dict
        ) -> None:
        self.load(database_data)

    # Optional for subclasses, required if data needs to be saved between moves.
    def load(
            self: typing.Self,
            data: dict
        ) -> None:
        """Method called when the bot is initialized, and allows for the loading of data from the database."""
        pass

    # Optional for subclasses, required if data needs to be saved between moves.
    def save(self: typing.Self) -> dict | None:
        """Method called after the bot is run. The dict returned will be saved to the database.
        This allows for the saving of data between moves.
        This only gets saved if the output is a dictionary, even a list will not be saved.

        If `None` is returned then nothing will be saved."""
        return None

    # This method is required for subclasses due to being an abstractmethod.
    @abc.abstractmethod
    def turn(
            self: typing.Self,
            board: chess.Board
        ) -> chess.Move:
        """Method called when it is this bot's turn in the Chess game.

        Args:
            board (chess.Board): A copy of the current board.

        Returns:
            chess.Move: The move this bot would like to play.
        """
        raise NotImplementedError

#############################################################################################################
#############################################################################################################
#############################################################################################################

def write_pgn(board: chess.Board) -> str:
    """Writes the given board's move stack as a pgn string.
    This does require the move stack having contents, so passing a board that was set from a FEN will only return the moves that were played.
    
    >>> board = chess.Board()
    >>> board.push_san("e4")
    Move.from_uci('e2e4')
    >>> board.push_san("e5")
    Move.from_uci('e7e5')
    >>> board.push_san("Nf3")
    Move.from_uci('g1f3')
    >>> write_pgn(board)
    '1. e4 e5 2. Nf3'"""
    board_copy = board.copy()

    moves_reverse = []

    for _ in range(len(board_copy.move_stack)):
        move = board_copy.pop()
        moves_reverse.append(board_copy.san(move))

    moves = list(reversed(moves_reverse))
    moves_pgn = []

    for index in range(0, len(moves_reverse), 2):
        moves_pgn.append(f"{index // 2 + 1}. {' '.join(moves[index:index+2])}")

    return " ".join(moves_pgn)

def parse_san(san: str) -> list[str]:
    """Parses san moves and returns a list of just the moves.
    
    Example:
    >>> parse_san("1. e4 c5 2. c3 Nf6 3. e5 Nd5 4. Nf3 d6 5. d4 cxd4 6. cxd4 Nc6 7. Bc4 f5 8. exf6")
    ['e4', 'c5', 'c3', 'Nf6', 'e5', 'Nd5', 'Nf3', 'd6', 'd4', 'cxd4', 'cxd4', 'Nc6', 'Bc4', 'f5', 'exf6']
    """
    out = []
    for move in san.split(" "):
        try:
            float(move)
            continue
        except ValueError:
            out.append(move)
    return out

def get_random_moves(
        amount: int,
        seed: str | int | float | bytes | bytearray | None = None
    ) -> list[str]:
    """Gets a list of random moves from `data/Games.txt` and returns a random list of opening moves from it.
    
    If you want to force a set of opening moves have this return the output from `parse_san`."""
    return random.Random(seed).choice(copy.deepcopy(lines)).split(" ")[:amount + 1]

def run_match(
        white: ChessBot,
        black: ChessBot,
        *, # This means the following arguments must be passed as keyword arguments, so like run_match(..., variate_starting_position=True) rather than run_match(..., True)
        variate_starting_position: bool = False,
        seed: str | int | float | bytes | bytearray | None = None,
        custom_start_san: str = None,
        log_progress: bool = True,
    ) -> dict:
    """Runs a single match between the two given bots.

    Args:
        white (ChessBot): The bot playing as white.
        black (ChessBot): The bot playing as black.
        variate_starting_position (bool, optional): Whether to use a random starting position generated from the `Games.txt` file in the `data` folder. Defaults to False.
        seed (str | int | float | bytes | bytearray | None, optional): A seed to be passed when choosing the random start position, only makes a difference if variate_starting_position is True. Defaults to None.
        custom_start_san (str, optional): A string Standard Algebraic Notation moves that will be parsed and played before the bots take control,
            which can be used to start a game from a set position. This requires `variate_starting_position` to be True, but overrides `seed`. Defaults to None.
        log_progress (bool, optional): Whether to log the progress of the game as it is being played. Defaults to True.

    Returns:
        dict: The result from the game, containing the winner, the PGN of the game, and the FEN of the board at the end.
    """    
    board = chess.Board()

    if variate_starting_position:
        if custom_start_san is None:
            starting_moves = get_random_moves(amount=6, seed=seed)
        else:
            starting_moves = parse_san(custom_start_san)

        for move in starting_moves:
            board.push_san(move)

    white_data = {}
    black_data = {}

    white_obj = white(white_data) # type: ChessBot
    black_obj = black(black_data) # type: ChessBot
    
    move_number = 1
    while board.outcome() is None:
        if log_progress:
            print(f"Progress: Tick: {move_number} Ply: {board.ply()} Fullmove: {board.fullmove_number} FEN: {board.fen()}")
        if board.turn == chess.WHITE:
            white_obj.load(white_data)
            
            move = white_obj.turn(board.copy())

            white_data = white_obj.save()
        else:
            black_obj.load(black_data)
            
            move = black_obj.turn(board.copy())

            black_data = black_obj.save()
        
        board.push(move)
        move_number += 1
    
    return {
        "winner": board.outcome().winner if board.is_checkmate() else None, # If it's not a checkmate then it's a draw.
        "pgn": f"""[White "[Bot] {white_obj.name}"]\n[Black "[Bot] {black_obj.name}"]\n[Result "{board.outcome().result()}"]\n\n{write_pgn(board)} {board.outcome().result()}""",
        "fen": board.fen()
    }

def run_bulk(
        bot_1: ChessBot,
        bot_2: ChessBot,
        amount: int = 1000,
        *, # This means the following arguments must be passed as keyword arguments, so like run_bulk(..., variate_starting_positions=True) rather than run_bulk(..., True)
        variate_starting_positions: bool = False,
        seeded_positions: bool = True,
        fancy_formatting: bool = True
    ) -> dict:
    """Runs a series of matches between two bots and returns the results.

    Args:
        bot_1 (ChessBot): The class for the bot first bot.
        bot_2 (ChessBot): The class for the second bot.
        amount (int, optional): The number of games to run. Defaults to 1000.
        variate_starting_positions (bool, optional): Whether to use random starting positions. Defaults to False.
        seeded_positions (bool, optional): Whether to use a seed for the starting positions,
            so running this multiple times will have the same starting positions. This only makes a
            difference if variate_starting_positions is True. Defaults to True.
        fancy_formatting (bool, optional): Whether to use a nice formatting method that doesn't clog up the terminal. Defaults to True.

    Returns:
        dict: The results from all the matches.
    """
    if fancy_formatting:
        print("\n" * 4)
        LINE_UP = '\033[1A'
        LINE_CLEAR = '\x1b[2K'
        LOG_START = (LINE_CLEAR + LINE_UP) * 4
    
    outcomes = {
        bot_1.name: 0,
        bot_2.name: 0,
        "draw": 0
    }

    increment = amount / 100

    starting_time = time.time()
    
    start_position = None
    starting_estimation = None

    for game in range(amount):
        game_white = bot_1 if game % 2 == 0 else bot_2
        game_black = bot_2 if game % 2 == 0 else bot_1
        
        if variate_starting_positions and game % 2 == 0:
            start_position = " ".join(get_random_moves(6))
        
        if seeded_positions:
            seed = game
        else:
            seed = None

        data = run_match(
            white = game_white,
            black = game_black,
            variate_starting_position = variate_starting_positions,
            custom_start_san = start_position,
            seed = seed,
            log_progress = False
        )

        if data["winner"] is None:
            outcomes["draw"] += 1
        elif data["winner"]:
            outcomes[game_white.name] += 1
        else:
            outcomes[game_black.name] += 1
        
        if (game + 1) % max(int(increment), 1) == 0:
            current = time.time()
            estimate = round(((current - starting_time) / (game + 1)) * (amount - (game + 1)), 2)
            
            if starting_estimation is None:
                starting_estimation = estimate
            
            current_results = "Current results: {name1}: {win1}, {name2}: {win2}, draw: {draws}, {name1} win: {name1win}%, {name2} win: {name2win}%, draw: {drawpercent}%".format(
                name1 = bot_1.name,
                win1 = outcomes[bot_1.name],
                name2 = bot_2.name,
                win2 = outcomes[bot_2.name],
                draws = outcomes["draw"],
                name1win = round(outcomes[bot_1.name] / (game + 1) * 100, 2),
                name2win = round(outcomes[bot_2.name] / (game + 1) * 100, 2),
                drawpercent = round(outcomes["draw"] / (game + 1) * 100, 2)
            )
            
            if not fancy_formatting:
                prefix = "{done}/{amount} | Elapsed: {elapsed} | Remaining: {estimated} | ".format(
                    done = str(game + 1).rjust(int(math.log10(amount)) + 1),
                    amount = amount,
                    elapsed = round(current - starting_time, 2),
                    estimated = estimate,
                )
                print(f"{prefix} {current_results}")
            else:
                info = "{done}/{amount} [{progress}{blank}] {elapsed} | {estimated}".format(
                    done = str(game + 1).rjust(int(math.log10(amount)) + 1),
                    amount = amount,
                    progress = "█" * int((game + 1) // increment),
                    blank = "░" * int(100 - ((game + 1) // increment)),
                    elapsed = round(current - starting_time, 2),
                    estimated = estimate,
                )
                
                print("{log_start}\n{line}\n# {info} #\n# {current_results} #\n{line}".format(
                    log_start = LOG_START,
                    line = "#" * (len(info) + 4),
                    info = info,
                    current_results = current_results.ljust(len(info))
                ), end="\r")
            
    print()
    return outcomes

def get_bot(identifier: str) -> ChessBot | None:
    """Gets a bot from the all_bots dictionary by name.
    Case is ignored, so an all uppercase name will still work.
    If nothing is found a ValueError is raised."""
    try:
        return all_bots[identifier.lower()]
    except KeyError:
        raise ValueError(f"Bot '{identifier}' not found.\nAvailable bots: {', '.join(all_bots.keys())}")

def get_module(identifier: str) -> ChessBot | None:
    """Gets a bot's module from the bot_modules dictionary by the bot's name.
    Case is ignored, so an all uppercase name will still work.
    If nothing is found then a ValueError will be raised."""
    try:
        return bot_modules[identifier.lower()]
    except KeyError:
        raise ValueError(f"Bot '{identifier}' not found.\nAvailable bots: {', '.join(all_bots.keys())}")

def refresh_bots():
    """Refreshes the all_bots dictionary with the bots in the `bots` and `dev` directories.
    This searches the directories recursively for .py files, so files in folders in folders will be found as well."""
    global all_bots, bot_modules, _module_files
    
    all_bots.clear()
    bot_modules.clear()
    module_file_list_copy = _module_files.copy()
    _module_files.clear()
    
    directory_list = [
        "bots",
        "dev"
    ]
    
    for directory in directory_list:
        file_list = []
        
        for root, _, files in os.walk(directory):
            # This is kind of ugly.
            file_list.extend(list(zip([root] * len(files), files)))
        
        for root, path in file_list:
            full_path = f"{root}{os.path.sep}{path}"
            if not os.path.isfile(full_path):
                continue
            
            if not path.endswith(".py"):
                continue
            
            filtered_root = root.replace('/', '.').replace('\\', '.')
            
            # If it's already been imported reload it, otherwise load it normally.
            if full_path in module_file_list_copy:
                try:
                    importlib.reload(module_file_list_copy[full_path])
                except Exception as e:
                    # Catch any errors that occur when reloading the file and print them.
                    print(f"{type(e).__name__} exception raised when reloading \"{full_path}\" for finding chess bots: {e}")
                    continue
                module = module_file_list_copy[full_path]
            else:
                module_name = f"{filtered_root}.{path.removesuffix('.py')}"
                try:
                    module = importlib.import_module(module_name)
                except Exception as e:
                    # Catch any errors that occur when loading the file and print them.
                    print(f"{type(e).__name__} raised when loading \"{full_path}\" for finding chess bots: {e}")
                    continue
                globals()[module_name] = module
            
            for obj in module.__dict__.values():
                try:
                    # issubclass won't work properly if this file is run directly, so it must be imported.
                    # When run directly the import causes the ChessBot class in the imported file to be
                    # different internally from the one in this file, so issubclass will always return False.
                    # This can be solved by importing the this file instead, in which case everything will
                    # work as expected.
                    if issubclass(obj, ChessBot):
                        all_bots[obj.name.lower()] = obj
                        bot_modules[obj.name.lower()] = module
                        _module_files[full_path] = module
                except TypeError: # If the object is not a class then issubclass will raise a TypeError.
                    pass
    
    # `sorted` returns a list of tuples, so convert it back to a dictionary.
    all_bots = dict(sorted(all_bots.items(), key=lambda x: x[0]))

# When the module is loaded, even as an import, refresh the bots.            
refresh_bots()

if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly, as the all_bots dictionary will not be populated correctly.")