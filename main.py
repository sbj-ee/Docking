import curses
import time
import sys
from math import sqrt


def init_curses():
    """Initialize curses and set up the screen."""
    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    curses.curs_set(0)  # Hide cursor
    return stdscr


def draw_target(stdscr, target_x, target_y):
    """Draw the docking target."""
    stdscr.addstr(target_y - 1, target_x - 2, "  +  ")
    stdscr.addstr(target_y, target_x - 2, "<- O ->")
    stdscr.addstr(target_y + 1, target_x - 2, "  +  ")


def draw_vehicle(stdscr, vehicle_x, vehicle_y):
    """Draw the approaching vehicle."""
    stdscr.addstr(vehicle_y, vehicle_x, "V")


def calculate_distance(vehicle_x, vehicle_y, target_x, target_y):
    """Calculate distance between vehicle and target."""
    return sqrt((vehicle_x - target_x) ** 2 + (vehicle_y - target_y) ** 2)


def main(stdscr):
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()

    # Initial positions
    target_x, target_y = max_x // 2, max_y // 2
    vehicle_x, vehicle_y = max_x // 4, max_y // 4
    velocity_x, velocity_y = 0, 0

    # Control parameters
    max_velocity = 1.0
    docking_threshold = 2.0

    stdscr.timeout(100)  # Non-blocking input with 100ms timeout

    while True:
        stdscr.clear()

        # Draw objects
        draw_target(stdscr, target_x, target_y)
        draw_vehicle(stdscr, vehicle_x, vehicle_y)

        # Display status
        distance = calculate_distance(vehicle_x, vehicle_y, target_x, target_y)
        stdscr.addstr(0, 0, f"Distance to target: {distance:.2f}")
        stdscr.addstr(1, 0, f"Velocity X: {velocity_x:.2f}, Y: {velocity_y:.2f}")
        stdscr.addstr(2, 0, "Controls: Arrows (move), Space (stop), Q (quit)")

        # Check docking condition
        if distance < docking_threshold:
            stdscr.addstr(4, 0, "DOCKING SUCCESSFUL!")
            stdscr.refresh()
            time.sleep(2)
            break

        # Handle input
        try:
            key = stdscr.getch()
        except:
            key = -1

        # Process controls
        if key == curses.KEY_UP:
            velocity_y = max(-max_velocity, velocity_y - 0.1)
        elif key == curses.KEY_DOWN:
            velocity_y = min(max_velocity, velocity_y + 0.1)
        elif key == curses.KEY_LEFT:
            velocity_x = max(-max_velocity, velocity_x - 0.1)
        elif key == curses.KEY_RIGHT:
            velocity_x = min(max_velocity, velocity_x + 0.1)
        elif key == ord(" "):
            velocity_x, velocity_y = 0, 0
        elif key == ord("q") or key == ord("Q"):
            break

        # Update vehicle position
        vehicle_x = max(0, min(max_x - 1, vehicle_x + velocity_x))
        vehicle_y = max(0, min(max_y - 1, vehicle_y + velocity_y))

        # Check for collision with boundaries
        if (
            vehicle_x <= 0
            or vehicle_x >= max_x - 1
            or vehicle_y <= 0
            or vehicle_y >= max_y - 1
        ):
            stdscr.addstr(4, 0, "COLLISION DETECTED!")
            stdscr.refresh()
            time.sleep(2)
            break

        stdscr.refresh()

        # Small delay for smooth animation
        time.sleep(0.05)


if __name__ == "__main__":
    try:
        stdscr = init_curses()
        main(stdscr)
    finally:
        # Clean up curses
        curses.cbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
