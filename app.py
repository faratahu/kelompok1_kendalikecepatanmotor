from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from simulation.motor_model import (BLACKBOX_DATA, TF_MODEL, BB_MODEL, K, TAU, VOLT_ARR, PWM_ARR, RPM_ARR,
                                    interp_rpm, in_range)
from simulation.simulator import Config, Simulation, MODES, PRESETS, run_full, open_loop_pwm_for
from simulation.performance import compute_metrics
from components import charts
from components.motor_visual import motor_html
from components.block_diagram import BLOCKS, diagram_html

st.set_page_config(page_title="DC MOTOR 12V — PID CONTROL SIMULATOR", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'assets' / 'style.css').read_text()}</style>", unsafe_allow_html=True)
ss = st.session_state
for k, v in dict(running=False, sim=None, mode="PID Ziegler-Nichols", model=TF_MODEL, sp=200.0, kp=1.08, ki=10.8,
                 kd=0.027, pwm=128, dt=0.01, dur=10.0, vs=12.0).items():
    ss.setdefault(k, v)


def get_cfg():
    return Config(mode=ss.mode, model=ss.model, setpoint=float(ss.sp), kp=float(ss.kp), ki=float(ss.ki),
                  kd=float(ss.kd), pwm_manual=float(ss.pwm), dt=float(ss.dt), duration=float(ss.dur),
                  vsupply=float(ss.vs))


def on_mode():
    p = PRESETS[ss.mode]
    if p:
        ss.kp, ss.ki, ss.kd = p


def do_start():
    if ss.sim is None or ss.sim.done:
        ss.sim = Simulation(get_cfg())
    ss.running = True


def do_pause():
    ss.running = False


def do_resume():
    if ss.sim is not None and not ss.sim.done:
        ss.running = True


def do_reset():
    ss.sim, ss.running = None, False


# ---------------- Sidebar: control panel ----------------
with st.sidebar:
    st.header("Control Panel")
    st.selectbox("Mode", MODES, key="mode", on_change=on_mode)
    st.selectbox("Plant model", [TF_MODEL, BB_MODEL], key="model")
    st.slider("Setpoint (RPM)", 0.0, 350.0, key="sp", step=1.0)
    gains = ss.mode != "PID Manual"
    st.number_input("Kp", 0.0, 100.0, key="kp", step=0.01, format="%.3f", disabled=gains)
    st.number_input("Ki", 0.0, 100.0, key="ki", step=0.01, format="%.3f", disabled=gains)
    st.number_input("Kd", 0.0, 10.0, key="kd", step=0.001, format="%.3f", disabled=gains)
    st.slider("PWM manual (Open Loop)", 0, 255, key="pwm", disabled=ss.mode != "Open Loop")
    st.number_input("Sampling time (s)", 0.001, 0.1, key="dt", step=0.001, format="%.3f", disabled=ss.sim is not None)
    st.caption("Sampling time identifikasi jurnal: 0.05 s. Reset untuk mengubah sampling time.")
    st.number_input("Simulation duration (s)", 1.0, 120.0, key="dur", step=1.0)
    st.slider("Supply voltage (V)", 6.0, 12.0, key="vs", step=0.5)
    st.caption("Gain diubah otomatis oleh preset; pilih *PID Manual* untuk mengedit.")

# ---------------- Header ----------------
h1, h2 = st.columns([3, 2])
with h1:
    st.markdown('<p class="hdr-title">DC MOTOR 12V — PID CONTROL SIMULATOR</p>'
                '<p class="hdr-sub"><i>Interactive DC Motor Speed Control Laboratory</i></p>', unsafe_allow_html=True)
with h2:
    b = st.columns(4)
    b[0].button("Start", on_click=do_start, use_container_width=True, type="primary")
    b[1].button("Pause", on_click=do_pause, use_container_width=True)
    b[2].button("Resume", on_click=do_resume, use_container_width=True)
    b[3].button("Reset", on_click=do_reset, use_container_width=True)

tabs = st.tabs(["Simulator", "Blackbox", "Ziegler-Nichols", "Performance", "Block Diagram & Docs"])

# ---------------- Tab 1: live simulator ----------------
with tabs[0]:
    @st.fragment(run_every=0.3 if ss.running else None)
    def live():
        sim = ss.sim
        if sim is not None:
            sim.set_cfg(get_cfg())
            if ss.running:
                for _ in range(max(1, int(round(0.3 / sim.cfg.dt)))):
                    if sim.done:
                        break
                    sim.step()
                if sim.done:
                    ss.running = False
                    st.rerun()
        df = sim.df if sim else pd.DataFrame(columns=["time", "setpoint", "rpm", "error", "pwm", "voltage"])
        rpm = sim.rpm if sim else 0.0
        status = sim.status() if sim else "STOP"
        state = "Running" if ss.running else ("Finished" if sim and sim.done else ("Paused" if sim else "Idle"))
        st.markdown(f'Simulation: <span class="badge">{state}</span> &nbsp; Motor: <span class="badge">{status}</span>',
                    unsafe_allow_html=True)
        c = st.columns(6)
        c[0].metric("Setpoint (RPM)", f"{ss.sp:.0f}" if ss.mode != "Open Loop" else "—")
        c[1].metric("Actual (RPM)", f"{rpm:.1f}")
        c[2].metric("Error (RPM)", f"{(ss.sp - rpm) if ss.mode != 'Open Loop' else 0:.1f}")
        c[3].metric("PWM Output", f"{sim.last_pwm:.1f}" if sim else "0.0")
        c[4].metric("Motor Voltage (V)", f"{sim.last_v:.2f}" if sim else "0.00")
        c[5].metric("Sim Time (s)", f"{sim.t:.2f}" if sim else "0.00")
        l, r = st.columns([1, 1.4])
        with l:
            components.html(motor_html(rpm, sim.angle if sim else 0.0, bool(ss.running), status), height=330)
        with r:
            st.plotly_chart(charts.speed_chart(df), use_container_width=True, key="g_speed")
        g = st.columns(3)
        g[0].plotly_chart(charts.line_chart(df, "pwm", "PWM Output", "PWM (0-255)", charts.GREEN), use_container_width=True, key="g_pwm")
        g[1].plotly_chart(charts.line_chart(df, "voltage", "Motor Voltage", "Voltage (V)", charts.ORANGE), use_container_width=True, key="g_v")
        g[2].plotly_chart(charts.line_chart(df, "error", "Control Error", "Error (RPM)", charts.GRAY), use_container_width=True, key="g_e")
        if len(df) > 2:
            m = compute_metrics(df.time, df.setpoint, df.rpm)
            st.caption("Live metrics — " + ", ".join(f"{k}: {v:.3f}" for k, v in m.items()))
    live()

# ---------------- Tab 2: Blackbox ----------------
with tabs[1]:
    st.subheader("Blackbox Identification")
    c1, c2 = st.columns([1, 2])
    c1.dataframe(pd.DataFrame(BLACKBOX_DATA), hide_index=True, use_container_width=True)
    with c2:
        a, b2 = st.columns(2)
        a.plotly_chart(charts.blackbox_chart(PWM_ARR, "PWM vs RPM", "PWM (0-255)"), use_container_width=True, key="bb1")
        b2.plotly_chart(charts.blackbox_chart(VOLT_ARR, "Voltage vs RPM", "Voltage (V)"), use_container_width=True, key="bb2")
    q = st.number_input("Input PWM untuk estimasi RPM", value=128.0, step=1.0, key="q_pwm")
    if in_range(q):
        st.success(f"Estimasi interpolasi: **{interp_rpm(q):.1f} RPM**  |  Transfer function steady-state: {K * 12 * q / 255:.1f} RPM")
    else:
        st.warning("PWM di luar rentang dataset (0–255). Ekstrapolasi tidak dilakukan; nilai tidak diestimasi.")
    st.plotly_chart(charts.comparison_chart(q if in_range(q) else None), use_container_width=True, key="bb3")

# ---------------- Tab 3: Ziegler-Nichols ----------------
with tabs[2]:
    st.subheader("Metode Ziegler-Nichols (Closed-Loop)")
    st.markdown("""
1. Nonaktifkan integral (Ki = 0). 2. Nonaktifkan derivatif (Kd = 0). 3. Naikkan Kp bertahap.
4. Amati *sustained oscillation*. 5. Catat ultimate gain **Ku**. 6. Ukur ultimate period **Pu**. 7. Hitung parameter PID.
""")
    ku, pu = 1.80, 0.2
    kp, ti, td = 0.6 * ku, pu / 2, pu / 8
    st.latex(r"K_p=0.6K_u,\quad T_i=P_u/2,\quad T_d=P_u/8,\quad K_i=K_p/T_i,\quad K_d=K_pT_d")
    st.table(pd.DataFrame({"Parameter": ["Ku", "Pu (s)", "Kp", "Ki", "Kd"],
                           "Nilai": [ku, pu, round(kp, 3), round(kp / ti, 3), round(kp * td, 3)]}))
    st.plotly_chart(charts.zn_chart(ku, pu), use_container_width=True, key="zn")

# ---------------- Tab 4: Performance ----------------
with tabs[3]:
    st.subheader("Performance Analysis (dari simulasi aplikasi)")
    base = get_cfg()
    rows = []
    for mode in MODES:
        cfg = replace(base, mode=mode)
        if PRESETS[mode]:
            cfg = replace(cfg, kp=PRESETS[mode][0], ki=PRESETS[mode][1], kd=PRESETS[mode][2])
        if mode == "Open Loop":
            cfg = replace(cfg, pwm_manual=open_loop_pwm_for(cfg))
        d = run_full(cfg)
        m = compute_metrics(d.time, d.setpoint, d.rpm)
        rows.append({"Mode": mode, "Rise Time (s)": m["rise_time"], "Overshoot (%)": m["overshoot"],
                     "Settling ±2% (s)": m["settling_time"], "Peak RPM": m["peak_rpm"],
                     "Peak Time (s)": m["peak_time"], "SS Error (RPM)": m["ss_error"], "RMSE (RPM)": m["rmse"]})
    st.dataframe(pd.DataFrame(rows).round(3), hide_index=True, use_container_width=True)
    st.caption("Open Loop memakai PWM ekuivalen yang menargetkan setpoint saat ini. PID Manual memakai Kp/Ki/Kd di sidebar.")
    st.markdown("**Referensi hasil jurnal** (isi manual dari jurnal; terpisah dari hasil simulasi):")
    st.data_editor(pd.DataFrame({"Mode": MODES, "Rise Time (s)": [None] * 4, "Overshoot (%)": [None] * 4,
                                 "Settling (s)": [None] * 4}), hide_index=True, use_container_width=True, key="jr")

# ---------------- Tab 5: Block diagram & docs ----------------
with tabs[4]:
    l, r = st.columns([1, 1.6])
    with l:
        components.html(diagram_html(), height=620)
    with r:
        st.subheader("Fungsi blok")
        for n, d in BLOCKS:
            st.markdown(f"**{n}** — {d}")
        st.info("Website ini adalah simulasi perangkat lunak, bukan koneksi langsung ke hardware Arduino atau BTS7960.")
    st.subheader("Dokumentasi model")
    st.markdown(f"""
- **Transfer Function Jurnal:** G(s) = {K} / ({TAU}s + 1), didiskritkan eksak: `rpm[k+1] = a·rpm[k] + (1−a)·K·V`, `a = exp(−dt/τ)`.
- **Blackbox Interpolation:** RPM steady-state diambil dari interpolasi linear dataset PWM–RPM jurnal, dengan dinamika orde-1 (τ sama).
  Model ini menangkap ketidaklinearan statis dataset, sedangkan transfer function murni linear (gain tetap).
- Konvensi PID: error dalam RPM, keluaran langsung dalam satuan PWM (0–255), dibatasi dan diberi anti-windup. Preset jurnal tidak dimodifikasi.
- Hasil simulasi **tidak** diklaim identik dengan MATLAB atau eksperimen fisik.
""")
