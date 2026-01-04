# Docking

A terminal-based spacecraft docking simulator using Python curses.

## Requirements

- Python 3.x
- curses (included in Python standard library)
- Terminal with Unicode support

## Usage

```bash
python3 main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Up | Thrust up (decrease Y velocity) |
| Arrow Down | Thrust down (increase Y velocity) |
| Arrow Left | Thrust left (decrease X velocity) |
| Arrow Right | Thrust right (increase X velocity) |
| R | Retro thrust (slow down) |
| H | View high scores (from menu) |
| Y/N | Play again prompt |
| Q | Quit |

## Objective

Navigate your spacecraft to dock with the station port.

```
  ╔═══╗            ▲
  ║   ║           ◄█►
══╣ ◎ ╠══          ▼
  ║   ║        Spacecraft
  ╚═══╝
Docking Port
```

### Success Conditions
- Be within docking threshold distance of target
- Approach speed must be below safe docking velocity

### Failure Conditions
- Collide with screen boundaries
- Approach target too fast
- Run out of fuel

## Physics

The simulation includes realistic space physics:

- **Inertia**: Vehicle maintains velocity until thrust is applied
- **Fuel**: Limited fuel supply - each thrust consumes fuel
- **No friction**: Vehicle will drift forever without counter-thrust

## Visual Features

- **Twinkling starfield**: Animated background with varying star brightness
- **Thrust flames**: Visual feedback when firing thrusters
- **Docking animation**: Clamp engagement sequence on successful dock
- **Explosion effects**: Animated debris on crash or failed docking
- **Color-coded HUD**: Fuel, speed, and distance indicators change color based on status

## High Scores

The game saves your top 5 scores for each difficulty level to `~/.docking_highscores.json`. Scores are displayed on the difficulty selection menu and can be viewed in detail by pressing H.

## Running Tests

```bash
pip install pytest
pytest test_main.py -v
```
