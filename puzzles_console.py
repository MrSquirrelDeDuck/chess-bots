from __future__ import annotations

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog

import typing
import threading
import traceback
import base
import csv
import os
import builtins
import time
import re

puzzle_data = []

if not os.path.isfile("data/lichess_db_puzzle.csv"):
    print()
    print("To have the bots solve puzzles you need to download the Lichess puzzle database.")
    print("Once downloaded, extract the `.zst` file and put the resulting `.csv` into the `data` folder.")
    print("The file should be named `lichess_db_puzzle.csv`.")
    print("The puzzle database is intentionally not tracked by GitHub due to its size (around 800 MB with 4.8 million puzzles.)")
    print("The database download can be found here:")
    print("https://database.lichess.org/#puzzles")
    print()
    
    messagebox.showerror(
        title = "Missing the puzzle database",
        message = "The copy of the Lichess puzzle database used by this file to run the puzzles does not appear to exist.\nYou can find instructions in the terminal on how to download and use it."
    )
    exit()
    

try:
    import chess
except ImportError:
    print()
    print("You need to install the chess library used by the bots.")
    print("This can be done via running `pip install chess` in the terminal.")
    print("The library can be found here:")
    print("https://pypi.org/project/chess/")
    print()
    
    messagebox.showerror(
        title = "Missing module",
        message = "The chess module is missing, please install it via running `pip install chess` in the terminal.\nThis module is required for the program to run."
    )
    exit()

try:
    import PIL.ImageTk as ImageTk
    import PIL.Image as Image
except ImportError:
    print()
    print("You need to install the PIL library used by the GUI.")
    print("This can be done via running `pip install pillow` in the terminal.")
    print("The library can be found here:")
    print("https://pypi.org/project/pillow/")
    print()
    
    messagebox.showerror(
        title = "Missing module",
        message = "The PIL module is missing, please install it via running `pip install pillow` in the terminal.\nThis module is required for the program to run."
    )
    exit()
    
try:
    import ttkbootstrap as ttk
    import ttkbootstrap.scrolled as ttk_scrolled
    use_bootstrap = True
except ImportError:
    # Importing ttkbootstrap didn't work, so mark that and import regular ttk.
    print()
    print("The library used to make the GUI look better has not been installed.")
    print("This program will still function, but it won't look as good as it can.")
    print("The library can be installed via running `pip install ttkbootstrap` in the terminal.")
    print("The library can be found here:")
    print("https://pypi.org/project/ttkbootstrap/")
    
    # Attempt to remove the ttkbootstrap imports.
    # If the second one raised the import error, then the first one will be removed.
    try:
        del ttk
        del ttk_scrolled
    except NameError:
        pass
    
    import tkinter.ttk as ttk
    
    messagebox.showwarning(
        title = "Missing module",
        message = """The module used to make the program look better, ttkbootstrap, has not been installed.
This is not required for the program to run, but it will look better with it.
Install it via running `pip install ttkbootstrap` in the terminal.

Press "OK" to continue with the default look."""
    )
    use_bootstrap = False

try:
    import playsound
    has_sound = True
except ImportError:
    print()
    print("The library used to play sounds has not been installed, so playing sounds is disabled.")
    print("This program will still function, but it won't be able to play sounds.")
    print("The library can be installed via running `pip install playsound` in the terminal.")
    print("The library can be found here:")
    print("https://pypi.org/project/playsound/")
    
    messagebox.showwarning(
        title = "Missing module",
        message = """The module used to play move sounds, playsound, has not been installed.
This is not required for the program to run, but it means sounds will be disabled.
Install it via running `pip install playsound` in the terminal.

Press "OK" to continue without sounds."""
    )
    
    has_sound = False

print()

PIECE_PHOTOS_WHITE = None
PIECE_PHOTOS_BLACK = None
BLANK_IMAGE = None

DARK_MODE = True

MAIN_STYLE = "light"

if DARK_MODE:
    # THEME = "darkly"
    THEME = "cyborg"
else:
    THEME = "cosmo"

if use_bootstrap:
    IMAGE_SIZE = 150
    
    bootstyle_kwargs = {
        "bootstyle": MAIN_STYLE
    }
else:
    IMAGE_SIZE = 100
    bootstyle_kwargs = {}
    
NOTE_NONE = 0
NOTE_CORRECT = 1
NOTE_INCORRECT = 2
    
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################

class SettingBase():
    def build(self: typing.Self, grid: tk.Grid, row: int) -> None:
        pass

    def run_build_command(self: typing.Self) -> None:
        pass

class SettingButton(SettingBase):
    def __init__(
            self: typing.Self,
            app: ChessApp,
            identifier: str,
            button_text: str,
            label: str = None,
            command: typing.Callable = None
        ) -> None:
        self.app = app
        self.identifier = identifier
        self.button_text = button_text
        self.label = label
        self.command = command

    def build(
            self: typing.Self,
            grid: tk.Grid,
            row: int
        ) -> None:
        if self.label is not None:
            self.label_widget = tk.Label(
                grid,
                text = self.label
            )
            self.label_widget.grid(row=row, column=0)

        self.button_widget = ttk.Button(
            grid,
            text = self.button_text,
            command = self.command,
            **bootstyle_kwargs
        )
        setattr(self.app, self.identifier, self.button_widget)

        # If the label is none the button should span both columns, otherwise it should only span one.
        if self.label is None:
            self.button_widget.grid(row=row, columnspan=2)
        else:
            self.button_widget.grid(row=row, column=1)

class SettingLabel(SettingBase):
    def __init__(
            self: typing.Self,
            label: str = None
        ) -> None:
        self.label = label

    def build(
            self: typing.Self,
            grid: tk.Grid,
            row: int
        ) -> None:
        self.label_widget = ttk.Label(
            grid,
            text = self.label
        )
        self.label_widget.grid(row=row, columnspan=2)


class Setting(SettingBase):
    def __init__(
            self: typing.Self,
            app: ChessApp,
            identifier: str,
            label: str = None
        ) -> None:
        self.label = label
        self.identifier = identifier
        self.app = app

        self.setting_class = None
        self.setting_args = tuple()
        self.setting_kwargs = dict()

        self.build_command = None
        self.build_command_args = tuple()
        self.build_command_kwargs = dict()

    def build(
            self: typing.Self,
            grid: tk.Grid,
            row: int
        ) -> None:
        self.label_widget = ttk.Label(
            grid,
            text = self.label
        )
        self.label_widget.grid(row=row, column=0)

        self.setting_kwargs.update(bootstyle_kwargs)

        self.setting_widget = self.setting_class(grid, *self.setting_args, **self.setting_kwargs)
        self.setting_widget.grid(row=row, column=1, pady=5)

        setattr(self.app, self.identifier, self.setting_widget)

    def run_build_command(self: typing.Self) -> None:
        if self.build_command is not None:
            self.build_command(*self.build_command_args, **self.build_command_kwargs)

class CheckboxSetting(Setting):
    def __init__(
            self: typing.Self,
            identifier: str,
            app: ChessApp,
            label: str = None,
            variable_name: str = None,
            builder: typing.Callable = None
        ) -> None:
        super().__init__(app, identifier, label)

        self.variable = tk.BooleanVar(app)
        setattr(app, variable_name, self.variable)

        if builder is None:
            command = app.build_checkbox_tick(variable_name, self.variable)
        else:
            command = builder(variable_name, self.variable)

        self.build_command = command

        self.setting_class = ttk.Checkbutton
        self.setting_kwargs = {
            "variable": self.variable,
            "command": command
        }

class OptionMenuSetting(Setting):
    def __init__(
            self: typing.Self,
            app: ChessApp,
            identifier: str,
            label: str = None,
            options: list[str] = None,
            variable_name: str = None,
            *, # Force keyword only arguments.
            command: typing.Callable = None,
            builder: typing.Callable = None
        ) -> None:
        super().__init__(app, identifier, label)

        self.variable = tk.StringVar(app)
        self.variable.set(options[0])
        setattr(app, variable_name, self.variable)


        if builder is None:
            builder = app.build_option_menu_change

        if command is None:
            command = builder(variable_name)

        self.build_command = command
        self.build_command_args = (self.variable.get(),)

        self.setting_class = ttk.OptionMenu
        self.setting_args = (self.variable, self.variable.get(), *options)
        self.setting_kwargs = {
            "command": command
        }

class BotMenuSetting(OptionMenuSetting):
    def __init__(
            self: typing.Self,
            app: ChessApp,
            identifier: str,
            label: str = None,
            variable_name: str = None,
            *, # Force keyword only arguments.
            command: typing.Callable = None
        ) -> None:
        super().__init__(
            app = app,
            identifier = identifier,
            label = label,
            options = app.bots_list,
            variable_name = variable_name,
            command = command,
            builder = app.build_bot_menu_change
        )

class EntrySetting(Setting):
    def __init__(
            self: typing.Self,
            app: ChessApp,
            identifier: str,
            label: str = None,
            variable_name: str = None,
            default: str = None,
            args = None,
            kwargs = None
        ) -> None:
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()
            
        super().__init__(app, identifier, label)

        self.variable = tk.StringVar(app, value=default)
        setattr(app, variable_name, self.variable)

        self.setting_class = ttk.Entry
        kwargs.update({
            "textvariable": self.variable
        })
        self.setting_args = args
        self.setting_kwargs = kwargs

#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################

if use_bootstrap:
    parent_class = ttk.Window
else:
    parent_class = tk.Tk

class PuzzleDatabase():
    def __init__(self: typing.Self) -> None:
        self.puzzle_cache = {}
        
        self.file_path = "data/lichess_db_puzzle.csv"
            
        self.reset_reader()
    
    def reset_reader(self: typing.Self) -> None:
        self.opened_file = open(self.file_path, "r")
        self.reader = csv.reader(self.opened_file)
    
    def read_puzzles(
            self: typing.Self,
            amount: int,
            category: str
        ) -> typing.Generator[tuple[str]]:
        index = 0
        while index < amount:
            give = next(self.reader)
            
            if give[1] == "FEN":
                give = next(self.reader)
            
            if category != "" and category not in give[7].split(" "):
                while category not in give[7].split(" "):
                    give = next(self.reader)
            
            yield give
            
            index += 1
    
    def find_puzzle_by_id(
            self: typing.Self,
            puzzle_id: str
        ) -> tuple[str] | None:
        if puzzle_id in self.puzzle_cache:
            return self.puzzle_cache[puzzle_id]
        
        self.reset_reader()
        
        for puzzle in self.reader:
            if puzzle[0] == puzzle_id:
                self.puzzle_cache[puzzle[0]] = puzzle
                return puzzle
            
        print(next(self.reader))
        
        self.puzzle_cache[puzzle_id] = None
        return None

    def teardown(self: typing.Self) -> None:
        self.opened_file.close()

class ChessApp(parent_class):
    SOUND_PATHS = {
        "check": "./data/sounds/Check.mp3",
        "capture": "./data/sounds/Capture.mp3",
        "castle": "./data/sounds/Castle.mp3",
        "move": "./data/sounds/Move.mp3",
        "promotion": "./data/sounds/Promote.mp3",
    }

    LIGHT_SQUARE = "#f0d9b5"
    DARK_SQUARE = "#b58863"

    LIGHT_SQUARE_MOVE = "#cdd26a"
    DARK_SQUARE_MOVE = "#aaa23a"

    CORRECT_LIGHT = "#829769"
    CORRECT_DARK = "#646f40"
    # CORRECT_LIGHT = "#b5f0b5" # Incredibly light, not sure if I like it.
    # CORRECT_DARK = "#63b663"
    
    INCORRECT_LIGHT = "#976969"
    INCORRECT_DARK = "#6f4040"

    squares: dict[chess.Square, tk.Button] = {}
    labels: list[tk.Label] = []

    board: chess.Board = None
    selected_square: chess.Square = None
    move_to: list[chess.Square] = []
    last_move: chess.Move = None

    letters = "abcdefgh"
    numbers = "87654321"
    
    def __init__(self: typing.Self, database: PuzzleDatabase, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.title("Chess Bots")

        if use_bootstrap:
            self.geometry("1350x575+100+100")
        else:
            self.geometry("840x375+100+100")
            
        # self.resizable(False, False)

        try:
            self.iconbitmap("./images/icon.ico")
            self.state('zoomed')
        except: # Mobile will raise issues with this.
            pass
        
        self.note_colors = {
            NOTE_NONE: {
                "light": self.LIGHT_SQUARE_MOVE,
                "dark": self.DARK_SQUARE_MOVE
            },
            NOTE_CORRECT: {
                "light": self.CORRECT_LIGHT,
                "dark": self.CORRECT_DARK
            },
            NOTE_INCORRECT: {
                "light": self.INCORRECT_LIGHT,
                "dark": self.INCORRECT_DARK
            }
        }
        self.move_note = NOTE_NONE
        
        self.database = database
        self.board = chess.Board()
        
        self.bot_dict = base.all_bots
        self.bots_list = list(self.bot_dict.keys())
        self.bot_class = list(self.bot_dict.values())[0]
        
        self.contents = tk.Frame(self)
        
        self.contents.grid_rowconfigure(1, weight=1)
        self.contents.grid_columnconfigure(1, weight=1)
        
        self.log = ["Welcome to the Chess bot puzzle tester!"]
        
        self.build_images()
    
        # print(list(self.database.find_puzzle_by_id("qqFk5")))
        self.board_flipped = False
        self.build_board()
        self.build_configuration()
        self.refresh()
        
        self.refresh_log()
        
        self.contents.pack(padx=10, pady=10, fill="both", expand=True)
    
    def report_callback_exception(self, exc, val, tb):
        pass
        # self.add_log(traceback.format_exc())

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################
    
    def report_error(func: typing.Callable):
        """Decorator to catch any errors that occur, log them, and then rereaise them."""
        def wrapped(self: typing.Self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except:
                # self.add_log(traceback.format_exc())
                raise
        
        return wrapped
    
    def run_in_thread(func: typing.Callable):
        """Decorator to run the function in a thread automatically when it is run."""
        def wrapped(self: typing.Self, *args, **kwargs):
            thread = threading.Thread(
                target = func,
                args = (self,) + args,
                kwargs = kwargs
            )
            thread.start()
        
        return wrapped

    def play_sound(
            self: typing.Self,
            sound_name: str
        ) -> None:
        if not self.play_sounds:
            return

        if not has_sound:
            return

        thread = threading.Thread(
            target = playsound.playsound,
            args = (self.SOUND_PATHS[sound_name],)
        )
        thread.start()
        
    def play_move(
            self: typing.Self,
            move: chess.Move,
            refresh: bool = False
        ) -> None:
        sound_name = "move"

        if self.board.is_capture(move):
            sound_name = "capture"

        if self.board.is_castling(move):
            sound_name = "castle"

        if self.board.gives_check(move):
            sound_name = "check"

        if move.promotion is not None:
            sound_name = "promotion"

        self.selected_square = None
        self.move_to = []
        self.board.push(move)
        self.last_move = move

        if refresh:
            self.refresh()

        self.play_sound(sound_name)

    def _bot_turn(self: typing.Self) -> None:
        self.bot.load(self.bot_data)
        try:
            # self.board.copy(), RIP CheatBot.
            move = self.bot.turn(self.board.copy())
        except:
            messagebox.showerror(
                title = "An error occurred!",
                message = "The bot ran into an error and was unable to find a move."
            )
            raise
        saved = self.bot.save()
        if saved is not None:
            self.bot_data = saved
        
        if move is None:
            raise TypeError("The move played by the bot is None.")
        
        return move
    
    def run_puzzle(
            self: typing.Self,
            puzzle_data: list[str]
        ) -> dict[str, str | int | bool]:
        puzzle_id, fen, moves, rating, ratingdeviation, populatity, playamount, themes, gameurl, openingtags = puzzle_data
        
        print(f"Playing puzzle {puzzle_id}")
        
        self.bot_data = {}
        self.bot = self.bot_class(self.bot_data)
        
        self.board.set_fen(fen)
        self.refresh_orientation(not self.board.turn)
        self.refresh()
        
        moves_split = moves.split(" ")
        
        correct = True
        
        self.bot_side = not self.board.turn
        for index, correct_move_uci in enumerate(moves_split):
            # If it's time for the bot to play its move.
            if self.board.turn == self.bot_side:
                move = self._bot_turn()
                
                print(f"Move {(index + 1) // 2}: {'Correct!' if move.uci() == correct_move_uci else 'Incorrect.'}")
                if move.uci() == correct_move_uci:
                    # Yippee
                    self.move_note = NOTE_CORRECT
                else:
                    self.board.push(move)
                    if self.board.is_checkmate():
                        self.move_note = NOTE_CORRECT
                    else:
                        self.move_note = NOTE_INCORRECT
                    self.board.pop()
            else:
                move = chess.Move.from_uci(correct_move_uci)
                self.move_note = NOTE_NONE
                
                if index != 0 and self.do_delay:
                    time.sleep(0.25)
                
            self.play_move(move, True)
            
            if self.move_note == NOTE_INCORRECT:
                correct = False
                break
        
        return {
            "correct": correct,
            "themes": themes.split(" "),
            "rating": int(rating),
            "puzzle_id": puzzle_id
        }
    
    @run_in_thread
    @report_error
    def run_bulk_puzzles(self: typing.Self) -> None:
        try:
            num_puzzles = int(self.bulk_puzzle_amount.get())
        except ValueError:
            messagebox.showerror(
                title = "Bulk game",
                message = "The entered number of bulk games to play is not a number."
            )
            return None
        
        correct = 0
        correct_rating_sum = 0
        incorrect_rating_sum = 0
        
        highest_correct_rating = 0
        highest_correct_id = None
        
        lowest_incorrect_rating = float("inf")
        lowest_incorrect_id = None
        
        themes = {}
        
        self.database.reset_reader()
        
        start = time.time()
        
        try:
            for index, puzzle in enumerate(self.database.read_puzzles(num_puzzles, self.specific_category.get())):
                data = self.run_puzzle(puzzle)
                
                if data["correct"]:
                    correct += 1
                    correct_rating_sum += data["rating"]
                    
                    if data["rating"] > highest_correct_rating:
                        highest_correct_rating = data["rating"]
                        highest_correct_id = data["puzzle_id"]
                else:
                    incorrect_rating_sum += data["rating"]
                
                    if data["rating"] < lowest_incorrect_rating:
                        lowest_incorrect_rating = data["rating"]
                        lowest_incorrect_id = data["puzzle_id"]
                
                for theme in data["themes"]:
                    if theme not in themes:
                        themes[theme] = {"played": 1, "correct": int(data["correct"])}
                    else:
                        themes[theme]["played"] += 1
                        if data["correct"]:
                            themes[theme]["correct"] += 1
                
                current = time.time()
                print(f"Done {index + 1}/{num_puzzles} ({round((index + 1) / num_puzzles * 100, 2)}%) | Elapsed: {round(current - start, 2)} | Remaining: {round((current - start) / (index + 1) * (num_puzzles - (index+ 1)), 2)}"
                    f" | Correct: {correct} ({round(correct / (index + 1) * 100, 2)}%), Incorrect: {index + 1 - correct} ({round((1 - correct / (index + 1)) * 100, 2)}%)"
                )
                if self.do_delay:
                    time.sleep(0.5)
        except RuntimeError:
            print("Out of puzzles to solve!\n")
        
        lines = [
            f"Correct: {correct} ({round(correct / num_puzzles * 100, 2)}%)",
            f"Incorrect: {num_puzzles - correct} ({round((1 - correct / num_puzzles) * 100, 2)}%)",
            f"Average correct rating: {round(correct_rating_sum / (correct if correct != 0 else 1), 2)}",
            f"Average incorrect rating: {round(incorrect_rating_sum / ((num_puzzles - correct) if correct != num_puzzles else 1), 2)}",
            "",
            "Highest rated correctly solved:",
            f"- Rating: {highest_correct_rating}",
            f"- Link: https://lichess.org/training/{highest_correct_id}",
            "",
            "Lowest rated incorrectly solved:",
            f"- Rating: {lowest_incorrect_rating}",
            f"- Link: https://lichess.org/training/{lowest_incorrect_id}",
            "",
            "Theme information:",
        ]
        lines.extend([
            f"- {name}: {data['correct']}/{data['played']} ({round(data['correct'] / data['played'] * 100, 2)}%)"
            for name, data in sorted(list(themes.items()), key=lambda a: a[1]['correct'] / a[1]['played'], reverse=True)
        ])
        
        max_length = len(max(lines, key=len))
        
        print(f" {num_puzzles} {'bulk' if self.specific_category.get() == '' else self.specific_category.get()} puzzles: ".center(max_length + 4, "#"))
        
        for line in lines:
            print("# " + line.ljust(max_length) + " #")
        
        print("#" * (max_length + 4))
            
            
        
    
    @run_in_thread
    @report_error
    def run_single_puzzle(self: typing.Self) -> None:
        # self.board.push("4")
        puzzle_data = self.database.find_puzzle_by_id(self.puzzle_id.get())
        
        if puzzle_data is None:
            messagebox.showerror(
                title = "Single puzzle",
                message = f"The given puzzle id, {self.puzzle_id.get()}, does not exist in the database."
            )
            return
        
        data = self.run_puzzle(puzzle_data)
        
        lines = [
            f"Bot got it correct: {str(data['correct'])}",
            f"Puzzle rating: {data['rating']}",
            "Themes:"
        ]
        lines.extend([f"- {i}" for i in data["themes"]])
        
        max_length = len(max(lines, key=len))
        
        print(f" Puzzle {data['puzzle_id']}: ".center(max_length + 4, "#"))
        
        for line in lines:
            print("# " + line.ljust(max_length) + " #")
        
        print("#" * (max_length + 4))
        

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

    def set_button_color(
            self: typing.Self,
            button: tk.Button,
            light_color: str,
            dark_color: str,
            color: bool
        ) -> None:
        if color:
            button["bg"] = light_color
            button["activebackground"] = light_color
        else:
            button["bg"] = dark_color
            button["activebackground"] = dark_color

    def refresh_square_piece(
            self: typing.Self,
            square: chess.Square,
            button: tk.Button
        ) -> None:
        piece = self.board.piece_at(square)

        if piece is None:
            button["image"] = BLANK_IMAGE
            return

        if piece.color:
            button["image"] = PIECE_PHOTOS_WHITE[piece.piece_type]
        else:
            button["image"] = PIECE_PHOTOS_BLACK[piece.piece_type]

    def refresh_square_color(
            self: typing.Self,
            square: chess.Square,
            button: tk.Button
        ) -> None:
        if self.selected_square == square or square in self.move_to:
            self.set_button_color(
                button = button,
                light_color = self.CORRECT_LIGHT,
                dark_color = self.CORRECT_DARK,
                color = button.square_color
            )
            return

        if self.last_move is None:
            self.set_button_color(
                button = button,
                light_color = self.LIGHT_SQUARE,
                dark_color = self.DARK_SQUARE,
                color = button.square_color
            )
            return

        if square == self.last_move.from_square \
            or square == self.last_move.to_square:
            self.set_button_color(
                button = button,
                light_color = self.note_colors[self.move_note]["light"],
                dark_color = self.note_colors[self.move_note]["dark"],
                color = button.square_color
            )
        else:
            self.set_button_color(
                button = button,
                light_color = self.LIGHT_SQUARE,
                dark_color = self.DARK_SQUARE,
                color = button.square_color
            )

    def refresh(self: typing.Self) -> None:
        for square, button in self.squares.items():
            self.refresh_square_piece(square, button)
            self.refresh_square_color(square, button)
            
    def refresh_log(self: typing.Self) -> None:
        self.bot_log.config(state=tk.NORMAL)
        self.bot_log.delete("1.0", tk.END)
        self.bot_log.insert(tk.END, "\n".join(self.log))
        self.bot_log.config(state=tk.DISABLED)
        self.bot_log.yview(tk.END)
    
    def add_log(self: typing.Self, message: str) -> None:
        message = re.sub("[lL][iI][aA][mM]", "BOINGE", message)
        self.bot_log.config(state=tk.NORMAL)
        self.log.append(message)
        self.bot_log.insert(tk.END, "\n" + message)
        self.bot_log.config(state=tk.DISABLED)
        self.bot_log.yview(tk.END)
    
    def refresh_orientation(
            self: typing.Self,
            new_state: bool = None
        ) -> None:
        if new_state is None:
            new_state = self.board.turn
        
        if new_state:
            if self.squares[chess.A1].initial_index == chess.A1:
                return
        else:
            if self.squares[chess.H8].initial_index == chess.A1:
                return
        
        squares_copy = self.squares.copy()
        self.squares.clear()
        
        for button in squares_copy.values():
            if new_state:
                self.squares[button.initial_index] = button
            else:
                self.squares[63 - button.initial_index] = button
        
        for label in self.labels:
            if new_state:
                if label.is_letter:
                    label.config(text=self.letters[label.initial_index])
                else:
                    label.config(text=self.numbers[label.initial_index])
            else:
                if label.is_letter:
                    label.config(text=self.letters[7 - label.initial_index])
                else:
                    label.config(text=self.numbers[7 - label.initial_index])

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

    def build_images(self: typing.Self) -> None:
        global PIECE_PHOTOS_WHITE, PIECE_PHOTOS_BLACK, BLANK_IMAGE

        PIECE_PATHS_WHITE = {
            chess.PAWN: "./images/Wpawn.png",
            chess.KNIGHT: "./images/Wknight.png",
            chess.BISHOP: "./images/Wbishop.png",
            chess.ROOK: "./images/Wrook.png",
            chess.QUEEN: "./images/Wqueen.png",
            chess.KING: "./images/Wking.png",
        }

        PIECE_PATHS_BLACK = {
            chess.PAWN: "./images/Bpawn.png",
            chess.KNIGHT: "./images/Bknight.png",
            chess.BISHOP: "./images/Bbishop.png",
            chess.ROOK: "./images/Brook.png",
            chess.QUEEN: "./images/Bqueen.png",
            chess.KING: "./images/Bking.png",
        }

        PIECE_PHOTOS_WHITE = {
            piece_key: ImageTk.PhotoImage(Image.open(path).resize((IMAGE_SIZE, IMAGE_SIZE)), master=self, width=IMAGE_SIZE, height=IMAGE_SIZE)
            for piece_key, path in PIECE_PATHS_WHITE.items()
        } 

        PIECE_PHOTOS_BLACK = {
            piece_key: ImageTk.PhotoImage(Image.open(path).resize((IMAGE_SIZE, IMAGE_SIZE)), master=self, width=IMAGE_SIZE, height=IMAGE_SIZE)
            for piece_key, path in PIECE_PATHS_BLACK.items()
        }

        BLANK_IMAGE = ImageTk.PhotoImage(Image.open("./images/blank.png").resize((IMAGE_SIZE, IMAGE_SIZE)), width=IMAGE_SIZE, height=IMAGE_SIZE, master=self)

        self.PIECE_PHOTOS_WHITE = PIECE_PHOTOS_WHITE
        self.PIECE_PHOTOS_BLACK = PIECE_PHOTOS_BLACK
        self.BLANK_IMAGE = BLANK_IMAGE
        
    def build_board(self: typing.Self) -> None:
        self.board_frame = tk.Frame(self.contents)
        
        for row in range(8):
            for column in range(8):
                color = self.DARK_SQUARE if (row + column) % 2 else self.LIGHT_SQUARE
                square_id = chess.square(column, row)

                new_button = tk.Button(
                    master = self.board_frame,
                    image = self.BLANK_IMAGE,
                    cursor = "hand2",
                    bg = color,
                    activebackground = color
                )
                new_button.square_color = ((row + column) % 2)
                new_button.initial_index = square_id

                if self.board_flipped:
                    new_button.grid(
                        column = 7 - column,
                        row = row
                    )
                else:
                    new_button.grid(
                        column = column,
                        row = 7 - row
                    )

                self.squares[square_id] = new_button

        if self.board_flipped:
            letters = "".join(reversed(self.letters))
            numbers = "".join(reversed(self.numbers))
        else:
            letters = self.letters
            numbers = self.numbers

        self.labels.clear()

        for index, letter in enumerate(letters):
            new_label = tk.Label(
                master = self.board_frame,
                text = letter
            )
            new_label.grid(
                row = 8,
                column = index
            )
            new_label.initial_index = index
            new_label.is_letter = True
            self.labels.append(new_label)

        for index, number in enumerate(numbers):
            new_label = tk.Label(
                master = self.board_frame,
                text = number
            )
            new_label.grid(
                row = index,
                column = 8
            )
            new_label.initial_index = index
            new_label.is_letter = False
            self.labels.append(new_label)
        
        self.board_frame.grid(row=0, column=0)

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

    def build_bot_menu_change(
            self: typing.Self,
            attr_name: str
        ) -> typing.Callable:
        def click(selected):
            setattr(self, attr_name, self.bot_dict[selected])

        return click

    def build_checkbox_tick(
            self: typing.Self,
            attr_name: str,
            variable: tk.Variable
        ) -> typing.Callable:
        def click():
            setattr(self, attr_name, variable.get())

        return click
    
    def build_configuration(self: typing.Self) -> None:
        style = ttk.Style()
        # style.theme_use("clam")
        style.configure("TButton", font=("Arial", 20, "bold"))
        
        if use_bootstrap:
            config_frame = ttk_scrolled.ScrolledFrame(self.contents, width=500, autohide=True)
        else:
            config_frame = tk.Frame(self.contents)
            
        self.settings_list = [
            BotMenuSetting(
                app = self,
                identifier = "bot_menu",
                label = "Bot to play against:",
                variable_name = "bot_class"
            ),
            EntrySetting(
                app = self,
                identifier = "bulk_puzzle_input",
                variable_name = "bulk_puzzle_amount",
                label = "Number of puzzles:",
                default = "25"
            ),
            EntrySetting(
                app = self,
                identifier = "category_input",
                variable_name = "specific_category",
                label = "Bulk puzzle category:",
                default = ""
            ),
            SettingButton(
                app = self,
                identifier = "bulk_puzzle_button",
                button_text = "Run bulk puzzle test",
                command = self.run_bulk_puzzles
            ),
            SettingLabel("Single puzzle settings:"),
            EntrySetting(
                app = self,
                identifier = "puzzle_id_input",
                variable_name = "puzzle_id",
                label = "Specific puzzle id:",
                default = "00008"
            ),
            SettingButton(
                app = self,
                identifier = "single_puzzle_button",
                button_text = "Run on a single puzzle",
                command = self.run_single_puzzle
            ),
            SettingLabel("Global settings:")
        ]
        
        if has_sound:
            self.settings_list.append(CheckboxSetting(
                app = self,
                identifier = "sounds",
                label = "Sounds?",
                variable_name = "play_sounds"
            ))
            
        self.settings_list.append(CheckboxSetting(
            app = self,
            identifier = "delay",
            label = "Delay between moves?",
            variable_name = "do_delay"
        ))

        for index, item in enumerate(self.settings_list):
            item.build(config_frame, index + 1)

        for index, item in enumerate(self.settings_list):
            item.run_build_command()

        config_frame.grid(row=1, column=0, sticky="ns")
        
        #########
        
        if use_bootstrap:
            self.bot_log = ttk.ScrolledText(
                master = self.contents,
                wrap = "word",
                state = "disabled"
            )
        else:
            self.bot_log = tk.Text(
                master = self.contents,
                wrap = "word",
                state = "disabled"
            )
            
        self.bot_log.grid(
            row = 0,
            column = 1,
            rowspan = 2,
            pady = 5,
            padx = 5,
            sticky = "nesw"
        )
        monospaced_font_tuple = ("Consolas", 10)
        self.bot_log.config(font=monospaced_font_tuple)

def main():
    database = PuzzleDatabase()
    try:
        # global puzzle_data
        
        kwargs = {}
        
        if use_bootstrap:
            kwargs["themename"] = THEME
            
        # database_loader = DatabaseLoader(**kwargs)
        # database_loader.mainloop()
        
        chess_app = ChessApp(database, **kwargs)
    
        global print
        
        def custom_print(*args, **kwargs):
            chess_app.add_log(" ".join(map(str, args)))
            builtins.print(*args, **kwargs)
            
        print = custom_print
        base.print = custom_print
        for module in base.bot_modules.values():
            module.print = custom_print
        
        chess_app.mainloop()
        
        # Attempt to free up the memory.
        # del puzzle_data
    finally:
        database.teardown()

if __name__ == "__main__":
    main()
