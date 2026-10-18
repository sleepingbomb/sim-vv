# Changelog

## 0.1.0 - 2026-10-17

First working version.

- 3-joint planar MuJoCo arm defined inline (`models/simple_arm.xml`)
- YAML scenarios validated by a pydantic schema, with readable error messages
- Headless, seeded runner with joint-space PD control and a CSV log per run
- Requirements REQ-001 to REQ-005 with thresholds and a traceability matrix
- pytest suite: one test per requirement on every scenario, hand-computed metric tests,
  traceability consistency test; three metrics still marked TODO
- GitHub Actions: ruff and pytest with coverage on Python 3.11
- MIT license
