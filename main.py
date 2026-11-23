"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: main.py
Role: program entry point and menu (new game, replay, quit)

Run with:  python main.py   (Python 3.7 or later)
"""

from interface import choose_level
from game_logic import play_game
from scores import (SCORES_FILE, board_key, load_scores, save_scores,
                    update_scores, show_scores)


def ask_menu(can_replay):
    """Show the menu and return the valid choice of the player.

    Parameters:
        can_replay (bool): True if a game was already played

    Returns:
        str: "1" new game, "2" replay the last game, "3" quit,
             "4" best times (extra)
    """
    print()
    print("1 - New game")
    if can_replay:
        print("2 - Replay the last game (same level and seed)")
    print("3 - Quit")
    print("4 - Best times")
    while True:
        answer = input("Your choice: ").strip()
        if answer in ("1", "3", "4") or (answer == "2" and can_replay):
            return answer
        print("Please type one of the numbers shown.")


def record_time(settings, seconds, scores):
    """OPTIONAL EXTRA - save the time of a won game if it is a record.

    Parameters:
        settings (tuple): (rows, cols, nb_mines, seed) of the game
        seconds (int): time of the game, or None if it was not won
        scores (dict): the scoreboard (changed in place)

    Returns:
        None
    """
    if seconds is None:
        return
    key = board_key(settings[0], settings[1], settings[2])
    if update_scores(scores, key, seconds):
        print("New best time for " + key + "!")
        save_scores(scores, SCORES_FILE)


def main():
    """Show the title, then the menu until the player quits.

    Returns:
        None
    """
    print("=" * 30)
    print("         MINESWEEPER")
    print("=" * 30)
    print("Type H during the game to see the commands.")
    last_settings = None                 # (rows, cols, nb_mines, seed)
    scores = load_scores(SCORES_FILE)    # extra: best times
    choice = ""
    while choice != "3":
        choice = ask_menu(last_settings is not None)
        if choice == "1":
            last_settings = choose_level()
            record_time(last_settings, play_game(last_settings), scores)
        elif choice == "2":                # same seed -> same board
            record_time(last_settings, play_game(last_settings), scores)
        elif choice == "4":
            show_scores(scores)
    print("Goodbye!")


if __name__ == "__main__":
    main()
