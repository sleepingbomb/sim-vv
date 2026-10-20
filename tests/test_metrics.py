"""Unit tests for sim_vv/metrics.py with hand-computed expected values.

The three metrics that are not written yet already have tests, marked
xfail(raises=NotImplementedError, strict=True). raises= means only the stub's exception counts
as expected, so a wrong implementation still fails; strict= means that once the implementation
passes, pytest reports XPASS(strict) as a failure until the marker is removed.

Compare floats with pytest.approx; in binary floating point 0.25 - 0.20 comes out as
0.04999999999999999.
"""

import math

import numpy as np
import pytest

from sim_vv.metrics import final_error, max_joint_velocity, success, time_to_goal


def test_final_error_is_the_largest_joint_error_at_the_last_step():
    positions = np.array([[0.0, 0.0], [0.10, -0.20]])  # only the last row matters
    target = np.array([0.12, -0.25])
    # |0.10 - 0.12| = 0.02, |-0.20 - (-0.25)| = 0.05 -> 0.05
    assert final_error(positions, target) == pytest.approx(0.05)


@pytest.mark.xfail(
    raises=NotImplementedError,
    strict=True,
    reason="TODO: implement metrics.success, then delete this marker",
)
def test_success_requires_staying_within_tolerance_for_the_last_steps():
    target = np.array([0.0, 0.0])
    settled = np.array([[0.5, 0.5], [0.01, -0.01], [0.0, 0.0], [0.005, 0.0]])
    assert success(settled, target, tolerance_rad=0.02, settle_steps=3)
    # third-from-last row is 0.03 off: passed through the goal, did not stay
    wobbled = np.array([[0.0, 0.0], [0.0, 0.0], [0.03, 0.0], [0.0, 0.0]])
    assert not success(wobbled, target, tolerance_rad=0.02, settle_steps=3)


@pytest.mark.xfail(
    raises=NotImplementedError,
    strict=True,
    reason="TODO: implement metrics.time_to_goal, then delete this marker",
)
def test_time_to_goal_is_the_first_time_all_joints_are_within_tolerance():
    times = np.array([0.1, 0.2, 0.3, 0.4])
    target = np.array([0.0, 0.0])
    positions = np.array([[1.0, 1.0], [0.5, 0.5], [0.01, -0.01], [0.0, 0.0]])
    assert time_to_goal(times, positions, target, tolerance_rad=0.02) == pytest.approx(0.3)
    never_arrives = np.ones((4, 2))
    assert time_to_goal(times, never_arrives, target, tolerance_rad=0.02) == math.inf


@pytest.mark.xfail(
    raises=NotImplementedError,
    strict=True,
    reason="TODO: implement metrics.max_joint_velocity, then delete this marker",
)
def test_max_joint_velocity_uses_finite_differences():
    times = np.array([0.0, 0.1, 0.2])
    positions = np.array([[0.0, 0.0], [0.1, 0.0], [0.1, -0.3]])
    # rows 0 -> 1: joint 0 moves 0.1 rad in 0.1 s = 1.0 rad/s
    # rows 1 -> 2: joint 1 moves 0.3 rad in 0.1 s = 3.0 rad/s, the max
    assert max_joint_velocity(times, positions) == pytest.approx(3.0)
