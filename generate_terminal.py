#!/usr/bin/env python3
"""Genera terminal.svg: terminal bash animada con Hello Kitty, tus lenguajes más usados
y el repo con más commits de los últimos 7 días (datos reales vía API de GitHub).
Uso local:  GITHUB_USER=tu-usuario GITHUB_TOKEN=xxx python generate_terminal.py
Sin token/usuario usa datos de ejemplo."""
import os, json, urllib.request, urllib.parse, datetime
from html import escape

# ---------- CONFIG (edita a gusto) ----------
USER   = os.getenv("GITHUB_USER") or os.getenv("GITHUB_REPOSITORY_OWNER") or ""
TOKEN  = os.getenv("GITHUB_TOKEN", "")
SHELL_USER, HOST = "majo", "Majo"
OS_LINE  = "Windows 11 Home Single Language (25H2) x86_64"
CPU_LINE = "Intel(R) Core(TM) i3-N305 (8) @ 1.80 GHz"
HOST_LINE = "E1504GAB (1.0)"
OUT = "terminal.svg"
# Tipografía estilo Cascadia (la de tu captura). Se usa la primera que tenga instalada quien vea el SVG.
FONT = '"Cascadia Code","Cascadia Mono","JetBrains Mono","Fira Code",Consolas,"DejaVu Sans Mono","Courier New",monospace'
FONT_SIZE = 15
CHAR_W = 0.586          # ancho de carácter / tamaño (Cascadia = 0.586; Courier = 0.6)
# --------------------------------------------

KITTY = ["⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⡀⣰⡿⠛⠛⠿⢶⣦⣀⠀⢀⣀⣀⣀⣀⣠⡾⠋⠀⠀⠹⣷⣄⣤⣶⡶⠿⠿⣷⡄⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⢰⣿⠁⠀⠀⠀⠀⠈⠙⠛⠛⠋⠉⠉⢹⡟⠁⠀⠀⣀⣀⠘⣿⠉⠀⠀⠀⠀⠘⣿⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⣾⡋⣽⠿⠛⠿⢶⣤⣤⣤⣤⣿⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⢸⣿⡴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣄⡀⠀⢈⣻⡏⠀⠀⠀⠀⣿⣀⠀⠈⠙⣷⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⣰⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠛⠛⠙⢷⣄⣀⣀⣼⣏⣿⠀⠀⢀⣿⠀⠀⠀⠀", "⠀⠀⠀⠀⢸⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⣿⡉⠉⠁⢀⣠⣿⡇⠀⠀⠀⠀", "⠀⠀⠀⠀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠗⠾⠟⠋⢹⣷⠀⠀⠀⠀", "⢀⣤⣤⣤⣿⣤⣄⠀⠀⠀⠴⠚⠲⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡆⠀⠀⠀⠀⢀⣈⣿⣀⣀⡀⠀", "⠀⠀⠀⠈⣿⣠⣾⠟⠛⢷⡄⠀⠀⠀⠀⠀⠀⠀⡤⠶⢦⡀⠀⠀⠀⠀⠹⠯⠃⠀⠀⠀⠈⠉⢩⡿⠉⠉⠉⠁", "⠀⠀⣤⡶⠿⣿⣇⠀⠀⠸⣷⠀⠀⠀⠀⠀⠀⠀⠓⠶⠞⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⣼⣯⣀⣀⠀⠀", "⠀⢰⣯⠀⠀⠈⠻⠀⠀⠀⣿⣶⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠁⠉⠉⠁⠀", "⠀⠀⠙⣷⣄⠀⠀⠀⠀⠀⢀⣀⣀⠙⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣿⡿⢷⣄⡀⠀⠀⠀", "⠀⠀⠀⠈⠙⣷⠀⠀⠀⣴⠟⠉⠉⠀⠀⣿⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣾⠟⠉⠀⠀⠈⠉⠀⠀⠀", "⠀⠀⠀⠀⠰⣿⠀⠀⠀⠙⢧⣤⡶⠟⢀⣿⠛⢟⡟⡯⠽⢶⡶⠾⢿⣻⣏⣹⡏⣁⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀⠀⣠⣾⠏⠀⠀⠙⠛⠛⠋⠀⠀⢀⣽⠟⠛⠖⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⠀⠀⠙⠻⠷⠶⠿⠟⠋⠹⣷⣤⣀⡀⠄⣡⣀⣠⣴⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣍⣉⣻⣏⣉⣡⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"]   # Hello Kitty en braille (cada carácter = 2x4 puntos)
BG  = "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"

def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN: req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def get_data():
    sample = ([("Python", 46), ("JavaScript", 27), ("TypeScript", 15), ("HTML", 12)],
              ("cozy-portfolio", 23))
    if not USER: return sample
    try:
        repos = api(f"/users/{USER}/repos?per_page=100&sort=pushed&type=owner")
        tot = {}
        for r in repos:
            if r.get("fork"): continue
            for lang, b in api(f"/repos/{r['full_name']}/languages").items():
                tot[lang] = tot.get(lang, 0) + b
        s = sum(tot.values()) or 1
        top = sorted(tot.items(), key=lambda x: -x[1])[:4]
        langs = [(k, round(v * 100 / s)) for k, v in top] or sample[0]
        since = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        q = urllib.parse.quote(f"author:{USER} author-date:>={since}")
        items = api(f"/search/commits?q={q}&per_page=100").get("items", [])
        cnt = {}
        for it in items:
            n = it["repository"]["name"]; cnt[n] = cnt.get(n, 0) + 1
        repo = max(cnt.items(), key=lambda x: x[1]) if cnt else ("(sin commits esta semana)", 0)
        return langs, repo
    except Exception as e:
        print("API error, usando ejemplo:", e); return sample

LANGS, (REPO, NCOMMITS) = get_data()

T = 20.0                      # duración del loop (s)
CW = FONT_SIZE * CHAR_W       # ancho de carácter en px
pct = lambda t: f"{t / T * 100:.3f}%"
css, body = [], []
_n = [0]
def kf(frames):
    _n[0] += 1; name = f"a{_n[0]}"
    css.append(f"@keyframes {name}{{{frames}}}")
    return name
def anim(name, extra=""):
    return f"animation:{name} {T}s linear infinite;{extra}"

def appear(t0, inner, dur=0.35):
    """grupo que aparece (fade) en t0 y se reinicia al final del loop"""
    n = kf(f"0%,{pct(t0)}{{opacity:0}}{pct(t0+dur)},{pct(T-1.6)}{{opacity:1}}{pct(T-0.6)},100%{{opacity:0}}")
    return f'<g style="{anim(n)}opacity:0">{inner}</g>'

def typed(t0, t1, y, prompt, cmd):
    """línea con prompt + comando que se 'teclea' de t0 a t1"""
    n = len(cmd); cid = f"c{_n[0]+1}"
    pw = len(prompt) * CW; fw = (len(prompt) + n) * CW
    k = kf(f"0%,{pct(t0)}{{width:{pw}px}}{pct(t0)}{{width:{pw}px;animation-timing-function:steps({n},end)}}"
           f"{pct(t1)},{pct(T-0.6)}{{width:{fw+4}px}}100%{{width:{pw}px}}")
    kc = kf(f"0%,{pct(t0)}{{transform:translateX(0);opacity:1}}{pct(t0)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{pct(t1)}{{transform:translateX({n*CW}px);opacity:1}}{pct(t1+0.25)},100%{{transform:translateX({n*CW}px);opacity:0}}")
    css.append(f"#{cid} rect{{{anim(k)}}}")
    line = (f'<clipPath id="{cid}"><rect x="40" y="{y-15}" width="{pw}" height="22"/></clipPath>'
            f'<g clip-path="url(#{cid})"><text x="40" y="{y}" textLength="{fw}" lengthAdjust="spacing"><tspan class="u">{SHELL_USER}@{HOST}</tspan>'
            f'<tspan class="w">:</tspan><tspan class="p">~</tspan><tspan class="w">$ </tspan>'
            f'<tspan class="c">{escape(cmd)}</tspan></text></g>'
            f'<rect x="{40+len(prompt)*CW}" y="{y-13}" width="{CW}" height="18" fill="var(--pink)" style="{anim(kc)}opacity:0"/>')
    return appear(t0, line, 0.01)

PROMPT = f"{SHELL_USER}@{HOST}:~$ "
# ---- neofetch ----
body.append(typed(0.5, 1.5, 62, PROMPT, "neofetch"))
BITS = {1: (0, 0), 2: (0, 1), 4: (0, 2), 8: (1, 0), 16: (1, 1), 32: (1, 2), 64: (0, 3), 128: (1, 3)}
def braille_dots(rows, x0, y0, P=2.6, r=1.05):
    d = []
    for ri, row in enumerate(rows):
        for ci, ch in enumerate(row):
            m = ord(ch) - 0x2800
            if not 0 < m < 256: continue
            for bit, (dx, dy) in BITS.items():
                if m & bit:
                    cx, cy = x0 + (ci * 2 + dx + .5) * P, y0 + (ri * 4 + dy + .5) * P
                    d.append(f"M{cx-r:.1f} {cy:.1f}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 -{2*r} 0")
    return "".join(d)
art = f'<path d="{braille_dots(KITTY, 40, 76)}" fill="var(--kitty)"/>'
body.append(appear(2.0, art, 0.9))
ix, rows = 272, []
rows.append(f'<text x="{ix}" y="124" class="u" font-weight="bold">{SHELL_USER}@{HOST}</text>')
for i, (lab, val) in enumerate([("OS", OS_LINE), ("CPU", CPU_LINE), ("Host", HOST_LINE)]):
    y = 170 + i * 22
    rows.append(f'<text x="{ix}" y="{y}"><tspan class="u">{lab}</tspan><tspan class="w"> {escape(val)}</tspan></text>')
cols = ["#3d2b4a", "#ffffff", "#ff8fc0", "#f06bb0", "#c9a0ff", "#ffc2e0", "#ff9ccf", "#ff5fa8"]
rows.append("".join(f'<circle cx="{ix+5+j*24}" cy="{244}" r="5" fill="{c}"/>' for j, c in enumerate(cols)))
for i, r in enumerate(rows):
    body.append(appear(2.4 + i * 0.25, r))

# ---- whoami ----
body.append(typed(4.6, 5.3, 308, PROMPT, "whoami"))
body.append(appear(5.6, f'<text x="40" y="330" class="w">{SHELL_USER}</text>'))

# ---- stats ----
body.append(typed(6.8, 8.6, 364, PROMPT, "devstats --langs --week"))
y = 392
body.append(appear(9.0, f'<text x="40" y="{y}" class="p" font-weight="bold">♥ top languages</text>'))
barcols = ["#ff8fc0", "#f06bb0", "#c9a0ff", "#ffc2e0"]
for i, (lang, p) in enumerate(LANGS):
    yy = y + 24 + i * 22
    bw = max(4, int(p * 2.2))
    kb = kf(f"0%,{pct(9.4+i*.3)}{{transform:scaleX(0)}}{pct(10.0+i*.3)},{pct(T-0.6)}{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}")
    row = (f'<text x="40" y="{yy}" class="w">{escape(lang):<12}</text>'
           f'<rect x="150" y="{yy-11}" width="220" height="10" rx="5" fill="#ffffff" opacity=".07"/>'
           f'<rect x="150" y="{yy-11}" width="{bw}" height="10" rx="5" fill="{barcols[i%4]}" '
           f'style="{anim(kb)}transform-box:fill-box;transform-origin:left;transform:scaleX(0)"/>'
           f'<text x="382" y="{yy}" class="d">{p}%</text>')
    body.append(appear(9.4 + i * 0.3, row))
y2 = y + 24 + len(LANGS) * 22 + 22
body.append(appear(11.6, f'<text x="40" y="{y2}" class="p" font-weight="bold">♥ currently working on</text>'))
body.append(appear(12.2, f'<text x="40" y="{y2+24}"><tspan class="u">{escape(REPO)}</tspan>'
                         f'<tspan class="d">  ·  {NCOMMITS} commits this week</tspan></text>'))
# ---- prompt final con cursor parpadeante ----
yf = y2 + 24 + 40
kfn = kf(f"0%,{pct(13.0)}{{opacity:0}}{pct(13.01)},{pct(T-1.6)}{{opacity:1}}{pct(T-0.6)},100%{{opacity:0}}")
css.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
body.append(f'<g style="{anim(kfn)}opacity:0"><text x="40" y="{yf}"><tspan class="u">{SHELL_USER}@{HOST}</tspan>'
            f'<tspan class="w">:</tspan><tspan class="p">~</tspan><tspan class="w">$ </tspan></text>'
            f'<rect x="{40+len(PROMPT)*CW}" y="{yf-13}" width="{CW}" height="18" fill="var(--pink)" style="animation:blink 1s steps(1) infinite"/></g>')

H = yf + 34
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{H}" viewBox="0 0 800 {H}">
<defs>
<clipPath id="win"><rect x="0" y="0" width="800" height="{H}" rx="14"/></clipPath>
</defs>
<style>
:root{{--bg:#1a1023;--bar:#241731;--pink:#ff7eb6;--kitty:#ffc9e0;--text:#f3e6ef;--dim:#a58fa8;--lav:#c9a0ff}}
text{{font-family:{FONT};font-size:{FONT_SIZE}px;white-space:pre}}
.u{{fill:var(--pink)}}.w{{fill:var(--text)}}.p{{fill:var(--lav)}}.c{{fill:var(--text)}}.d{{fill:var(--dim)}}.k{{fill:var(--kitty);font-size:8.5px}}
{chr(10).join(css)}
</style>
<g clip-path="url(#win)">
<rect width="800" height="{H}" fill="var(--bg)"/>
<image href="data:image/jpeg;base64,{BG}" x="0" y="34" width="800" height="{H-34}" preserveAspectRatio="xMidYMid slice" opacity=".10"/>
<rect width="800" height="34" fill="var(--bar)"/>
<circle cx="20" cy="17" r="6" fill="#ff6b8b"/><circle cx="42" cy="17" r="6" fill="#ffc27a"/><circle cx="64" cy="17" r="6" fill="#b69cff"/>
<text x="400" y="22" text-anchor="middle" fill="#a58fa8" font-size="13">{SHELL_USER}@{HOST}: ~ — bash</text>
{chr(10).join(body)}
</g>
<rect x=".5" y=".5" width="799" height="{H-1}" rx="14" fill="none" stroke="#ff7eb6" stroke-opacity=".35"/>
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg)
print("OK ->", OUT, len(svg) // 1024, "KB")
