"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: main.py
Role: start of the program and menu (new game, replay, quit)

Run with:  python main.py   (Python 3.7 or later)
"""

from interface import choose_level
from game_logic import play_game
from scores import board_key, update_scores, show_scores


def ask_menu(can_replay):
    """Show the menu and return the choice of the player.

    Parameters:
        can_replay (bool): True if a game was already played

    Returns:
        str: "1" new game, "2" replay the last game, "3" quit,
             "4" best times (extra)
    """
    print()
    print("1 - New game")
    if can_replay == True:
        print("2 - Replay the last game (same level and seed)")
    print("3 - Quit")
    print("4 - Best times")

    choice = ""
    while choice == "":
        answer = input("Your choice: ")
        answer = answer.strip()
        if answer == "1" or answer == "3" or answer == "4":
            choice = answer
        elif answer == "2" and can_replay == True:
            choice = answer
        else:
            print("Please type one of the numbers shown.")
    return choice


def record_time(settings, seconds, scores):
    """OPTIONAL EXTRA - save the time of a won game if it is a record.

    Parameters:
        settings (tuple): (rows, cols, nb_mines, seed) of the game
        seconds (int): time of the game, or None if the game was not won
        scores (dict): the best times (it is changed)

    Returns:
        None
    """
    if seconds == None:
        return
    key = board_key(settings[0], settings[1], settings[2])
    is_record = update_scores(scores, key, seconds)
    if is_record == True:
        print("New best time for " + key + "!")


def main():
    """Show the title, then the menu until the player quits.

    If the input is closed (Ctrl+Z then Enter on Windows) or the player
    presses Ctrl+C, the program stops with a message instead of crashing.

    Returns:
        None
    """
    print("=" * 30)
    print("         MINESWEEPER")
    print("=" * 30)
    print("Type H during the game to see the commands.")

    try:
        last_settings = None                  # (rows, cols, nb_mines, seed)
        scores = {}                           # extra: best times (board -> seconds)

        choice = ""
        while choice != "3":
            can_replay = False
            if last_settings != None:
                can_replay = True
            choice = ask_menu(can_replay)

            if choice == "1":
                last_settings = choose_level()
                seconds = play_game(last_settings)
                record_time(last_settings, seconds, scores)
            elif choice == "2":
                # same settings and same seed -> same board
                seconds = play_game(last_settings)
                record_time(last_settings, seconds, scores)
            elif choice == "4":
                show_scores(scores)
        print("Goodbye!")
    except EOFError:
        # the input was closed: there is nothing more to read
        print()
        print("The input was closed. Goodbye!")
    except KeyboardInterrupt:
        # the player pressed Ctrl+C
        print()
        print("The program was stopped. Goodbye!")


main()
