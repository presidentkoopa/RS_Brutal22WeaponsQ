"""b2_hands.png: BrutalSMG rest / steadied / firing, from the eye (front) and from the side (rig frames, left eye, 480 px)."""
import sys, os
from PIL import Image, ImageDraw
D = '/home/claude/lane_b_b2run/shots'
pick = dict(a.split('=') for a in sys.argv[1:])
rows = [('eye', 'BrutalSMG, from the eye'), ('side', 'BrutalSMG, from the side')]; sts = ['rest', 'steady', 'fire']
lab = {'rest': 'at rest', 'steady': 'steadied (off hand on, grip)', 'fire': 'firing (squeeze)'}
tiles = [[Image.open(os.path.join(D, 'b2%s_BrutalSMG_%s_%s.png' % (r, s, pick.get('%s_%s' % (r, s), '5')))).convert('RGB') for s in sts] for r, _ in rows]
w, h = tiles[0][0].size; top = 34; lh = 22
sheet = Image.new('RGB', (w * 3, top + (h + lh) * len(rows)), (24, 24, 24)); dr = ImageDraw.Draw(sheet)
dr.text((8, 8), 'batch 2 (BD22_VR-Reloaded_1.99x-lb-r6-hands.pk3): BrutalSMG, the pistol FBX hand (index re-solved) + FBX palm under. QZD 17.3 rig, doom2 > brutal22test6 > BD_VoxelPack > pack. Rig only, not headset-confirmed', fill=(230, 230, 230))
for r, (tag, name) in enumerate(rows):
    y = top + r * (h + lh)
    for c, s in enumerate(sts):
        dr.text((c * w + 6, y + 4), '%s: %s' % (name, lab[s]), fill=(255, 220, 120)); sheet.paste(tiles[r][c], (c * w, y + lh))
sheet.save('/home/claude/lane_b_out/b2_hands.png'); print(sheet.size)
