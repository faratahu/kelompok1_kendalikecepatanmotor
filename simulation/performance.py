"""Metrik performa dihitung dari data simulasi (tanpa angka hardcode)."""
import numpy as np


def compute_metrics(t, setpoint, rpm, tol=0.02):
    t, sp, y = np.asarray(t, float), np.asarray(setpoint, float), np.asarray(rpm, float)
    nan = float("nan")
    out = dict(rise_time=nan, overshoot=nan, settling_time=nan, peak_rpm=nan,
               peak_time=nan, ss_error=nan, rmse=nan)
    if len(t) < 2:
        return out
    target = sp[-1]
    k = int(np.argmax(y))
    out["peak_rpm"], out["peak_time"] = float(y[k]), float(t[k])
    out["rmse"] = float(np.sqrt(np.mean((sp - y) ** 2)))
    out["ss_error"] = float(target - np.mean(y[-max(5, len(y) // 20):]))
    if target <= 1e-9:   # setpoint nol: metrik relatif tidak terdefinisi
        return out
    i10, i90 = np.where(y >= 0.1 * target)[0], np.where(y >= 0.9 * target)[0]
    if len(i10) and len(i90):
        out["rise_time"] = float(t[i90[0]] - t[i10[0]])
    out["overshoot"] = float(max(0.0, (y[k] - target) / target * 100.0))
    outside = np.where(np.abs(y - target) > tol * target)[0]
    if len(outside) == 0:
        out["settling_time"] = 0.0
    elif outside[-1] < len(y) - 1:
        out["settling_time"] = float(t[outside[-1] + 1])
    return out
