from __future__ import annotations

import tkinter as tk
import tkinter.messagebox as messagebox

import typing
import threading
import traceback
import builtins

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

DARK_MODE = True
    
MAIN_STYLE = "light"

if DARK_MODE:
    # THEME = "darkly"
    THEME = "cyborg"
else:
    THEME = "cosmo"

if use_bootstrap:
    bootstyle_kwargs = {
        "bootstyle": MAIN_STYLE
    }
else:
    bootstyle_kwargs = {}

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
        self.setting_widget.grid(row=row, column=1)

        setattr(self.app, self.identifier, self.setting_widget)

    def run_build_command(self: typing.Self) -> None:
        if self.build_command is not None:
            self.build_command(*self.build_command_args, **self.build_command_kwargs)

class CheckboxSetting(Setting):
    def __init__(
            self: typing.Self,
            app: ChessApp,
            identifier: str,
            label: str = None,
            variable_name: str = None,
            builder: typing.Callable = None
        ) -> None:
        super().__init__(app, identifier, label)

        self.variable = tk.BooleanVar(app, name=variable_name+"_variable")
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

        self.variable = tk.StringVar(app, name=variable_name+"_variable")
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
    thread: threading.Thread = None
    
    def __init__(self: typing.Self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.title("Chess Bots")

        if use_bootstrap:
            self.geometry("1350x575+100+100")
        else:
            self.geometry("840x375+100+100")
            
        self.resizable(False, False)

        try:
            self.iconbitmap("./images/icon.ico")
        except: # Mobile will raise issues with this.
            pass
        
        self.log = ["Welcome to the Chess bot match manager!"]
        
        self.bot_dict = base.all_bots
        self.bots_list = list(self.bot_dict.keys())
        
        self.build_configuration()
        self.refresh_log()
    
    def report_callback_exception(self, exc, val, tb):
        self.add_log(traceback.format_exc())

    #######################################################################################################################
    #######################################################################################################################
    #######################################################################################################################
    
    def report_error(func: typing.Callable):
        """Decorator to catch any errors that occur, log them, and then rereaise them."""
        def wrapped(self: typing.Self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except:
                self.add_log(traceback.format_exc())
                raise
        
        return wrapped
    
    @report_error
    def _run_match_internal(self: typing.Self) -> None:
        # Before starting the game, make sure the given start SAN is valid.
        # Only do this, however, if the random start tickbox is enabled.
        custom_start = None
        
        if self.random_start:
            board = chess.Board()
            
            if len(self.custom_start_san.get()) != 0:
                for move in base.parse_san(self.custom_start_san.get()):
                    try:
                        board.push_san(move)
                    except (chess.IllegalMoveError, chess.InvalidMoveError, chess.AmbiguousMoveError):
                        messagebox.showerror(
                            title = "Chess match",
                            message = f"The given custom start SAN moves contains an invalid move: {move}"
                        )
                        return None
                
                custom_start = self.custom_start_san.get()
            
            
        bot1 = base.get_bot(self.bot_1.name)
        bot2 = base.get_bot(self.bot_2.name)
        
        bots = {
            chess.WHITE: self.bot_1.name, # White
            chess.BLACK: self.bot_2.name # Black
        }
        
        result = base.run_match(
            white = bot1,
            black = bot2,
            variate_starting_position = self.random_start,
            custom_start_san = custom_start
        )
        
        print(result)
        
        result_fen = "FEN: " + result["fen"]
        
        if result["winner"] is None:
            winner = "Draw"
        else:
            winner = bots[result['winner']]
        
        print("#" * (len(result_fen) + 4))
        print(f"# Winner: {winner: <{len(result_fen) - 8}} #")
        print(f"# {result_fen} #")
        print("#" * (len(result_fen) + 4))
        print("PGN:")
        print(result["pgn"])
        return None

    @report_error
    def _run_bulk_internal(self: typing.Self) -> None:
        bot1 = base.get_bot(self.bot_1.name)
        bot2 = base.get_bot(self.bot_2.name)
        
        try:
            amount = int(self.bulk_amount.get())
        except ValueError:
            messagebox.showerror(
                title = "Bulk game",
                message = "The entered number of bulk games to play is not a number."
            )
            return None
        
        if bot1 == bot2:
            if not messagebox.askokcancel(
                title = "Bulk Game",
                message = "The two bots set to play against each other have the same name, this will mess up the output.\nDo you wish to proceed with the bulk games anyway?"
            ):
                return None
        
        result = base.run_bulk(
            bot_1 = bot1,
            bot_2 = bot2,
            amount = amount,
            variate_starting_positions = self.random_start,
            seeded_positions = True,
            fancy_formatting = False # The fancy formatting is disabled here due to not really working properly.
        )
        
        print(result)
        
        lines = [
            f"Results from {amount} Chess games:",
            f"{bot1.name}: {result[bot1.name]} ({round(result[bot1.name] / amount * 100, 2)}%)",
            f"{bot2.name}: {result[bot2.name]} ({round(result[bot2.name] / amount * 100, 2)}%)",
            f"Draws: {result['draw']} ({round(result['draw'] / amount * 100, 2)}%)"
        ]
        
        max_length = len(max(lines, key=len))
        
        print("#" * (max_length + 4))
        for line in lines:
            print("# " + line.ljust(max_length, " ") + " #")
        print("#" * (max_length + 4))
        
        return None
    
    def run_match(self: typing.Self) -> None:
        self.thread = threading.Thread(target=self._run_match_internal)
        self.thread.start()
    
    def run_bulk(self: typing.Self) -> None:
        self.thread = threading.Thread(target=self._run_bulk_internal)
        self.thread.start()

    def refresh_log(self: typing.Self) -> None:
        self.bot_log.config(state=tk.NORMAL)
        self.bot_log.delete("1.0", tk.END)
        self.bot_log.insert(tk.END, "\n".join(self.log))
        self.bot_log.config(state=tk.DISABLED)
        self.bot_log.yview(tk.END)
    
    def add_log(self: typing.Self, message: str) -> None:
        self.bot_log.config(state=tk.NORMAL)
        self.log.append(message)
        self.bot_log.insert(tk.END, "\n" + message)
        self.bot_log.config(state=tk.DISABLED)
        self.bot_log.yview(tk.END)
    
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
                setting.setting_widget["menu"].add_command(label=option, command=tk._setit(setting.variable, option, setting.build_command))
        
        print("Bots reloaded successfully.")
    
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

    def build_checkbox_tick(
            self: typing.Self,
            attr_name: str,
            variable: tk.Variable
        ) -> typing.Callable:
        def click():
            setattr(self, attr_name, variable.get())

        return click
    
    #######################################################################################################################
    
    def build_configuration(self: typing.Self) -> None:
        config_frame = ttk.Frame(self)
        
        self.settings_list = [
            SettingLabel("Chess bot match manager:"),
            BotMenuSetting(
                app = self,
                identifier = "bot_1",
                label = "White:",
                variable_name = "bot_1"
            ),
            BotMenuSetting(
                app = self,
                identifier = "bot_2",
                label = "Black:",
                variable_name = "bot_2"
            ),
            CheckboxSetting(
                app = self,
                identifier = "random_start_tickbox",
                label = "Use a random start?",
                variable_name = "random_start"
            ),
            EntrySetting(
                app = self,
                identifier = "custom_start_entry",
                label = "Custom start SAN moves:",
                variable_name = "custom_start_san"
            ),
            EntrySetting(
                app = self,
                identifier = "amount_entry",
                label = "Bulk game count:",
                variable_name = "bulk_amount",
                default = "1000"
            ),
            SettingButton(
                app = self,
                identifier = "run_button",
                button_text = "Run single match",
                command = self.run_match
            ),
            SettingButton(
                app = self,
                identifier = "run_bulk_button",
                button_text = "Run bulk matches",
                command = self.run_bulk
            ),
            SettingButton(
                app = self,
                identifier = "refresh_bots_button",
                button_text = "Refresh bot list",
                command = self.refresh_bots
            )
        ]

        for index, item in enumerate(self.settings_list):
            item.build(config_frame, index + 1)

        for index, item in enumerate(self.settings_list):
            item.run_build_command()
            
        ######
        
        if use_bootstrap:
            self.bot_log = ttk.ScrolledText(
                master = config_frame,
                wrap = "word",
                state = "disabled"
            )
        else:
            self.bot_log = tk.Text(
                master = config_frame,
                wrap = "word",
                state = "disabled"
            )
            
        self.bot_log.grid(
            row = 0,
            column = 2,
            rowspan = len(self.settings_list) + 1,
            pady = 5,
            padx = 5
        )
        monospaced_font_tuple = ("Consolas", 10)
        self.bot_log.config(font=monospaced_font_tuple)

        config_frame.pack(expand=tk.YES, fill=tk.BOTH)

#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################

def main():
    kwargs = {}
    
    if use_bootstrap:
        kwargs["themename"] = THEME
        
    chess_app = ChessApp(**kwargs)
    
    global print
    
    def custom_print(*args, **kwargs):
        chess_app.add_log(" ".join(map(str, args)))
        builtins.print(*args, **kwargs)
        
    print = custom_print
    base.print = custom_print
    for module in base.bot_modules.values():
        module.print = custom_print
        
    chess_app.mainloop()

if __name__ == "__main__":
    main()
