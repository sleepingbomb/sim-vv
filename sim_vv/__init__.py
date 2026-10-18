"""sim-vv: scenario-based regression tests for a MuJoCo robot-arm simulation.

Three small modules, used in this order:
  scenario.py  reads and validates a scenario .yaml file
  runner.py    runs that scenario headless in MuJoCo and logs joint positions
  metrics.py   turns a log into pass/fail numbers (some are TODO(student))
"""
