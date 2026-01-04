# Docking

A terminal-based spacecraft docking simulator using Python curses.

## Requirements

- Python 3.x
- curses (included in Python standard library)

## Usage

```bash
python3 main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Up | Decrease Y velocity (move up) |
| Arrow Down | Increase Y velocity (move down) |
| Arrow Left | Decrease X velocity (move left) |
| Arrow Right | Increase X velocity (move right) |
| Space | Stop (zero velocity) |
| Q | Quit |

## Objective

Navigate the vehicle `V` to dock with the target `O`. The docking is successful when the vehicle is within the threshold distance of the target.

Avoid colliding with the screen boundaries.
