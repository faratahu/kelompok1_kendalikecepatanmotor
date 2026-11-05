"""Visual motor DC (SVG + JS). Sudut awal dihitung Python dari integrasi RPM simulasi,
JS melanjutkan putaran dengan rotation_speed = RPM * 360 / 60 (deg/s)."""

_HTML = """
<style>
body { margin: 0; font-family: Inter, Segoe UI, Arial, sans-serif; background: transparent; }
.txt-title { font-size: 26px; font-weight: 700; fill: #2F3640; text-anchor: middle; }
.txt-sub { font-size: 11px; fill: #6B7482; text-anchor: middle; }
.txt-badge { font-size: 12px; fill: #3B5B8C; text-anchor: middle; }
.lbl-box { fill: #F7F8FA; stroke: #6B7482; }
.lbl-t1 { font-size: 11px; font-weight: 700; text-anchor: middle; fill: #2F3640; }
.lbl-t2 { font-size: 11px; text-anchor: middle; fill: #3B5B8C; }
.rotor-housing { fill: #F4F6F8; stroke: #8D96A3; }
.rotor-plate { fill: #E4E8EE; stroke: #3B5B8C; stroke-width: 2; }
@media (prefers-color-scheme: dark) {
  .txt-title { fill: #FAFAFA; }
  .txt-sub { fill: #A0AAB8; }
  .txt-badge { fill: #7AA2E3; }
  .lbl-box { fill: #262730; stroke: #8D96A3; }
  .lbl-t1 { fill: #FAFAFA; }
  .lbl-t2 { fill: #7AA2E3; }
  .rotor-housing { fill: #1E232A; stroke: #4D5666; }
  .rotor-plate { fill: #2A323D; stroke: #5B82B8; }
}
</style>
<svg viewBox="0 0 520 300" width="100%" xmlns="http://www.w3.org/2000/svg">
<defs>
 <linearGradient id="m" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#E9ECF0"/><stop offset=".45" stop-color="#C9CFD8"/><stop offset="1" stop-color="#A9B1BD"/></linearGradient>
 <linearGradient id="c" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#9AA3B0"/><stop offset="1" stop-color="#707A89"/></linearGradient>
</defs>
<rect x="60" y="212" width="170" height="14" rx="3" fill="url(#c)" stroke="#6B7482"/>
<circle cx="80" cy="219" r="3.5" fill="#4B5563"/><circle cx="210" cy="219" r="3.5" fill="#4B5563"/>
<rect x="36" y="88" width="30" height="124" rx="6" fill="url(#c)" stroke="#6B7482"/>
<rect x="64" y="88" width="170" height="124" fill="url(#m)" stroke="#6B7482"/>
<rect x="234" y="88" width="30" height="124" rx="6" fill="url(#c)" stroke="#6B7482"/>
<g stroke="#8D96A3" stroke-width="2"><line x1="90" y1="104" x2="90" y2="140"/><line x1="100" y1="104" x2="100" y2="140"/>
<line x1="110" y1="104" x2="110" y2="140"/><line x1="120" y1="104" x2="120" y2="140"/><line x1="130" y1="104" x2="130" y2="140"/></g>
<rect x="150" y="150" width="76" height="40" rx="4" class="lbl-box"/>
<text x="188" y="167" class="lbl-t1">DC MOTOR</text>
<text x="188" y="182" class="lbl-t2">12 V</text>
<rect x="264" y="140" width="66" height="20" fill="#B8BFC9" stroke="#6B7482"/>
<g id="stripes" stroke="#6B7482" stroke-width="1.5"><line x1="280" y1="140" x2="280" y2="160"/><line x1="300" y1="140" x2="300" y2="160"/><line x1="320" y1="140" x2="320" y2="160"/></g>
<text x="150" y="250" class="txt-sub">Side view</text>
<circle cx="420" cy="150" r="100" fill="url(#m)" stroke="#6B7482" stroke-width="2"/>
<circle cx="420" cy="150" r="84" class="rotor-housing"/>
<g fill="#4B5563"><circle cx="352" cy="82" r="5"/><circle cx="488" cy="82" r="5"/><circle cx="352" cy="218" r="5"/><circle cx="488" cy="218" r="5"/></g>
<g id="rot">
 <circle cx="420" cy="150" r="64" class="rotor-plate"/>
 <g stroke="#3B5B8C" stroke-width="5" stroke-linecap="round">
  <line x1="420" y1="150" x2="420" y2="94"/><line x1="420" y1="150" x2="468.5" y2="122"/><line x1="420" y1="150" x2="468.5" y2="178"/>
  <line x1="420" y1="150" x2="420" y2="206"/><line x1="420" y1="150" x2="371.5" y2="178"/><line x1="420" y1="150" x2="371.5" y2="122"/></g>
 <circle cx="420" cy="98" r="7" fill="#D98B4A"/>
 <circle cx="420" cy="150" r="14" fill="#7A8493" stroke="#4B5563"/>
</g>
<text x="420" y="268" class="txt-sub">Front view (rotor, shaft end)</text>
<text x="330" y="36" class="txt-title">__RPM__ RPM</text>
<text x="330" y="58" class="txt-badge">STATUS: __STATUS__  |  &#8635; CW</text>
<text x="330" y="290" class="txt-sub">Motor animation follows simulated RPM.</text>
</svg>
<script>
const g=document.getElementById('rot'), a0=__ANGLE__, w=__RPM_RAW__*360/60, run=__RUN__, t0=performance.now();
function f(n){const a=(a0+(run?w*(n-t0)/1000:0))%360;g.setAttribute('transform','rotate('+a.toFixed(2)+' 420 150)');requestAnimationFrame(f);}
requestAnimationFrame(f);
</script>
"""


def motor_html(rpm, angle, running, status):
    return (_HTML.replace("__RPM_RAW__", f"{rpm:.4f}").replace("__RPM__", f"{rpm:.1f}")
            .replace("__ANGLE__", f"{angle:.3f}").replace("__RUN__", "true" if running else "false")
            .replace("__STATUS__", status))
