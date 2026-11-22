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


def ask_menu(can_replay):
    """Show the menu and return the valid choice of the player.

    Parameters:
        can_replay (bool): True if a game was already played

    Returns:
        str: "1" new game, "2" replay the last game, "3" quit
    """
    print()
    print("1 - New game")
    if can_replay:
        print("2 - Replay the last game (same level and seed)")
    print("3 - Quit")
    while True:
        answer = input("Your choice: ").strip()
        if answer == "1" or answer == "3" or (answer == "2" and can_replay):
            return answer
        print("Please type one of the numbers shown.")


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
    choice = ""
    while choice != "3":
        choice = ask_menu(last_settings is not None)
        if choice == "1":
            last_settings = choose_level()
            play_game(last_settings)
        elif choice == "2":
            play_game(last_settings)     # same seed -> same board
    print("Goodbye!")


if __name__ == "__main__":
    main()
