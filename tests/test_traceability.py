"""Keeps requirements.md, traceability.md and tests/test_requirements.py in agreement.

A traceability matrix nobody checks goes stale within a week. These tests fail when a
requirement has no row in the matrix or no test, or when the matrix or the tests mention an
ID that requirements.md does not define; when the matrix names a test that does not exist,
or another requirement's test; and when a threshold stated in requirements.md differs from
the constant that tests/test_requirements.py compares against.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_ID = re.compile(r"REQ-\d{3}")  # matches e.g. REQ-002
# A matrix row, e.g. | REQ-002 | `test_req_002_final_error_within_tolerance` | all | ...
# Captures the ID and the test name; the backticks around the name are optional.
MATRIX_ROW = re.compile(r"^\|\s*(REQ-\d{3})\s*\|\s*`?(\w+)`?\s*\|", re.MULTILINE)
# Thresholds that requirements.md states and tests/test_requirements.py repeats as a constant:
# constant name -> how requirements.md writes the threshold, with the number as the group.
SHARED_THRESHOLDS = {
    "TIME_TO_GOAL_MAX_FRACTION": r"`time_to_goal` <= ([\d.]+) x episode duration",
    "MAX_JOINT_VELOCITY_RAD_S": r"`max_joint_velocity` <= ([\d.]+) rad/s",
}


def test_every_requirement_has_a_matrix_row_and_a_test():
    requirements = set(REQ_ID.findall((ROOT / "requirements.md").read_text()))
    matrix = set(REQ_ID.findall((ROOT / "traceability.md").read_text()))
    # Test functions are named test_req_002_...; turn the "002" back into "REQ-002".
    test_source = (ROOT / "tests" / "test_requirements.py").read_text()
    tested = {f"REQ-{number}" for number in re.findall(r"def test_req_(\d{3})_", test_source)}

    assert requirements, "requirements.md defines no REQ-xxx IDs"
    assert matrix == requirements, f"traceability.md vs requirements.md: {matrix ^ requirements}"
    assert tested == requirements, f"tests vs requirements.md: {tested ^ requirements}"


def test_matrix_names_the_test_for_each_requirement():
    # Both sides as (ID, test name) pairs, e.g. ("REQ-002", "test_req_002_final_error_...").
    named = set(MATRIX_ROW.findall((ROOT / "traceability.md").read_text()))
    test_source = (ROOT / "tests" / "test_requirements.py").read_text()
    defined = {
        (f"REQ-{number}", name)
        for name, number in re.findall(r"def (test_req_(\d{3})_\w*)\(", test_source)
    }

    assert named == defined, (
        f"only in traceability.md: {named - defined}; "
        f"only in tests/test_requirements.py: {defined - named}"
    )


def test_threshold_constants_match_requirements():
    requirements = (ROOT / "requirements.md").read_text()
    test_source = (ROOT / "tests" / "test_requirements.py").read_text()

    for constant, pattern in SHARED_THRESHOLDS.items():
        stated = re.search(pattern, requirements)
        assert stated, f"requirements.md: no text matching {pattern!r}"
        used = re.search(rf"^{constant} = ([\d.]+)", test_source, re.MULTILINE)
        assert used, f"tests/test_requirements.py: no line '{constant} = <number>'"
        # Exact == on purpose: both numbers are parsed from text, so no rounding error creeps in.
        assert float(stated[1]) == float(used[1]), (
            f"requirements.md says {stated[0]!r}, "
            f"but tests/test_requirements.py has {constant} = {used[1]}"
        )
