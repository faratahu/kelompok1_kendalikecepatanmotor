import numpy as np
import plotly.graph_objects as go
from simulation.motor_model import PWM_ARR, VOLT_ARR, RPM_ARR, K

BLUE, ORANGE, GREEN, GRAY = "#3B5B8C", "#D98B4A", "#5B9279", "#8A94A3"


def _base(title, xt, yt, h=300):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", title=dict(text=title, font=dict(size=15, color="#2F3640")),
                      height=h, margin=dict(l=50, r=20, t=50, b=45), hovermode="x unified",
                      legend=dict(orientation="h", y=1.15, x=0), font=dict(color="#2F3640"),
                      xaxis=dict(title=xt, showgrid=True, gridcolor="#ECEFF3"),
                      yaxis=dict(title=yt, showgrid=True, gridcolor="#ECEFF3"))
    return fig


def speed_chart(df):
    f = _base("Speed Response", "Time (s)", "Speed (RPM)", 340)
    f.add_scatter(x=df.time, y=df.setpoint, name="Setpoint", line=dict(color=ORANGE, dash="dash"))
    f.add_scatter(x=df.time, y=df.rpm, name="Actual RPM", line=dict(color=BLUE, width=2.5))
    return f


def line_chart(df, col, title, ylabel, color):
    f = _base(title, "Time (s)", ylabel)
    f.add_scatter(x=df.time, y=df[col], name=ylabel, line=dict(color=color, width=2))
    return f


def blackbox_chart(xs, label, xlabel):
    f = _base(f"Blackbox Characteristic: {label}", xlabel, "Speed (RPM)", 320)
    f.add_scatter(x=xs, y=RPM_ARR, mode="lines+markers", name="Data jurnal", line=dict(color=BLUE))
    return f


def comparison_chart(query_pwm=None):
    p = np.linspace(0, 255, 256)
    f = _base("Model Comparison", "PWM (0-255)", "Speed (RPM)", 360)
    f.add_scatter(x=PWM_ARR, y=RPM_ARR, mode="markers", name="Data aktual jurnal", marker=dict(color=BLUE, size=9))
    f.add_scatter(x=p, y=np.interp(p, PWM_ARR, RPM_ARR), name="Interpolasi", line=dict(color=GREEN))
    f.add_scatter(x=p, y=K * 12.0 * p / 255.0, name="Transfer function (steady-state)",
                  line=dict(color=ORANGE, dash="dash"))
    if query_pwm is not None:
        f.add_vline(x=query_pwm, line=dict(color=GRAY, dash="dot"))
    return f


def zn_chart(ku=1.8, pu=0.2):
    t = np.linspace(0, 1.0, 600)
    f = _base("Sustained oscillation (ILUSTRASI, bukan data mentah penelitian)", "Time (s)", "Speed deviation (a.u.)", 300)
    f.add_scatter(x=t, y=np.sin(2 * np.pi * t / pu), name=f"Kp = Ku = {ku}, Pu = {pu} s", line=dict(color=BLUE))
    return f
