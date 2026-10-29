"""Generador de carruseles y Reels DVITAS · versión 2 (diseño dinámico).

Uso:
  python3 tools/render.py posts/AAAA-MM-DD_tema/spec.json

Ficha (spec.json):
  {"fondo": "azul" | "crema", "eje": "PSICOLOGÍA INFANTIL", "tema": "MIEDOS", "reel": false,
   "slides": [...]}

Palabra destacada en títulos: rodéala con asteriscos, p. ej. "¿Tu hijo duerme *lo suficiente?*".
  - Crema: el texto destacado sale en teal.  - Azul: sale en blanco sobre un trazo naranja tipo rotulador.

Tipos de slide:
  portada   {"titulo", "subtitulo"}
  lista     {"titulo", "items": [..3-5], "aviso": true|false}
  pasos     {"titulo", "pasos": [["Título", "explicación"], ..2-4]}
  tarjetas  {"titulo", "tarjetas": [["Título", "texto"], ..2-4], "nota": "opcional"}
  mito      {"titulo", "mito": "...", "realidad": "..."}
  datos     {"titulo", "filas": [["Etapa", 0.6, "rango"], ..], "nota": "..."}
  cta       {"titulo"}
  cierre    {"titulo", "texto"}

Salida: slide_1.jpg … (1080x1350) y, si reel=true, reel.mp4 (1080x1920, sin audio, con zoom suave y fundidos).
"""
import json, os, re, subprocess, sys, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
LOGO_WHITE = os.path.join(ROOT, "assets", "logo_blanco_para_fondo_azul.png")
LOGO_TEAL = os.path.join(ROOT, "assets", "logo_teal_para_fondo_crema.png")

AZUL = (0x1B, 0xA3, 0xA8)
TEAL = (0x03, 0x98, 0x9E)
NARANJA = (0xF7, 0x74, 0x2B)
GRIS = (0x86, 0x87, 0x87)
CREMA = (0xF3, 0xF8, 0xF7)
BLANCO = (255, 255, 255)
TINTA = (0x12, 0x39, 0x3B)      # titulares sobre crema
CUERPO = (0x2E, 0x3A, 0x3B)     # texto sobre crema/tarjetas blancas
W, H, M = 1080, 1350, 90
AVISO = "Una señal suelta no es un diagnóstico. Si varias se repiten, consulta con un profesional."


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Theme:
    def __init__(self, fondo):
        self.azul = fondo == "azul"
        self.bg = AZUL if self.azul else CREMA
        self.title = BLANCO if self.azul else TINTA
        self.accent = BLANCO if self.azul else TEAL
        self.body = BLANCO if self.azul else CUERPO
        self.muted = (225, 245, 245) if self.azul else GRIS
        self.logo = LOGO_WHITE if self.azul else LOGO_TEAL


# ---------- decoración ----------
def sparkle(d, cx, cy, r, fill):
    k = r * 0.28
    pts = [(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k),
           (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)]
    d.polygon(pts, fill=fill)


def decor(im, th, i, portada=False):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    big = 300 + (i % 3) * 40
    if th.azul:
        d.ellipse([W - big + 60, -big + 120, W + big + 60, big + 120], fill=(255, 255, 255, 34))
        d.ellipse([-220, H - 260, 220, H + 180], fill=TEAL + (150,))
    else:
        d.ellipse([W - big + 60, -big + 120, W + big + 60, big + 120], fill=TEAL + (30,))
        d.ellipse([-220, H - 260, 220, H + 180], fill=NARANJA + (36,))
    if portada:
        # anillo y destellos, estilo "ilustración" de portada
        ring = BLANCO + (120,) if th.azul else TEAL + (90,)
        d.ellipse([700, 120, 960, 380], outline=ring, width=10)
        sparkle(d, 930, 140, 38, NARANJA + (255,))
        sparkle(d, 985, 255, 22, NARANJA + (255,))
        sparkle(d, 690, 395, 18, NARANJA + (255,))
    im.alpha_composite(ov)


def pill(d, eje, tema):
    fe, ft = font("Poppins-Medium.ttf", 22), font("Poppins-Bold.ttf", 30)
    pad = 28
    tw = max(d.textlength(eje, font=fe), d.textlength(tema, font=ft))
    pw, ph = int(tw + pad * 2), 100
    d.rounded_rectangle([M, M, M + pw, M + ph], radius=50, fill=NARANJA)
    d.text((M + pad, M + 14), eje, font=fe, fill=BLANCO)
    mix = tuple(int(NARANJA[k] * 0.3 + 255 * 0.7) for k in range(3))  # blanco al 70 %
    d.text((M + pad, M + 46), tema, font=ft, fill=mix)


def footer(d, th, i, n):
    y = H - 78
    fb, fs = font("Poppins-Bold.ttf", 26), font("Poppins-Regular.ttf", 24)
    d.text((M, y), "DVITAS", font=fb, fill=th.accent)
    mid = "Psicología y Logopedia · Málaga"
    d.text(((W - d.textlength(mid, font=fs)) / 2, y + 2), mid, font=fs, fill=th.muted)
    num = f"{i}/{n}"
    d.text((W - M - d.textlength(num, font=fb), y), num, font=fb, fill=th.accent)


def swipe(d, th):
    f = font("Poppins-Bold.ttf", 24)
    txt = "DESLIZA"
    tw = d.textlength(txt, font=f)
    x, y = M, H - M - 56
    fill = BLANCO if th.azul else TEAL
    col = AZUL if th.azul else BLANCO
    d.rounded_rectangle([x, y, x + tw + 110, y + 56], radius=28, fill=fill)
    d.text((x + 28, y + 12), txt, font=f, fill=col)
    ax = x + tw + 44
    d.line([ax, y + 28, ax + 40, y + 28], fill=col, width=5)
    d.polygon([(ax + 46, y + 28), (ax + 32, y + 17), (ax + 32, y + 39)], fill=col)


def logo(im, th, pos):
    lg = Image.open(th.logo).convert("RGBA")
    lw = 200 if pos == "esquina" else 300
    lh = int(lg.height * lw / lg.width)
    lg = lg.resize((lw, lh), Image.LANCZOS)
    xy = (W - M - lw, H - M - lh) if pos == "esquina" else ((W - lw) // 2, H - M - lh)
    im.alpha_composite(lg, xy)


# ---------- texto ----------
def rich_title(d, th, text, y, size=84, maxlines=3):
    f = font("Poppins-Bold.ttf", size)
    parts = text.split("*")
    words = []
    for k, part in enumerate(parts):
        for w in part.split():
            words.append((w, k % 2 == 1))
    space = d.textlength(" ", font=f)
    lines, cur, curw = [], [], 0
    for w, hl in words:
        ww = d.textlength(w, font=f)
        add = ww if not cur else ww + space
        if cur and curw + add > W - 2 * M:
            lines.append(cur)
            cur, curw = [(w, hl)], ww
        else:
            cur.append((w, hl))
            curw += add
    if cur:
        lines.append(cur)
    lh = int(size * 1.16)
    for line in lines[:maxlines]:
        pos, x = [], M
        for w, hl in line:
            ww = d.textlength(w, font=f)
            pos.append((x, ww, w, hl))
            x += ww + space
        if th.azul:
            k = 0
            while k < len(pos):
                if pos[k][3]:
                    j = k
                    while j + 1 < len(pos) and pos[j + 1][3]:
                        j += 1
                    x0, x1 = pos[k][0], pos[j][0] + pos[j][1]
                    d.rounded_rectangle([x0 - 10, y + int(size * 0.58), x1 + 10, y + int(size * 1.06)],
                                        radius=12, fill=NARANJA)
                    k = j + 1
                else:
                    k += 1
        for x, ww, w, hl in pos:
            d.text((x, y), w, font=f, fill=(th.accent if hl else th.title))
        y += lh
    return y


def paragraph(d, color, text, y, size=36, maxw=None, italic=False, x=M):
    f = font("Poppins-Italic.ttf" if italic else "Poppins-Regular.ttf", size)
    for ln in wrap(d, text, f, maxw or W - 2 * M):
        d.text((x, y), ln, font=f, fill=color)
        y += int(size * 1.38)
    return y


def rich_lines(d, text, fr, fb, maxw):
    """Texto con **negritas**: devuelve líneas de (palabra, negrita)."""
    words = []
    for k, part in enumerate(text.split("**")):
        for j, w in enumerate(part.split()):
            glue = j == 0 and words and part[:1] in ".,;:!?)»”…"
            words.append((w, k % 2 == 1, bool(glue)))
    sp = d.textlength(" ", font=fr)
    lines, cur, cw = [], [], 0
    for w, b, g in words:
        ww = d.textlength(w, font=fb if b else fr)
        add = ww if (not cur or g) else ww + sp
        if cur and not g and cw + add > maxw:
            lines.append(cur)
            cur, cw = [(w, b, g)], ww
        else:
            cur.append((w, b, g))
            cw += add
    if cur:
        lines.append(cur)
    return lines


def draw_rich(d, line, x, y, fr, fb, color, bold_color):
    sp = d.textlength(" ", font=fr)
    for k, (w, b, g) in enumerate(line):
        if g and k:
            x -= sp
        f = fb if b else fr
        d.text((x, y), w, font=f, fill=bold_color if b else color)
        x += d.textlength(w, font=f) + sp


def card(d, th, box, solid=False):
    if th.azul and not solid:
        d.rounded_rectangle(box, radius=28, fill=(0x3F, 0xB5, 0xB9))
    else:
        d.rounded_rectangle(box, radius=28, fill=BLANCO)


def aviso(d, th, y):
    f = font("Poppins-Italic.ttf", 28)
    for ln in wrap(d, AVISO, f, W - 2 * M):
        d.text((M, y), ln, font=f, fill=th.muted)
        y += 40
    return y


# ---------- render ----------
def render(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    out = os.path.dirname(os.path.abspath(spec_path))
    th = Theme(spec.get("fondo", "azul"))
    eje, tema = spec["eje"].upper(), spec["tema"].upper()
    slides = spec["slides"]
    n = len(slides)
    files = []
    for i, s in enumerate(slides, 1):
        t = s["tipo"]
        first, last = i == 1, i == n
        im = Image.new("RGBA", (W, H), th.bg + (255,))
        decor(im, th, i, portada=(t == "portada"))
        d = ImageDraw.Draw(im)
        pill(d, eje, tema)
        top = 300
        if t == "portada":
            y = rich_title(d, th, s["titulo"], 470, 104)
            if s.get("subtitulo"):
                paragraph(d, th.body, s["subtitulo"], y + 34, 38, maxw=W - 2 * M - 40)
            swipe(d, th)
        elif t == "lista":
            y = rich_title(d, th, s["titulo"], top, 76) + 40
            fr, fbb = font("Poppins-Regular.ttf", 33), font("Poppins-Bold.ttf", 33)
            items = s["items"][:6]
            gap = 18 if len(items) <= 4 else 12
            for k, it in enumerate(items, 1):
                lines = rich_lines(d, it, fr, fbb, W - 2 * M - 120)
                hgt = 40 + len(lines) * 44
                card(d, th, [M, y, W - M, y + hgt])
                cy = y + hgt // 2
                if s.get("numerada"):
                    d.ellipse([M + 26, cy - 22, M + 70, cy + 22], fill=NARANJA)
                    fn = font("Poppins-Bold.ttf", 24)
                    d.text((M + 48 - d.textlength(str(k), font=fn) / 2, cy - 17), str(k), font=fn, fill=BLANCO)
                else:
                    d.rounded_rectangle([M + 32, cy - 14, M + 60, cy + 14], radius=8, fill=NARANJA)
                yy = y + 20
                for ln in lines:
                    draw_rich(d, ln, M + 96, yy, fr, fbb, BLANCO if th.azul else CUERPO, BLANCO if th.azul else TEAL)
                    yy += 44
                y += hgt + gap
            if s.get("aviso"):
                aviso(d, th, y + 14)
        elif t == "pasos":
            y = rich_title(d, th, s["titulo"], top, 76) + 40
            ft, fs = font("Poppins-Bold.ttf", 36), font("Poppins-Regular.ttf", 30)
            for k, (pt, ps) in enumerate(s["pasos"][:4], 1):
                lines = wrap(d, ps, fs, W - 2 * M - 160)
                hgt = max(130, 74 + len(lines) * 40)
                card(d, th, [M, y, W - M, y + hgt], solid=True)
                d.ellipse([M + 28, y + 28, M + 104, y + 104], fill=TEAL)
                d.text((M + 66 - d.textlength(str(k), font=ft) / 2, y + 40), str(k), font=ft, fill=BLANCO)
                d.text((M + 130, y + 24), pt, font=ft, fill=TEAL)
                yy = y + 74
                for ln in lines:
                    d.text((M + 130, yy), ln, font=fs, fill=CUERPO)
                    yy += 40
                y += hgt + 18
        elif t == "tarjetas":
            y = rich_title(d, th, s["titulo"], top, 76) + 40
            items = s["tarjetas"][:4]
            cw = (W - 2 * M - 26) // 2
            ft, fs = font("Poppins-Bold.ttf", 34), font("Poppins-Regular.ttf", 28)
            rows = [items[r:r + 2] for r in range(0, len(items), 2)]
            for row in rows:
                hs = []
                for ct, cx in row:
                    hs.append(20 + len(wrap(d, ct, ft, cw - 56)) * 44 + 12 + len(wrap(d, cx, fs, cw - 56)) * 38 + 30)
                hgt = max(hs)
                for c, (ct, cx) in enumerate(row):
                    x0 = M + c * (cw + 26)
                    card(d, th, [x0, y, x0 + cw, y + hgt], solid=True)
                    col = TEAL if (rows.index(row) + c) % 2 == 0 else NARANJA
                    d.rounded_rectangle([x0 + 28, y + 28, x0 + 70, y + 36], radius=4, fill=col)
                    yy = y + 50
                    for ln in wrap(d, ct, ft, cw - 56):
                        d.text((x0 + 28, yy), ln, font=ft, fill=col)
                        yy += 44
                    yy += 8
                    for ln in wrap(d, cx, fs, cw - 56):
                        d.text((x0 + 28, yy), ln, font=fs, fill=CUERPO)
                        yy += 38
                y += hgt + 24
            if s.get("nota"):
                paragraph(d, th.body, s["nota"], y + 10, 32)
        elif t == "mito":
            y = rich_title(d, th, s.get("titulo", "¿Mito o realidad?"), top, 76) + 40
            ftag = font("Poppins-Bold.ttf", 26)
            for tag, txt, col in (("MITO", s["mito"], NARANJA), ("REALIDAD", s["realidad"], TEAL)):
                if tag == "MITO":
                    fr = fbb = font("Poppins-Bold.ttf", 36)
                    txt = "«" + txt.strip("«»\"") + "»"
                else:
                    fr, fbb = font("Poppins-Regular.ttf", 32), font("Poppins-Bold.ttf", 32)
                lh = 50 if tag == "MITO" else 44
                lines = rich_lines(d, txt, fr, fbb, W - 2 * M - 90)
                hgt = 96 + len(lines) * lh
                card(d, th, [M, y, W - M, y + hgt], solid=True)
                d.rounded_rectangle([M, y, M + 12, y + hgt], radius=6, fill=col)
                d.text((M + 44, y + 28), tag, font=ftag, fill=col)
                yy = y + 78
                for ln in lines:
                    draw_rich(d, ln, M + 44, yy, fr, fbb, TINTA if tag == "MITO" else CUERPO, TINTA)
                    yy += lh
                y += hgt + 26
        elif t == "cita":
            fq = font("Poppins-Bold.ttf", 220)
            d.text((M - 10, 330), "«", font=fq, fill=NARANJA)
            y = rich_title(d, th, s["cita"].strip("«»\"“” "), 590, 88, maxlines=4)
            if s.get("autor"):
                paragraph(d, th.muted, s["autor"], y + 24, 30)
        elif t == "datos":
            y = rich_title(d, th, s["titulo"], top, 76) + 40
            filas = s["filas"][:6]
            hgt = 50 + len(filas) * 112
            card(d, th, [M, y, W - M, y + hgt], solid=True)
            fl, fv = font("Poppins-Medium.ttf", 32), font("Poppins-Bold.ttf", 32)
            yy = y + 36
            for etapa, frac, etiqueta in filas:
                d.text((M + 34, yy), etapa, font=fl, fill=CUERPO)
                d.text((W - M - 34 - d.textlength(etiqueta, font=fv), yy), etiqueta, font=fv, fill=TEAL)
                yy += 50
                d.rounded_rectangle([M + 34, yy, W - M - 34, yy + 20], radius=10, fill=(0xDD, 0xE3, 0xE3))
                d.rounded_rectangle([M + 34, yy, M + 34 + int((W - 2 * M - 68) * max(0.05, min(1, frac))), yy + 20],
                                    radius=10, fill=TEAL)
                yy += 62
            if s.get("nota"):
                paragraph(d, th.muted, s["nota"], y + hgt + 24, 26, italic=True)
        elif t == "cta":
            y = rich_title(d, th, s.get("titulo", "Guárdalo y *envíaselo* a quien lo necesite"), top, 80) + 40
            fb = font("Poppins-Bold.ttf", 38)
            btn = "Reserva tu cita en la bio"
            d.rounded_rectangle([M, y, M + d.textlength(btn, font=fb) + 90, y + 92], radius=46, fill=NARANJA)
            d.text((M + 45, y + 20), btn, font=fb, fill=BLANCO)
            y += 130
            card(d, th, [M, y, W - M, y + 170], solid=True)
            d.text((M + 34, y + 30), "WhatsApp 744 646 732", font=font("Poppins-Bold.ttf", 38), fill=TEAL)
            d.text((M + 34, y + 94), "Doctoralia · C/ Alhucemas 9, Málaga", font=font("Poppins-Regular.ttf", 32), fill=CUERPO)
        elif t == "cierre":
            y = rich_title(d, th, s["titulo"], top, 80)
            if s.get("texto"):
                y = paragraph(d, th.body, s["texto"], y + 24)
            fb = font("Poppins-Bold.ttf", 38)
            btn = "Reserva tu cita en la bio"
            d.rounded_rectangle([M, y + 40, M + d.textlength(btn, font=fb) + 90, y + 132], radius=46, fill=NARANJA)
            d.text((M + 45, y + 60), btn, font=fb, fill=BLANCO)
            aviso(d, th, y + 170)
        else:
            raise SystemExit(f"tipo de slide desconocido: {t}")
        if first:
            logo(im, th, "esquina")
        elif last:
            logo(im, th, "centro")
        else:
            footer(d, th, i, n)
        p = os.path.join(out, f"slide_{i}.jpg")
        im.convert("RGB").save(p, "JPEG", quality=92, optimize=True)
        files.append(p)
    print("slides:", len(files))
    if spec.get("reel"):
        make_reel(files, th, out)


def ffmpeg_bin():
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "imageio-ffmpeg"], check=True)
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def make_reel(files, th, out, dur=5.0, fade=0.5, fps=30):
    """Reel 1080x1920: cada slide con zoom suave (Ken Burns) y fundido entre escenas. Sin audio."""
    ff = ffmpeg_bin()
    frames = []
    for k, f in enumerate(files, 1):
        c = Image.new("RGB", (1080, 1920), th.bg)
        c.paste(Image.open(f), (0, (1920 - H) // 2))
        p = os.path.join(out, f"_reel_{k}.png")
        c.save(p)
        frames.append(p)
    n = len(frames)
    nf = int(dur * fps)
    args = [ff, "-y", "-loglevel", "error"]
    for p in frames:
        # -framerate igual a fps: cada imagen da exactamente dur*fps fotogramas (sin esto el
        # vídeo se queda en ~4 s porque zoompan recibe 25 fps y los fundidos se salen de rango)
        args += ["-loop", "1", "-framerate", str(fps), "-t", str(dur), "-i", p]
    parts = []
    for k in range(n):
        zin = k % 2 == 0  # alterna acercar / alejar
        z = f"1+0.06*on/{nf}" if zin else f"1.06-0.06*on/{nf}"
        parts.append(f"[{k}:v]scale=2160:3840,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                     f":d=1:s=1080x1920:fps={fps},format=yuv420p,setsar=1[v{k}]")
    last = "v0"
    for k in range(1, n):
        off = k * (dur - fade)
        parts.append(f"[{last}][v{k}]xfade=transition=fade:duration={fade}:offset={off:.2f}[x{k}]")
        last = f"x{k}"
    mp4 = os.path.join(out, "reel.mp4")
    args += ["-filter_complex", ";".join(parts), "-map", f"[{last}]", "-r", str(fps),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", mp4]
    subprocess.run(args, check=True)
    for p in frames:
        os.remove(p)
    total = n * dur - (n - 1) * fade
    print("reel:", mp4, f"{total:.1f}s")


if __name__ == "__main__":
    render(sys.argv[1])
