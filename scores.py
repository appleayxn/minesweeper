"""
Minesweeper - Algorithms and Programming 1 - UFAZ
Team: Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton,
      Nuruzada Nihat, Hamzayev Altair
File: scores.py
Role: OPTIONAL EXTRA - best times kept in a dictionary
      and saved in the text file scores.txt
"""

from interface import is_number

SCORES_FILE = "scores.txt"    # the file is next to main.py


def board_key(rows, cols, nb_mines):
    """Make the name of a board for the scoreboard, e.g. '9x9, 10 mines'.

    Parameters:
        rows (int): number of rows
        cols (int): number of columns
        nb_mines (int): number of mines

    Returns:
        str: the key used in the dictionary of best times
    """
    return str(rows) + "x" + str(cols) + ", " + str(nb_mines) + " mines"


def load_scores(filename):
    """Read the best times from the text file.

    Each line of the file looks like this:   9x9, 10 mines;42
    (the name of the board, then ";", then the time in seconds).
    The first time, the file does not exist yet: then we return
    an empty dictionary.

    Parameters:
        filename (str): name of the file

    Returns:
        dict: board key (str) -> best time in seconds (int)
    """
    scores = {}
    try:
        file = open(filename, "r")      # "r" = open the file to read it
        lines = file.readlines()        # a list with all the lines
        file.close()                    # always close the file
    except FileNotFoundError:
        return scores                   # no file yet: no best times

    for line in lines:
        line = line.strip()             # remove the "\n" at the end
        parts = line.split(";")         # "9x9, 10 mines;42" -> ["9x9, 10 mines", "42"]
        if len(parts) == 2:
            key = parts[0]
            seconds = parts[1]
            if is_number(seconds):      # a wrong line is ignored
                scores[key] = int(seconds)
    return scores


def save_scores(scores, filename):
    """Write all the best times in the text file, one line per board.

    Parameters:
        scores (dict): board key -> best time in seconds
        filename (str): name of the file

    Returns:
        None
    """
    file = open(filename, "w")          # "w" = write: the old content is erased
    for key in scores:
        line = key + ";" + str(scores[key]) + "\n"    # "\n" = go to a new line
        file.write(line)
    file.close()                        # always close the file


def update_scores(scores, key, seconds):
    """Keep the new time if it is the best time for this board.

    Parameters:
        scores (dict): board key -> best time (it is changed)
        key (str): the name of the board
        seconds (int): the time of the game that was won

    Returns:
        bool: True if it is a new record
    """
    if key not in scores:
        scores[key] = seconds
        return True
    if seconds < scores[key]:
        scores[key] = seconds
        return True
    return False


def show_scores(scores):
    """Print the best time of every board.

    Parameters:
        scores (dict): board key -> best time in seconds

    Returns:
        None
    """
    print()
    print("Best times:")
    if len(scores) == 0:
        print("  no game won yet")
    for key in scores:
        print("  " + key + ": " + str(scores[key]) + " s")
