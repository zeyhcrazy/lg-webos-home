"""Gera fundo 'aurora' escuro para o banner da Início LG (sem texto, bordas somem no preto)."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 3492, 900
out = sys.argv[1]
random.seed(7)

base = Image.new('RGB', (W, H), (2, 3, 8))

def ribbon(color, y0, amp, freq, phase, thick, blur):
    layer = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts_top, pts_bot = [], []
    for x in range(-40, W + 41, 12):
        t = x / W
        y = y0 + amp * math.sin(2 * math.pi * freq * t + phase) + amp * 0.35 * math.sin(2 * math.pi * freq * 2.3 * t + phase * 1.7)
        th = thick * (0.55 + 0.45 * math.sin(math.pi * t + phase))
        pts_top.append((x, y - th / 2)); pts_bot.append((x, y + th / 2))
    d.polygon(pts_top + pts_bot[::-1], fill=color)
    return layer.filter(ImageFilter.GaussianBlur(blur))

layers = [
    ((20, 60, 140), 380, 120, 0.8, 0.3, 260, 90),
    ((70, 30, 130), 470, 150, 0.6, 1.9, 220, 100),
    ((10, 120, 130), 330, 90, 1.1, 3.1, 120, 60),
    ((90, 60, 200), 420, 70, 1.4, 4.4, 60, 30),
    ((30, 160, 170), 360, 60, 1.7, 0.9, 30, 14),
]
for args in layers:
    base = ImageChops.add(base, ribbon(*args))

# brilho fino (linhas de luz) sobre as faixas
glow = Image.new('RGB', (W, H), (0, 0, 0))
dg = ImageDraw.Draw(glow)
for k in range(18):
    ph = random.uniform(0, 6.28); y0 = random.uniform(300, 520); amp = random.uniform(40, 130); fr = random.uniform(0.6, 1.6)
    col = random.choice([(60, 120, 220), (120, 80, 220), (40, 190, 200)])
    pts = [(x, y0 + amp * math.sin(2 * math.pi * fr * x / W + ph)) for x in range(0, W + 1, 10)]
    dg.line(pts, fill=col, width=2)
base = ImageChops.add(base, glow.filter(ImageFilter.GaussianBlur(3)))

# poeira de estrelas bem discreta
stars = Image.new('RGB', (W, H), (0, 0, 0)); ds = ImageDraw.Draw(stars)
for _ in range(500):
    x, y = random.randrange(W), random.randrange(H); b = random.randint(40, 140)
    ds.point((x, y), fill=(b, b, b + 20))
base = ImageChops.add(base, stars.filter(ImageFilter.GaussianBlur(0.6)))

# vinheta: some no preto à esquerda (perto dos ícones), à direita e embaixo
mask = Image.new('L', (W, H), 0); dm = ImageDraw.Draw(mask)
for x in range(W):
    t = x / W
    a = min(1.0, t / 0.22) * min(1.0, (1 - t) / 0.18)
    dm.line([(x, 0), (x, H)], fill=int(255 * a ** 1.4))
vmask = Image.new('L', (W, H), 0); dv = ImageDraw.Draw(vmask)
for y in range(H):
    t = y / H
    a = min(1.0, t / 0.12) * min(1.0, (1 - t) / 0.40)
    dv.line([(0, y), (W, y)], fill=int(255 * a ** 1.2))
m = ImageChops.multiply(mask, vmask).filter(ImageFilter.GaussianBlur(40))
final = Image.composite(base, Image.new('RGB', (W, H), (0, 0, 0)), m)
final.save(out + '_4k.png', optimize=True)
final.resize((1746, 450), Image.LANCZOS).save(out + '_2k.png', optimize=True)
final.resize((1264, 326), Image.LANCZOS).save(out + '_hd.png', optimize=True)
final.resize((1164, 300), Image.LANCZOS).save(out + '_preview.png')
print('ok')
