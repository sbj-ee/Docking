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
| Arrow Up | Thrust up (decrease Y velocity) |
| Arrow Down | Thrust down (increase Y velocity) |
| Arrow Left | Thrust left (decrease X velocity) |
| Arrow Right | Thrust right (increase X velocity) |
| R | Retro thrust (slow down) |
| Q | Quit |

## Objective

Navigate the vehicle `V` to dock with the target `O`.

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

## Running Tests

```bash
pip install pytest
pytest test_main.py -v
```
