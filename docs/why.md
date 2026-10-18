# Why each file exists, and what breaks without it

The roadmap's rule: anything you cannot explain in two sentences gets rewritten by you.
This file is the written version of that test. The entries below are a starting point written
with the scaffold; **rewrite each one in your own words after you have read the file it
describes**, and add an entry whenever you add a module.

| File | Why it exists | What breaks without it |
|---|---|---|
| `sim_vv/scenario.py` | Reads a scenario `.yaml` into a validated `Scenario` object. The pydantic model is the single written definition of what a scenario is. | A typo such as `tolerence_rad` would be silently ignored and the run would use no tolerance at all; a missing field would crash deep inside the runner with an unhelpful `KeyError` instead of naming the file and the field. |
| `sim_vv/runner.py` | Runs one scenario headless in MuJoCo: seeded start pose, N steps of joint-space PD control, and a CSV log. It is the only module that touches the simulator. | No evidence. Without the CSV there is nothing to audit after a pass or fail, and without the seeded start the "same seed, same result" requirement would be trivially true and prove nothing. |
| `sim_vv/metrics.py` | Pure functions that turn a log into one number each (final error, time to goal, peak speed, success). Pure means: arrays in, number out, no MuJoCo, no files. | Thresholds could not be checked. Mixing metric code into the runner would also make the metrics untestable with hand-computed values, which is the only way to be sure they are right. |
| `models/simple_arm.xml` | A 3-joint planar arm written inline so nothing has to be downloaded and every number is visible. Horizontal so gravity does not load the joints and plain PD can hit the target. | Nothing to simulate. A downloaded model would add a network step to CI and hide the physics parameters you will be asked about in interviews. |
| `scenarios/*.yaml` | Each file is one reproducible test case: target, seed, length, tolerance. Adding a scenario is adding a file, not code. | Tests would hard-code targets and seeds, so adding the 20+ scenarios the roadmap asks for would mean editing Python every time. |
| `requirements.md` | The written requirements with IDs and thresholds, and the reason for each threshold. | Tests would check "whatever passes" instead of a requirement, and nobody could answer "why 3.0 rad/s?" in a review. |
| `traceability.md` | The REQ -> test -> scenario matrix a reviewer asks for first. | You could not show which requirement a failing test belongs to, or which requirement has no test at all. |
| `tests/test_requirements.py` | One test per requirement, parametrized over every scenario file, with the shared thresholds as named constants. | Requirements would be prose only. The whole point of the project is that a code change which violates a requirement turns CI red. |
| `tests/test_metrics.py` | Hand-computed unit tests for every metric, including the three you still have to write (marked xfail). | A metric with a sign error or an off-by-one would quietly pass every scenario. The strict xfail markers are also your to-do list. |
| `tests/test_scenario.py` | Checks that the example scenarios load and that broken ones fail with the file name and field in the message. | A bad scenario file would fail somewhere else with a confusing message, or not fail at all. |
| `tests/test_runner.py` | Checks the harness itself: wrong joint count is a clear error, the seed changes the start pose, the CSV matches the returned arrays exactly. | A broken harness can pass every requirement test by accident (for example, a CSV that is written but wrong). Testing the test tool is part of V&V. |
| `tests/test_traceability.py` | Fails when requirements.md, traceability.md and the test names disagree about the set of REQ IDs. | The matrix goes stale the first time someone adds a requirement and forgets one of the three places. |
| `.github/workflows/ci.yml` | Runs ruff and pytest on every push on a clean Ubuntu machine. | "Works on my Mac" is the only evidence; a missing dependency or an OS-specific path is never caught. |
| `pyproject.toml` | Declares dependencies, the package, and the pytest and ruff settings in one file. | `pip install -e .` would not work, CI would have no single install command, and lint and test settings would live in four different files. |
| `.gitignore` | Keeps the virtualenv, caches and the regenerated `results/` logs out of git. | Megabytes of binary and generated files in every commit, and merge conflicts on CSVs that are regenerated on every run. |
