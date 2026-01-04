import curses
import time
import sys
from math import sqrt
from dataclasses import dataclass


# Default physics constants (used as base for difficulties)
THRUST_POWER = 0.05  # Acceleration per thrust
MAX_VELOCITY = 2.0  # Maximum velocity in any direction
FUEL_PER_THRUST = 1.0  # Fuel consumed per thrust
INITIAL_FUEL = 100.0  # Starting fuel
DOCKING_THRESHOLD = 2.0  # Distance to dock successfully
DOCKING_MAX_VELOCITY = 0.5  # Max velocity for safe docking

# Color pair constants
COLOR_NORMAL = 1
COLOR_SUCCESS = 2
COLOR_WARNING = 3
COLOR_DANGER = 4
COLOR_TARGET = 5
COLOR_VEHICLE = 6

# Scoring constants
SCORE_FUEL_MULTIPLIER = 10  # Points per unit of fuel remaining
SCORE_SOFT_DOCK_BONUS = 200  # Bonus for very gentle docking
SCORE_SOFT_DOCK_THRESHOLD = 0.2  # Speed threshold for soft dock bonus


@dataclass
class Difficulty:
    """Difficulty settings for the game."""
    name: str
    fuel: float
    thrust_power: float
    fuel_per_thrust: float
    docking_threshold: float
    docking_max_velocity: float
    start_distance_factor: float  # Multiplier for starting distance
    score_multiplier: float  # Multiplier for final score


# Difficulty presets
DIFFICULTIES = {
    1: Difficulty(
        name="EASY",
        fuel=150.0,
        thrust_power=0.08,
        fuel_per_thrust=0.5,
        docking_threshold=3.0,
        docking_max_velocity=0.8,
        start_distance_factor=0.5,
        score_multiplier=0.5,
    ),
    2: Difficulty(
        name="NORMAL",
        fuel=100.0,
        thrust_power=0.05,
        fuel_per_thrust=1.0,
        docking_threshold=2.0,
        docking_max_velocity=0.5,
        start_distance_factor=1.0,
        score_multiplier=1.0,
    ),
    3: Difficulty(
        name="HARD",
        fuel=75.0,
        thrust_power=0.04,
        fuel_per_thrust=1.5,
        docking_threshold=1.5,
        docking_max_velocity=0.3,
        start_distance_factor=1.5,
        score_multiplier=1.5,
    ),
    4: Difficulty(
        name="EXPERT",
        fuel=50.0,
        thrust_power=0.03,
        fuel_per_thrust=2.0,
        docking_threshold=1.0,
        docking_max_velocity=0.2,
        start_distance_factor=2.0,
        score_multiplier=2.0,
    ),
}


def init_curses():
    """Initialize curses and set up the screen."""
    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    curses.curs_set(0)  # Hide cursor

    # Initialize colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_NORMAL, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_SUCCESS, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_WARNING, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_DANGER, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_TARGET, curses.COLOR_CYAN, -1)
        curses.init_pair(COLOR_VEHICLE, curses.COLOR_MAGENTA, -1)

    return stdscr


def get_fuel_color(fuel, max_fuel):
    """Get color based on fuel level."""
    percentage = fuel / max_fuel
    if percentage > 0.5:
        return COLOR_SUCCESS
    elif percentage > 0.2:
        return COLOR_WARNING
    else:
        return COLOR_DANGER


def get_speed_color(speed, distance):
    """Get color based on speed and distance to target."""
    if distance < 10:
        if speed <= DOCKING_MAX_VELOCITY:
            return COLOR_SUCCESS
        elif speed <= DOCKING_MAX_VELOCITY * 2:
            return COLOR_WARNING
        else:
            return COLOR_DANGER
    return COLOR_NORMAL


def get_distance_color(distance):
    """Get color based on distance to target."""
    if distance < DOCKING_THRESHOLD:
        return COLOR_SUCCESS
    elif distance < 10:
        return COLOR_WARNING
    else:
        return COLOR_NORMAL


def draw_target(stdscr, target_x, target_y):
    """Draw the docking target."""
    color = curses.color_pair(COLOR_TARGET)
    stdscr.addstr(target_y - 1, target_x - 2, "  +  ", color)
    stdscr.addstr(target_y, target_x - 2, "<- O ->", color)
    stdscr.addstr(target_y + 1, target_x - 2, "  +  ", color)


def draw_vehicle(stdscr, vehicle_x, vehicle_y):
    """Draw the approaching vehicle."""
    color = curses.color_pair(COLOR_VEHICLE) | curses.A_BOLD
    stdscr.addstr(int(vehicle_y), int(vehicle_x), "V", color)


def draw_fuel_gauge(stdscr, fuel, max_fuel, row):
    """Draw a fuel gauge bar with color."""
    gauge_width = 20
    filled = int((fuel / max_fuel) * gauge_width)
    empty = gauge_width - filled

    fuel_color = get_fuel_color(fuel, max_fuel)

    stdscr.addstr(row, 0, "Fuel: [")
    stdscr.addstr("#" * filled, curses.color_pair(fuel_color))
    stdscr.addstr("-" * empty)
    stdscr.addstr(f"] {fuel:.1f}", curses.color_pair(fuel_color))


def calculate_distance(vehicle_x, vehicle_y, target_x, target_y):
    """Calculate distance between vehicle and target."""
    return sqrt((vehicle_x - target_x) ** 2 + (vehicle_y - target_y) ** 2)


def calculate_speed(velocity_x, velocity_y):
    """Calculate total speed from velocity components."""
    return sqrt(velocity_x ** 2 + velocity_y ** 2)


def apply_thrust(velocity, thrust, max_vel):
    """Apply thrust to velocity, respecting max velocity."""
    new_velocity = velocity + thrust
    return max(-max_vel, min(max_vel, new_velocity))


def calculate_score(fuel, speed):
    """Calculate final score based on fuel efficiency and docking speed."""
    # Base score from fuel remaining
    fuel_score = int(fuel * SCORE_FUEL_MULTIPLIER)

    # Bonus for soft docking
    soft_dock_bonus = SCORE_SOFT_DOCK_BONUS if speed <= SCORE_SOFT_DOCK_THRESHOLD else 0

    return fuel_score + soft_dock_bonus


def get_score_rating(score):
    """Get a rating string based on score."""
    if score >= 1000:
        return "EXPERT"
    elif score >= 800:
        return "EXCELLENT"
    elif score >= 600:
        return "GOOD"
    elif score >= 400:
        return "ADEQUATE"
    elif score >= 200:
        return "POOR"
    else:
        return "NOVICE"


def get_score_color(score):
    """Get color based on score."""
    if score >= 800:
        return COLOR_SUCCESS
    elif score >= 400:
        return COLOR_WARNING
    else:
        return COLOR_DANGER


def show_difficulty_menu(stdscr):
    """Display difficulty selection menu and return selected difficulty."""
    stdscr.clear()
    stdscr.timeout(-1)  # Blocking input for menu

    title_color = curses.color_pair(COLOR_TARGET) | curses.A_BOLD
    stdscr.addstr(2, 10, "=== DOCKING SIMULATOR ===", title_color)
    stdscr.addstr(4, 10, "Select Difficulty:")

    for key, diff in DIFFICULTIES.items():
        if diff.name == "EASY":
            color = curses.color_pair(COLOR_SUCCESS)
        elif diff.name == "NORMAL":
            color = curses.color_pair(COLOR_NORMAL)
        elif diff.name == "HARD":
            color = curses.color_pair(COLOR_WARNING)
        else:
            color = curses.color_pair(COLOR_DANGER)

        stdscr.addstr(6 + key, 10, f"{key}. {diff.name}", color)
        stdscr.addstr(f"  (Fuel: {diff.fuel:.0f}, Score: x{diff.score_multiplier})")

    stdscr.addstr(12, 10, "Press 1-4 to select, Q to quit")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord("q") or key == ord("Q"):
            return None
        if key in [ord("1"), ord("2"), ord("3"), ord("4")]:
            return DIFFICULTIES[int(chr(key))]


def main(stdscr, difficulty=None):
    """Main game loop."""
    # Show menu if no difficulty provided
    if difficulty is None:
        difficulty = show_difficulty_menu(stdscr)
        if difficulty is None:
            return  # User quit

    # Use difficulty settings
    fuel = difficulty.fuel
    thrust_power = difficulty.thrust_power
    fuel_per_thrust = difficulty.fuel_per_thrust
    docking_threshold = difficulty.docking_threshold
    docking_max_velocity = difficulty.docking_max_velocity
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()

    # Initial positions (use floats for smooth movement)
    # Starting position based on difficulty
    target_x, target_y = max_x // 2, max_y // 2
    start_offset_x = int((max_x // 4) * difficulty.start_distance_factor)
    start_offset_y = int((max_y // 4) * difficulty.start_distance_factor)
    vehicle_x = float(max(1, target_x - start_offset_x))
    vehicle_y = float(max(1, target_y - start_offset_y))
    velocity_x, velocity_y = 0.0, 0.0

    stdscr.timeout(100)  # Non-blocking input with 100ms timeout

    while True:
        stdscr.clear()

        # Draw objects
        draw_target(stdscr, target_x, target_y)
        draw_vehicle(stdscr, vehicle_x, vehicle_y)

        # Calculate status
        distance = calculate_distance(vehicle_x, vehicle_y, target_x, target_y)
        speed = calculate_speed(velocity_x, velocity_y)

        # Display distance with color
        dist_color = curses.color_pair(get_distance_color(distance))
        stdscr.addstr(0, 0, "Distance: ")
        stdscr.addstr(f"{distance:.1f}", dist_color)

        # Display speed with color
        speed_color = curses.color_pair(get_speed_color(speed, distance))
        stdscr.addstr("  Speed: ")
        stdscr.addstr(f"{speed:.2f}", speed_color)

        # Display velocity
        stdscr.addstr(1, 0, f"Velocity X: {velocity_x:+.2f}  Y: {velocity_y:+.2f}")

        # Draw fuel gauge
        draw_fuel_gauge(stdscr, fuel, difficulty.fuel, 2)

        # Display difficulty
        diff_color = curses.color_pair(COLOR_TARGET)
        stdscr.addstr(3, 0, f"Difficulty: {difficulty.name}", diff_color)

        # Controls help
        stdscr.addstr(4, 0, "Controls: Arrows (thrust), R (retro), Q (quit)")

        # Warning if approaching too fast
        if distance < 10 and speed > docking_max_velocity:
            warning_color = curses.color_pair(COLOR_DANGER) | curses.A_BOLD | curses.A_BLINK
            stdscr.addstr(5, 0, "WARNING: Reduce speed for docking!", warning_color)

        # Check docking condition
        if distance < docking_threshold:
            if speed <= docking_max_velocity:
                # Calculate and display score with difficulty multiplier
                base_score = calculate_score(fuel, speed)
                final_score = int(base_score * difficulty.score_multiplier)
                rating = get_score_rating(final_score)
                score_color = curses.color_pair(get_score_color(final_score)) | curses.A_BOLD

                success_color = curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD
                stdscr.addstr(6, 0, "DOCKING SUCCESSFUL!", success_color)
                stdscr.addstr(7, 0, f"Fuel remaining: {fuel:.1f}")

                # Show score breakdown
                stdscr.addstr(9, 0, "=== SCORE ===")
                stdscr.addstr(10, 0, f"Fuel bonus:      {int(fuel * SCORE_FUEL_MULTIPLIER)}")
                row = 11
                if speed <= SCORE_SOFT_DOCK_THRESHOLD:
                    stdscr.addstr(row, 0, f"Soft dock bonus: {SCORE_SOFT_DOCK_BONUS}")
                    row += 1
                stdscr.addstr(row, 0, f"Base score:      {base_score}")
                row += 1
                stdscr.addstr(row, 0, f"Difficulty x{difficulty.score_multiplier}")
                row += 1
                stdscr.addstr(row, 0, "-" * 20)
                row += 1
                stdscr.addstr(row, 0, f"TOTAL: {final_score}", score_color)
                row += 1
                stdscr.addstr(row, 0, f"Rating: {rating}", score_color)
            else:
                fail_color = curses.color_pair(COLOR_DANGER) | curses.A_BOLD
                stdscr.addstr(6, 0, "DOCKING FAILED: Too fast!", fail_color)
                stdscr.addstr(7, 0, "Score: 0", fail_color)
            stdscr.refresh()
            time.sleep(3)
            break

        # Check for out of fuel
        if fuel <= 0:
            warn_color = curses.color_pair(COLOR_WARNING) | curses.A_BOLD
            stdscr.addstr(5, 0, "OUT OF FUEL - Drifting...", warn_color)

        # Handle input
        try:
            key = stdscr.getch()
        except:
            key = -1

        # Process controls (only if fuel available)
        thrust_used = False
        if fuel > 0:
            if key == curses.KEY_UP:
                velocity_y = apply_thrust(velocity_y, -thrust_power, MAX_VELOCITY)
                thrust_used = True
            elif key == curses.KEY_DOWN:
                velocity_y = apply_thrust(velocity_y, thrust_power, MAX_VELOCITY)
                thrust_used = True
            elif key == curses.KEY_LEFT:
                velocity_x = apply_thrust(velocity_x, -thrust_power, MAX_VELOCITY)
                thrust_used = True
            elif key == curses.KEY_RIGHT:
                velocity_x = apply_thrust(velocity_x, thrust_power, MAX_VELOCITY)
                thrust_used = True
            elif key == ord("r") or key == ord("R"):
                # Retro thrust - slow down in both axes
                if abs(velocity_x) > thrust_power:
                    velocity_x = apply_thrust(
                        velocity_x,
                        thrust_power if velocity_x < 0 else -thrust_power,
                        MAX_VELOCITY,
                    )
                    thrust_used = True
                else:
                    velocity_x = 0
                if abs(velocity_y) > thrust_power:
                    velocity_y = apply_thrust(
                        velocity_y,
                        thrust_power if velocity_y < 0 else -thrust_power,
                        MAX_VELOCITY,
                    )
                    thrust_used = True
                else:
                    velocity_y = 0

        if key == ord("q") or key == ord("Q"):
            break

        # Consume fuel
        if thrust_used:
            fuel = max(0, fuel - fuel_per_thrust)

        # Update vehicle position (inertia - keeps moving)
        vehicle_x += velocity_x
        vehicle_y += velocity_y

        # Check for collision with boundaries
        if (
            vehicle_x <= 0
            or vehicle_x >= max_x - 1
            or vehicle_y <= 0
            or vehicle_y >= max_y - 1
        ):
            crash_color = curses.color_pair(COLOR_DANGER) | curses.A_BOLD
            stdscr.addstr(6, 0, "COLLISION DETECTED!", crash_color)
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
