# sim-vv

![ci](https://github.com/sleepingbomb/sim-vv/actions/workflows/ci.yml/badge.svg)

Regression tests for a MuJoCo robot-arm simulation, organised the way a V&V (verification and
validation) process wants them: scenarios are YAML files, requirements have IDs and thresholds,
every requirement has a pytest test that runs against every scenario, and GitHub Actions runs the
lot on every push.

**Status: work in progress.** The runner, the scenario loader, one metric and the test harness
work. Three metrics are still on my to-do list, see "What is next".

## Why this exists

If you ship robots you want to know, on every code change, whether behaviour regressed. That
takes reproducible scenarios, pass/fail criteria that trace back to written requirements,
automated runs in CI, and logs you can go back to afterwards. This repo is my attempt at the
smallest setup that does all four.

## Architecture

```
scenarios/*.yaml ──▶ sim_vv/scenario.py ──▶ sim_vv/runner.py ──▶ results/<name>.csv
                     (validate)              (MuJoCo, no window,    (one row per step,
                                              seeded, PD control)    one column per joint)
                                                     │
requirements.md ──▶ tests/test_requirements.py ◀─────┘
  REQ-001..005        one test per REQ, run on every scenario
                      uses sim_vv/metrics.py: final_error, success*, time_to_goal*, max_joint_velocity*
traceability.md ◀── tests/test_traceability.py   (IDs, test names and thresholds must agree)

.github/workflows/ci.yml:  pip install -e ".[dev]"  →  ruff check .  →  pytest --cov
                                                                            * = TODO
```

The robot is `models/simple_arm.xml`, a 3-joint planar arm (shoulder, elbow, wrist) moving in the
horizontal plane. It is written by hand so nothing has to be downloaded. The hinge axes are
vertical, so gravity puts no torque on the joints and a plain PD controller gets to the target
with no steady-state error.

## How to run

Needs Python 3.11 (`python3.11 --version`). No GPU or display, and `MUJOCO_GL` does not need to
be set.

```bash
cd sim-vv
```
```bash
python3.11 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
python -m pip install --upgrade pip
```
```bash
python -m pip install -e ".[dev]"
```

Run one scenario and look at its log:

```bash
python -m sim_vv.runner scenarios/reach_small.yaml
```
```bash
head -3 results/reach_small.csv
```

You should get a line like `reach_small: 1250 steps = 2.500 s simulated, final_error = 0.0001 rad
(tolerance 0.01)` and a CSV with the columns `step,time_s,q_shoulder,q_elbow,q_wrist`.

Run the suite and the linter (same as CI):

```bash
python -m pytest
```
```bash
ruff check .
```

Everything should pass apart from a block of `XFAIL` entries with `TODO` reasons. Those are the
metrics I have not written yet. Coverage, with the same command CI uses:

```bash
python -m pytest --cov=sim_vv --cov-report=term-missing
```

## What is next

Three functions in `sim_vv/metrics.py` are still stubs that raise `NotImplementedError`. I wrote
the tests first, with hand-computed expected values, so each one has a target to hit:

| Function | Used by | Test with hand-computed values |
|---|---|---|
| `success` | (unit test only, for now) | `tests/test_metrics.py::test_success_requires_staying_within_tolerance_for_the_last_steps` |
| `time_to_goal` | REQ-003 | `test_metrics.py::test_time_to_goal_...` and `test_requirements.py::test_req_003_...` |
| `max_joint_velocity` | REQ-004 | `test_metrics.py::test_max_joint_velocity_...` and `test_requirements.py::test_req_004_...` |

Each docstring has the definition and a worked example. The tests are marked
`@pytest.mark.xfail(raises=NotImplementedError, strict=True, ...)`, so finishing one goes:

1. Replace the `raise NotImplementedError(...)` line with the implementation.
2. Run `python -m pytest`. If the implementation is right the test shows up as `XPASS(strict)`,
   which pytest counts as a failure. That is the reminder to delete the marker.
3. Delete the `@pytest.mark.xfail(...)` block above that test. Run again, green.

## Mutation checks

Break something, run `python -m pytest`, check that it goes red, undo:

- In `sim_vv/runner.py`, set `KP = 2.0`. The arm is too slow and REQ-002 fails on every scenario.
- In `models/simple_arm.xml`, change the joint axis to `0 1 0` (a vertical arm). Gravity pulls
  the links down, the PD controller sags, REQ-002 fails.
- In `sim_vv/runner.py`, replace the seeded `rng` with `np.random.default_rng()`. REQ-001 fails
  because two runs no longer match.

## Swapping in a real arm (MuJoCo Menagerie)

`run_scenario` takes a `model_path`, so any MuJoCo XML should work in principle:

```bash
git clone https://github.com/google-deepmind/mujoco_menagerie ../mujoco_menagerie
```

Then call `run_scenario(scenario, model_path=Path("../mujoco_menagerie/universal_robots_ur5e/ur5e.xml"))`
with one target per joint in the scenario. Three things need sorting out, in this order:

1. Actuators. The runner wants one torque motor per joint (`nq == nu`) and raises otherwise.
   Menagerie arms come with position actuators, where `ctrl` is a target angle rather than a
   torque. Either send the target straight to `data.ctrl` or replace their `<actuator>` block
   with `<motor>` elements like the ones in `models/simple_arm.xml`.
2. Gravity. Real arms are vertical, so plain PD sags and REQ-002 fails. The usual fix is PD plus
   gravity compensation, i.e. add `data.qfrc_bias` to the torque.
3. Thresholds. Work out `tolerance_rad` and the speed cap from the real arm's data sheet and
   write the reasoning into `requirements.md`.

## Layout

```
sim_vv/            scenario.py (load + validate), runner.py (simulate + log), metrics.py (numbers)
models/            simple_arm.xml
scenarios/         reach_small.yaml, reach_large.yaml, hold_rest.yaml
tests/             test_scenario.py, test_runner.py, test_metrics.py, test_requirements.py, test_traceability.py
requirements.md    REQ-001..REQ-005 with thresholds and the reason for each
traceability.md    REQ -> test -> scenario -> status
docs/why.md        per file: why it exists, what breaks without it
results/           CSV logs, regenerated on every run (git-ignored)
.github/workflows/ci.yml
```

## Limitations and what comes next

- Three scenarios, one controller, one arm. The plan is 20+ scenarios and 3 controller versions.
- The traceability matrix is maintained by hand. Generating it is on the list.
- No results database, dashboard, triage tooling or property-based tests yet. Those come after
  the metrics.
- Determinism is only checked on one machine. MuJoCo does not promise bit-identical results
  across platforms, so CI and my Mac could disagree one day. If that happens I want to work out
  why rather than just rerun the job.

## License

MIT, see [LICENSE](LICENSE).
