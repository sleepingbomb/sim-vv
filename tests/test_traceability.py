"""Keeps requirements.md, traceability.md and tests/test_requirements.py in agreement.

A traceability matrix nobody checks goes stale within a week. This test fails when a
requirement has no row in the matrix, has no test, or when the matrix or the tests mention
an ID that requirements.md does not define.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_ID = re.compile(r"REQ-\d{3}")  # matches e.g. REQ-002


def test_every_requirement_has_a_matrix_row_and_a_test():
    requirements = set(REQ_ID.findall((ROOT / "requirements.md").read_text()))
    matrix = set(REQ_ID.findall((ROOT / "traceability.md").read_text()))
    # Test functions are named test_req_002_...; turn the "002" back into "REQ-002".
    test_source = (ROOT / "tests" / "test_requirements.py").read_text()
    tested = {f"REQ-{number}" for number in re.findall(r"def test_req_(\d{3})_", test_source)}

    assert requirements, "requirements.md defines no REQ-xxx IDs"
    assert matrix == requirements, f"traceability.md vs requirements.md: {matrix ^ requirements}"
    assert tested == requirements, f"tests vs requirements.md: {tested ^ requirements}"
