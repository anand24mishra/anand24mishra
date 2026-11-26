#!/usr/bin/env python3
"""Generate the CloudForge deploy-path diagram (light + dark) into ../assets.

Run:  python3 scripts/build_svgs.py
The flow mirrors the Architecture section of the CloudForge README.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0d1117", box="#161b22", line="#30363d", fg="#e6edf3",
                 muted="#8b949e", accent="#4493f8"),
    "light": dict(bg="#ffffff", box="#f6f8fa", line="#d0d7de", fg="#1f2328",
                  muted="#59636e", accent="#0969da"),
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

W, BW, BH = 880, 150, 52
# two rows of five steps; (title, detail)
ROW1 = [("Git repo", "any app"), ("cloudforge init", "detect stack"),
        ("GitHub Actions", "build · Trivy scan"), ("GHCR", "multi-arch image"),
        ("deploy-config", "GitOps repo")]
ROW2 = [("Argo CD", "sync"), ("Helm chart", "probes · HPA · rollback"),
        ("k3s / kind", "Terraform on OCI"), ("Traefik", "ingress · TLS"),
        ("app", "running")]
Y1, Y2 = 40, 150
GAP = (W - 40 - 5 * BW) / 4


def box(x, y, title, detail, t, hi=False):
    return (f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="6" fill="{t["box"]}" '
            f'stroke="{t["accent"] if hi else t["line"]}"/>'
            f'<text x="{x + BW / 2}" y="{y + 22}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="13" fill="{t["fg"]}">{escape(title)}</text>'
            f'<text x="{x + BW / 2}" y="{y + 40}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="11" fill="{t["muted"]}">{escape(detail)}</text>')


def svg(t):
    H = 290
    p = []
    xs = [20 + i * (BW + GAP) for i in range(5)]
    for i, (a, b) in enumerate(ROW1):
        p.append(box(xs[i], Y1, a, b, t, hi=(i == 1)))
        if i:
            p.append(f'<path d="M{xs[i - 1] + BW + 4} {Y1 + BH / 2} H{xs[i] - 6}" stroke="{t["muted"]}" marker-end="url(#a)"/>')
    # row 2 runs right-to-left so the flow wraps like a U
    for i, (a, b) in enumerate(ROW2):
        x = xs[4 - i]
        p.append(box(x, Y2, a, b, t))
        if i:
            p.append(f'<path d="M{xs[5 - i] - 4} {Y2 + BH / 2} H{x + BW + 6}" stroke="{t["muted"]}" marker-end="url(#a)"/>')
    p.append(f'<path d="M{xs[4] + BW / 2} {Y1 + BH + 4} V{Y2 - 6}" stroke="{t["muted"]}" marker-end="url(#a)"/>')
    # observability strip
    p.append(f'<line x1="20" y1="236" x2="{W - 20}" y2="236" stroke="{t["line"]}"/>'
             f'<text x="20" y="262" font-family="{FONT}" font-size="12" fill="{t["muted"]}">'
             f'Cluster bootstrap: Prometheus, Grafana, Loki, cert-manager, Sealed Secrets</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="CloudForge deploy path: Git repo, cloudforge init, GitHub Actions, GHCR, '
            f'deploy-config, Argo CD, Helm chart, k3s or kind, Traefik, app">'
            f'<title>CloudForge deploy path</title>'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{t["muted"]}"/></marker></defs>'
            f'<rect width="{W}" height="{H}" rx="8" fill="{t["bg"]}"/>{"".join(p)}</svg>')


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for name, t in THEMES.items():
        (OUT / f"cloudforge-{name}.svg").write_text(svg(t), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
