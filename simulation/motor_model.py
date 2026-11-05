"""Model plant motor DC 12 V: transfer function jurnal dan interpolasi blackbox."""
import numpy as np

K = 28.37      # RPM / V
TAU = 0.192    # s
V_MAX = 12.0
PWM_MAX = 255.0

BLACKBOX_DATA = [
    {"pwm": 0, "voltage": 0.00, "rpm": 0}, {"pwm": 20, "voltage": 0.94, "rpm": 18},
    {"pwm": 40, "voltage": 1.88, "rpm": 41}, {"pwm": 60, "voltage": 2.82, "rpm": 67},
    {"pwm": 80, "voltage": 3.76, "rpm": 94}, {"pwm": 100, "voltage": 4.71, "rpm": 122},
    {"pwm": 120, "voltage": 5.65, "rpm": 151}, {"pwm": 140, "voltage": 6.59, "rpm": 179},
    {"pwm": 160, "voltage": 7.53, "rpm": 207}, {"pwm": 180, "voltage": 8.47, "rpm": 236},
    {"pwm": 200, "voltage": 9.41, "rpm": 264}, {"pwm": 220, "voltage": 10.35, "rpm": 292},
    {"pwm": 240, "voltage": 11.29, "rpm": 319}, {"pwm": 255, "voltage": 12.00, "rpm": 337},
]
PWM_ARR = np.array([d["pwm"] for d in BLACKBOX_DATA], dtype=float)
VOLT_ARR = np.array([d["voltage"] for d in BLACKBOX_DATA], dtype=float)
RPM_ARR = np.array([d["rpm"] for d in BLACKBOX_DATA], dtype=float)

TF_MODEL = "Transfer Function Jurnal"
BB_MODEL = "Blackbox Interpolation"


def pwm_to_voltage(pwm, supply=V_MAX):
    """Konversi PWM (0-255) ke tegangan motor, dibatasi 0..supply (maks 12 V)."""
    pwm = float(np.clip(pwm, 0.0, PWM_MAX))
    return float(np.clip(supply * pwm / PWM_MAX, 0.0, min(supply, V_MAX)))


def step_tf(rpm, voltage, dt, k=K, tau=TAU):
    """Diskritisasi eksak tau*dRPM/dt + RPM = K*V."""
    a = np.exp(-dt / tau)
    return float(max(0.0, a * rpm + (1.0 - a) * k * voltage))


def interp_rpm(pwm):
    """Interpolasi linear PWM -> RPM (tanpa ekstrapolasi: nilai di-clip ke rentang data)."""
    return float(np.interp(pwm, PWM_ARR, RPM_ARR))


def step_blackbox(rpm, voltage, dt, tau=TAU):
    """Steady-state dari interpolasi dataset, dinamika orde-1 dengan tau yang sama."""
    pwm_eq = np.clip(voltage / V_MAX * PWM_MAX, 0.0, PWM_MAX)
    target = interp_rpm(pwm_eq)
    a = np.exp(-dt / tau)
    return float(max(0.0, a * rpm + (1.0 - a) * target))


def in_range(pwm):
    return PWM_ARR[0] <= pwm <= PWM_ARR[-1]
