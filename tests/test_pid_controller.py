import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from simulation.pid_controller import PID
from simulation.simulator import Config, run_full
from simulation.performance import compute_metrics


def test_output_limits():
    pid = PID(100, 100, 0, 0.01)
    assert pid.update(300, 0) == 255.0 and pid.update(0, 300) == 0.0


def test_anti_windup():
    pid = PID(1, 10, 0, 0.01)
    for _ in range(1000):
        pid.update(350, 0)
    assert pid.integral < 1.0   # tidak menumpuk saat saturasi


def test_closed_loop_tracks():
    d = run_full(Config(setpoint=200, duration=10))
    m = compute_metrics(d.time, d.setpoint, d.rpm)
    assert abs(m["ss_error"]) < 2 and d.pwm.between(0, 255).all() and d.voltage.between(0, 12).all()


def test_zero_setpoint_safe():
    d = run_full(Config(setpoint=0, duration=2))
    compute_metrics(d.time, d.setpoint, d.rpm)
