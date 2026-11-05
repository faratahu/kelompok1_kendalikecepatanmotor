import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import numpy as np
from simulation.motor_model import step_tf, pwm_to_voltage, interp_rpm, step_blackbox


def test_voltage_limits():
    assert pwm_to_voltage(999) == 12.0 and pwm_to_voltage(-5) == 0.0


def test_tf_steady_state():
    r = 0.0
    for _ in range(3000):
        r = step_tf(r, 12.0, 0.01)
    assert abs(r - 28.37 * 12) < 0.5


def test_no_negative_rpm():
    assert step_tf(0.0, 0.0, 0.01) == 0.0


def test_interp_and_blackbox():
    assert interp_rpm(255) == 337 and abs(interp_rpm(30) - 29.5) < 1e-9
    r = 0.0
    for _ in range(3000):
        r = step_blackbox(r, 12.0, 0.01)
    assert abs(r - 337) < 0.5
