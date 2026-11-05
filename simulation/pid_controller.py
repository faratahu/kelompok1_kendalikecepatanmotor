"""PID digital: derivative on measurement, anti-windup (conditional integration), output PWM 0-255.

Satuan: error dalam RPM, output langsung dalam satuan PWM (0-255). Preset jurnal tidak diubah.
"""
import numpy as np


class PID:
    def __init__(self, kp, ki, kd, dt, out_min=0.0, out_max=255.0):
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.out_min, self.out_max = out_min, out_max
        self.reset()

    def reset(self):
        self.integral = 0.0
        self.prev_meas = None
        self.terms = (0.0, 0.0, 0.0)

    def update(self, setpoint, measured):
        e = setpoint - measured
        p = self.kp * e
        d_meas = 0.0 if self.prev_meas is None else (measured - self.prev_meas) / self.dt
        d = -self.kd * d_meas
        cand = self.integral + e * self.dt
        i = self.ki * cand
        u = p + i + d
        u_sat = float(np.clip(u, self.out_min, self.out_max))
        # anti-windup: integral berhenti bertambah saat saturasi mendorong lebih jauh
        saturating = (u > self.out_max and e > 0) or (u < self.out_min and e < 0)
        if not saturating:
            self.integral = cand
        self.prev_meas = measured
        self.terms = (p, self.ki * self.integral, d)
        return u_sat
