# kelompok1_kendalikecepatanmotor

# DC MOTOR 12V — PID CONTROL SIMULATOR
*Interactive DC Motor Speed Control Laboratory* — laboratorium virtual Streamlit untuk kendali kecepatan motor DC 12 V (Blackbox + PID Ziegler-Nichols).

## Fitur
Open Loop, PID Manual, PID Ziegler-Nichols, PID Optimized; visual motor SVG yang berputar mengikuti RPM simulasi; 6 grafik Plotly; identifikasi blackbox; halaman Ziegler-Nichols; analisis performa (rise time, overshoot, settling ±2%, peak, SS error, RMSE); diagram blok.

## Model
G(s) = 28.37 / (0.192s + 1), diskritisasi eksak `a = exp(-dt/tau)`; `V = Vsupply * PWM / 255`. Alternatif: interpolasi dataset blackbox jurnal.

## PID
Error dalam RPM, output langsung dalam PWM 0–255. Derivative on measurement, anti-windup (conditional integration). Preset: ZN Kp=1.08, Ki=10.8, Kd=0.027 (Ku=1.8, Pu=0.2 s); Optimized Kp=2.50, Ki=0.50, Kd=0.10.

## Asumsi
Simulasi satu arah, plant ideal tanpa noise/beban, driver BTS7960 dan encoder diasumsikan ideal. Hasil tidak diklaim identik dengan MATLAB atau eksperimen fisik. Sampling default 0.01 s (identifikasi jurnal 0.05 s).

## Instalasi & Menjalankan (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Tes: `pytest`

## Struktur
`app.py`, `simulation/` (model, PID, simulator, performa), `components/` (visual motor, grafik, diagram blok), `assets/style.css`, `data/blackbox_data.csv`, `tests/`.

## Referensi
Jurnal yang dilampirkan pengguna (isi sitasi lengkap di sini).
