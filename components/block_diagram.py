BLOCKS = [
    ("Setpoint RPM", "Kecepatan target (0-350 RPM) dari pengguna."),
    ("Summing Junction", "Menghitung error = setpoint - RPM terukur."),
    ("PID Controller", "Menghitung aksi P, I, D (derivative on measurement, anti-windup)."),
    ("PWM Limiter", "Membatasi keluaran ke 0-255."),
    ("Voltage Conversion", "V = Vsupply x PWM / 255 (maks 12 V)."),
    ("BTS7960 Motor Driver", "Driver daya H-bridge pada sistem fisik (disimulasikan sebagai konversi ideal)."),
    ("DC Motor 12V", "Plant: G(s) = 28.37 / (0.192s + 1) atau interpolasi blackbox."),
    ("Rotary Encoder", "Sensor kecepatan pada sistem fisik (disimulasikan sebagai pengukuran ideal)."),
    ("Actual RPM Feedback", "RPM aktual dikembalikan ke summing junction."),
]


def diagram_html():
    items = []
    for i, (n, _) in enumerate(BLOCKS):
        items.append(f'<div class="b">{i+1}. {n}</div>')
        if i < len(BLOCKS) - 1:
            items.append('<div class="a">&#8595;</div>')
    return ("<style>body{font-family:Inter,Segoe UI,Arial,sans-serif;margin:0}.b{border:1px solid #CBD2DB;"
            "border-radius:6px;padding:8px 14px;background:#F7F9FC;color:#2F3640;text-align:center;font-size:14px}"
            ".a{text-align:center;color:#3B5B8C;font-size:16px;line-height:16px}"
            ".n{margin-top:10px;font-size:12px;color:#6B7482;text-align:center}</style>"
            + "".join(items) + '<div class="n">&#8635; Feedback: blok 9 kembali ke blok 2</div>')
