"""b3_hands.png: each fitted gun at rest / steadied / firing, from the eye and from the side (QZD 17.3 rig frames), next to its
1.92 render (Depot docs/reference/bd22q_192_poses/<Class>_eye.jpg / _side.jpg)."""
import sys, os
from PIL import Image, ImageDraw
D = '/home/claude/lane_b_b3run/shots'; REF = '/home/claude/rsq_weapondepot/docs/reference/bd22q_192_poses/'
guns = sys.argv[1].split(','); pick = dict(a.split('=') for a in sys.argv[2:])
sts = ['rest', 'steady', 'fire']; lab = {'rest': 'at rest', 'steady': 'steadied (off hand on, grip)', 'fire': 'firing (squeeze)'}
rows = [(g, v) for g in guns for v in ('eye', 'side')]
w, h = Image.open(os.path.join(D, 'b3eye_%s_rest_5.png' % guns[0])).size; top = 34; lh = 22
sheet = Image.new('RGB', (w * 4, top + (h + lh) * len(rows)), (24, 24, 24)); dr = ImageDraw.Draw(sheet)
dr.text((8, 8), 'batch 3 (BD22_VR-Reloaded_1.99x-lb-r6-hands3.pk3): FBX hand fitted from 1.92. QZD 17.3 rig, doom2 > brutal22test6 > BD_VoxelPack > pack. Rig only, not headset-confirmed', fill=(230, 230, 230))
for r, (g, v) in enumerate(rows):
    y = top + r * (h + lh)
    ref = Image.open(REF + '%s_%s.jpg' % (g, v)).convert('RGB'); ref = ref.resize((w, int(ref.size[1] * w / ref.size[0])))
    dr.text((6, y + 4), '%s: 1.92 (%s)' % (g, v), fill=(150, 200, 255)); sheet.paste(ref.crop((0, 0, w, h)), (0, y + lh))
    for c, s in enumerate(sts):
        f = os.path.join(D, 'b3%s_%s_%s_%s.png' % (v, g, s, pick.get('%s_%s_%s' % (g, v, s), '5')))
        dr.text(((c + 1) * w + 6, y + 4), '%s, %s: %s' % (g, v, lab[s]), fill=(255, 220, 120))
        if os.path.exists(f): sheet.paste(Image.open(f).convert('RGB'), ((c + 1) * w, y + lh))
sheet.save('/home/claude/lane_b_out/b3_hands.png'); print(sheet.size)
