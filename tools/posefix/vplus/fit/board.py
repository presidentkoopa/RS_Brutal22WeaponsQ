"""Storyboard: side views of chosen frames of a Vanilla VR Plus gun, labelled sprite+frame."""
import sys
import vplus, guns, gunview
from PIL import Image, ImageDraw
OUT = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/vplus/out/'
def board(cls, frames, labels, rng, out, cols=6, px=3):
    ims = []
    for fr, lab in zip(frames, labels):
        it = vplus.vitem(cls, fr); it['color'] = [150, 155, 170]
        p = OUT + 'tmp_board.png'
        gunview.view([it], p, 'side', px=px, rng=rng, title='%s f%d' % (lab, fr))
        ims.append(Image.open(p).copy())
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    O = Image.new('RGB', (w * cols, h * rows))
    for i, im in enumerate(ims):
        O.paste(im, ((i % cols) * w, (i // cols) * h))
    O.save(out)
if __name__ == '__main__':
    pass
