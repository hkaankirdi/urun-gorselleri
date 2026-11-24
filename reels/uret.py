"""Ürün görsellerinden 9:16 Reels videosu üretir (sessiz, 30 fps).

python3 reels/uret.py  -> reels/plan.json içindeki her reels için reels/<id>.mp4 ve kapak üretir
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
SLAYT, GECIS, SON = 1.9, 0.35, 2.4
BG = (237, 232, 225)
KOYU = (34, 34, 36)
TURUNCU = (240, 123, 31)
FD = "/usr/share/fonts/truetype/google-fonts/ofl/firasans/"
F = lambda w, s: ImageFont.truetype(FD + f"FiraSans-{w}.ttf", s)


def ortala(d, y, metin, font, renk):
    w = d.textlength(metin, font=font)
    d.text(((W - w) / 2, y), metin, font=font, fill=renk)


def sar(d, metin, font, genislik):
    satirlar, s = [], ""
    for k in metin.split():
        t = (s + " " + k).strip()
        if d.textlength(t, font=font) <= genislik:
            s = t
        else:
            satirlar.append(s)
            s = k
    satirlar.append(s)
    return satirlar


def slayt_kare(urun, t, kanca, etiket, no):
    """t: 0..1 slayt içi ilerleme."""
    im = Image.new("RGB", (W, H), urun.getpixel((3, 3)))
    # ürün: 980x1180 kutuya sığdır, yavaş yakınlaştırma
    z = 1.0 + 0.07 * t
    bw, bh = 980, 1180
    oran = min(bw / urun.width, bh / urun.height) * z
    u = urun.resize((int(urun.width * oran), int(urun.height * oran)), Image.LANCZOS)
    cx, cy = W // 2, 930
    kx, ky = cx - u.width // 2, cy - u.height // 2
    im.paste(u, (kx, ky))
    d = ImageDraw.Draw(im)
    # üst kanca
    f = F("ExtraBold", 74)
    y = 120
    for s in sar(d, kanca, f, 960):
        ortala(d, y, s, f, KOYU)
        y += 86
    # alt bant
    d.rectangle([0, 1600, W, 1920], fill=KOYU)
    if no:
        r = 46
        d.ellipse([W // 2 - r, 1560 - r + 20, W // 2 + r, 1560 + r + 20], fill=TURUNCU)
        fn = F("Bold", 50)
        ortala(d, 1550, str(no), fn, (255, 255, 255))
    ortala(d, 1650, etiket, F("Bold", 54), (255, 255, 255))
    ortala(d, 1735, "Metal lazer kesim  ·  Trendyol: Sahil Art and Design", F("Regular", 34), (200, 200, 200))
    ortala(d, 1810, "@sahilartdesign", F("Medium", 36), TURUNCU)
    return im


def son_kare(soru):
    im = Image.new("RGB", (W, H), KOYU)
    d = ImageDraw.Draw(im)
    f = F("ExtraBold", 80)
    y = 560
    for s in sar(d, soru, f, 940):
        ortala(d, y, s, f, (255, 255, 255))
        y += 96
    d.rounded_rectangle([170, 960, 910, 1110], radius=40, fill=TURUNCU)
    ortala(d, 990, "TAKİP ET", F("ExtraBold", 76), (255, 255, 255))
    ortala(d, 1170, "@sahilartdesign", F("Bold", 60), (255, 255, 255))
    ortala(d, 1270, "Satın almak için profildeki linke tıkla", F("Regular", 40), (210, 210, 210))
    ortala(d, 1330, "Trendyol: Sahil Art and Design", F("Regular", 40), (210, 210, 210))
    return im


def uret(r):
    cikti = os.path.join(KOK, "reels", r["id"] + ".mp4")
    urunler = [Image.open(os.path.join(KOK, p)).convert("RGB") for p in r["gorseller"]]
    n_s, n_g, n_e = int(SLAYT * FPS), int(GECIS * FPS), int(SON * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", cikti]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    onceki = None
    kareler = []
    for i, u in enumerate(urunler):
        etiket = r["etiketler"][i] if r.get("etiketler") else r["baslik"]
        no = i + 1 if r.get("numarali") else None
        for k in range(n_s):
            fr = slayt_kare(u, k / n_s, r["kanca"], etiket, no)
            if onceki is not None and k < n_g:
                fr = Image.blend(onceki, fr, k / n_g)
            p.stdin.write(fr.tobytes())
            if k == n_s // 2 and i == 0:
                fr.save(os.path.join(KOK, "reels", r["id"] + "_kapak.jpg"), quality=90)
        onceki = slayt_kare(u, 1.0, r["kanca"], etiket, no)
    son = son_kare(r["soru"])
    for k in range(n_e):
        fr = Image.blend(onceki, son, k / n_g) if k < n_g else son
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    p.wait()
    return cikti


if __name__ == "__main__":
    plan = json.load(open(os.path.join(KOK, "reels", "plan.json"), encoding="utf-8"))
    secim = sys.argv[1:]
    for r in plan:
        if secim and r["id"] not in secim:
            continue
        print(uret(r), flush=True)
