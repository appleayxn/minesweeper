"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: main.py
Role: program entry point, play again or quit

Run with:  python main.py   (Python 3.7 or later)
"""

from game_logic import play_game


def ask_play_again():
    """Ask the player if they want another game.

    Returns:
        bool: True for a new game, False to quit
    """
    while True:
        answer = input("\nPlay again? (Y/N): ").strip().upper()
        if answer in ("Y", "YES"):
            return True
        if answer in ("N", "NO"):
            return False
        print("Please answer Y or N.")


def main():
    """Show the title, then play games until the player quits.

    Returns:
        None
    """
    print("=" * 30)
    print("         MINESWEEPER")
    print("=" * 30)
    print("Type H during the game to see the commands.")
    playing = True
    while playing:
        finished = play_game()
        if finished:
            playing = ask_play_again()
        else:
            playing = False              # the player typed Q
    print("Goodbye!")


if __name__ == "__main__":
    main()
