"""Turn an episode log into numbers that a requirement can be checked against.

Every function here is pure: arrays in, a number out, no MuJoCo, no files. That is what
makes them easy to unit-test with hand-computed values (see tests/test_metrics.py).

Inputs are always the arrays that runner.run_scenario returns:
    times      shape (n_steps,)            simulated seconds after each step
    positions  shape (n_steps, n_joints)   joint angles in radians after each step
    target     shape (n_joints,)           goal angle per joint, in radians

Only final_error is implemented so far. The other three are TODO: replace the
`raise NotImplementedError` line with the implementation, then remove the
@pytest.mark.xfail marker from the matching tests and run `python -m pytest`.
"""

import numpy as np


def final_error(positions: np.ndarray, target: np.ndarray) -> float:
    """Largest absolute joint error at the last logged step, in radians.

    "Largest" rather than "average" so that one bad joint cannot hide behind two good ones.
    Example: last row [0.10, -0.20], target [0.12, -0.25] -> errors [0.02, 0.05] -> 0.05
    """
    last_row = positions[-1]
    return float(np.max(np.abs(last_row - target)))


def success(
    positions: np.ndarray, target: np.ndarray, tolerance_rad: float, settle_steps: int
) -> bool:
    """True if the arm reached the goal AND stayed there.

    Definition: in each of the last `settle_steps` rows of `positions`, every joint is within
    `tolerance_rad` of its target. Checking several rows (not just the last one) rejects a run
    that merely passes through the goal at the final instant.

    Example (settle_steps=3, tolerance 0.02, target [0, 0]):
        rows [[0.5, 0.5], [0.01, -0.01], [0.0, 0.0], [0.005, 0.0]] -> True  (last 3 rows ok)
        rows [[0.0, 0.0], [0.0, 0.0], [0.03, 0.0], [0.0, 0.0]]     -> False (0.03 is too far)
    """
    # TODO: implement. Plan: positions[-settle_steps:], then np.abs and np.all.
    raise NotImplementedError("TODO: metrics.success is not implemented yet")


def time_to_goal(
    times: np.ndarray, positions: np.ndarray, target: np.ndarray, tolerance_rad: float
) -> float:
    """Simulated time (seconds) of the first row where every joint is within tolerance.

    Returns math.inf if that never happens. Note this is the FIRST arrival only; it does not
    check that the arm stays (that is what `success` is for).

    Example (tolerance 0.02, target [0, 0]):
        times [0.1, 0.2, 0.3, 0.4], rows [[1, 1], [0.5, 0.5], [0.01, -0.01], [0, 0]] -> 0.3
        same times, rows that never get within 0.02                                  -> inf
    """
    # TODO: implement. Plan: a boolean per row (np.all over joints), then np.argmax finds
    # the first True, after checking that at least one row is True.
    raise NotImplementedError("TODO: metrics.time_to_goal is not implemented yet")


def max_joint_velocity(times: np.ndarray, positions: np.ndarray) -> float:
    """Largest joint speed in rad/s over the whole episode, estimated from the log.

    Use finite differences between consecutive rows: |q[i+1] - q[i]| / (t[i+1] - t[i]),
    then take the maximum over all joints and all steps. We estimate from the logged
    positions instead of trusting the simulator's internal velocity, so the metric only
    depends on the evidence we actually recorded.

    Example: times [0.0, 0.1, 0.2], rows [[0, 0], [0.1, 0], [0.1, -0.3]]
        speeds between rows: [[1.0, 0.0], [0.0, 3.0]] -> 3.0
    """
    # TODO: implement. Plan: np.diff(positions, axis=0) over np.diff(times).
    raise NotImplementedError("TODO: metrics.max_joint_velocity is not implemented yet")
