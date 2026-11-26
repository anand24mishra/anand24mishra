#!/usr/bin/env python3
"""Generate the profile SVGs (light + dark) into ../assets.

Run:  python3 scripts/build_svgs.py
Everything drawn here comes from the projects' own READMEs; edit the
CARDS data below when a project changes, then re-run and commit.
"""
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape as esc

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0d1117", card="#161b22", line="#30363d", fg="#e6edf3", muted="#8b949e",
                 accent="#4493f8", green="#3fb950", orange="#d29922", purple="#ab7df8",
                 chip="#21262d", grid="#161b22"),
    "light": dict(bg="#ffffff", card="#f6f8fa", line="#d0d7de", fg="#1f2328", muted="#59636e",
                  accent="#0969da", green="#1a7f37", orange="#9a6700", purple="#8250df",
                  chip="#eaeef2", grid="#f3f5f7"),
}
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def svg(w, h, title, body, t, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}"><title>{esc(title)}</title>'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
            f'orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{t["muted"]}"/></marker></defs>'
            f'{body}</svg>')


def text(x, y, s, t, size=13, fill="fg", font=SANS, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{t.get(fill, fill)}" {extra}>{esc(s)}</text>')


def chips(x, y, items, t, maxw):
    out, cx = [], x
    for it in items:
        w = len(it) * 6.6 + 16
        if cx + w > x + maxw:
            break
        out.append(f'<rect x="{cx}" y="{y}" width="{w}" height="22" rx="11" fill="{t["chip"]}"/>'
                   + text(cx + w / 2, y + 15, it, t, 11, "muted", MONO, anchor="middle"))
        cx += w + 6
    return "".join(out)


# ------------------------------------------------------------------ banner --
def banner(t):
    W, H = 880, 210
    b = [f'<rect width="{W}" height="{H}" rx="12" fill="{t["bg"]}" stroke="{t["line"]}"/>']
    # dotted grid on the right half
    for gx in range(520, W - 10, 18):
        for gy in range(16, H - 10, 18):
            b.append(f'<circle cx="{gx}" cy="{gy}" r="1.2" fill="{t["line"]}"/>')
    # CloudForge's U-shaped deploy path, abstracted, with a request travelling it
    path = "M560 70 H820 V140 H560"
    b.append(f'<path d="{path}" fill="none" stroke="{t["accent"]}" stroke-width="2" opacity=".55"/>')
    labels = [(560, 70, "repo"), (690, 70, "CI"), (820, 70, "GHCR"),
              (820, 140, "Argo CD"), (690, 140, "k3s"), (560, 140, "app")]
    for x, y, s in labels:
        b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        b.append(text(x, y - 13 if y == 70 else y + 24, s, t, 11, "muted", MONO, anchor="middle"))
    b.append(f'<circle r="4.5" fill="{t["green"]}"><animateMotion dur="4s" repeatCount="indefinite" path="{path}"/></circle>')
    # identity
    b.append(text(40, 82, "Anand Mishra", t, 40, "fg", SANS, 700))
    b.append(text(42, 116, "Backend & infrastructure engineer", t, 17, "fg"))
    b.append(text(42, 142, "APIs, CI/CD pipelines, Kubernetes", t, 14, "muted"))
    b.append(text(42, 176, "B.Tech AI/ML · Newton School of Technology · Sonipat, IN", t, 12, "muted", MONO))
    return svg(W, H, "Anand Mishra", "".join(b), t,
               "Anand Mishra, backend and infrastructure engineer. B.Tech AI/ML, Newton School of Technology.")


# ------------------------------------------------------------------- cards --
CW, CH = 430, 250


def card_frame(name, tagline, stack, t, visual):
    b = [f'<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>',
         text(22, 36, name, t, 17, "fg", MONO, 700),
         text(CW - 22, 36, "↗", t, 16, "muted", anchor="end")]
    for i, ln in enumerate(wrap(tagline, 58)[:2]):
        b.append(text(22, 62 + i * 19, ln, t, 13, "muted"))
    b.append(visual)
    b.append(chips(22, CH - 40, stack, t, CW - 44))
    return "".join(b)


def v_cloudforge(t):
    steps = ["repo", "detect", "build", "GHCR", "Argo CD", "k3s"]
    x0, y, gap = 22, 122, 66
    out = []
    for i, s in enumerate(steps):
        x = x0 + i * gap
        out.append(f'<rect x="{x}" y="{y}" width="58" height="30" rx="6" fill="{t["bg"]}" stroke="{t["line"]}"/>'
                   + text(x + 29, y + 19, s, t, 10.5, "fg", MONO, anchor="middle"))
        if i:
            out.append(f'<path d="M{x - 7} {y + 15} H{x - 2}" stroke="{t["muted"]}" marker-end="url(#a)"/>')
    out.append(f'<rect x="{x0}" y="{y}" width="58" height="30" rx="6" fill="none" stroke="{t["green"]}" stroke-width="1.5">'
               f'<animate attributeName="x" values="' + ";".join(str(x0 + i * gap) for i in range(6)) +
               f'" dur="4.8s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    out.append(text(22, 180, "$ cloudforge deploy examples/node-app", t, 11.5, "accent", MONO))
    return "".join(out)


def v_drk(t):
    parts = [("engagement", 40, "accent"), ("referral", 30, "purple"), ("quality", 30, "green")]
    x, y, w = 22, 120, CW - 44
    out = [text(22, 112, "entry score", t, 11, "muted", MONO)]
    for lbl, pct, c in parts:
        seg = w * pct / 100
        out.append(f'<rect x="{x}" y="{y}" width="{seg - 3}" height="12" rx="3" fill="{t[c]}"/>')
        out.append(text(x, y + 30, f"{pct}% {lbl}", t, 11, "fg", MONO))
        x += seg
    out.append(text(22, 182, "escrow → YouTube-verified views → results-day payout", t, 11, "muted", MONO))
    return "".join(out)


def v_finsaathi(t):
    out = []
    x = 22
    for s in ["NIFTY 50", "SENSEX", "BANK NIFTY"]:
        w = len(s) * 7.4 + 22
        out.append(f'<rect x="{x}" y="110" width="{w}" height="28" rx="6" fill="{t["bg"]}" stroke="{t["line"]}"/>'
                   f'<circle cx="{x + 11}" cy="124" r="3" fill="{t["green"]}">'
                   f'<animate attributeName="opacity" values="1;.3;1" dur="2s" repeatCount="indefinite"/></circle>'
                   + text(x + 19, 128, s, t, 11.5, "fg", MONO))
        x += w + 8
    out.append(f'<rect x="22" y="150" width="112" height="26" rx="13" fill="none" stroke="{t["line"]}"/>'
               f'<rect x="24" y="152" width="54" height="22" rx="11" fill="{t["accent"]}"/>'
               + text(51, 167, "हिंदी", t, 11.5, "#ffffff", SANS, 600, "middle")
               + text(106, 167, "EN", t, 11.5, "muted", MONO, anchor="middle")
               + text(146, 167, "live quotes · Telegram alerts", t, 11, "muted", MONO))
    return "".join(out)


def v_devdeck(t):
    out = []
    rows = [("web-app", ":5173  :3001", "2 processes"), ("api", ":8080", "3 containers")]
    y = 106
    for proj, ports, what in rows:
        out.append(f'<rect x="22" y="{y}" width="{CW - 44}" height="30" rx="6" fill="{t["bg"]}" stroke="{t["line"]}"/>'
                   f'<circle cx="36" cy="{y + 15}" r="4" fill="{t["green"]}"/>'
                   + text(48, y + 19, proj, t, 11.5, "fg", MONO, 600)
                   + text(140, y + 19, ports, t, 11.5, "accent", MONO)
                   + text(250, y + 19, what, t, 11, "muted", MONO)
                   + f'<rect x="{CW - 84}" y="{y + 6}" width="54" height="18" rx="4" fill="none" stroke="{t["orange"]}"/>'
                   + text(CW - 57, y + 19, "stop", t, 10.5, "orange", MONO, anchor="middle"))
        y += 38
    out.append(text(22, 192, "illustrative · never sudo, only your own dev processes", t, 10.5, "muted", MONO))
    return "".join(out)


CARDS = {
    "cloudforge": ("CloudForge",
                   "A small PaaS in Go: turns a Git repository into a Kubernetes deployment via Helm and Argo CD.",
                   ["Go", "Kubernetes", "Helm", "Argo CD", "Terraform"], v_cloudforge),
    "drk": ("DRK/MTTR",
            "Contest marketplace for YouTube creators. Brands fund prize pools held in escrow.",
            ["React", "Express", "Prisma", "MongoDB", "Razorpay"], v_drk),
    "finsaathi": ("FinSaathi",
                  "Hindi and English app for Indian retail investors: markets, research, portfolio.",
                  ["Fastify", "TypeScript", "Expo", "MongoDB"], v_finsaathi),
    "devdeck": ("DevDeck",
                "macOS app that groups dev processes, ports and Docker containers by project.",
                ["Electron", "React", "TypeScript", "dockerode"], v_devdeck),
}

# TermPlayer's interface, redrawn from the screenshot in its README
def termplayer(t):
    W, H = 880, 270
    b = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>',
         text(22, 36, "TermPlayer", t, 17, "fg", MONO, 700),
         text(W - 22, 36, "↗", t, 16, "muted", anchor="end"),
         text(22, 62, "Keyboard-driven music player for the terminal: Hindi radio, DJ tools, colours that follow the time of day.", t, 13, "muted"),
         f'<rect x="22" y="78" width="{W - 44}" height="142" rx="6" fill="{t["bg"]}" stroke="{t["line"]}"/>',
         text(36, 98, "◉ TERMPLAYER", t, 11.5, "accent", MONO, 700, extra='letter-spacing="2"'),
         text(160, 98, "▶ PLAYING", t, 11.5, "green", MONO),
         text(W - 36, 98, "☾ Night · 23:41", t, 11.5, "purple", MONO, anchor="end")]
    # library pane
    lx, ly, lw, lh = 36, 108, 300, 100
    b.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="5" fill="none" stroke="{t["line"]}"/>')
    b.append(text(lx + 10, ly + 4, " LIBRARY · 3/14 ", t, 10.5, "muted", MONO, extra=f'style="paint-order:stroke" stroke="{t["bg"]}" stroke-width="6"'))
    lib = [("Midnight City", "M83"), ("Strobe", "deadmau5"), ("Breathe", "Telepopmusik"), ("Kids", "MGMT")]
    for i, (song, artist) in enumerate(lib):
        y = ly + 26 + i * 20
        if i == 2:
            b.append(f'<rect x="{lx + 6}" y="{y - 14}" width="{lw - 12}" height="19" rx="3" fill="{t["chip"]}"/>')
            b.append(text(lx + 14, y, "▸", t, 12, "accent", MONO))
        b.append(text(lx + 30, y, song, t, 12, "fg", MONO))
        b.append(text(lx + lw - 12, y, artist, t, 12, "muted", MONO, anchor="end"))
    # now playing pane
    nx, nw = 350, W - 36 - 350
    b.append(f'<rect x="{nx}" y="{ly}" width="{nw}" height="{lh}" rx="5" fill="none" stroke="{t["line"]}"/>')
    b.append(text(nx + 10, ly + 4, " NOW PLAYING ", t, 10.5, "muted", MONO, extra=f'style="paint-order:stroke" stroke="{t["bg"]}" stroke-width="6"'))
    b.append(text(nx + 14, ly + 28, "♫ Strobe", t, 13, "fg", MONO, 700))
    b.append(text(nx + 14, ly + 46, "deadmau5 · For Lack of a Better Name", t, 11.5, "muted", MONO))
    # equaliser
    for i in range(24):
        h0 = 4 + (i * 7) % 15
        h1 = 4 + (i * 11 + 5) % 15
        x = nx + nw - 14 - (24 - i) * 7
        d = 0.7 + (i % 5) * 0.15
        b.append(f'<rect x="{x}" y="{ly + 50 - h0}" width="5" height="{h0}" fill="{t["green"]}" opacity=".85">'
                 f'<animate attributeName="height" values="{h0};{h1};{h0}" dur="{d:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{ly + 50 - h0};{ly + 50 - h1};{ly + 50 - h0}" dur="{d:.2f}s" repeatCount="indefinite"/></rect>')
    # progress bar
    py = ly + 76
    bx0, bx1 = nx + 52, nx + nw - 52
    b.append(text(nx + 14, py + 4, "2:14", t, 11, "muted", MONO))
    b.append(text(nx + nw - 14, py + 4, "4:03", t, 11, "muted", MONO, anchor="end"))
    b.append(f'<line x1="{bx0}" y1="{py}" x2="{bx1}" y2="{py}" stroke="{t["line"]}" stroke-width="3" stroke-linecap="round"/>')
    pos = bx0 + (bx1 - bx0) * 0.55
    b.append(f'<line x1="{bx0}" y1="{py}" x2="{pos}" y2="{py}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round">'
             f'<animate attributeName="x2" from="{pos}" to="{bx1}" dur="60s" repeatCount="indefinite"/></line>')
    b.append(text(22, 248, "$ npx @anand24/termplayer", t, 12.5, "accent", MONO))
    b.append(chips(W - 22 - 150, 232, ["Node.js", "VLC"], t, 160))
    return svg(W, H, "TermPlayer", "".join(b), t, "TermPlayer, a terminal music player. Run: npx @anand24/termplayer")


# ------------------------------------------------------ cloudforge diagram --
def cloudforge_flow(t):
    W, H, BW, BH = 880, 300, 150, 54
    row1 = [("Git repo", "any app"), ("cloudforge init", "detect stack"), ("GitHub Actions", "build · Trivy scan"),
            ("GHCR", "multi-arch image"), ("deploy-config", "GitOps repo")]
    row2 = [("Argo CD", "sync"), ("Helm chart", "probes · HPA · rollback"), ("k3s / kind", "Terraform on OCI"),
            ("Traefik", "ingress · TLS"), ("app", "live")]
    Y1, Y2 = 34, 150
    gap = (W - 40 - 5 * BW) / 4
    xs = [20 + i * (BW + gap) for i in range(5)]
    b = [f'<rect width="{W}" height="{H}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>']

    def box(x, y, a, d, hi=None):
        return (f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="8" fill="{t["card"]}" stroke="{t[hi] if hi else t["line"]}"/>'
                + text(x + BW / 2, y + 23, a, t, 13, "fg", MONO, anchor="middle")
                + text(x + BW / 2, y + 41, d, t, 11, "muted", anchor="middle"))
    for i, (a, d) in enumerate(row1):
        b.append(box(xs[i], Y1, a, d, "accent" if i == 1 else None))
    for i, (a, d) in enumerate(row2):
        b.append(box(xs[4 - i], Y2, a, d, "green" if i == 4 else None))
    path = (f"M{xs[0] + BW / 2} {Y1 + BH / 2} H{xs[4] + BW / 2} V{Y2 + BH / 2} H{xs[0] + BW / 2}")
    b.insert(1, f'<path d="{path}" fill="none" stroke="{t["line"]}" stroke-width="2"/>')
    b.append(f'<circle r="5" fill="{t["green"]}"><animateMotion dur="6s" repeatCount="indefinite" path="{path}"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.03;.95;1" dur="6s" repeatCount="indefinite"/></circle>')
    # move the travelling dot under the boxes by re-drawing boxes on top
    b.append("".join(box(xs[i], Y1, a, d, "accent" if i == 1 else None) for i, (a, d) in enumerate(row1)))
    b.append("".join(box(xs[4 - i], Y2, a, d, "green" if i == 4 else None) for i, (a, d) in enumerate(row2)))
    b.append(f'<line x1="20" y1="236" x2="{W - 20}" y2="236" stroke="{t["line"]}"/>')
    b.append(text(20, 264, "cluster bootstrap", t, 11, "muted", MONO))
    b.append(chips(150, 249, ["Prometheus", "Grafana", "Loki", "cert-manager", "Sealed Secrets"], t, 700))
    return svg(W, H, "CloudForge deploy path", "".join(b), t,
               "CloudForge deploy path: Git repo, cloudforge init, GitHub Actions, GHCR, deploy-config, Argo CD, Helm chart, k3s or kind, Traefik, app")


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for th, t in THEMES.items():
        (OUT / f"banner-{th}.svg").write_text(banner(t), encoding="utf-8")
        (OUT / f"cloudforge-{th}.svg").write_text(cloudforge_flow(t), encoding="utf-8")
        (OUT / f"termplayer-{th}.svg").write_text(termplayer(t), encoding="utf-8")
        for key, (name, tag, stack, vis) in CARDS.items():
            body = card_frame(name, tag, stack, t, vis(t))
            (OUT / f"card-{key}-{th}.svg").write_text(svg(CW, CH, name, body, t, f"{name}: {tag}"), encoding="utf-8")
    print("wrote", len(list(OUT.glob("*.svg"))), "svgs")


if __name__ == "__main__":
    main()
