"""Tests for the Docking app."""

import pytest
from main import (
    calculate_distance,
    calculate_speed,
    apply_thrust,
    get_fuel_color,
    get_speed_color,
    get_distance_color,
    calculate_score,
    get_score_rating,
    get_score_color,
    THRUST_POWER,
    MAX_VELOCITY,
    INITIAL_FUEL,
    FUEL_PER_THRUST,
    DOCKING_THRESHOLD,
    DOCKING_MAX_VELOCITY,
    SCORE_FUEL_MULTIPLIER,
    SCORE_SOFT_DOCK_BONUS,
    SCORE_SOFT_DOCK_THRESHOLD,
    COLOR_NORMAL,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
)


class TestCalculateDistance:
    """Tests for the calculate_distance function."""

    def test_same_position(self):
        """Distance should be 0 when positions are identical."""
        assert calculate_distance(10, 10, 10, 10) == 0

    def test_horizontal_distance(self):
        """Test horizontal distance calculation."""
        assert calculate_distance(0, 0, 3, 0) == 3.0

    def test_vertical_distance(self):
        """Test vertical distance calculation."""
        assert calculate_distance(0, 0, 0, 4) == 4.0

    def test_diagonal_distance(self):
        """Test diagonal distance (3-4-5 triangle)."""
        assert calculate_distance(0, 0, 3, 4) == 5.0

    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        assert calculate_distance(-5, -5, -2, -1) == 5.0

    def test_symmetry(self):
        """Distance should be the same regardless of direction."""
        d1 = calculate_distance(0, 0, 10, 10)
        d2 = calculate_distance(10, 10, 0, 0)
        assert d1 == d2


class TestCalculateSpeed:
    """Tests for the calculate_speed function."""

    def test_zero_velocity(self):
        """Speed should be 0 when not moving."""
        assert calculate_speed(0, 0) == 0

    def test_horizontal_only(self):
        """Speed with only horizontal velocity."""
        assert calculate_speed(5, 0) == 5.0

    def test_vertical_only(self):
        """Speed with only vertical velocity."""
        assert calculate_speed(0, 3) == 3.0

    def test_diagonal_velocity(self):
        """Speed with diagonal velocity (3-4-5 triangle)."""
        assert calculate_speed(3, 4) == 5.0

    def test_negative_velocity(self):
        """Speed should be positive regardless of direction."""
        assert calculate_speed(-3, -4) == 5.0


class TestApplyThrust:
    """Tests for the apply_thrust function."""

    def test_positive_thrust(self):
        """Applying positive thrust increases velocity."""
        result = apply_thrust(0, 0.1, MAX_VELOCITY)
        assert result == 0.1

    def test_negative_thrust(self):
        """Applying negative thrust decreases velocity."""
        result = apply_thrust(0, -0.1, MAX_VELOCITY)
        assert result == -0.1

    def test_max_velocity_clamp(self):
        """Velocity should not exceed max."""
        result = apply_thrust(MAX_VELOCITY, 0.5, MAX_VELOCITY)
        assert result == MAX_VELOCITY

    def test_min_velocity_clamp(self):
        """Velocity should not go below negative max."""
        result = apply_thrust(-MAX_VELOCITY, -0.5, MAX_VELOCITY)
        assert result == -MAX_VELOCITY

    def test_thrust_accumulation(self):
        """Multiple thrusts should accumulate."""
        velocity = 0
        velocity = apply_thrust(velocity, THRUST_POWER, MAX_VELOCITY)
        velocity = apply_thrust(velocity, THRUST_POWER, MAX_VELOCITY)
        assert velocity == 2 * THRUST_POWER


class TestDockingThreshold:
    """Tests for docking threshold logic."""

    def test_within_threshold(self):
        """Vehicle within threshold should dock successfully."""
        distance = calculate_distance(10, 10, 11, 10)
        assert distance < DOCKING_THRESHOLD

    def test_outside_threshold(self):
        """Vehicle outside threshold should not dock."""
        distance = calculate_distance(10, 10, 15, 15)
        assert distance >= DOCKING_THRESHOLD


class TestDockingVelocity:
    """Tests for safe docking velocity."""

    def test_safe_docking_speed(self):
        """Speed below threshold should allow docking."""
        speed = calculate_speed(0.3, 0.3)
        assert speed <= DOCKING_MAX_VELOCITY

    def test_unsafe_docking_speed(self):
        """Speed above threshold should fail docking."""
        speed = calculate_speed(1.0, 1.0)
        assert speed > DOCKING_MAX_VELOCITY


class TestFuelConsumption:
    """Tests for fuel consumption logic."""

    def test_initial_fuel(self):
        """Initial fuel should be set correctly."""
        assert INITIAL_FUEL == 100.0

    def test_fuel_consumption_rate(self):
        """Fuel consumption per thrust should be defined."""
        assert FUEL_PER_THRUST > 0

    def test_fuel_depletion(self):
        """Fuel should deplete with thrusts."""
        fuel = INITIAL_FUEL
        thrusts = 10
        fuel -= thrusts * FUEL_PER_THRUST
        assert fuel == INITIAL_FUEL - (thrusts * FUEL_PER_THRUST)

    def test_fuel_cannot_go_negative(self):
        """Fuel should not go below zero."""
        fuel = 5.0
        fuel = max(0, fuel - 10 * FUEL_PER_THRUST)
        assert fuel == 0


class TestPhysicsConstants:
    """Tests for physics constants."""

    def test_thrust_power_reasonable(self):
        """Thrust power should be small for gradual acceleration."""
        assert 0 < THRUST_POWER < 1

    def test_max_velocity_reasonable(self):
        """Max velocity should allow gameplay."""
        assert MAX_VELOCITY > 0

    def test_docking_max_velocity_less_than_max(self):
        """Safe docking speed should be less than max velocity."""
        assert DOCKING_MAX_VELOCITY < MAX_VELOCITY


class TestGetFuelColor:
    """Tests for get_fuel_color function."""

    def test_high_fuel_green(self):
        """High fuel (>50%) should return success color."""
        assert get_fuel_color(75, 100) == COLOR_SUCCESS

    def test_medium_fuel_yellow(self):
        """Medium fuel (20-50%) should return warning color."""
        assert get_fuel_color(35, 100) == COLOR_WARNING

    def test_low_fuel_red(self):
        """Low fuel (<20%) should return danger color."""
        assert get_fuel_color(10, 100) == COLOR_DANGER

    def test_empty_fuel_red(self):
        """Empty fuel should return danger color."""
        assert get_fuel_color(0, 100) == COLOR_DANGER


class TestGetSpeedColor:
    """Tests for get_speed_color function."""

    def test_far_away_normal(self):
        """Speed color should be normal when far from target."""
        assert get_speed_color(1.0, 50) == COLOR_NORMAL

    def test_close_slow_green(self):
        """Close and slow should return success color."""
        assert get_speed_color(0.3, 5) == COLOR_SUCCESS

    def test_close_medium_yellow(self):
        """Close and medium speed should return warning color."""
        assert get_speed_color(0.7, 5) == COLOR_WARNING

    def test_close_fast_red(self):
        """Close and fast should return danger color."""
        assert get_speed_color(2.0, 5) == COLOR_DANGER


class TestGetDistanceColor:
    """Tests for get_distance_color function."""

    def test_docking_range_green(self):
        """Within docking threshold should return success color."""
        assert get_distance_color(1.5) == COLOR_SUCCESS

    def test_approach_range_yellow(self):
        """Within approach range should return warning color."""
        assert get_distance_color(5) == COLOR_WARNING

    def test_far_normal(self):
        """Far from target should return normal color."""
        assert get_distance_color(50) == COLOR_NORMAL


class TestCalculateScore:
    """Tests for calculate_score function."""

    def test_full_fuel_soft_dock(self):
        """Full fuel with soft dock should give maximum score."""
        score = calculate_score(INITIAL_FUEL, 0.1)
        expected = int(INITIAL_FUEL * SCORE_FUEL_MULTIPLIER) + SCORE_SOFT_DOCK_BONUS
        assert score == expected

    def test_full_fuel_no_soft_dock(self):
        """Full fuel without soft dock bonus."""
        score = calculate_score(INITIAL_FUEL, 0.4)
        expected = int(INITIAL_FUEL * SCORE_FUEL_MULTIPLIER)
        assert score == expected

    def test_half_fuel_soft_dock(self):
        """Half fuel with soft dock."""
        score = calculate_score(50, 0.1)
        expected = int(50 * SCORE_FUEL_MULTIPLIER) + SCORE_SOFT_DOCK_BONUS
        assert score == expected

    def test_empty_fuel(self):
        """Empty fuel should give zero fuel score."""
        score = calculate_score(0, 0.4)
        assert score == 0

    def test_soft_dock_threshold_boundary(self):
        """Speed at threshold should get bonus."""
        score_at = calculate_score(50, SCORE_SOFT_DOCK_THRESHOLD)
        score_above = calculate_score(50, SCORE_SOFT_DOCK_THRESHOLD + 0.01)
        assert score_at > score_above


class TestGetScoreRating:
    """Tests for get_score_rating function."""

    def test_expert_rating(self):
        """Score >= 1000 should be EXPERT."""
        assert get_score_rating(1000) == "EXPERT"
        assert get_score_rating(1200) == "EXPERT"

    def test_excellent_rating(self):
        """Score 800-999 should be EXCELLENT."""
        assert get_score_rating(800) == "EXCELLENT"
        assert get_score_rating(999) == "EXCELLENT"

    def test_good_rating(self):
        """Score 600-799 should be GOOD."""
        assert get_score_rating(600) == "GOOD"
        assert get_score_rating(799) == "GOOD"

    def test_adequate_rating(self):
        """Score 400-599 should be ADEQUATE."""
        assert get_score_rating(400) == "ADEQUATE"
        assert get_score_rating(599) == "ADEQUATE"

    def test_poor_rating(self):
        """Score 200-399 should be POOR."""
        assert get_score_rating(200) == "POOR"
        assert get_score_rating(399) == "POOR"

    def test_novice_rating(self):
        """Score < 200 should be NOVICE."""
        assert get_score_rating(0) == "NOVICE"
        assert get_score_rating(199) == "NOVICE"


class TestGetScoreColor:
    """Tests for get_score_color function."""

    def test_high_score_green(self):
        """High score should return success color."""
        assert get_score_color(800) == COLOR_SUCCESS
        assert get_score_color(1000) == COLOR_SUCCESS

    def test_medium_score_yellow(self):
        """Medium score should return warning color."""
        assert get_score_color(400) == COLOR_WARNING
        assert get_score_color(799) == COLOR_WARNING

    def test_low_score_red(self):
        """Low score should return danger color."""
        assert get_score_color(0) == COLOR_DANGER
        assert get_score_color(399) == COLOR_DANGER
