"""Requirement checks: one test per REQ in requirements.md, run against every scenario file.

Thresholds that are the same for every scenario live here as constants AND in requirements.md;
keep the two in sync (test_traceability.py checks the IDs, not the numbers). Per-scenario
thresholds (tolerance_rad) come from the scenario file itself.
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from sim_vv.metrics import final_error, max_joint_velocity, time_to_goal
from sim_vv.runner import run_scenario
from sim_vv.scenario import load_scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILES = sorted((ROOT / "scenarios").glob("*.yaml"))

# REQ-003: the goal must be reached within the first half of the episode, so that the second
# half is evidence that the arm holds position.
TIME_TO_GOAL_MAX_FRACTION = 0.5
# REQ-004: joint speed cap in rad/s; just under 180 deg/s (3.14 rad/s). See requirements.md.
MAX_JOINT_VELOCITY_RAD_S = 3.0

# Applies to every test in this file: each one runs once per scenario file, and the file's
# stem shows up in the test id, e.g. test_req_002_final_error_within_tolerance[reach_small].
pytestmark = pytest.mark.parametrize("scenario_path", SCENARIO_FILES, ids=lambda p: p.stem)


def run(scenario_path, results_dir):
    """Load and run one scenario; returns everything a requirement check needs."""
    scenario = load_scenario(scenario_path)
    times, positions = run_scenario(scenario, results_dir=results_dir)
    target = np.array(scenario.target_qpos_rad)
    return scenario, times, positions, target


def test_req_001_same_seed_same_trajectory(scenario_path, tmp_path):
    """REQ-001: running a scenario twice gives bit-for-bit identical logs."""
    _, times_a, positions_a, _ = run(scenario_path, tmp_path / "a")
    _, times_b, positions_b, _ = run(scenario_path, tmp_path / "b")
    assert np.array_equal(times_a, times_b)
    assert np.array_equal(positions_a, positions_b)


def test_req_002_final_error_within_tolerance(scenario_path, tmp_path):
    """REQ-002: at the last step, every joint is within the scenario's tolerance."""
    scenario, _, positions, target = run(scenario_path, tmp_path)
    assert final_error(positions, target) <= scenario.tolerance_rad


@pytest.mark.xfail(
    raises=NotImplementedError,
    strict=True,
    reason="TODO(student): implement metrics.time_to_goal, then delete this marker",
)
def test_req_003_reaches_goal_in_first_half(scenario_path, tmp_path):
    """REQ-003: the arm first comes within tolerance no later than halfway through the episode."""
    scenario, times, positions, target = run(scenario_path, tmp_path)
    reached_at = time_to_goal(times, positions, target, scenario.tolerance_rad)
    assert reached_at <= TIME_TO_GOAL_MAX_FRACTION * times[-1]


@pytest.mark.xfail(
    raises=NotImplementedError,
    strict=True,
    reason="TODO(student): implement metrics.max_joint_velocity, then delete this marker",
)
def test_req_004_joint_speed_under_limit(scenario_path, tmp_path):
    """REQ-004: no joint ever moves faster than the speed cap."""
    _, times, positions, _ = run(scenario_path, tmp_path)
    assert max_joint_velocity(times, positions) <= MAX_JOINT_VELOCITY_RAD_S


def test_req_005_log_is_complete(scenario_path, tmp_path):
    """REQ-005: the CSV has one row per step, one column per joint, and no NaN or inf."""
    scenario, _, positions, _ = run(scenario_path, tmp_path)
    with open(tmp_path / f"{scenario.name}.csv", newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    assert len(header) == 2 + positions.shape[1]  # step, time_s, then one column per joint
    assert len(body) == scenario.episode_steps
    values = np.array([[float(value) for value in row] for row in body])
    assert np.isfinite(values).all()
