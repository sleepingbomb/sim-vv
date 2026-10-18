# Traceability matrix

Requirement -> test -> scenarios -> status. Hand-maintained for now; roadmap build step 6
replaces this file with a generator. `tests/test_traceability.py` fails if an ID here is missing
from `requirements.md` or has no test.

| Requirement | Test in `tests/test_requirements.py` | Scenarios | Status |
|---|---|---|---|
| REQ-001 | `test_req_001_same_seed_same_trajectory` | all files in `scenarios/` | verified, passing |
| REQ-002 | `test_req_002_final_error_within_tolerance` | all | verified, passing |
| REQ-003 | `test_req_003_reaches_goal_in_first_half` | all | pending: needs `metrics.time_to_goal` (xfail) |
| REQ-004 | `test_req_004_joint_speed_under_limit` | all | pending: needs `metrics.max_joint_velocity` (xfail) |
| REQ-005 | `test_req_005_log_is_complete` | all | verified, passing |
