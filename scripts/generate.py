#!/usr/bin/env python3
"""Genera los SVG animados del perfil en assets/.

GitHub sirve los SVG del README como <img>: sin JavaScript ni fuentes web.
Por eso todo se anima con SMIL y el texto monoespaciado se coloca glifo a
glifo (atributo x por carácter), así la maquetación no depende de qué fuente
monoespaciada tenga instalada quien visita el perfil.

Uso:  python3 scripts/generate.py
"""
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

BG = "#070706"
PANEL = "#0d0d0b"
LINE = "#23231f"
CREAM = "#f2f0ea"
MUTED = "#8a887f"
SOFT = "#b5b3aa"
ACID = "#ccff00"

MONO = "'Space Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
DISPLAY = "'Syne','Archivo Black','Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"


def svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
        f"<title>{escape(label)}</title>\n{body}\n</svg>\n"
    )


def mono(segments, x, y, fs, cw, extra=""):
    """Texto monoespaciado con cada glifo en su columna. segments: [(texto, color)]."""
    out, col = [], 0
    for text, fill in segments:
        xs = " ".join(f"{x + (col + i) * cw:.1f}" for i in range(len(text)))
        out.append(f'<tspan x="{xs}" fill="{fill}">{escape(text)}</tspan>')
        col += len(text)
    return (
        f'<text y="{y}" font-family="{MONO}" font-size="{fs}" '
        f'xml:space="preserve" style="white-space:pre" {extra}>{"".join(out)}</text>'
    )


def pulse_dot(cx, cy, r, dur="1.6s", begin="0s"):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ACID}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ACID}" stroke-width="1.5">'
        f'<animate attributeName="r" values="{r};{r * 3}" dur="{dur}" begin="{begin}" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.9;0" dur="{dur}" begin="{begin}" repeatCount="indefinite"/>'
        f"</circle>"
    )


def discrete(attr, frames, total):
    """<animate> discreto a partir de [(segundo, valor)] dentro de un ciclo de `total` s."""
    kt = ";".join(f"{t / total:.4f}" for t, _ in frames)
    vs = ";".join(f"{v:.1f}" if isinstance(v, float) else str(v) for _, v in frames)
    return (
        f'<animate attributeName="{attr}" dur="{total}s" repeatCount="indefinite" '
        f'calcMode="discrete" keyTimes="{kt}" values="{vs}"/>'
    )


# --------------------------------------------------------------------------- header

def header():
    W, H = 1200, 420
    rnd = random.Random(7)
    parts = [
        f'<defs>'
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1.5" cy="1.5" r="1.2" fill="#1f1f1b"/></pattern>'
        f'<radialGradient id="glow" cx="0.72" cy="0.45" r="0.55">'
        f'<stop offset="0" stop-color="{ACID}" stop-opacity="0.13"/>'
        f'<stop offset="1" stop-color="{ACID}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
        f"</defs>",
        f'<g clip-path="url(#frame)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#glow)">'
        f'<animate attributeName="opacity" values="0.6;1;0.6" dur="6s" repeatCount="indefinite"/></rect>',
    ]

    # píxeles ácidos que parpadean, guiño al fondo WebGL del portfolio
    for _ in range(26):
        x = rnd.choice([rnd.randint(20, 590), rnd.randint(600, 1180)])
        y = rnd.randint(16, H - 16)
        s = rnd.choice([4, 5, 6, 8])
        d = rnd.uniform(2.5, 6.0)
        b = rnd.uniform(0, 6.0)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{ACID}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.85;0" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite"/></rect>'
        )

    # --- bloque izquierdo: nombre
    parts.append(mono([("// ", MUTED), ("FULL STACK DEVELOPER", ACID), (" · BARCELONA", MUTED)], 64, 92, 14, 8.6))

    def glitch(text, y, length, filled):
        style = (f'fill="{CREAM}"' if filled else f'fill="none" stroke="{ACID}" stroke-width="2.2"')
        base = (f'font-family="{DISPLAY}" font-size="108" font-weight="800" '
                f'textLength="{length}" lengthAdjust="spacingAndGlyphs"')
        ghost = ACID if filled else CREAM
        return (
            f'<text x="66" y="{y}" {base} fill="{ghost}" opacity="0">{text}'
            f'<animate attributeName="opacity" dur="7s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;0.86;0.87;0.88;0.9;0.91;1" values="0;0.9;0;0.7;0;0;0"/>'
            f'<animate attributeName="x" dur="7s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;0.86;0.88;0.9;1" values="66;72;59;69;66"/></text>'
            f'<text x="62" y="{y}" {base} {style}>{text}'
            f'<animate attributeName="x" dur="7s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;0.86;0.87;0.88;0.9;1" values="62;58;65;60;62;62"/></text>'
        )

    parts.append(glitch("ALEX", 196, 262, True))
    parts.append(glitch("ÁLVAREZ", 304, 486, False))
    parts.append(mono([("Almendros", CREAM), (" · web, móvil y escritorio · +5 años", MUTED)], 64, 348, 14, 8.6))

    # píldora de estado
    pill = "ABIERTO A PROYECTOS"
    pw = 44 + len(pill) * 7.4
    parts.append(f'<rect x="64" y="366" width="{pw:.0f}" height="30" rx="15" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    parts.append(pulse_dot(84, 381, 4))
    parts.append(mono([(pill, CREAM)], 98, 386, 12, 7.4, 'letter-spacing="0"'))

    # --- terminal
    tx, ty, tw, th = 640, 58, 500, 304
    parts.append(
        f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>'
        f'<line x1="{tx}" y1="{ty + 38}" x2="{tx + tw}" y2="{ty + 38}" stroke="{LINE}" stroke-width="1.5"/>'
        f'<circle cx="{tx + 22}" cy="{ty + 19}" r="5.5" fill="{ACID}"/>'
        f'<circle cx="{tx + 40}" cy="{ty + 19}" r="5.5" fill="#34342e"/>'
        f'<circle cx="{tx + 58}" cy="{ty + 19}" r="5.5" fill="#34342e"/>'
    )
    parts.append(mono([("alex@barcelona: ~", MUTED)], tx + tw / 2 - 17 * 7.2 / 2, ty + 24, 12, 7.2))

    fs, cw, lh = 15, 9.0, 28
    x0, y0 = tx + 24, ty + 74
    prompt = [("~ ", ACID), ("$ ", MUTED)]
    script = [
        ("cmd", "whoami"),
        ("out", [("alex álvarez almendros", CREAM), (" — full stack developer", SOFT)]),
        ("cmd", "cat ahora.txt"),
        ("out", [("consultor en ", SOFT), ("Capitole", CREAM), (": .NET, Blazor y React", SOFT)]),
        ("out", [("+ productos propios: SaaS, IA local, Rust", SOFT)]),
        ("cmd", "ls stack/"),
        ("out", [("react/  ts/  node/  dotnet/  rust/  kotlin/", ACID)]),
        ("end", None),
    ]

    type_dt, pause, total = 0.075, 0.55, 16.0
    t = 0.8
    cursor = [(0.0, (x0 + 4 * cw, y0))]
    for i, (kind, content) in enumerate(script):
        y = y0 + i * lh
        cid = f"tl{i}"
        if kind == "out":
            segs, n = content, sum(len(s) for s, _ in content)
            frames = [(0.0, 0.0), (t, n * cw + cw)]
            t += 0.18
            cursor.append((t, (x0 + 4 * cw, y + lh)))
        else:
            cmd = content or ""
            segs = prompt + [(cmd, CREAM)]
            frames = [(0.0, 0.0), (t, 4 * cw)]
            for k in range(1, len(cmd) + 1):
                frames.append((t + pause + k * type_dt, (4 + k) * cw))
                cursor.append((t + pause + k * type_dt, (x0 + (4 + k) * cw, y)))
            t += pause + len(cmd) * type_dt + (0.35 if cmd else 0)
        frames.append((total - 0.4, 0.0))
        parts.append(
            f'<clipPath id="{cid}"><rect x="{x0 - 2}" y="{y - lh + 8}" width="0" height="{lh}">'
            f'{discrete("width", frames, total)}</rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#{cid})">{mono(segs, x0, y, fs, cw)}</g>')

    cursor.append((total - 0.4, (x0 + 4 * cw, y0)))
    cursor.sort(key=lambda c: c[0])
    parts.append(
        f'<rect x="{x0 + 4 * cw}" y="{y0 - 14}" width="{cw}" height="18" fill="{ACID}">'
        + discrete("x", [(tt, p[0]) for tt, p in cursor], total)
        + discrete("y", [(tt, p[1] - 14) for tt, p in cursor], total)
        + '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
        + "</rect>"
    )

    parts.append("</g>")
    parts.append(f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    return svg(W, H, "\n".join(parts), "Alex Álvarez Almendros — Full Stack Developer en Barcelona")


# --------------------------------------------------------------------------- marquee

def marquee():
    W, H = 1200, 54
    items = ["REACT", "TYPESCRIPT", "NODE.JS", ".NET", "BLAZOR", "C#", "RUST", "TAURI", "KOTLIN",
             "JETPACK COMPOSE", "PYTHON", "C++", "ASTRO", "FASTIFY", "TURSO", "STRIPE", "AZURE", "IA LOCAL"]
    text = "".join(f"{it}  ✦  " for it in items)
    cw = 12.6
    L = len(text) * cw
    run = (
        f'<text y="35" font-family="{MONO}" font-size="19" font-weight="700" fill="{BG}" '
        f'textLength="{L:.0f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve" style="white-space:pre"'
    )
    body = (
        f'<defs><clipPath id="m"><rect width="{W}" height="{H}" rx="10"/></clipPath></defs>'
        f'<g clip-path="url(#m)"><rect width="{W}" height="{H}" fill="{ACID}"/>'
        f"<g>{run} x=\"0\">{escape(text)}</text>{run} x=\"{L:.0f}\">{escape(text)}</text>"
        f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{L:.0f} 0" '
        f'dur="{L / 55:.1f}s" repeatCount="indefinite"/></g></g>'
    )
    return svg(W, H, body, "Stack: " + ", ".join(items))


# --------------------------------------------------------------------------- tarjetas

PROJECTS = [
    ("ttylauncher", "01", "TTYLauncher", "KOTLIN", "OPEN SOURCE",
     ["Launcher Android en forma de terminal: sin iconos,", "sin cuadrícula. Escribes «open spotify» y se abre."],
     ["Kotlin", "Compose", "Termux"]),
    ("samplecurator", "02", "SampleCurator", "RUST", "RELEASE",
     ["Triaje de librerías de samples a golpe de tecla:", "escucha y clasifica miles de sonidos sin un clic."],
     ["Tauri 2", "Rust", "React"]),
    ("ganttero", "03", "Ganttero", "TYPESCRIPT", "SELF-HOSTED",
     ["Planificas en el Gantt y el Kanban del día se llena", "solo. Las tareas se crean hablando, con IA local."],
     ["React 19", "Fastify", "Whisper", "Gemma"]),
    ("orchidlights", "04", "OrchidLights", "C++", "OPEN SOURCE",
     ["Iluminación DMX desde el navegador: motor C++", "headless y una UI web para cabina, tablet y móvil."],
     ["C++", "React", "DMX", "QLC+"]),
    ("clicaptcrm", "05", "ClicaptCRM", "JAVASCRIPT", "SAAS",
     ["CRM para freelances y micropymes: pipeline kanban,", "tareas que se recuerdan solas y suscripciones."],
     ["Auth0", "Turso", "Stripe"]),
    ("fincastrimar", "06", "FincasTrimarWeb", "JAVASCRIPT", "EN PRODUCCIÓN",
     ["Portal inmobiliario con buscador SEO, fichas listas", "para compartir y panel para publicar sin manual."],
     ["React", "Express", "Turso"]),
]


def card(slug, num, title, lang, status, desc, tags, idx):
    W, H = 440, 210
    uid = slug
    parts = [
        f'<defs><clipPath id="c-{uid}"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
        f'<linearGradient id="s-{uid}" x1="0" x2="1"><stop offset="0" stop-color="{ACID}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{ACID}"/><stop offset="1" stop-color="{ACID}" stop-opacity="0"/></linearGradient></defs>',
        f'<g clip-path="url(#c-{uid})">',
        f'<rect width="{W}" height="{H}" fill="{PANEL}"/>',
        f'<rect x="0" y="0" width="4" height="{H}" fill="{ACID}"/>',
        # barrido de luz por el borde superior
        f'<rect x="-160" y="0" width="160" height="2" fill="url(#s-{uid})">'
        f'<animate attributeName="x" values="-160;{W};{W}" keyTimes="0;0.45;1" dur="5s" begin="{idx * 0.8:.1f}s" repeatCount="indefinite"/></rect>',
        "</g>",
        f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="14" fill="none" stroke="{LINE}" stroke-width="1.5"/>',
        mono([(num, ACID), (" / " + lang, MUTED)], 26, 36, 12, 7.4),
    ]
    sw = 30 + len(status) * 7.0
    sx = W - 22 - sw
    parts.append(f'<rect x="{sx:.1f}" y="19" width="{sw:.1f}" height="24" rx="12" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    parts.append(pulse_dot(sx + 14, 31, 3.2, begin=f"{idx * 0.3:.1f}s"))
    parts.append(mono([(status, CREAM)], sx + 24, 35.5, 11, 7.0))
    parts.append(
        f'<text x="26" y="84" font-family="{DISPLAY}" font-size="27" font-weight="800" fill="{CREAM}">{escape(title)}</text>'
    )
    for i, line in enumerate(desc):
        parts.append(
            f'<text x="26" y="{116 + i * 21}" font-family="{SANS}" font-size="14" fill="{SOFT}">{escape(line)}</text>'
        )
    x = 26
    for tag in tags:
        w = 18 + len(tag) * 7.0
        parts.append(f'<rect x="{x}" y="168" width="{w:.1f}" height="22" rx="4" fill="#151512" stroke="{LINE}"/>')
        parts.append(mono([(tag, SOFT)], x + 9, 183, 11, 7.0))
        x += w + 8
    parts.append(
        f'<text x="{W - 26}" y="186" text-anchor="end" font-family="{SANS}" font-size="20" fill="{ACID}">↗'
        f'<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" begin="{idx * 0.4:.1f}s" repeatCount="indefinite"/></text>'
    )
    return svg(W, H, "\n".join(parts), f"{title}: {' '.join(desc)}")


# --------------------------------------------------------------------------- footer

def footer():
    W, H = 1200, 150
    rnd = random.Random(42)
    parts = [
        f'<defs><clipPath id="f"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
        f'<linearGradient id="fade" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{ACID}" stop-opacity="0.15"/>'
        f'<stop offset="0.5" stop-color="{ACID}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{ACID}" stop-opacity="0.15"/></linearGradient></defs>',
        f'<g clip-path="url(#f)"><rect width="{W}" height="{H}" fill="{BG}"/>',
    ]
    base, bw, gap = H, 10, 6
    bars = []
    for i in range(int(W / (bw + gap)) + 1):
        hs = [rnd.randint(6, 74) for _ in range(5)]
        hs.append(hs[0])
        dur = rnd.uniform(1.4, 2.6)
        hv = ";".join(map(str, hs))
        yv = ";".join(str(base - h) for h in hs)
        bars.append(
            f'<rect x="{i * (bw + gap)}" y="{base - hs[0]}" width="{bw}" height="{hs[0]}">'
            f'<animate attributeName="height" values="{hv}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{yv}" dur="{dur:.2f}s" repeatCount="indefinite"/></rect>'
        )
    parts.append(f'<g fill="url(#fade)" opacity="0.55">{"".join(bars)}</g>')
    line = "$ exit  — gracias por pasarte"
    parts.append(mono([("$ ", ACID), ("exit", CREAM), ("  — gracias por pasarte", SOFT)],
                      W / 2 - len(line) * 9.6 / 2, 60, 16, 9.6))
    parts.append(mono([("alexalvarez.dev", ACID)], W / 2 - 15 * 7.8 / 2, 88, 13, 7.8))
    parts.append("</g>")
    parts.append(f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    return svg(W, H, "\n".join(parts), "Gracias por pasarte — alexalvarez.dev")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "marquee.svg").write_text(marquee(), encoding="utf-8")
    (OUT / "footer.svg").write_text(footer(), encoding="utf-8")
    for idx, p in enumerate(PROJECTS):
        (OUT / f"card-{p[0]}.svg").write_text(card(*p, idx), encoding="utf-8")
    print("SVG generados en", OUT)


if __name__ == "__main__":
    main()
