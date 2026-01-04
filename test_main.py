"""Tests for the Docking app."""

import pytest
from unittest.mock import MagicMock, patch
from main import calculate_distance


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


class TestDockingThreshold:
    """Tests for docking threshold logic."""

    def test_within_threshold(self):
        """Vehicle within threshold should dock successfully."""
        docking_threshold = 2.0
        distance = calculate_distance(10, 10, 11, 10)
        assert distance < docking_threshold

    def test_outside_threshold(self):
        """Vehicle outside threshold should not dock."""
        docking_threshold = 2.0
        distance = calculate_distance(10, 10, 15, 15)
        assert distance >= docking_threshold


class TestVelocityBounds:
    """Tests for velocity clamping logic."""

    def test_velocity_clamp_max(self):
        """Velocity should not exceed max."""
        max_velocity = 1.0
        velocity = 0.5
        velocity = min(max_velocity, velocity + 0.1)
        assert velocity <= max_velocity

    def test_velocity_clamp_min(self):
        """Velocity should not go below negative max."""
        max_velocity = 1.0
        velocity = -0.5
        velocity = max(-max_velocity, velocity - 0.1)
        assert velocity >= -max_velocity


class TestPositionBounds:
    """Tests for position boundary logic."""

    def test_position_clamp_min(self):
        """Position should not go below 0."""
        max_x = 80
        position_x = -5
        position_x = max(0, min(max_x - 1, position_x))
        assert position_x == 0

    def test_position_clamp_max(self):
        """Position should not exceed screen bounds."""
        max_x = 80
        position_x = 100
        position_x = max(0, min(max_x - 1, position_x))
        assert position_x == max_x - 1

    def test_position_within_bounds(self):
        """Position within bounds should remain unchanged."""
        max_x = 80
        position_x = 40
        result = max(0, min(max_x - 1, position_x))
        assert result == 40
