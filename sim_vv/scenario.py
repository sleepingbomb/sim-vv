"""Read and validate one scenario file.

A scenario is a small YAML file that fully describes one reproducible test case:
where the arm should go, how long it has, how close counts as "there", and which
seed to use. Validating it here means a typo in a YAML file fails loudly, right
away, with the file name in the message, instead of producing a silently wrong run.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Scenario(BaseModel):
    """One test case for the arm. Field names are exactly the YAML keys."""

    # extra="forbid": an unknown key (for example the typo "tolerence_rad") is an error.
    # Without it, pydantic would ignore the typo and the scenario would use no tolerance at all.
    model_config = ConfigDict(extra="forbid")

    # Used as the CSV file name under results/, so keep it filesystem-safe.
    name: str = Field(pattern=r"^[a-z0-9_]+$")
    description: str
    # Seeds the random start-pose perturbation in runner.py. Same seed, same run.
    seed: int = Field(ge=0)
    # Number of physics steps to simulate (the model's timestep decides how many seconds that is).
    episode_steps: int = Field(gt=0)
    # Target angle for each joint, in radians, in the model's joint order.
    target_qpos_rad: list[float] = Field(min_length=1)
    # How close every joint must be to its target to count as "at the goal".
    tolerance_rad: float = Field(gt=0)


def load_scenario(path: Path) -> Scenario:
    """Load and validate a scenario .yaml file.

    Raises ValueError (with the file path in the message) when the file is not valid YAML
    or does not match the Scenario schema. A missing file raises FileNotFoundError as usual.
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
        # pydantic's message already lists every bad field; we only add which file it came from.
        raise ValueError(f"{path}: invalid scenario:\n{err}") from err
