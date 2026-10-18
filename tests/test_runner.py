"""Tests for sim_vv/runner.py itself (not the requirements): errors, seeding, and the CSV."""

import csv

import numpy as np
import pytest

from sim_vv.runner import run_scenario
from sim_vv.scenario import Scenario


def make_scenario(**overrides) -> Scenario:
    """A short valid scenario built in code; each test changes one field."""
    fields = {
        "name": "unit",
        "description": "built inside a test",
        "seed": 0,
        "episode_steps": 20,
        "target_qpos_rad": [0.0, 0.0, 0.0],
        "tolerance_rad": 0.01,
    }
    fields.update(overrides)
    return Scenario(**fields)


def test_wrong_number_of_targets_is_a_clear_error(tmp_path):
    scenario = make_scenario(target_qpos_rad=[0.0, 0.0])  # the arm has 3 joints
    with pytest.raises(ValueError, match="3 joints"):
        run_scenario(scenario, results_dir=tmp_path)


def test_seed_changes_the_start_pose(tmp_path):
    _, positions_a = run_scenario(make_scenario(seed=0), results_dir=tmp_path)
    _, positions_b = run_scenario(make_scenario(seed=1), results_dir=tmp_path)
    assert not np.array_equal(positions_a[0], positions_b[0])


def test_csv_is_an_exact_copy_of_the_returned_arrays(tmp_path):
    scenario = make_scenario()
    times, positions = run_scenario(scenario, results_dir=tmp_path)

    with open(tmp_path / "unit.csv", newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]

    assert header == ["step", "time_s", "q_shoulder", "q_elbow", "q_wrist"]
    logged = np.array([[float(value) for value in row] for row in body])
    assert np.array_equal(logged[:, 0], np.arange(scenario.episode_steps))
    assert np.array_equal(logged[:, 1], times)
    assert np.array_equal(logged[:, 2:], positions)
