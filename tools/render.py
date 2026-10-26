"""Generador de carruseles y Reels DVITAS.

Uso:
  python3 tools/render.py posts/AAAA-MM-DD_tema/spec.json

La ficha (spec.json) tiene:
  {"fondo": "azul" | "crema",
   "eje": "PSICOLOGIA INFANTIL", "tema": "MIEDOS",
   "reel": false,
   "slides": [ {"tipo": "portada", "titulo": "...", "subtitulo": "..."},
               {"tipo": "lista", "titulo": "...", "items": ["...", ...], "aviso": true},
               {"tipo": "pasos", "titulo": "...", "pasos": [["Titulo", "explicacion"], ...]},
               {"tipo": "datos", "titulo": "...", "filas": [["Etapa", 0.6, "rango"], ...], "nota": "..."},
               {"tipo": "cta", "titulo": "Guardalo y envíaselo a quien lo necesite"},
               {"tipo": "cierre", "titulo": "...", "texto": "..."} ]}

Salida en la misma carpeta: slide_1.jpg ... (1080x1350) y, si reel=true, reel.mp4 (1080x1920, sin audio).
"""
import json, os, subprocess, sys, shutil
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
OSCURO = (0x2E, 0x3A, 0x3B)
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
        self.title = BLANCO if self.azul else TEAL
        self.body = BLANCO if self.azul else OSCURO
        self.muted = BLANCO if self.azul else GRIS
        self.logo = LOGO_WHITE if self.azul else LOGO_TEAL
        self.circle = BLANCO if self.azul else TEAL
        self.circle_num = AZUL if self.azul else BLANCO


def base(th, eje, tema, logo_pos=None):
    im = Image.new("RGB", (W, H), th.bg)
    d = ImageDraw.Draw(im)
    fe, ft = font("Poppins-Medium.ttf", 22), font("Poppins-Bold.ttf", 30)
    pad = 26
    tw = max(d.textlength(eje, font=fe), d.textlength(tema, font=ft))
    pw, ph = int(tw + pad * 2), 100
    d.rounded_rectangle([M, M, M + pw, M + ph], radius=22, fill=NARANJA)
    d.text((M + pad, M + 14), eje, font=fe, fill=BLANCO)
    mix = tuple(int(NARANJA[i] * 0.3 + 255 * 0.7) for i in range(3))  # blanco al 70 %
    d.text((M + pad, M + 46), tema, font=ft, fill=mix)
    if logo_pos:
        lg = Image.open(th.logo).convert("RGBA")
        lw = 200 if logo_pos == "esquina" else 300
        lh = int(lg.height * lw / lg.width)
        lg = lg.resize((lw, lh), Image.LANCZOS)
        pos = (W - M - lw, H - M - lh) if logo_pos == "esquina" else ((W - lw) // 2, H - M - lh)
        im.paste(lg, pos, lg)
    return im, d


def title(d, th, text, y, size=80):
    f = font("Poppins-Bold.ttf", size)
    for ln in wrap(d, text, f, W - 2 * M)[:3]:
        d.text((M, y), ln, font=f, fill=th.title)
        y += int(size * 1.18)
    return y


def paragraph(d, th, text, y, size=38, color=None, maxw=None, italic=False):
    f = font("Poppins-Italic.ttf" if italic else "Poppins-Regular.ttf", size)
    for ln in wrap(d, text, f, maxw or W - 2 * M):
        d.text((M, y), ln, font=f, fill=color or th.body)
        y += int(size * 1.4)
    return y


def aviso(d, th, y_max):
    f = font("Poppins-Italic.ttf", 30)
    lines = wrap(d, AVISO, f, 640)
    y = y_max - len(lines) * 42
    for ln in lines:
        d.text((M, y), ln, font=f, fill=th.muted)
        y += 42


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
        logo = "esquina" if i == 1 else ("centro" if i == n else None)
        im, d = base(th, eje, tema, logo)
        if t == "portada":
            y = title(d, th, s["titulo"], 380, 100)
            if s.get("subtitulo"):
                paragraph(d, th, s["subtitulo"], y + 40)
        elif t == "lista":
            y = title(d, th, s["titulo"], 330) + 60
            fb = font("Poppins-Regular.ttf", 38)
            for it in s["items"][:5]:
                d.ellipse([M, y + 14, M + 18, y + 32], fill=NARANJA)
                for ln in wrap(d, it, fb, W - 2 * M - 50):
                    d.text((M + 50, y), ln, font=fb, fill=th.body)
                    y += 52
                y += 26
            if s.get("aviso"):
                aviso(d, th, H - M - (360 if logo else 20))
        elif t == "pasos":
            y = title(d, th, s["titulo"], 330) + 60
            for k, (pt, ps) in enumerate(s["pasos"][:5], 1):
                d.ellipse([M, y, M + 80, y + 80], fill=th.circle)
                d.text((M + 27, y + 14), str(k), font=font("Poppins-Bold.ttf", 44), fill=th.circle_num)
                d.text((M + 110, y), pt, font=font("Poppins-Bold.ttf", 40), fill=th.title)
                yy = y + 52
                for ln in wrap(d, ps, font("Poppins-Regular.ttf", 33), W - 2 * M - 110):
                    d.text((M + 110, yy), ln, font=font("Poppins-Regular.ttf", 33), fill=th.body)
                    yy += 44
                y = max(y + 120, yy + 30)
        elif t == "datos":
            y = title(d, th, s["titulo"], 330) + 50
            fl, fv = font("Poppins-Medium.ttf", 32), font("Poppins-Bold.ttf", 32)
            for etapa, frac, etiqueta in s["filas"][:6]:
                d.text((M, y), etapa, font=fl, fill=th.body)
                d.text((W - M - d.textlength(etiqueta, font=fv), y), etiqueta, font=fv, fill=th.title)
                y += 50
                d.rounded_rectangle([M, y, W - M, y + 22], radius=11, fill=(0xD9, 0xDE, 0xDE))
                d.rounded_rectangle([M, y, M + int((W - 2 * M) * max(0.05, min(1, frac))), y + 22], radius=11,
                                    fill=BLANCO if th.azul else TEAL)
                y += 60
            if s.get("nota"):
                paragraph(d, th, s["nota"], y + 20, 28, th.muted, italic=True)
        elif t == "cta":
            y = title(d, th, s.get("titulo", "Guárdalo y envíaselo a quien lo necesite"), 330)
            d.rounded_rectangle([M, y + 50, W - M, y + 130], radius=40, fill=NARANJA)
            d.text((M + 40, y + 72), "Reserva tu cita en la bio", font=font("Poppins-Bold.ttf", 40), fill=BLANCO)
            d.text((M, y + 170), "WhatsApp 744 646 732", font=font("Poppins-Medium.ttf", 40), fill=th.body)
            d.text((M, y + 230), "Doctoralia · C/ Alhucemas 9, Málaga", font=font("Poppins-Regular.ttf", 36), fill=th.body)
        elif t == "cierre":
            y = title(d, th, s["titulo"], 330)
            if s.get("texto"):
                y = paragraph(d, th, s["texto"], y + 30)
            d.rounded_rectangle([M, y + 40, W - M, y + 120], radius=40, fill=NARANJA)
            d.text((M + 40, y + 62), "Reserva tu cita en la bio", font=font("Poppins-Bold.ttf", 40), fill=BLANCO)
            aviso(d, th, H - M - 330)
        else:
            raise SystemExit(f"tipo de slide desconocido: {t}")
        p = os.path.join(out, f"slide_{i}.jpg")
        im.save(p, "JPEG", quality=92, optimize=True)
        files.append(p)
    print("slides:", len(files))
    if spec.get("reel"):
        make_reel(files, th, out)


def make_reel(files, th, out):
    ff = shutil.which("ffmpeg")
    if not ff:
        try:
            import imageio_ffmpeg
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "imageio-ffmpeg"], check=True)
            import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
    frames = []
    for k, f in enumerate(files, 1):
        c = Image.new("RGB", (1080, 1920), th.bg)
        c.paste(Image.open(f), (0, (1920 - H) // 2))
        p = os.path.join(out, f"_reel_{k}.png")
        c.save(p)
        frames.append(p)
    dur = 5
    lst = os.path.join(out, "_reel.txt")
    with open(lst, "w") as fh:
        for p in frames:
            fh.write(f"file '{p}'\nduration {dur}\n")
        fh.write(f"file '{frames[-1]}'\n")
    mp4 = os.path.join(out, "reel.mp4")
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-an", "-movflags", "+faststart", mp4], check=True)
    for p in frames + [lst]:
        os.remove(p)
    print("reel:", mp4, f"{len(files) * dur}s")


if __name__ == "__main__":
    render(sys.argv[1])
