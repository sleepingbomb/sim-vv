# Why each file exists, and what breaks without it

A rule I try to hold myself to: if I cannot say in two sentences why a file is there, the file
needs rewriting. Those two sentences go here, one row per file, and I add a row whenever I add
a module.

| File | Why it exists | What breaks without it |
|---|---|---|
| `sim_vv/scenario.py` | Loads a scenario `.yaml` into a `Scenario` object and validates it. The pydantic model is the one place that says what a scenario contains. | A typo like `tolerence_rad` would be ignored and the run would use no tolerance. A missing field would blow up somewhere inside the runner with a `KeyError` instead of saying which file and which field. |
| `sim_vv/runner.py` | Runs one scenario in MuJoCo with no window: seeded start pose, N steps of PD control, CSV log. The only module that imports mujoco. | Without the CSV there is nothing to look at after a pass or a fail. Without the seeded start pose the determinism requirement would pass trivially. |
| `sim_vv/metrics.py` | Functions that turn a log into one number each: final error, time to goal, peak speed, success. Arrays in, number out, no MuJoCo and no file I/O. | Nothing to compare the thresholds against. If this lived inside the runner I could not test it with small hand-made arrays, and that is the only way I trust a metric. |
| `models/simple_arm.xml` | A 3-joint planar arm, written by hand so nothing has to be downloaded and all the numbers are in one place. Horizontal, so gravity stays out of it and plain PD can hit the target. | Nothing to simulate. A downloaded model means a network step in CI and parameters I did not pick and cannot explain. |
| `scenarios/*.yaml` | One file per test case: target, seed, length, tolerance. Adding a scenario means adding a file. | Targets and seeds would be hard-coded in the tests, and each of the 20+ scenarios I am planning would mean editing Python. |
| `requirements.md` | The requirements, with IDs, thresholds, and where each threshold comes from. | The tests would end up checking whatever the code does today, and nobody could say where 3.0 rad/s came from. |
| `traceability.md` | The REQ -> test -> scenario table. | No quick way to see which requirement a failing test belongs to, or which requirement has no test. |
| `tests/test_requirements.py` | One test per requirement, run on every scenario file. Shared thresholds are named constants at the top. | The requirements would just be a document. The point of the project is that breaking one turns CI red. |
| `tests/test_metrics.py` | Unit tests for every metric with hand-computed expected values, including the two metrics I have not written yet (marked xfail). | A sign error or an off-by-one in a metric would pass every scenario without anyone noticing. The xfail markers are also my to-do list. |
| `tests/test_scenario.py` | The example scenarios load, and broken ones fail with the file name and the field in the message. | A bad scenario file would fail somewhere unrelated with a confusing message, or not fail at all. |
| `tests/test_runner.py` | Tests for the runner itself: wrong joint count gives a clear error, the seed changes the start pose, the CSV matches the returned arrays. | A broken runner can pass every requirement test by accident, say by writing a CSV that is wrong. The harness needs tests too. |
| `tests/test_traceability.py` | Fails when requirements.md, traceability.md and the tests disagree: a REQ ID missing from one of them, a matrix row naming the wrong test, or a shared threshold (like the 3.0 rad/s cap) that differs between requirements.md and the test constant. | The matrix goes stale the first time I add a requirement and forget one of the three places. A threshold changed in only one file means CI is checking a number requirements.md no longer says. |
| `.github/workflows/ci.yml` | Runs ruff and pytest on every push, on a clean Ubuntu machine. | "Works on my Mac" would be the only evidence. A missing dependency or a Mac-only path would never get caught. |
| `pyproject.toml` | Dependencies, package metadata, pytest and ruff settings, all in one file. | `pip install -e .` would not work, and the tool settings would be spread over four files. |
| `.gitignore` | Keeps the venv, the caches and the generated `results/` logs out of git. | Megabytes of generated files in every commit, and merge conflicts on CSVs that change on every run. |
