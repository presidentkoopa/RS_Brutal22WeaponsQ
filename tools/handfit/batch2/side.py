"""Side view (F right, U up, |L|<3) of gun meshes at their 1.99 MODELDEF placement, surfaces coloured, 1 cm ticks."""
import sys, numpy as np
sys.path.insert(0, '/home/claude/lane_c/hands_tool'); sys.path.insert(0, '/home/claude/lane_b_b2run/tools')
from PIL import Image, ImageDraw
import revlm, scene
SRC = '/home/claude/lane_b_b2/src/models/bd/'
G = {
 'BrutalSMG': dict(path=SRC + 'BrutalSMG/BrutalSMG.md3', frame=3, scale=[-1.0, 1.0, 1.0], off=[0.0, 0.0, -5.0]),
 'MP40': dict(path=SRC + 'MP40/MP40.md3', frame=2, scale=[-1.0, 1.0, 1.0], off=[0.0, 0.0, -5.0]),
 'Rifle': dict(path=SRC + 'Rifle/Rifle.md3', frame=3, scale=[-1.0, 1.0, 1.0], off=[0.0, 0.0, -5.0]),
 'Sniper': dict(path=SRC + 'XM21/XM21.md3', frame=0, scale=[-10.485, 10.485, 10.485], off=[-0.2816, -44.5467, -6.3157]),
 'BrutalPistol': scene.GUNS['BrutalPistol'],
}
COL = [(255, 255, 255), (255, 80, 80), (80, 255, 80), (80, 160, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (200, 120, 60), (150, 150, 0), (0, 150, 150), (120, 120, 255), (255, 150, 150)]
if __name__ == '__main__':
    names = sys.argv[2:]; sc = 10; f0, f1, u0, u1 = -30, 70, -25, 12
    W = Image.new('RGB', ((f1 - f0) * sc, (u1 - u0) * sc * len(names)), (0, 0, 0)); d = ImageDraw.Draw(W)
    for k, n in enumerate(names):
        S, I = revlm.samples(G[n], 0.25); oy = k * (u1 - u0) * sc
        for s, i in zip(S, I):
            if abs(s[1]) < 3:
                x = int((s[0] - f0) * sc); y = oy + int((u1 - s[2]) * sc)
                if 0 <= x < W.size[0] and oy <= y < oy + (u1 - u0) * sc: d.point((x, y), fill=COL[i % len(COL)])
        for f in range(f0, f1, 5): d.line([(int((f - f0) * sc), oy), (int((f - f0) * sc), oy + 6)], fill=(255, 255, 255)); d.text((int((f - f0) * sc) + 2, oy + 6), str(f), fill=(160, 160, 160))
        for u in range(u0, u1, 5): d.line([(0, oy + int((u1 - u) * sc)), (6, oy + int((u1 - u) * sc))], fill=(255, 255, 255)); d.text((8, oy + int((u1 - u) * sc) - 5), str(u), fill=(160, 160, 160))
        d.text((40, oy + 20), n + '  surfaces: ' + ' '.join('%d' % j for j in sorted(set(I))), fill=(255, 255, 255))
        for j in sorted(set(I)): d.text((40 + 30 * j, oy + 34), str(j), fill=COL[j % len(COL)])
    W.save(sys.argv[1])
