from __future__ import annotations

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog

import typing
import threading
import time
import base


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

#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################

class PromotionDialog(simpledialog.Dialog):
    def __init__(self, parent, title = None, piece_color: chess.Color = chess.WHITE):
        if piece_color:
            self.pieces = PIECE_PHOTOS_WHITE
        else:
            self.pieces = PIECE_PHOTOS_BLACK
        self.result = None

        super().__init__(parent, title)

    def buttonbox(self):
        box = tk.Frame(self)

        label = tk.Label(
            box,
            text = "Which type of piece would you like to promote to?",
        )
        label.pack(
            side = tk.TOP
        )

        for piece in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
            new_button = ttk.Button(
                box,
                image = self.pieces[piece],
                command = self.build_click(piece),
                default = tk.ACTIVE,
                **bootstyle_kwargs
            )
            new_button.pack(
                side = tk.LEFT,
                padx = 5,
                pady = 5
            )

        box.pack()

    def build_click(
            self: typing.Self,
            piece: chess.Piece
        ) -> typing.Callable:
        def click():
            self.result = piece
            self.ok()
        return click

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

    SELECTED_LIGHT = "#829769"
    SELECTED_DARK = "#646f40"

    SUQARES: dict[chess.Square, tk.Button] = {}
    LABELS: list[tk.Label] = []

    board: chess.Board = None
    selected_square: chess.Square = None
    move_to: list[chess.Square] = []
    last_move: chess.Move = None

    thread: threading.Thread = None

    def __init__(self: typing.Self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.title("Chess Bots")

        self.geometry("848x848+100+100")

        try:
            self.iconbitmap("./images/icon.ico")
            self.state('zoomed')
        except: # Mobile will raise issues with this.
            pass

        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(pady=10)

        # Setup data, this is updated when a game starts in start_game.
        self.player_color = chess.WHITE
        self.start_player_color = chess.WHITE
        self.board_flipped = not self.player_color
        self.bot_class = None
        self.play_sounds = False
        self.do_random_start = False
        self.starting_fen = None

        self.random_start_delays = {
            "1 second": 1,
            "2 seconds": 2,
            "3 seconds": 3,
            "4 seconds": 4,
            "5 seconds": 5,
            "Half a second": 0.5,
            "Quarter of a second": 0.25,
            "Tenth of a second": 0.1,
            "No delay": 0,
            "Instant": -1, # This one also disables refreshing the board and sounds.
        }

        self.build_images()

        self.board = chess.Board()
        
        self.bot_dict = base.all_bots
        self.bots_list = list(self.bot_dict.keys())
        self.bot_class = list(self.bot_dict.values())[0]

        self.build_board()
        self.build_configuration()

        self.refresh()

        self.moves_playable = False

        self.bvb_bot_1 = list(self.bot_dict.values())[0]
        self.bvb_1_data = {}
        self.bvb_bot_2 = list(self.bot_dict.values())[0]
        self.bvb_2_data = {}

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

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

    def play_random_start(self: typing.Self) -> None:
        if self.random_start_pgn.get():
            moves = base.parse_san(self.random_start_pgn.get())
        else:
            moves = base.get_random_moves(amount=5)

        delay = self.random_start_delays[self.random_start_delay_var]

        for move in moves:
            played = self.board.parse_san(move)

            sound_name = "move"

            if self.board.is_capture(played):
                sound_name = "capture"

            if self.board.is_castling(played):
                sound_name = "castle"

            if self.board.gives_check(played):
                sound_name = "check"

            if played.promotion is not None:
                sound_name = "promotion"

            self.board.push(played)
            self.last_move = played
            if delay != -1:
                self.refresh()
                self.play_sound(sound_name)
                time.sleep(delay)

        self.refresh()

    def start_bvb(self: typing.Self) -> None:
        self.thread = threading.Thread(target=self._start_bvb_internal)
        self.thread.start()

    def _start_bvb_internal(self: typing.Self) -> None:
        self.bot_vs_bot = True
        self.moves_playable = False

        self.board.reset()

        self.selected_square = None
        self.move_to = []
        self.last_move = None

        if self.do_random_start:
            self.play_random_start()

        self.bot_data = {}
        self.refresh()

        self.start_bvb_bot_1()

    def start_game(
            self: typing.Self,
            bot_class: typing.Callable = None,
            player_side: chess.Color = None,
            fen: str = None
        ) -> None:
        self.thread = threading.Thread(target=self._start_game_internal, args=(bot_class, player_side, fen))
        self.thread.start()

    def _start_game_internal(
            self: typing.Self,
            bot_class: typing.Callable = None,
            player_side: chess.Color = None,
            fen: str = None,
            skip_turn: bool = False # Use if a FEN string is passed and is black to move.
        ) -> None:
        if fen is None:
            fen = chess.STARTING_BOARD_FEN
            self.starting_fen = None
        else:
            self.starting_fen = fen

        self.bot_vs_bot = False

        if bot_class is not None:
            self.bot_class = bot_class
        if player_side is None:
            player_side = self.start_player_color

        self.moves_playable = True

        prior_player_color = self.player_color

        self.player_color = player_side
        self.board_flipped = not self.player_color

        if self.player_color != prior_player_color:
            self.rebuild_board()

        self.board.reset()
        self.board.set_board_fen(fen)

        if skip_turn:
            self.board.push(chess.Move.null())

        if self.starting_fen is not None:
            self.starting_fen = self.board.fen()

        self.selected_square = None
        self.move_to = []
        self.last_move = None

        if self.do_random_start and self.starting_fen is None:
            self.play_random_start()

        self.bot_data = {}
        self.refresh()

        if self.player_color != self.board.turn:
            self.start_bot()

    def check_end(self: typing.Self) -> bool:
        if not self.board.is_game_over():
            return False

        self.game_over = True
        self.moves_playable = False

        outcome = self.board.outcome()

        messagebox.showinfo(
            title = "Game over!",
            message = f"The game has ended by {outcome.termination.name.lower().replace('_', ' ')}."
        )
        return True

    def _bot_turn(self: typing.Self) -> None:
        self.bot.load(self.bot_data)
        try:
            # self.board.copy(), RIP CheatBot.
            move = self.bot.turn(self.board.copy())
        except:
            messagebox.showinfo(
                title = "Game over!",
                message = "The bot ran into an error while figuring out what move to play. As far as I am concerned that counts as a win for you, great job!"
            )
            self.game_over = True
            self.moves_playable = False
            raise
        saved = self.bot.save()
        if saved is not None:
            self.bot_data = saved

        self.play_move(
            move = move,
            refresh = True
        )

    def _bvb_bot_1_turn(self: typing.Self) -> None:
        self.bvb_1.load(self.bvb_1_data)
        try:
            move = self.bvb_1.turn(self.board.copy())
        except:
            messagebox.showinfo(
                title = "Game over!",
                message = "The bot ran into an error while figuring out what move to play. As far as I am concerned that counts as a win for you, great job!"
            )
            self.game_over = True
            self.moves_playable = False
            raise
        saved = self.bvb_1.save()
        if saved is not None:
            self.bvb_1_data = saved

        self.play_move(
            move = move,
            refresh = True
        )

    def _bvb_bot_2_turn(self: typing.Self) -> None:
        self.bvb_2.load(self.bvb_2_data)
        try:
            move = self.bvb_2.turn(self.board.copy())
        except:
            messagebox.showinfo(
                title = "Game over!",
                message = "The bot ran into an error while figuring out what move to play. As far as I am concerned that counts as a win for you, great job!"
            )
            self.game_over = True
            self.moves_playable = False
            raise
        saved = self.bvb_2.save()
        if saved is not None:
            self.bvb_2_data = saved

        self.play_move(
            move = move,
            refresh = True
        )

    def start_bot(self: typing.Self) -> None:
        self.bot = self.bot_class(self.bot_data)
        self.thread = threading.Thread(target=self._bot_turn)
        self.thread.start()

    def start_bvb_bot_1(self: typing.Self) -> None:
        self.bvb_1 = self.bvb_bot_1(self.bvb_1_data)
        print(f"[BVB] Time for {self.bvb_1.name} to play.")
        self.thread = threading.Thread(target=self._bvb_bot_1_turn)
        self.thread.start()

    def start_bvb_bot_2(self: typing.Self) -> None:
        self.bvb_2 = self.bvb_bot_2(self.bvb_2_data)
        print(f"[BVB] Time for {self.bvb_2.name} to play.")
        self.thread = threading.Thread(target=self._bvb_bot_2_turn)
        self.thread.start()

    def play_move(
            self: typing.Self,
            move: chess.Move,
            refresh: bool = False
        ) -> None:
        sound_name = "move"

        # Check for promotion.
        if move.promotion is None and self.board.turn == self.player_color:
            if (chess.square_rank(move.to_square) == 0 \
               or chess.square_rank(move.to_square) == 7) \
               and self.board.piece_at(move.from_square).piece_type == chess.PAWN:
                move.promotion = PromotionDialog(self, title="Promotion").result

                if move.promotion is None:
                    return

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

        if self.check_end():
            return

        self.play_sound(sound_name)

        if self.bot_vs_bot:
            if self.board.turn:
                self.start_bvb_bot_1()
            else:
                self.start_bvb_bot_2()
        else:
            # If it's time for the bot to play its move.
            if self.board.turn != self.player_color:
                self.start_bot()

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
                light_color = self.SELECTED_LIGHT,
                dark_color = self.SELECTED_DARK,
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
                light_color = self.LIGHT_SQUARE_MOVE,
                dark_color = self.DARK_SQUARE_MOVE,
                color = button.square_color
            )
        else:
            self.set_button_color(
                button = button,
                light_color = self.LIGHT_SQUARE,
                dark_color = self.DARK_SQUARE,
                color = button.square_color
            )

    def refresh_board_info(self: typing.Self) -> None:
        self.fen_box_var.set(self.board.fen())

        #################

        board_copy = self.board.copy()

        moves_reverse = []

        for _ in range(len(board_copy.move_stack)):
            move = board_copy.pop()
            moves_reverse.append(board_copy.san(move))

        moves = list(reversed(moves_reverse))
        moves_pgn = []

        for index in range(0, len(moves_reverse), 2):
            moves_pgn.append(f"{index // 2 + 1}. {' '.join(moves[index:index+2])}")

        pgn = " ".join(moves_pgn)

        if self.starting_fen is not None:
            pgn = f"""[Variant "From Position"]\n[FEN "{self.starting_fen}"]\n\n{pgn}"""

        self.pgn_box_var.set(pgn)

    def refresh(self: typing.Self) -> None:
        for square, button in self.SUQARES.items():
            self.refresh_square_piece(square, button)
            self.refresh_square_color(square, button)

        self.refresh_board_info()
    
    def refresh_bots(self: typing.Self) -> None:
        base.refresh_bots()
        self.bot_dict = base.all_bots
        self.bots_list = list(self.bot_dict.keys())
        
        for setting in self.settings_list:
            if not isinstance(setting, BotMenuSetting):
                continue
                
            setting.variable.set(self.bots_list[0])
            setting.setting_widget["menu"].delete(0, tk.END)
            
            for option in self.bots_list:
                setting.setting_widget["menu"].add_command(label=option, command=tk._setit(setting.variable, option))

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

    def build_click(
            self: typing.Self,
            square: chess.Square
        ) -> typing.Callable[[None], None]:
        def click():
            if not self.moves_playable:
                return

            if self.board.turn != self.player_color:
                return

            if square in self.move_to:
                new_move = chess.Move(
                    from_square = self.selected_square,
                    to_square = square
                )

                self.play_move(
                    move = new_move,
                    refresh = True
                )
                return

            if square == self.selected_square:
                self.selected_square = None
                self.move_to = []
                self.refresh()
                return

            piece = self.board.piece_at(square)

            if piece is None:
                if square is not None:
                    self.selected_square = None
                    self.move_to = []
                    self.refresh()
                return

            if piece.color == self.player_color:
                self.selected_square = square
                self.move_to = []

                for move in self.board.legal_moves:
                    if move.from_square != square:
                        continue

                    self.move_to.append(move.to_square)

            self.refresh()

        return click

    def build_board(self: typing.Self) -> None:
        # import random
        # square_positions = [(r, c) for r in range(8) for c in range(8)]
        # random.shuffle(square_positions)

        for row in range(8):
            for column in range(8):
                color = self.DARK_SQUARE if (row + column) % 2 else self.LIGHT_SQUARE
                square_id = chess.square(column, row)

                new_button = tk.Button(
                    master = self.grid_frame,
                    image = self.BLANK_IMAGE,
                    command = self.build_click(square_id),
                    cursor = "hand2",
                    bg = color,
                    activebackground = color
                )
                new_button.square_color = ((row + column) % 2)

                # new_button.grid(
                #     row = square_positions[square_id][0],
                #     column = square_positions[square_id][1]
                # )
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

                self.SUQARES[square_id] = new_button

        letters = "abcdefgh"
        numbers = "87654321"

        if self.board_flipped:
            letters = "".join(reversed(letters))
            numbers = "".join(reversed(numbers))

        self.LABELS.clear()

        for index, letter in enumerate(letters):
            new_label = tk.Label(
                master = self.grid_frame,
                text = letter
            )
            new_label.grid(
                row = 8,
                column = index
            )
            self.LABELS.append(new_label)

        for index, number in enumerate(numbers):
            new_label = tk.Label(
                master = self.grid_frame,
                text = number
            )
            new_label.grid(
                row = index,
                column = 8
            )
            self.LABELS.append(new_label)

    def rebuild_board(self: typing.Self) -> None:
        for button in self.SUQARES.values():
            button.destroy()

        for label in self.LABELS:
            label.destroy()

        self.SUQARES.clear()

        self.build_board()
        self.refresh()

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################

    def build_option_menu_change(
            self: typing.Self,
            attr_name: str
        ) -> typing.Callable:
        def click(selected):
            setattr(self, attr_name, selected)

        return click

    def build_bot_menu_change(
            self: typing.Self,
            attr_name: str
        ) -> typing.Callable:
        def click(selected):
            setattr(self, attr_name, self.bot_dict[selected])

        return click

    def build_random_start_change(
            self: typing.Self,
            attr_name: str,
            variable: tk.Variable
        ) -> typing.Callable:
        def click():
            state = variable.get()
            setattr(self, attr_name, state)

            if state:
                self.random_start_entry["state"] = "normal"
            else:
                self.random_start_entry["state"] = "readonly"


        return click

    def on_color_selection_change(
            self: typing.Self,
            selected: str
        ) -> None:
        self.start_player_color = chess.WHITE if selected == "White" else chess.BLACK

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

        self.fen_box_var = tk.StringVar(self)
        self.fen_box = ttk.Entry(
            master = self,
            state = "readonly",
            textvariable = self.fen_box_var,
            width = 100
        )
        self.fen_box.pack()

        self.pgn_box_var = tk.StringVar(self)
        self.pgn_box = ttk.Entry(
            master = self,
            state = "readonly",
            textvariable = self.pgn_box_var,
            width = 100
        )
        self.pgn_box.pack()

        ####################
        # config_frame = tk.Frame(self)
        if use_bootstrap:
            config_frame = ttk_scrolled.ScrolledFrame(self, width=500, autohide=True)
        else:
            config_frame = tk.Frame(self)

        self.settings_list = [
            # Index 0
            SettingButton(
                app = self,
                identifier = "start_button",
                button_text = "Start game",
                command = self.start_game
            ),
            # Index 1
            BotMenuSetting(
                app = self,
                identifier = "bot_menu",
                label = "Bot to play against:",
                variable_name = "bot_class"
            ),
            # Index 2
            OptionMenuSetting(
                app = self,
                identifier = "color_menu",
                label = "Side to play as:",
                options = ["White", "Black"],
                variable_name = "color_menu_variable",
                command = self.on_color_selection_change
            ),
            # Index 3
            # This is where the sounds tickbox will go if it is enabled.
            ##################################
            # Index 4
            SettingLabel("Random start:"),
            # Index 5
            CheckboxSetting(
                app = self,
                identifier = "random_start",
                label = "Random start?",
                variable_name = "do_random_start",
                builder = self.build_random_start_change
            ),
            # Index 6
            EntrySetting(
                app = self,
                identifier = "random_start_entry",
                label = "Random start pgn:",
                variable_name = "random_start_pgn"
            ),
            # Index 7
            OptionMenuSetting(
                app = self,
                identifier = "random_start_delay",
                label = "Random start move delay:",
                options = list(self.random_start_delays.keys()),
                variable_name = "random_start_delay_var"
            ),
            ##################################
            # Index 8
            SettingLabel("Bot versus bot:"),
            # Index 9
            BotMenuSetting(
                app = self,
                identifier = "bvb_menu_1",
                label = "White:",
                variable_name = "bvb_bot_1"
            ),
            # Index 10
            BotMenuSetting(
                app = self,
                identifier = "bvb_menu_2",
                label = "Black:",
                variable_name = "bvb_bot_2"
            ),
            # Index 11
            SettingButton(
                app = self,
                identifier = "bvb_start_game",
                button_text = "Start bot vs bot game",
                command = self.start_bvb
            ),
            SettingLabel(),
            SettingButton(
                app = self,
                identifier = "refresh_bots",
                button_text = "Refresh bots",
                command = self.refresh_bots
            ),
        ]
        
        if has_sound:
            self.settings_list.insert(3, CheckboxSetting(
                app = self,
                identifier = "sounds",
                label = "Sounds?",
                variable_name = "play_sounds"
            ))

        for index, item in enumerate(self.settings_list):
            item.build(config_frame, index + 1)

        for index, item in enumerate(self.settings_list):
            item.run_build_command()

        config_frame.pack(expand=tk.YES, fill=tk.Y)

def main():
    kwargs = {}
    
    if use_bootstrap:
        kwargs["themename"] = THEME
        
    chess_app = ChessApp(**kwargs)
    chess_app.mainloop()

if __name__ == "__main__":
    main()
