"""Metrics: turn an episode log into one number each.

No MuJoCo and no file I/O in here, so everything can be unit-tested with small hand-made arrays
(tests/test_metrics.py). Inputs are what runner.run_scenario returns:
    times      (n_steps,)            simulated seconds after each step
    positions  (n_steps, n_joints)   joint angles in radians after each step
    target     (n_joints,)           goal angle per joint, radians

Only final_error is done. For the other three: replace the `raise NotImplementedError` line,
then delete the @pytest.mark.xfail marker on the matching tests and run pytest.
"""

import numpy as np


def final_error(positions: np.ndarray, target: np.ndarray) -> float:
    """Largest absolute joint error at the last logged step, in radians.

    Max rather than mean, so one bad joint cannot hide behind two good ones.
    Example: last row [0.10, -0.20], target [0.12, -0.25] -> errors [0.02, 0.05] -> 0.05
    """
    last_row = positions[-1]
    return float(np.max(np.abs(last_row - target)))


def success(
    positions: np.ndarray, target: np.ndarray, tolerance_rad: float, settle_steps: int
) -> bool:
    """True if the arm reached the goal and stayed there.

    In each of the last `settle_steps` rows of `positions`, every joint is within `tolerance_rad`
    of its target. Several rows rather than just the last one, so a run that only passes through
    the goal at the very end does not count.

    Example (settle_steps=3, tolerance 0.02, target [0, 0]):
        rows [[0.5, 0.5], [0.01, -0.01], [0.0, 0.0], [0.005, 0.0]] -> True  (last 3 rows ok)
        rows [[0.0, 0.0], [0.0, 0.0], [0.03, 0.0], [0.0, 0.0]]     -> False (0.03 is too far)
    """
    # TODO: positions[-settle_steps:], np.abs, np.all
    raise NotImplementedError("TODO: metrics.success is not implemented yet")


def time_to_goal(
    times: np.ndarray, positions: np.ndarray, target: np.ndarray, tolerance_rad: float
) -> float:
    """Simulated time (seconds) of the first row where every joint is within tolerance.

    math.inf if that never happens. First arrival only; whether the arm then stays is what
    `success` is for.

    Example (tolerance 0.02, target [0, 0]):
        times [0.1, 0.2, 0.3, 0.4], rows [[1, 1], [0.5, 0.5], [0.01, -0.01], [0, 0]] -> 0.3
        same times, rows that never get within 0.02                                  -> inf
    """
    # TODO: one bool per row (np.all over joints), check any(), np.argmax for the first True
    raise NotImplementedError("TODO: metrics.time_to_goal is not implemented yet")


def max_joint_velocity(times: np.ndarray, positions: np.ndarray) -> float:
    """Largest joint speed in rad/s over the episode, estimated from the log.

    Finite differences between consecutive rows, |q[i+1] - q[i]| / (t[i+1] - t[i]), then the max
    over all joints and steps. Computed from the logged positions rather than the simulator's
    qvel so it only depends on what is actually in the CSV.

    Example: times [0.0, 0.1, 0.2], rows [[0, 0], [0.1, 0], [0.1, -0.3]]
        speeds between rows: [[1.0, 0.0], [0.0, 3.0]] -> 3.0
    """
    # TODO: np.diff(positions, axis=0) / np.diff(times)[:, None]
    raise NotImplementedError("TODO: metrics.max_joint_velocity is not implemented yet")
