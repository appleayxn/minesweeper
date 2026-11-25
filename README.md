# Minesweeper (text version)

Final project for *Algorithms and Programming 1*, UFAZ.

**Team:** Zeynalzada Ayxan, Maharramli Anvar, Qurbanli Elton, Nuruzada Nihat, Hamzayev Altair

## Run

```
python main.py
```

Python 3.7 or later. No library to install (only `random` and `time` from the standard library are allowed).

## Commands

| Command | Effect |
|---|---|
| `R E5` | reveal cell E5 |
| `F C3` | put or remove a flag on C3 |
| `D` | debug: show all mines, the game continues |
| `H` | help |
| `Q` | quit the current game |
| `HINT` | show a safe cell (extra) |

Commands are not case-sensitive. Symbols: `#` hidden, `F` flag, `.` empty, `1`-`8` mines around, `*` mine, `X` mine hit, `!` wrong flag.

## Optional extras

- `HINT` command: shows a safe hidden cell next to the open area.
- Timer and scoreboard of best times (dictionary), saved in `scores.txt`; menu option 4.
- Safe start: menu option 5, no mine on the first cell and its 8 neighbours.
- Custom board size (level 4): 5 to 20 rows and columns, at most 25 % of mines.

## Demo

Level 1, seed 7, first move `R E5` gives exactly the example board of the assignment.

## Files

| File | Content |
|---|---|
| `main.py` | entry point, play again / quit |
| `board.py` | constants, board, mines, neighbours, numbers |
| `game_logic.py` | game state, reveal (flood fill), flags, win / loss, one game |
| `interface.py` | level and seed, display, command parsing, help |
| `scores.py` | extra: best times in a dictionary, saved in `scores.txt` |
| `report/main.tex` | report template (Overleaf) |
