"""Run one scenario in MuJoCo (no rendering) and log the joint positions to results/<name>.csv.

Scenario -> MjModel -> seeded start pose -> N steps of PD control -> CSV, one row per step
(step, time_s, then one column per joint).
"""

import argparse
import csv
from pathlib import Path

import mujoco
import numpy as np

from sim_vv.metrics import final_error
from sim_vv.scenario import Scenario, load_scenario

# repo root; this file is sim_vv/runner.py and the package is installed editable
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "models" / "simple_arm.xml"
DEFAULT_RESULTS_DIR = ROOT / "results"

# PD gains, shared by all joints:  torque = KP * (target - qpos) - KD * qvel
KP = 12.0  # N*m per rad
KD = 4.0  # N*m per rad/s

# start pose = rest pose + seeded uniform noise of at most this much, in radians
START_NOISE_RAD = 0.05


def run_scenario(
    scenario: Scenario,
    model_path: Path = DEFAULT_MODEL,
    results_dir: Path = DEFAULT_RESULTS_DIR,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate one scenario, write results/<name>.csv and return (times, positions).

    times:     shape (episode_steps,), simulated seconds after each step
    positions: shape (episode_steps, n_joints), joint angles in radians after each step
    """
    model = mujoco.MjModel.from_xml_path(str(model_path))
    data = mujoco.MjData(model)

    # one motor per joint, in joint order, so ctrl[i] drives joint i
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

    rng = np.random.default_rng(scenario.seed)
    data.qpos[:] = rng.uniform(-START_NOISE_RAD, START_NOISE_RAD, size=model.nq)

    times = np.zeros(scenario.episode_steps)
    positions = np.zeros((scenario.episode_steps, model.nq))

    for step in range(scenario.episode_steps):
        data.ctrl[:] = KP * (target - data.qpos) - KD * data.qvel
        mujoco.mj_step(model, data)
        times[step] = data.time
        positions[step] = data.qpos  # copies; data.qpos is a view that changes next step

    joint_names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j) for j in range(model.nq)]
    write_csv(Path(results_dir) / f"{scenario.name}.csv", joint_names, times, positions)
    return times, positions


def write_csv(path: Path, joint_names: list[str], times: np.ndarray, positions: np.ndarray) -> None:
    """Write the episode log at full float precision."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "time_s"] + [f"q_{name}" for name in joint_names])
        for step in range(len(times)):
            writer.writerow([step, times[step]] + list(positions[step]))


def main() -> None:
    """python -m sim_vv.runner scenarios/reach_small.yaml"""
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
