"""Tests for sim_vv/scenario.py: the example files load, and bad files fail with clear errors."""

from pathlib import Path

import pytest

from sim_vv.scenario import load_scenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILES = sorted((ROOT / "scenarios").glob("*.yaml"))

# A valid scenario. The "bad file" tests below each break exactly one thing in it.
GOOD_TEXT = """\
name: good
description: a valid scenario used as the starting point for the bad ones
seed: 0
episode_steps: 10
target_qpos_rad: [0.0, 0.0, 0.0]
tolerance_rad: 0.01
"""


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=lambda p: p.stem)
def test_example_scenario_loads(path):
    scenario = load_scenario(path)
    # The file name and the name inside it must agree, or results/<name>.csv gets confusing.
    assert scenario.name == path.stem


def test_missing_fields_are_reported_with_the_file_name(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: bad\nseed: 0\n")  # everything else is missing
    with pytest.raises(ValueError) as excinfo:
        load_scenario(bad)
    message = str(excinfo.value)
    assert str(bad) in message
    for field in ["description", "episode_steps", "target_qpos_rad", "tolerance_rad"]:
        assert field in message


def test_unknown_key_is_an_error(tmp_path):
    bad = tmp_path / "typo.yaml"
    bad.write_text(GOOD_TEXT.replace("tolerance_rad", "tolerence_rad"))
    with pytest.raises(ValueError, match="tolerence_rad"):
        load_scenario(bad)


def test_out_of_range_value_is_an_error(tmp_path):
    bad = tmp_path / "zero_tolerance.yaml"
    bad.write_text(GOOD_TEXT.replace("tolerance_rad: 0.01", "tolerance_rad: 0"))
    with pytest.raises(ValueError, match="tolerance_rad"):
        load_scenario(bad)


def test_broken_yaml_syntax_is_an_error(tmp_path):
    bad = tmp_path / "broken.yaml"
    bad.write_text("name: [unclosed\n")
    with pytest.raises(ValueError, match="not valid YAML"):
        load_scenario(bad)
