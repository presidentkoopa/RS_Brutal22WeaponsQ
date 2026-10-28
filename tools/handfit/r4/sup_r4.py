"""Hands r4: FBX SUPPORT hand (left) solved on a moved gun, any hold, then baked as an RQFS-style frame + its support row.
usage: python3 sup_r4.py <scenario.json> <outdir> [--nfev N] [--seeds K] [--x0 sup_<name>.json] [--thr 0.25] [--h 0.3]
  --x0: refine a previous result (its x is the only seed); --thr: penetration hinge (cm); --h: distance-grid step (cm)
scenario.json (written by the gun's setup script, every number measured there):
  gun: {path (under src/models/bd), frame, scale, off}, move: {R, t} (shipped controller frame -> drawn), gunhand: md3 + frame (or null)
  hold: 'under' (open palm cupped under a cylinder) | 'bar' (fist round a bar/handle: the bar runs THROUGH the fist)
  axis a, point c (on the axis), radius r, s0 (palm target along a, from c), s_lo/s_hi (usable part of the axis), down (for 'under')
Unknowns: hand rotation (rotvec), translation (cm), 18 FBX pose parameters (handmodel: authored open->fist curls, spreads, thumb, wrist).
Terms (cm / deg; hinge = 0 inside the band):
  all   penetration into the gun and the gun hand <= 0.25 (every 2nd vertex; reported on every vertex), pose prior
  under (under_rules.py U1-U6): palm touching (0.3), palm within 25 deg of straight under the axis, palm normal within 25 deg of
        up-into-the-axis, pads touching (0.4), fingertips 45..120 deg round the axis from the palm, forearm within 40 deg of the
        axis in top view, palm near s0 (+-4)
  bar   (SKILL handlebar rule, fistwrap.py): palm touching the bar (0.3), I/M/R/P pads on the bar (0.3), thumb pad on it (0.6),
        every finger chain palm->base->mid->top->tip wraps >= 200 deg round the bar axis, index->pinky along +a (>= 4 cm),
        palm inside s_lo..s_hi, forearm within 70 deg of back (-F)
Bake: bake.bake(side L) with the wrist where fbx_b1_L.md3 frame 1 (RQFS B) has it, so the new frame swaps in for RQFS B;
sup_hook / sup_rot = hook_from_rigid of the frame onto the solved hand (port_gun.py --support writes these)."""
import os, sys, json, time, argparse, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common_r4 as C
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as Rot
import handmodel, exactpen, evaluate, bake, hook, metrics, gunfield
LANE = C.LANE
def load_L():
    L = dict(json.load(open(os.path.join(LANE, 'landmarks_fbx.json')))['L']); L['_reg'] = json.load(open(os.path.join(LANE, 'regions.json')))['fbx']; return L
FTIP = dict(I='INDEX', M='MIDDLE_F', R='RING', P='PINK')
THR = [0.25]; GRID = [0.3]
class Model:
    def __init__(s, sc):
        s.sc = sc; s.H = handmodel.FbxHand('L'); s.L = load_L(); s.scale = json.load(open(os.path.join(LANE, 'calib.json')))['scale']
        g = sc['gun']; F, V, it = C.gun(g['path'], g['frame'], g['scale'], g['off']); R = np.array(sc['move']['R']); t = np.array(sc['move']['t'])
        s.Vg = V @ R.T + t; s.Fg = F; s.exg = exactpen.Exact(s.Vg, F)
        s.exh = None
        if sc.get('gunhand'):
            Y, T = C.md3_hand(os.path.join(C.FBXDIR, sc['gunhand']['md3']), sc['gunhand']['frame']); s.Xh = Y; s.exh = exactpen.Exact(Y, np.asarray(T))
        s.a = np.array(sc['a'], float); s.a /= np.linalg.norm(s.a); s.c = np.array(sc['c'], float); s.r = float(sc['r'])
        ctr = s.c + s.a * (sc['s0'] if sc['hold'] == 'under' else 0.5 * (sc['s_lo'] + sc['s_hi'])); B = float(sc.get('box', 20.0))
        # the solve uses signed distance grids (gunfield.Field, 0.3 cm, a box round the hold); the reported numbers use exactpen
        s.fg = gunfield.Field(s.Vg, F, ctr - B, ctr + B, h=GRID[0], band=1.0)
        s.fh = gunfield.Field(s.Xh, np.asarray(T), ctr - B, ctr + B, h=GRID[0], band=1.0) if s.exh is not None else None
        s.reg = {k: evaluate.reg(s.L, k) for k in ('palm', 'web', 'pad_I', 'pad_M', 'pad_R', 'pad_P', 'pad_T')}
        s.cuff = np.array(s.L['cuff']); s.sub = np.arange(0, len(s.H.Vh), 2 if THR[0] >= 0.2 else 1)
        x_, y_, n_ = s.H.axes(); s.ax = dict(x=x_, y=y_, n=n_)
        V0, J0 = s.H.pose(np.zeros(18)); s.palm0 = V0[s.reg['palm']].mean(0)
        s.q0 = np.clip(np.array(sc.get('q_prior', [0.5, 0.5, 0] * 4 + [0.4, 0.3, 0, 0] + [0, 0])), handmodel.QLO, handmodel.QHI)
    def X(s, x):
        R = Rot.from_rotvec(x[:3]).as_matrix(); V, J = s.H.pose(x[6:24]); return s.scale * V @ R.T + x[3:6], {k: s.scale * R @ v + x[3:6] for k, v in J.items()}, R
    def radial(s, P):
        q = np.atleast_2d(P) - s.c; ax = q @ s.a; rr = q - np.outer(ax, s.a); return ax, rr
    def frame2(s):
        e1 = np.array(s.sc.get('down', [0, 0, -1.0])); e1 = e1 - (e1 @ s.a) * s.a; e1 /= np.linalg.norm(e1); e2 = np.cross(s.a, e1); return e1, e2
    def ang2(s, P):
        e1, e2 = s.frame2(); _, rr = s.radial(P); return np.degrees(np.arctan2(rr @ e2, rr @ e1))
    def res(s, x, full=False):
        X, J, R = s.X(x); r = []; sc = s.sc; m = {}
        dg = s.exg.depth(X) if full else np.maximum(0, -s.fg(X[s.sub])); r += list(6.0 * np.maximum(0, dg - THR[0])); m['pen_gun'] = float(dg.max())
        if s.exh is not None:
            dh = s.exh.depth(X) if full else np.maximum(0, -s.fh(X[s.sub])); r += list(6.0 * np.maximum(0, dh - THR[0])); m['pen_gunhand'] = float(dh.max())
        r += list(0.3 * (x[6:24] - s.q0) / np.array([1, 1, 30] * 4 + [1, 1, 30, 30] + [30, 30]))
        pc = X[s.reg['palm']].mean(0)
        ug = (lambda k: float(s.exg.unsigned(X[s.reg[k]]).min())) if full else (lambda k: float(np.abs(s.fg(X[s.reg[k]])).min()))
        m['palm_gap'] = ug('palm'); r.append(2.0 * (m['palm_gap'] - 0.3))
        ax_pc, rr_pc = s.radial(pc); m['palm_s'] = float(ax_pc[0])
        n_w = R @ s.ax['n']; cuffc = X[s.cuff].mean(0); fore = pc - cuffc; fore /= np.linalg.norm(fore)
        if sc['hold'] == 'under':
            e1, e2 = s.frame2(); u = rr_pc[0] / np.linalg.norm(rr_pc[0]); m['palm_under_deg'] = float(np.degrees(np.arccos(np.clip(u @ e1, -1, 1))))
            r.append(0.15 * max(0, m['palm_under_deg'] - 25)); m['palm_normal_deg'] = float(np.degrees(np.arccos(np.clip(n_w @ -u, -1, 1)))); r.append(0.15 * max(0, m['palm_normal_deg'] - 25))
            r.append(0.5 * max(0, abs(m['palm_s'] - sc['s0']) - 4.0))
            a0 = s.ang2(pc)[0]
            for f in 'IMRP':
                gp = ug('pad_' + f); m['gap_' + f] = gp; r.append(1.0 * max(0, gp - 0.4))
                tip = J[FTIP[f] + '_UP_TOP_joint']; w = abs((s.ang2(tip)[0] - a0 + 180) % 360 - 180); m['wrap_' + f] = float(w)
                r.append(0.05 * max(0, 45 - w)); r.append(0.05 * max(0, w - 120))
            ft = fore - (fore @ np.array([0, 0, 1.])) * np.array([0, 0, 1.]); at = s.a - (s.a @ np.array([0, 0, 1.])) * np.array([0, 0, 1.])
            m['fore_top_deg'] = float(np.degrees(np.arccos(np.clip(abs(ft @ at) / np.linalg.norm(ft) / np.linalg.norm(at), -1, 1)))); r.append(0.05 * max(0, m['fore_top_deg'] - 40))
            _, rc = s.radial(cuffc); m['cuff_below'] = float(rc[0] @ e1); r.append(0.2 * max(0, -m['cuff_below']))
        else:
            for f in 'IMRP':
                gp = ug('pad_' + f); m['gap_' + f] = gp; r.append(1.5 * max(0, gp - 0.3))
                pts = [pc] + [J[FTIP[f] + k] for k in ('_BASE_joint', '_MID_joint', '_TOP_joint', '_UP_TOP_joint')]
                an = np.unwrap(np.radians(s.ang2(np.array(pts)))); w = float(abs(np.degrees(an[-1] - an[0]))); m['wrap_' + f] = w
                r.append(0.05 * max(0, 200 - w))
            m['gap_T'] = ug('pad_T'); r.append(1.0 * max(0, m['gap_T'] - 0.6))
            sI = s.radial(X[s.reg['pad_I']].mean(0))[0][0]; sP = s.radial(X[s.reg['pad_P']].mean(0))[0][0]; m['I_to_P_along'] = float(sP - sI); r.append(0.5 * max(0, 4.0 - (sP - sI)))
            r.append(0.5 * max(0, sc['s_lo'] + 1 - m['palm_s'])); r.append(0.5 * max(0, m['palm_s'] - (sc['s_hi'] - 1)))
            m['fore_back_deg'] = float(np.degrees(np.arccos(np.clip(-fore @ np.array([-1, 0, 0.]), -1, 1)))); r.append(0.05 * max(0, m['fore_back_deg'] - 70))
        return (np.array(r), m) if full else np.array(r)
def seeds(M):
    sc = M.sc; out = []; e1, e2 = M.frame2(); hx, hy, hn = M.ax['x'], M.ax['y'], M.ax['n']; B = np.stack([hx, hy, hn], 1)
    def place(xw, nw, pos, q):
        xw = xw / np.linalg.norm(xw); nw = nw - (nw @ xw) * xw; nw /= np.linalg.norm(nw); W = np.stack([xw, np.cross(nw, xw), nw], 1)
        Bo = np.stack([hx, np.cross(hn, hx), hn], 1); R = W @ np.linalg.inv(Bo); U, _, Vt = np.linalg.svd(R); R = U @ Vt
        t = pos - M.scale * R @ M.palm0; return np.r_[Rot.from_matrix(R).as_rotvec(), t, q]
    if sc['hold'] == 'under':
        for th in (0, 30, 60, 90, -30, -60):
            xw = np.cos(np.radians(th)) * M.a + np.sin(np.radians(th)) * e2; pos = M.c + sc['s0'] * M.a + e1 * (M.r + 1.5)
            out.append(place(xw, -e1, pos, M.q0))
    else:
        sm = 0.5 * (sc['s_lo'] + sc['s_hi'])
        for d in sc.get('approach', [[-1, 0, 0], [0, 0, 1], [0, 0, -1]]):
            d = np.array(d, float); d -= (d @ M.a) * M.a; d /= np.linalg.norm(d)
            for sgn in (1, -1):
                xw = sgn * np.cross(M.a, d); pos = M.c + sm * M.a - d * (M.r + 1.2)
                out.append(place(xw, d, pos, np.clip(handmodel.q_fist() * 0.8, handmodel.QLO, handmodel.QHI)))
    return out
def ref_cuff():
    Y, T = C.md3_hand(os.path.join(C.FBXDIR, 'fbx_b1_L.md3'), 1); I = C.fbx_index('L'); Xf = np.zeros((len(I['dom']), 3)); Xf[I['src']] = Y
    Lc = json.load(open(os.path.join(LANE, 'landmarks_fbx.json')))['R']['cuff']; return Xf[Lc]
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('scenario'); ap.add_argument('out'); ap.add_argument('--nfev', type=int, default=200); ap.add_argument('--seeds', type=int, default=99)
    ap.add_argument('--x0'); ap.add_argument('--thr', type=float, default=0.25); ap.add_argument('--h', type=float, default=0.3)
    a = ap.parse_args(); sc = json.load(open(a.scenario)); os.makedirs(a.out, exist_ok=True); THR[0] = a.thr; GRID[0] = a.h; M = Model(sc); t0 = time.time()
    lo = np.r_[[-np.inf] * 6, handmodel.QLO]; hi = np.r_[[np.inf] * 6, handmodel.QHI]; best = None; log = []
    S0 = [np.array(json.load(open(a.x0))['x'])] if a.x0 else seeds(M)[:a.seeds]
    for k, x0 in enumerate(S0):
        x0[6:] = np.clip(x0[6:], handmodel.QLO + 1e-6, handmodel.QHI - 1e-6)
        s = least_squares(M.res, x0, bounds=(lo, hi), max_nfev=a.nfev, x_scale=np.r_[[0.05] * 3, [1] * 3, [0.1, 0.1, 5] * 4 + [0.1, 0.1, 5, 5] + [5, 5]])
        _, m = M.res(s.x, full=True); c = float(s.cost); log.append(dict(seed=k, cost=c, nfev=int(s.nfev), **m)); print('seed', k, 'cost %.3f' % c, json.dumps({kk: round(v, 2) for kk, v in m.items()}), flush=True)
        if best is None or c < best[0]: best = (c, s.x, m, k)
    c, x, m, k = best; X, J, R = M.X(x)
    rows, paths, _ = bake.bake([dict(name=sc['name'][:15], side='L', X=X, cuff_ref=ref_cuff())], os.path.join(a.out, 'fbx_r4_%s.md3' % sc['name']))
    r0 = rows[0]; Rw, tw = metrics.rigid(ref_cuff(), X[np.array(json.load(open(os.path.join(LANE, 'landmarks_fbx.json')))['R']['cuff'])])
    pc = X[M.reg['palm']].mean(0)
    o = dict(name=sc['name'], hold=sc['hold'], best_seed=k, cost=c, metrics=m, x=x.tolist(), q=x[6:24].tolist(), R=R.tolist(), t=x[3:6].tolist(), scale=M.scale,
             sup_hook=r0['hook'], sup_rot=r0['rot'], sup_point_m=(pc / 100).round(4).tolist(), bake_check_max_cm=r0['bake_check_max_cm'], md3=os.path.basename(paths['L']), frame=0,
             wrist_vs_RQFSB=dict(rot_deg=r0['wrist_rot_deg'], move_cm=r0['wrist_move_cm']), seeds=log, refined_from=a.x0, thr=a.thr, grid=a.h, minutes=round((time.time() - t0) / 60, 2), scenario=sc,
             X=X.round(4).tolist())
    json.dump(o, open(os.path.join(a.out, 'sup_%s.json' % sc['name']), 'w'), indent=1, default=float)
    print('BEST seed', k, 'cost %.3f' % c, json.dumps(m, default=float), 'hook', r0['hook'], 'rot', r0['rot'], 'bake_check', r0['bake_check_max_cm'], 'minutes', o['minutes'])
if __name__ == '__main__': main()
