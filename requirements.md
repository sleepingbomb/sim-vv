# Requirements

What the arm simulation must do, written down *before* the tests, so that each test checks a
requirement and not "whatever the code happens to do today". Every ID below appears in
`traceability.md` and in the name of exactly one test in `tests/test_requirements.py`;
`tests/test_traceability.py` fails if the three files disagree.

Every requirement is checked against every scenario file in `scenarios/`.

| ID | Requirement | Threshold | Why this threshold |
|---|---|---|---|
| REQ-001 | **Determinism.** Running a scenario twice produces identical joint-position logs. | Bit-for-bit equal (maximum difference 0.0). | A regression suite is worthless if the same input can pass today and fail tomorrow. MuJoCo on one machine is deterministic, so demand exact equality, not "close enough". |
| REQ-002 | **Final accuracy.** At the last step, every joint is within the scenario's tolerance of its target. | `tolerance_rad` from the scenario file (0.01 to 0.02 rad, about 0.6 to 1.1 degrees). | Tight enough that a controller with steady-state error fails (try the gravity mutation in `models/simple_arm.xml`), loose enough for a plain PD controller to meet. Per scenario, because a large move may be allowed more than a hold. |
| REQ-003 | **Settling.** The arm first comes within tolerance no later than halfway through the episode. | `time_to_goal` <= 0.5 x episode duration. | The second half of every episode is then evidence that the controller *holds* position, not only that it passes through the goal. |
| REQ-004 | **Joint speed.** No joint exceeds the speed cap at any time during the episode. | `max_joint_velocity` <= 3.0 rad/s. | Just under 180 degrees/s (3.14 rad/s), comparable to the joint-speed limits on several collaborative arms; on real hardware exceeding it trips a safety stop. |
| REQ-005 | **Evidence.** The runner writes one CSV row per step with one column per joint, and no value is NaN or infinite. | rows = `episode_steps`; columns = 2 + number of joints; all values finite. | A pass with an incomplete or corrupt log cannot be audited. NaN in a physics log means the simulation blew up, even if the final row looks fine. |

## Status

- REQ-001, REQ-002, REQ-005: verified by passing tests.
- REQ-003, REQ-004: tests are written, but they call `time_to_goal` and `max_joint_velocity`,
  which are still `TODO` in `sim_vv/metrics.py`. Until I implement them, those tests are
  marked xfail (expected failure) and show up as the TODO list at the end of every pytest run.

## Adding a requirement

1. Add a row here with the next ID.
2. Add a `test_req_<id>_<short_name>` function to `tests/test_requirements.py`.
3. Add a row to `traceability.md`.

`python -m pytest tests/test_traceability.py` fails if one of the three was missed.
