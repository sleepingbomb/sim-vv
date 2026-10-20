"""Load and validate one scenario .yaml file.

A scenario is one reproducible test case: target pose, episode length, tolerance, seed.
Validation happens here so a typo in a yaml file fails straight away with the file name in the
message, rather than quietly producing a wrong run.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Scenario(BaseModel):
    """One test case for the arm. Field names are the YAML keys."""

    # unknown keys are errors, otherwise a typo like "tolerence_rad" would just be ignored
    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-z0-9_]+$")  # also the CSV file name under results/
    description: str
    seed: int = Field(ge=0)  # seeds the start-pose perturbation in runner.py
    episode_steps: int = Field(gt=0)  # seconds = episode_steps * the model's timestep
    target_qpos_rad: list[float] = Field(min_length=1)  # one per joint, in the model's joint order
    tolerance_rad: float = Field(gt=0)  # a joint counts as at the goal when within this


def load_scenario(path: Path) -> Scenario:
    """Load a scenario file.

    Bad YAML or a schema mismatch raises ValueError with the file path in the message. A missing
    file raises FileNotFoundError as usual.
    """
    path = Path(path)
    text = path.read_text()

    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as err:
        raise ValueError(f"{path}: not valid YAML: {err}") from err

    try:
        return Scenario.model_validate(raw)
    except ValidationError as err:
        # pydantic already lists every bad field, just say which file
        raise ValueError(f"{path}: invalid scenario:\n{err}") from err
