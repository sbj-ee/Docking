import curses
import time
import sys
from math import sqrt


# Physics constants
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


def main(stdscr):
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()

    # Initial positions (use floats for smooth movement)
    target_x, target_y = max_x // 2, max_y // 2
    vehicle_x, vehicle_y = float(max_x // 4), float(max_y // 4)
    velocity_x, velocity_y = 0.0, 0.0

    # Fuel
    fuel = INITIAL_FUEL

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
        draw_fuel_gauge(stdscr, fuel, INITIAL_FUEL, 2)

        # Controls help
        stdscr.addstr(3, 0, "Controls: Arrows (thrust), R (retro), Q (quit)")

        # Warning if approaching too fast
        if distance < 10 and speed > DOCKING_MAX_VELOCITY:
            warning_color = curses.color_pair(COLOR_DANGER) | curses.A_BOLD | curses.A_BLINK
            stdscr.addstr(4, 0, "WARNING: Reduce speed for docking!", warning_color)

        # Check docking condition
        if distance < DOCKING_THRESHOLD:
            if speed <= DOCKING_MAX_VELOCITY:
                success_color = curses.color_pair(COLOR_SUCCESS) | curses.A_BOLD
                stdscr.addstr(5, 0, "DOCKING SUCCESSFUL!", success_color)
                stdscr.addstr(6, 0, f"Fuel remaining: {fuel:.1f}", success_color)
            else:
                fail_color = curses.color_pair(COLOR_DANGER) | curses.A_BOLD
                stdscr.addstr(5, 0, "DOCKING FAILED: Too fast!", fail_color)
            stdscr.refresh()
            time.sleep(2)
            break

        # Check for out of fuel
        if fuel <= 0:
            warn_color = curses.color_pair(COLOR_WARNING) | curses.A_BOLD
            stdscr.addstr(4, 0, "OUT OF FUEL - Drifting...", warn_color)

        # Handle input
        try:
            key = stdscr.getch()
        except:
            key = -1

        # Process controls (only if fuel available)
        thrust_used = False
        if fuel > 0:
            if key == curses.KEY_UP:
                velocity_y = apply_thrust(velocity_y, -THRUST_POWER, MAX_VELOCITY)
                thrust_used = True
            elif key == curses.KEY_DOWN:
                velocity_y = apply_thrust(velocity_y, THRUST_POWER, MAX_VELOCITY)
                thrust_used = True
            elif key == curses.KEY_LEFT:
                velocity_x = apply_thrust(velocity_x, -THRUST_POWER, MAX_VELOCITY)
                thrust_used = True
            elif key == curses.KEY_RIGHT:
                velocity_x = apply_thrust(velocity_x, THRUST_POWER, MAX_VELOCITY)
                thrust_used = True
            elif key == ord("r") or key == ord("R"):
                # Retro thrust - slow down in both axes
                if abs(velocity_x) > THRUST_POWER:
                    velocity_x = apply_thrust(
                        velocity_x,
                        THRUST_POWER if velocity_x < 0 else -THRUST_POWER,
                        MAX_VELOCITY,
                    )
                    thrust_used = True
                else:
                    velocity_x = 0
                if abs(velocity_y) > THRUST_POWER:
                    velocity_y = apply_thrust(
                        velocity_y,
                        THRUST_POWER if velocity_y < 0 else -THRUST_POWER,
                        MAX_VELOCITY,
                    )
                    thrust_used = True
                else:
                    velocity_y = 0

        if key == ord("q") or key == ord("Q"):
            break

        # Consume fuel
        if thrust_used:
            fuel = max(0, fuel - FUEL_PER_THRUST)

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
            stdscr.addstr(5, 0, "COLLISION DETECTED!", crash_color)
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
