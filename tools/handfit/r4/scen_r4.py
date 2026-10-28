"""Hands r4: write the support scenarios (sup_r4.py inputs), every number measured here from the meshes / port records.
usage: python3 scen_r4.py <outdir>
  Minigun_bar:   side handle = surface 0 ('Runko', 111 verts) of Minigun.md3 ready frame 4; least-squares cylinder through it;
                 the gun at its r9 port placement (port/fits/ported_Minigun.json R, t); gun hand fbx_hv_Minigun_R.md3 frame 0
  FlameCannon_under40 / _under58: housing cylinder (fc_place.py) at the r4 placement (fc_place.json R, t); palm target 40 / 58 cm
                 along the axis from the rear slit (mid-body over the flesh underside / the front ring section); no gun hand drawn"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common_r4 as C
from scipy.optimize import least_squares
def cyl_any(P, d0):
    d0 = np.asarray(d0, float); d0 /= np.linalg.norm(d0); e1 = np.cross(d0, [0, 0, 1.]) if abs(d0[2]) < 0.9 else np.cross(d0, [1, 0, 0.]); e1 /= np.linalg.norm(e1); e2 = np.cross(d0, e1); c0 = P.mean(0)
    def r(p):
        d = d0 + p[0] * e1 + p[1] * e2; d /= np.linalg.norm(d); c = c0 + p[2] * e1 + p[3] * e2; q = P - c; q = q - np.outer(q @ d, d); return np.linalg.norm(q, axis=1) - p[4]
    s = least_squares(r, [0, 0, 0, 0, 1.5], loss='soft_l1', f_scale=0.3); d = d0 + s.x[0] * e1 + s.x[1] * e2; d /= np.linalg.norm(d)
    return d, c0 + s.x[2] * e1 + s.x[3] * e2, float(s.x[4]), float(np.median(np.abs(s.fun)))
def main(out):
    os.makedirs(out, exist_ok=True); REPO = C.REPO
    # MiniGun
    P = json.load(open(os.path.join(REPO, 'tools/handfit/port/fits/ported_Minigun.json'))); R = np.array(P['R']); t = np.array(P['t'])
    g = dict(path='Minigun/Minigun.md3', frame=4, scale=[-1.0, 1.0, 1.0], off=[0.0, 0.0, -5.0])
    it = dict(path=os.path.join(C.SRC, 'models/bd', g['path']), frame=4, scale=g['scale'], off=g['off']); surf = C.scene.item_verts(it)
    Vb = surf[0][1] @ R.T + t; d, c, r, res = cyl_any(Vb, R @ np.array([0, 1.0, 0]))
    if d @ (R @ np.array([0, 1.0, 0])) < 0: d = -d
    s = (Vb - c) @ d; Vall = np.concatenate([v for _, v in surf]) @ R.T + t
    # where the bar leaves the body: the outer part = along-axis span where only surface 0 is near the axis
    others = np.concatenate([v for k, (_, v) in enumerate(surf) if k != 0]) @ R.T + t; qo = others - c; so = qo @ d; ro = np.linalg.norm(qo - np.outer(so, d), axis=1)
    body_end = float(so[ro < r + 3.0].max()) if (ro < r + 3.0).any() else float(s.min())
    sc = dict(name='Minigun_bar', hold='bar', gun=g, move=dict(R=R.tolist(), t=t.tolist()), gunhand=dict(md3='fbx_hv_Minigun_R.md3', frame=0),
              a=d.tolist(), c=c.tolist(), r=r, s_lo=max(float(s.min()), body_end), s_hi=float(s.max()), approach=[[-1, 0, 0], [0, 0, 1], [0, 0, -1], [1, 0, 0]],
              measured=dict(bar_surface=0, bar_verts=int(len(Vb)), bar_radius_cm=r, cyl_fit_median_res_cm=res, bar_span=[float(s.min()), float(s.max())], body_end=body_end))
    json.dump(sc, open(os.path.join(out, 'Minigun_bar.json'), 'w'), indent=1); print('Minigun bar', json.dumps(sc['measured']), 'axis', d.round(3), 'c', c.round(2))
    # FlameCannon
    FC = json.load(open(os.path.join(out, 'fc_place.json'))); R = np.array(FC['R']); t = np.array(FC['t']); me = FC['measured']
    a = R @ np.array(me['housing_axis']); p0 = R @ np.array(me['housing_axis_point_F0']) + t; sl = np.array(FC['slit_after']); c = p0 + ((sl - p0) @ a) * a
    for s0, nm in ((40.0, 'FlameCannon_under40'), (58.0, 'FlameCannon_under58')):
        sc = dict(name=nm, hold='under', gun=dict(path='FlameCannon/FlameCannon.md3', frame=0, scale=[-1.0, 1.0, 1.0], off=[0.0, 0.0, -5.0]), move=dict(R=R.tolist(), t=t.tolist()),
                  gunhand=None, a=a.tolist(), c=c.tolist(), r=me['housing_radius_cm'], s0=s0, down=[0, 0, -1.0], measured=dict(axis_from='fc_place.json housing cylinder', c='axis point level with the rear slit'))
        json.dump(sc, open(os.path.join(out, nm + '.json'), 'w'), indent=1)
    print('FlameCannon axis', a.round(4), 'c', c.round(2))
if __name__ == '__main__': main(sys.argv[1])
