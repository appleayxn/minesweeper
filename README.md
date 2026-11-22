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
| `Q` | quit |

Commands are not case-sensitive. Symbols: `#` hidden, `F` flag, `.` empty, `1`–`8` mines around, `*` mine, `X` mine hit, `!` wrong flag.

## Files

| File | Content |
|---|---|
| `main.py` | entry point, play again / quit |
| `board.py` | constants, board, mines, neighbours, numbers |
| `game_logic.py` | game state, reveal (flood fill), flags, win / loss, one game |
| `interface.py` | level and seed, display, command parsing, help |
| `report/main.tex` | report template (Overleaf) |
