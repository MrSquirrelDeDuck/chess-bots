# Chess Bots
This is a collection of [Python](https://www.python.org/) Chess bots that my friends and I have created using the [python-chess](https://pypi.org/project/chess/) library.

Python and library version information:
- While this is built in Python 3.11.0, it likely works on other versions.
- [python-chess](https://pypi.org/project/chess/) (built in version 1.11.1, probably works for other versions)
- [pillow](https://pypi.org/project/pillow/) (built in 11.0.0, probably works in other versions)
- (Optional) [ttkbootstrap](https://pypi.org/project/ttkbootstrap/) is used to make the UI look a little better, but is not required. (Built in 1.10.1, probably works in other versions)
- (Optional) [playsound](https://pypi.org/project/playsound/) is used to play sounds, but is not required. (Built in 1.3.0, probably works in other versions)

## File information:
- [`base.py`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/base.py): Base utility file, contains the main `ChessBot` class that all bots should subclass. This should be imported in every bot file.
- [`bot_testing_console.py`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bot_testing_console.py): Program for putting bots against each other. It can run a single match between two bots or a bulk number of matches between two bots.
- [`bot_testing.pyw`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bot_testing.pyw): Same as `bot_testing_console.py`, but double clicking to run it will not open up a terminal window.
- [`play_against_console.py`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/play_against_console.py): Program for playing against a bot. This also has the ability to put two bots against each other in a single game, similar to `bot_testing_console.py`, but this one has a visual board so you can watch the game as it is going.
- [`play_against.pyw`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/play_against.pyw): Same as `play_against_console.py`, but double clicking to run it will not open up a terminal window.

## Directory information:
- [`images`](https://github.com/MrSquirrelDeDuck/chess-bots/tree/main/images): Folder containing the images used by both programs.
- [`data`](https://github.com/MrSquirrelDeDuck/chess-bots/tree/main/data): Folder containing data used by the programs or the bots.
- [`bots`](https://github.com/MrSquirrelDeDuck/chess-bots/tree/main/bots): Public folder containing a Python file for each bot. This is used by the programs to generate the bot lists.
- `dev`: Private folder to be used for bot development. This folder is also used to generate the bot lists. Cloning this repository will not create this folder, as it is in the `.gitignore` file, so you will need to create it yourself.

Note about `bots` and `dev`:
When making the bot lists these folders are searched recursively, so folders inside these folders will also be checked for bots. This means while developing a bot you can store different bots in different folders, and still have all of them be loaded.

## Bot development:
In the [`base.py`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/base.py) file there is a `ChessBot` class that is a base class for all Chess bots made with this. As such, all Chess bots subclass the `ChessBot` class. To keep things organized, all bots should go in the `bots` folder if they're complete, or the `dev` folder if they're still in development. Folders in these folders are also accepted, and will be searched to find bots.

When it is the bot's turn to play a move, the `turn` method in the bot's class will be run, and the current board will be passed as a [`chess.Board`](https://python-chess.readthedocs.io/en/latest/core.html#board) object. In this function the bot determine what move it wants to play and should return a [`chess.Move`](https://python-chess.readthedocs.io/en/latest/core.html#moves) object for the move it wants to play. All the calulcation involved does not need to reside in this method, however, and can be done in other methods.

If a bot needs to store information between moves, it should use the `load` and `save` methods of the `ChessBot` class. Examples of this can be found in the bots [`pi`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bots/pi.py), [`e`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bots/e.py), and [`tau`](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bots/tau.py).

Here is an example of a bot, [random_checkmate](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bots/randomcheckmate.py), that will play a random move a random piece has, however if the bot has a checkmate in 1 move it will play that instead.
```python
class RandomCheckmate(ChessBot):
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
```

### Bot rules:
If possible bots should be finding their move in under a second, just to make things go quickly. This isn't a hard requirement but more of a "It would be nice if this is the case."
There aren't really any restrictions on what strategies are and aren't allowed, and making a bot that isn't good at the game is perfectly okay. [AlphaMove](https://github.com/MrSquirrelDeDuck/chess-bots/blob/main/bots/alphamove.py) from [xkcd 3045](https://xkcd.com/3045/), for example, isn't intended to be good, and is purely silly.

### Contributing:
To add a new bot to the bot list, you can either create a pull request to add one, or if you know me you can send me your code and I can add it if you don't want to work with GitHub.

## Setting up
To setup the repository and start making Chess bots:
1. Install the [Git command line interface](https://git-scm.com/downloads) if you have not already.
2. Create a new folder where you want to put the code.
3. Open up the new folder in the terminal or Git Bash.
4. Clone the repository to this folder with the command `git clone https://github.com/MrSquirrelDeDuck/chess-bots/`.
5. Open up the `chess-bots` folder that was created.
6. Create a new folder in the `chess-bots` folder named `dev`, this is where your mid-development bots will reside.
7. Create a new Python file in the `dev` folder and open it up in your code editor of choice.
8. Type or paste the following into the new file and save it:
    ```python
    import typing
    import chess

    import base

    class MyBot(base.ChessBot):
        def turn(
                self: typing.Self,
                board: chess.Board
            ) -> chess.Move:
            pass
    ```
Now you're ready to go! You can replace the `pass` with your bot's code, and can use this file (or any file in the `bots` folder) as a base to create your bot!