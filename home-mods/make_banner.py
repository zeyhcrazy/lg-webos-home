"""Monta o banner da Início LG (3492x900 + 2k/hd) a partir de uma foto/wallpaper.
Uso: python make_banner.py <foto> <saida_prefixo> [altura_frac=0.62] [centro_y=0.5] [alinh=right|center] [faixa=640]
- vinheta (7o arg) = 1 escurece as bordas ate o preto (padrao), 0 = foto limpa sem efeito
- faixa = altura do herobanner no home.xml; a LG ENCAIXA a imagem inteira no espaco (contain),
  entao o PNG sai exatamente 3492 x faixa (2k/hd proporcionais) pra preencher tudo
- mostra 'altura_frac' da altura da foto (menor = mais zoom), centrado em 'centro_y'
- se sobrar largura, preenche com a cor da borda da foto e funde
- bordas somem no preto (esq perto dos ícones, dir, baixo) pra combinar com a Início
"""
import sys
from PIL import Image, ImageDraw, ImageChops, ImageFilter, ImageStat

W, H = 3492, 900
src, out = sys.argv[1], sys.argv[2]
hf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.62
cy = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
al = sys.argv[5] if len(sys.argv) > 5 else 'right'
FULL_H = H
H = int(sys.argv[6]) if len(sys.argv) > 6 else 640   # conteudo so na faixa visivel
VINHETA = (sys.argv[7] != '0') if len(sys.argv) > 7 else True

im = Image.open(src).convert('RGB')
w, h = im.size
ch = int(h * hf)
y0 = max(0, min(h - ch, int(h * cy - ch / 2)))
crop = im.crop((0, y0, w, y0 + ch))
nw = round(w * H / ch)
if W - 60 <= nw < W:   # faltam poucos px: estica (imperceptivel) em vez de preencher a borda
    nw = W
crop = crop.resize((nw, H), Image.LANCZOS)

if nw >= W:
    x = (nw - W) if al == 'right' else (nw - W) // 2
    canvas = crop.crop((x, 0, x + W, H))
else:
    edge = ImageStat.Stat(crop.crop((0, 0, 8, H))).median
    canvas = Image.new('RGB', (W, H), tuple(int(v) for v in edge))
    x = (W - nw) if al == 'right' else (W - nw) // 2
    m = Image.new('L', (nw, H), 255); dm = ImageDraw.Draw(m)
    for i in range(min(260, nw)):
        dm.line([(i, 0), (i, H)], fill=int(255 * i / 260))
    canvas.paste(crop, (x, 0), m)

# vinheta pro preto
mx = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mx)
for xx in range(W):
    t = xx / W
    d.line([(xx, 0), (xx, H)], fill=int(255 * (min(1, t / 0.18) * min(1, (1 - t) / 0.08)) ** 1.3))
my = Image.new('L', (W, H), 0); d = ImageDraw.Draw(my)
for yy in range(H):
    t = yy / H
    d.line([(0, yy), (W, yy)], fill=int(255 * (min(1, t / 0.14) * min(1, (1 - t) / 0.30)) ** 1.2))
mask = ImageChops.multiply(mx, my).filter(ImageFilter.GaussianBlur(30))
final = Image.composite(canvas, Image.new('RGB', (W, H), (0, 0, 0)), mask) if VINHETA else canvas

final.save(out + '_4k.png', optimize=True)
final.resize((W // 2, H // 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(out + '_2k.png', optimize=True)
final.resize((1264, round(H * 1264 / W)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.0, 60, 2)).save(out + '_hd.png', optimize=True)
final.resize((1164, round(H * 1164 / W)), Image.LANCZOS).save(out + '_preview.png')
print('ok', src)
