"""TEST ONLY: PNG frames -> one contact sheet. strip.py <out.png> <cols> <crop x0,y0,x1,y1|-> <png...>"""
import sys
from PIL import Image
out, cols, crop = sys.argv[1], int(sys.argv[2]), sys.argv[3]; fs = sys.argv[4:]
ims = [Image.open(f).convert('RGB') for f in fs]
if crop != '-':
    x0, y0, x1, y1 = map(int, crop.split(','))
    ims = [im.crop((x0, y0, x1, y1)).resize(((x1 - x0), (y1 - y0))) if True else im for im in ims]
    from PIL import ImageDraw
w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (w * cols, h * rows), (40, 40, 40))
for k, im in enumerate(ims):
    S.paste(im, ((k % cols) * w, (k // cols) * h))
S.save(out); print(out, S.size)
