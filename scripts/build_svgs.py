#!/usr/bin/env python3
"""Generate the animated profile SVGs (light + dark) into ../assets.

Run:  python3 scripts/build_svgs.py
Edit the TERMINAL lines or the NODES/ROUTES below, re-run, commit.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d", fg="#e6edf3",
                 muted="#7d8590", accent="#2f81f7", green="#3fb950",
                 orange="#d29922", purple="#a371f7", red="#f85149"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", fg="#1f2328",
                  muted="#656d76", accent="#0969da", green="#1a7f37",
                  orange="#9a6700", purple="#8250df", red="#cf222e"),
}

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- terminal --
# Each entry: (kind, text). kind "cmd" is typed out; "out" appears instantly.
# Output rows may colour segments with [[colour:text]].
TERMINAL = [
    ("cmd", "whoami"),
    ("out", "[[fg:Anand Mishra]] — backend & cloud-native engineer · Sonipat, IN"),
    ("cmd", "kubectl get pods -n anand"),
    ("out", "[[muted:NAME              READY   STATUS      AGE]]"),
    ("out", "api-node-express  1/1     [[green:Running]]     3y"),
    ("out", "web-react-next    1/1     [[green:Running]]     2y"),
    ("out", "btech-ai-ml       1/1     [[green:Running]]     NST"),
    ("out", "learning-loop     1/1     [[orange:Restarting]]  ∞"),
    ("cmd", "curl -s anandmishra.dev/health"),
    ("out", '{ [[accent:"status"]]: [[green:"ok"]], [[accent:"open_to"]]: [[green:"collaborate"]], [[accent:"coffee"]]: [[orange:"low"]] }'),
]

CHAR_W = 8.4          # ~0.6em at 14px for common monospace fonts
LINE_H = 22
TYPE_SPEED = 0.045    # seconds per char
PAUSE = 0.35


def nbsp(s):
    """Escape and keep runs of spaces (renderers collapse them otherwise)."""
    return escape(s).replace("  ", "\u00a0\u00a0").replace("\u00a0 ", "\u00a0\u00a0")


def segments(text, t):
    out, i = [], 0
    while i < len(text):
        j = text.find("[[", i)
        if j == -1:
            out.append(("muted2", text[i:]))
            break
        if j > i:
            out.append(("muted2", text[i:j]))
        k = text.find("]]", j)
        colour, body = text[j + 2:k].split(":", 1)
        out.append((colour, body))
        i = k + 2
    return "".join(
        f'<tspan fill="{t["fg"] if c in ("fg", "muted2") else t[c]}"'
        f'{" opacity=\"0.82\"" if c == "muted2" else ""}>{nbsp(s)}</tspan>'
        for c, s in out)


def terminal_svg(t):
    W, top, left = 880, 66, 24
    H = top + LINE_H * len(TERMINAL) + 20
    prompt = "anand@prod:~$ "
    clock, rows, defs = 0.6, [], []
    for n, (kind, text) in enumerate(TERMINAL):
        y = top + n * LINE_H
        if kind == "cmd":
            dur = max(0.4, len(text) * TYPE_SPEED)
            cid = f"c{n}"
            x0 = left + len(prompt) * CHAR_W
            defs.append(
                f'<clipPath id="{cid}"><rect x="{x0}" y="{y - 16}" height="{LINE_H}" width="0">'
                f'<animate attributeName="width" from="0" to="{len(text) * CHAR_W + 2}" '
                f'begin="{clock:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
            rows.append(
                f'<g opacity="0"><set attributeName="opacity" to="1" begin="{clock:.2f}s" fill="freeze"/>'
                f'<text x="{left}" y="{y}"><tspan fill="{t["green"]}">anand@prod</tspan>'
                f'<tspan fill="{t["muted"]}">:</tspan><tspan fill="{t["accent"]}">~</tspan>'
                f'<tspan fill="{t["muted"]}">$ </tspan></text>'
                f'<text x="{x0}" y="{y}" fill="{t["fg"]}" clip-path="url(#{cid})">{escape(text)}</text></g>')
            clock += dur + PAUSE
        else:
            rows.append(
                f'<text x="{left}" y="{y}" opacity="0">{segments(text, t)}'
                f'<set attributeName="opacity" to="1" begin="{clock:.2f}s" fill="freeze"/></text>')
            clock += 0.12
    # final prompt with blinking cursor
    y = top + len(TERMINAL) * LINE_H
    cx = left + len(prompt) * CHAR_W
    rows.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{clock:.2f}s" fill="freeze"/>'
        f'<text x="{left}" y="{y}"><tspan fill="{t["green"]}">anand@prod</tspan>'
        f'<tspan fill="{t["muted"]}">:</tspan><tspan fill="{t["accent"]}">~</tspan>'
        f'<tspan fill="{t["muted"]}">$ </tspan></text>'
        f'<rect x="{cx}" y="{y - 14}" width="8" height="17" fill="{t["fg"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
        f'</rect></g>')
    dots = "".join(f'<circle cx="{24 + i * 20}" cy="20" r="6" fill="{c}"/>'
                   for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: Anand Mishra, backend and cloud-native engineer">
<title>anand@prod — terminal</title>
<defs>{"".join(defs)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
<path d="M0.5 40 V12.5 a12 12 0 0 1 12 -12 H{W - 12.5} a12 12 0 0 1 12 12 V40 Z" fill="{t["panel"]}"/>
<line x1="0.5" y1="40" x2="{W - 0.5}" y2="40" stroke="{t["border"]}"/>
{dots}
<text x="{W / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{t["muted"]}">anand@prod: ~ — zsh — 120×{len(TERMINAL) + 1}</text>
<g font-family="{MONO}" font-size="14" style="white-space:pre" xml:space="preserve">{"".join(rows)}</g>
</svg>'''


# ------------------------------------------------------------ architecture --
# (id, x, y, w, h, title, subtitle, colour-key)
NODES = [
    ("client", 20, 214, 132, 58, "client", "React · Next.js", "accent"),
    ("gw", 192, 214, 132, 58, "gateway", "Nginx · JWT", "purple"),
    ("p1", 374, 160, 168, 44, "api-node-7f9c", "Express · Prisma", "green"),
    ("p2", 374, 221, 168, 44, "api-node-b21e", "Express · Prisma", "green"),
    ("p3", 374, 282, 168, 44, "auth-svc-4d0a", "Passport · Firebase", "green"),
    ("kafka", 592, 214, 120, 58, "events", "Kafka", "orange"),
    ("mongo", 752, 160, 108, 48, "MongoDB", "documents", "green"),
    ("mysql", 752, 278, 108, 48, "MySQL", "relational", "accent"),
    ("prom", 388, 392, 140, 44, "Prometheus", "scrape /metrics", "red"),
]
PIPE = ["git push", "GitHub Actions", "jest · cypress · k6", "docker build", "helm upgrade"]

ROUTES = [  # request path: client -> gw -> pod -> kafka -> db
    "M152 243 H192 M324 243 C350 243 350 182 374 182 H542 C566 182 566 243 592 243 M712 243 C732 243 730 184 752 184",
    "M152 243 H192 M324 243 H374 H542 H592 M712 243 C732 243 730 302 752 302",
    "M152 243 H192 M324 243 C350 243 350 304 374 304 H542 C566 304 566 243 592 243 M712 243 C732 243 730 184 752 184",
]


def node(n, t):
    _id, x, y, w, h, title, sub, c = n
    blink = 1.6 + (sum(map(ord, _id)) % 7) / 10
    return (f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>'
            f'<rect x="{x}" y="{y + 8}" width="3" height="{h - 16}" rx="1.5" fill="{t[c]}"/>'
            f'<circle cx="{x + w - 12}" cy="{y + 12}" r="3.5" fill="{t["green"]}">'
            f'<animate attributeName="opacity" values="1;.25;1" dur="{blink:.1f}s" repeatCount="indefinite"/></circle>'
            f'<text x="{x + 14}" y="{y + h / 2 - 3}" font-size="13" font-weight="600" fill="{t["fg"]}">{escape(title)}</text>'
            f'<text x="{x + 14}" y="{y + h / 2 + 13}" font-size="11" fill="{t["muted"]}">{escape(sub)}</text></g>')


def system_svg(t):
    W, H = 880, 470
    parts = []
    # pipeline strip
    px, pw, gap = 20, 152, 20
    pipe_y = 54
    parts.append(f'<text x="20" y="36" font-size="11" letter-spacing="1.5" fill="{t["muted"]}">CI / CD</text>')
    for i, label in enumerate(PIPE):
        x = px + i * (pw + gap)
        a, b = i / len(PIPE), (i + 1) / len(PIPE)
        parts.append(f'<rect x="{x}" y="{pipe_y}" width="{pw}" height="30" rx="15" fill="none" stroke="{t["border"]}" stroke-width="1.5">'
                     f'<animate attributeName="stroke" dur="5s" repeatCount="indefinite" calcMode="discrete" '
                     f'values="{t["border"]};{t["purple"]};{t["border"]}" keyTimes="0;{a:.2f};{b:.2f}"/></rect>'
                     f'<text x="{x + pw / 2}" y="{pipe_y + 19}" text-anchor="middle" font-size="12" fill="{t["fg"]}">{escape(label)}</text>')
        if i:
            parts.append(f'<path d="M{x - gap + 3} {pipe_y + 15} H{x - 4}" stroke="{t["muted"]}" marker-end="url(#arr)"/>')
    last_x = px + (len(PIPE) - 1) * (pw + gap) + pw
    # deploy arrow into cluster
    parts.append(f'<path d="M{last_x - 76} {pipe_y + 30} V120 H520 V140" fill="none" stroke="{t["purple"]}" stroke-dasharray="4 4" marker-end="url(#arr)">'
                 f'<animate attributeName="stroke-dashoffset" from="16" to="0" dur="1s" repeatCount="indefinite"/></path>')
    parts.append(f'<text x="{last_x - 68}" y="114" font-size="11" fill="{t["purple"]}">rollout</text>')
    # cluster boundary
    parts.append(f'<rect x="358" y="140" width="200" height="204" rx="12" fill="none" stroke="{t["accent"]}" stroke-dasharray="6 5" opacity=".7"/>'
                 f'<rect x="372" y="132" width="124" height="16" fill="{t["bg"]}"/>'
                 f'<text x="378" y="144" font-size="11" letter-spacing="1" fill="{t["accent"]}">⎈ k8s ns/anand</text>')
    # static edges
    edge = f'fill="none" stroke="{t["border"]}" stroke-width="1.5"'
    for d in ROUTES:
        parts.append(f'<path d="{d}" {edge}/>')
    # prometheus scrape lines
    parts.append(f'<path d="M458 392 V344" fill="none" stroke="{t["red"]}" stroke-dasharray="3 4" opacity=".8">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="14" dur="1s" repeatCount="indefinite"/></path>')
    parts.append(f'<text x="540" y="412" font-size="11" fill="{t["muted"]}">p99</text>'
                 f'<polyline fill="none" stroke="{t["red"]}" stroke-width="1.5" points="566,416 578,408 590,412 602,398 614,404 626,396 638,401 650,393 662,399 674,390">'
                 f'<animate attributeName="points" dur="4s" repeatCount="indefinite" values="'
                 f'566,416 578,408 590,412 602,398 614,404 626,396 638,401 650,393 662,399 674,390;'
                 f'566,410 578,412 590,402 602,406 614,396 626,402 638,392 650,400 662,391 674,397;'
                 f'566,416 578,408 590,412 602,398 614,404 626,396 638,401 650,393 662,399 674,390"/></polyline>'
                 f'<text x="682" y="400" font-size="11" fill="{t["fg"]}">42ms</text>')
    # request packets
    colours = [t["accent"], t["green"], t["orange"]]
    for i, d in enumerate(ROUTES):
        for k in range(2):
            begin = i * 1.1 + k * 2.2
            parts.append(f'<circle r="4.5" fill="{colours[i]}" opacity="0">'
                         f'<animateMotion dur="3.3s" begin="{begin:.1f}s" repeatCount="indefinite" path="{d}"/>'
                         f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.04;.94;1" dur="3.3s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>')
    # nodes drawn last so packets pass *through* the services
    parts += [node(n, t) for n in NODES]
    # footer
    parts.append(f'<text x="20" y="{H - 16}" font-size="11" fill="{t["muted"]}">'
                 f'every box is something I have built with · uptime: always learning · infra: Docker · Kubernetes · AWS · GCP · Vercel</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Anand's stack drawn as a running system: React client, Nginx gateway, Node pods on Kubernetes, Kafka, MongoDB and MySQL, monitored by Prometheus, deployed by GitHub Actions and Helm">
<title>anand.sys — my stack, running</title>
<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{t["muted"]}"/></marker></defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
<g font-family="{MONO}">{"".join(parts)}</g>
</svg>'''


def main():
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"terminal-{name}.svg").write_text(terminal_svg(t), encoding="utf-8")
        (OUT / f"system-{name}.svg").write_text(system_svg(t), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
