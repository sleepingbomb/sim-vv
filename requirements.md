# Requirements

What the arm simulation has to do. I wrote these down before the tests, so the tests check a
requirement rather than whatever the code happens to do today. Every ID here also appears in
`traceability.md` and in the name of exactly one test in `tests/test_requirements.py`;
`tests/test_traceability.py` fails if the three disagree.

Every requirement is checked against every scenario file in `scenarios/`.

| ID | Requirement | Threshold | Why this threshold |
|---|---|---|---|
| REQ-001 | Determinism: running a scenario twice produces identical joint-position logs. | Bit-for-bit equal (maximum difference 0.0). | If the same input can pass today and fail tomorrow the suite is useless. MuJoCo is deterministic on a single machine, so there is no reason to allow any tolerance here. |
| REQ-002 | Final accuracy: at the last step, every joint is within the scenario's tolerance of its target. | `tolerance_rad` from the scenario file (0.01 to 0.02 rad, about 0.6 to 1.1 degrees). | Tight enough that a controller with steady-state error fails (try the gravity mutation in `models/simple_arm.xml`) but still reachable with plain PD. Per scenario because a big move can reasonably get more slack than a hold. |
| REQ-003 | Settling: the arm first comes within tolerance no later than halfway through the episode. | `time_to_goal` <= 0.5 x episode duration. | If the arm has to be there by the halfway point, the second half of the log shows whether it stays there instead of just passing through. |
| REQ-004 | Joint speed: no joint exceeds the speed cap at any time during the episode. | `max_joint_velocity` <= 3.0 rad/s. | Just under 180 degrees/s (3.14 rad/s), which is in the range of the joint speed limits on several collaborative arms. On real hardware going over trips a safety stop. |
| REQ-005 | Evidence: the runner writes one CSV row per step with one column per joint, and no value is NaN or infinite. | rows = `episode_steps`; columns = 2 + number of joints; all values finite. | A pass with a truncated or corrupt log cannot be checked afterwards. A NaN anywhere in a physics log means the simulation blew up at some point, even if the last row looks fine. |

## Status

- REQ-001, REQ-002, REQ-005: verified by passing tests.
- REQ-003, REQ-004: the tests exist but call `time_to_goal` and `max_joint_velocity`, which are
  still stubs in `sim_vv/metrics.py`. Until I write them those tests are marked xfail and show
  up as the TODO list at the end of every pytest run.

## Adding a requirement

1. Add a row here with the next ID.
2. Add a `test_req_<id>_<short_name>` function to `tests/test_requirements.py`. If the threshold
   is the same for every scenario, make it a named constant there and list the constant in
   `SHARED_THRESHOLDS` in `tests/test_traceability.py`.
3. Add a row to `traceability.md`.

`python -m pytest tests/test_traceability.py` fails if one of the three was missed, if the
matrix names a test that does not exist, or if a threshold here and its constant differ.
