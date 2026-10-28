"""Hands r4 fit sheet: the moved gun (textured) + the FBX gun hand (baked md3 frame, hook 0 = the pinned wrist) + the FBX support
hand (baked frame placed by its support hook/rot), four orthographic views and the player's eye view, numbers in the title.
usage: python3 sheet_r4.py <spec.json> <out.png>
spec: {title, gun: {path, skin, frame, scale, off}, R, t (gun move), gunhand: {md3 (path), frame} | null,
       support: {md3, frame, hook, rot} | null, ghost: {md3, frame} | null (drawn translucent: the undrawn hand, for placement),
       lines: [text, ...]}"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common_r4 as C
import render, hudrender, hook
from PIL import Image, ImageDraw
def textured(g, R, t):
    it = dict(path=os.path.join(C.SRC, 'models/bd', g['path']), frame=g['frame'], scale=g['scale'], off=g['off']); out = []
    im = np.asarray(Image.open(os.path.join(C.SRC, 'models/bd', g['skin'])).convert('RGB')); h, w, _ = im.shape
    for (T, V), s in zip(C.scene.item_verts(it), C.scene.md3_full(it['path'])):
        st = s['st'][T].mean(1); fc = im[((st[:, 1] % 1) * (h - 1)).astype(int), ((st[:, 0] % 1) * (w - 1)).astype(int)].astype(float)
        out.append(dict(V=V @ np.asarray(R).T + np.asarray(t), F=np.asarray(T), fcol=fc))
    return out
def placed(md3, frame, hk=(0, 0, 0), rt=(0, 0, 0)):
    s = C.scene.md3_full(md3)[0]; return 100 * (hudrender.to_local(s['xyz'][frame], dict(hook=list(hk), rot=list(rt), **hook.PL)) @ hook.P.T), np.asarray(s['tris'])
def main(spec, out):
    S = json.load(open(spec)); M = textured(S['gun'], S['R'], S['t']); hands = []
    if S.get('gunhand'): V, T = placed(S['gunhand']['md3'], S['gunhand']['frame']); hands.append(dict(V=V, F=T, col=(214, 170, 140)))
    if S.get('support'): sp = S['support']; V, T = placed(sp['md3'], sp['frame'], sp['hook'], sp['rot']); hands.append(dict(V=V, F=T, col=(150, 175, 230)))
    if S.get('ghost'): V, T = placed(S['ghost']['md3'], S['ghost']['frame']); hands.append(dict(V=V, F=T, col=(120, 230, 120), alpha=0.45))
    allV = np.concatenate([m['V'] for m in M + hands]); lo = allV.min(0); hi = allV.max(0)
    ims = [render.render(M + hands, k, px=7, title=S['title'] + '  ' + k) for k in ('side', 'left', 'bottom', 'top')]
    eye = np.array([-70.0, -12.0, 28.0]); look = 0.5 * (lo + hi)
    ims.append(render.render(M + hands, eye=eye, look=look, W=760, H=420, fov=50, title='player eye (approx.)'))
    sh = render.sheet(ims, 2); d = ImageDraw.Draw(sh); y = sh.height - 14 * len(S.get('lines', [])) - 6
    pad = Image.new('RGB', (sh.width, sh.height + 14 * len(S.get('lines', [])) + 10), (20, 20, 28)); pad.paste(sh, (0, 0)); d = ImageDraw.Draw(pad)
    for k, l in enumerate(S.get('lines', [])): d.text((8, sh.height + 4 + 14 * k), l, fill=(235, 235, 235))
    pad.save(out)
if __name__ == '__main__': main(*sys.argv[1:3])
