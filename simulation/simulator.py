"""Simulator langkah-per-langkah (untuk live) dan batch."""
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd
from .motor_model import (TF_MODEL, K, step_tf, step_blackbox, pwm_to_voltage, interp_rpm)
from .pid_controller import PID

MODES = ["Open Loop", "PID Manual", "PID Ziegler-Nichols", "PID Optimized"]
PRESETS = {"Open Loop": None, "PID Manual": None,
           "PID Ziegler-Nichols": (1.08, 10.8, 0.027),
           "PID Optimized": (2.50, 0.50, 0.10)}
COLS = ["time", "setpoint", "rpm", "error", "pwm", "voltage"]


@dataclass(frozen=True)
class Config:
    mode: str = "PID Ziegler-Nichols"
    model: str = TF_MODEL
    setpoint: float = 200.0
    kp: float = 1.08
    ki: float = 10.8
    kd: float = 0.027
    pwm_manual: float = 128.0
    dt: float = 0.01
    duration: float = 10.0
    vsupply: float = 12.0


class Simulation:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.pid = PID(cfg.kp, cfg.ki, cfg.kd, cfg.dt)
        self.t = 0.0
        self.rpm = 0.0
        self.angle = 0.0
        self.last_pwm = 0.0
        self.last_v = 0.0
        self.rows = []

    def set_cfg(self, cfg: Config):
        cfg = replace(cfg, dt=self.cfg.dt)
        self.cfg = cfg
        self.pid.kp, self.pid.ki, self.pid.kd = cfg.kp, cfg.ki, cfg.kd

    @property
    def done(self):
        return self.t >= self.cfg.duration - 1e-9

    def step(self):
        c = self.cfg
        pwm = float(np.clip(c.pwm_manual, 0, 255)) if c.mode == "Open Loop" \
            else self.pid.update(c.setpoint, self.rpm)
        v = pwm_to_voltage(pwm, c.vsupply)
        sp = c.setpoint
        self.rows.append((self.t, sp, self.rpm, sp - self.rpm, pwm, v))
        f = step_tf if c.model == TF_MODEL else step_blackbox
        new = f(self.rpm, v, c.dt)
        self.angle = (self.angle + 0.5 * (self.rpm + new) * 360.0 / 60.0 * c.dt) % 360.0
        self.rpm, self.t, self.last_pwm, self.last_v = new, self.t + c.dt, pwm, v

    @property
    def df(self):
        return pd.DataFrame(self.rows, columns=COLS)

    def status(self):
        if self.rpm < 0.5 and self.last_pwm <= 0.0:
            return "STOP"
        ref = self.cfg.setpoint if self.cfg.mode != "Open Loop" else K * self.last_v
        if self.rpm < 0.9 * ref:
            return "STARTING"
        if abs(self.rpm - ref) <= 0.02 * max(ref, 1.0):
            return "STABLE"
        return "RUNNING"


def run_full(cfg: Config) -> pd.DataFrame:
    sim = Simulation(cfg)
    while not sim.done:
        sim.step()
    return sim.df


def open_loop_pwm_for(cfg: Config) -> float:
    """PWM open-loop yang secara teori memberi steady-state = setpoint."""
    from .motor_model import PWM_ARR, RPM_ARR
    if cfg.model == TF_MODEL:
        return float(np.clip(cfg.setpoint / K / cfg.vsupply * 255.0, 0, 255))
    return float(np.interp(cfg.setpoint, RPM_ARR, PWM_ARR))
