"""Run one scenario headless in MuJoCo and log the joint positions.

Pipeline:  Scenario  ->  MuJoCo model  ->  seeded start pose  ->  N steps of PD control
           ->  results/<name>.csv  (one row per step: step, time_s, one column per joint)

Headless means no window and no rendering: we only step the physics and read numbers,
so this runs the same way on a laptop and on a GitHub Actions machine.
"""

import argparse
import csv
from pathlib import Path

import mujoco
import numpy as np

from sim_vv.metrics import final_error
from sim_vv.scenario import Scenario, load_scenario

# The repository root: this file is sim_vv/runner.py, so two levels up.
# This works because the project is installed in editable mode (pip install -e .).
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "models" / "simple_arm.xml"
DEFAULT_RESULTS_DIR = ROOT / "results"

# PD controller gains, the same for every joint on purpose: easy to reason about and easy to
# break on purpose (a mutation check: lower KP and watch REQ-002 fail).
#   torque = KP * (target - position) - KD * velocity
KP = 12.0  # N*m per radian of position error
KD = 4.0  # N*m per radian/second of joint velocity

# The start pose is the rest pose plus a seeded random offset of at most this much (radians).
# Without this, the seed would change nothing and the determinism requirement would be trivial.
START_NOISE_RAD = 0.05


def run_scenario(
    scenario: Scenario,
    model_path: Path = DEFAULT_MODEL,
    results_dir: Path = DEFAULT_RESULTS_DIR,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate one scenario and return (times, positions); also write results/<name>.csv.

    times:     shape (episode_steps,), simulated seconds after each step
    positions: shape (episode_steps, n_joints), joint angles in radians after each step
    """
    model = mujoco.MjModel.from_xml_path(str(model_path))
    data = mujoco.MjData(model)

    # This runner assumes one motor per joint, in joint order, so that ctrl[i] drives joint i.
    # nq = number of joint positions, nu = number of actuators.
    if model.nq != model.nu:
        raise ValueError(
            f"{model_path}: runner.py needs one motor per joint, "
            f"but the model has {model.nq} joints and {model.nu} motors"
        )
    target = np.array(scenario.target_qpos_rad, dtype=float)
    if target.shape[0] != model.nq:
        raise ValueError(
            f"scenario '{scenario.name}': target_qpos_rad has {target.shape[0]} values "
            f"but the model has {model.nq} joints"
        )

    # Seeded start pose. numpy's default_rng gives the same numbers for the same seed.
    rng = np.random.default_rng(scenario.seed)
    data.qpos[:] = rng.uniform(-START_NOISE_RAD, START_NOISE_RAD, size=model.nq)

    times = np.zeros(scenario.episode_steps)
    positions = np.zeros((scenario.episode_steps, model.nq))

    for step in range(scenario.episode_steps):
        # Joint-space PD control: push toward the target, resist velocity.
        data.ctrl[:] = KP * (target - data.qpos) - KD * data.qvel
        mujoco.mj_step(model, data)
        times[step] = data.time
        positions[step] = data.qpos  # copies the values into our array

    joint_names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(model.nq)]
    write_csv(Path(results_dir) / f"{scenario.name}.csv", joint_names, times, positions)
    return times, positions


def write_csv(path: Path, joint_names: list[str], times: np.ndarray, positions: np.ndarray) -> None:
    """Write the episode log. Full float precision, so the CSV is an exact record of the run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "time_s"] + [f"q_{name}" for name in joint_names])
        for step in range(len(times)):
            writer.writerow([step, times[step]] + list(positions[step]))


def main() -> None:
    """Command line: python -m sim_vv.runner scenarios/reach_small.yaml"""
    parser = argparse.ArgumentParser(
        description="Run one scenario headless and log it to results/."
    )
    parser.add_argument("scenario", type=Path, help="path to a scenario .yaml file")
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)
    times, positions = run_scenario(scenario)
    error = final_error(positions, np.array(scenario.target_qpos_rad))
    print(
        f"{scenario.name}: {len(times)} steps = {times[-1]:.3f} s simulated, "
        f"final_error = {error:.4f} rad (tolerance {scenario.tolerance_rad})"
    )
    print(f"log written to {DEFAULT_RESULTS_DIR / (scenario.name + '.csv')}")


if __name__ == "__main__":
    main()
