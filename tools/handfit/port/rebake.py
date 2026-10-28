"""rebake.py: the solved hand poses as DATA (tools/handfit/poses/<Class>.json), and the MD3 frames rebuilt from them.
  rebake.py export <Class>              fits/curl3_<Class>.json + fits/ported_<Class>.json -> poses/<Class>.json
  rebake.py place <Class>...            the placement numbers (MODELDEF Offset/ZOffset/Angle/Pitch/Roll, gunmoves Pivot + fire rows)
                                         regenerated from poses/<Class>.json with port_gun's functions, compared to src/ and fits/ported_<Class>.json
  rebake.py check [<Class>...]           bake + place for every poses/*.json (bakes go to a temp dir)
  rebake.py bake <poses.json> <out>      the FBX hand (env RSQ_FBX, same skeleton) posed by the JSON's joint vectors -> <out>_R.md3
                                         frames 0 trigger, 1 squeeze, 2 the approved pistol check; prints the difference (bytes, max
                                         md3 units / cm) to the committed bake (`bake_md3`) and the shipped md3 (`baked` / `baked_md3`)
Three pose JSON forms are read: batch 4/5 (q_trigger / q_squeeze, export below), heavies / fit farm (poses.trigger.pose_vector,
heavies/poses_hv.py) and shotguns (joints.trigger / joints.squeeze, shotguns/poses_sg.py).
The pose JSON: `q_trigger` / `q_squeeze` = the full joint-parameter vector of fbx_fitter's hand model (solve.hand_X order: the r5
pistol pose with the solved fingers replaced), `solved_fingers` (those take the pose as solved; the rest keep the approved pistol
hand's per-vertex correction `delta`, exactly as curl3 did), the wrist placement on the gun (R, t: hand -> gun scene frame; `shift`
d), the gun move (MODELDEF Offset/ZOffset/Angle/Pitch/Roll), and the FBX source + take. `support` (batch 5): the FBX support pose
(fbx_b1_L.md3 frame) and the hook / rot / point the handtable row holds, with its measurements.
Needs RSQ_HANDS_TOOL = a full fitter checkout (lane data) and the FBX (fbx_fitter/handmodel.py FBX, or RSQ_FBX)."""
import sys, os, re, json, glob, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..')); POSES = os.path.join(HERE, '..', 'poses')
sys.path.insert(0, os.path.join(HERE, '..', 'batch2')); sys.path.insert(0, os.environ.get('RSQ_HANDS_TOOL', os.path.join(HERE, '..', 'fbx_fitter')))
import handmodel
if os.environ.get('RSQ_FBX'): handmodel.FBX = os.environ['RSQ_FBX']
import solve, bake, scene, revindex
BONES_PREFIX = None
def setup():
    from rigid3 import BONES	# finger -> bone prefix (batch 3)
    return revindex.setup(), BONES
sys.path.insert(0, os.path.join(HERE, '..', 'batch3'))
def bake_of(g):	# the newest committed bake of this gun's hand (batch 5, then batch 4)
    for b in ('b5', 'b4', 'r9'):	# r9: the Sniper (sniper_fit.py, the Rifle's hold on the Ruger)
        if os.path.exists(os.path.join(HERE, 'fits', 'bake', 'fbx_%s_%s_R.md3' % (b, g))): return 'fits/bake/fbx_%s_%s_R.md3' % (b, g)
    return 'fits/bake/fbx_b4_%s_R.md3' % g
SUP_FILE = dict(Rifle='Rifle', Revolver='Revolver', BrutalRevolver='Revolver')	# BrutalRevolver shares the Revolver's row 17 (one cup clears both)
def support_of(g):
    """batch 5: the FBX support hand as data (support_gun.py's solve: fbx_b1_L.md3 frame, the handtable hook / rot / point, measurements)."""
    p = [q for q in (os.path.join(HERE, 'fits', d, 'sup_%s.json' % SUP_FILE.get(g, g)) for d in ('b5', 'r9', 'r10', 'r11')) if os.path.exists(q)]	# r9-r11: support_gun.py's json, same form
    if not p: return 'Ermac support pose (no FBX support solved)'
    p = p[0]
    S = json.load(open(p)); S['md3'] = 'models/rsq/fbx/fbx_b1_L.md3'; S['label'] = 'FbxSupF (RQFS B)' if S['pose'] == 'B' else 'FbxSupP (RQFS A)'
    S['how'] = 'support_gun.py %s %s, applied with port_gun.py --support (handtable row %s)' % (S['cls'], S['pose'], {'Rifle': 18, 'Sniper': 22}.get(S['cls'], 17)); return S
def export(g):
    C = json.load(open(os.path.join(HERE, 'fits', 'curl3_%s.json' % g))); P = json.load(open(os.path.join(HERE, 'fits', 'ported_%s.json' % g)))
    (ctx, x, to_g, Xf, delta), B = setup()
    q = np.array(C['q_MRP']); idx = len(q) == 12; sl = list(range(6 if idx else 9, 18))
    xt = x.copy(); xt[sl] = q; xs = xt.copy(); xs[6:9] = C['q_I_sqz']
    out = dict(cls=g, fbx=os.path.basename(handmodel.FBX), fbx_take='the FBX\'s single 1279-frame take: joint LIMITS only; the pose is the parameter vector below (bind pose + these rotations)',
               model='tools/handfit/fbx_fitter/handmodel.py + solve.hand_X (lane_c r5 parameterisation)', q_pistol_r5=x.tolist(), q_trigger=xt.tolist(), q_squeeze=xs.tolist(),
               solved_fingers='IMRP' if idx else 'MRP', squeeze_fingers='I', wrist_on_gun=dict(R=C['R'], t=C['t'], shift=C['shift']),
               gun_move=dict(zip(['Offset_x', 'Offset_y', 'ZOffset', 'AngleOffset', 'PitchOffset', 'RollOffset'], P['place'])),
               fit=dict(trigger=C['trigger'], squeeze=C['squeeze']), bake_md3=bake_of(g), support=support_of(g))
    os.makedirs(POSES, exist_ok=True); json.dump(out, open(os.path.join(POSES, '%s.json' % g), 'w'), indent=1); print('poses/%s.json' % g)
def rebuild(J):
    (ctx, x, to_g, Xf, delta), B = setup(); dom = ctx.H.dom
    fm = lambda fs: np.array([any(str(b).startswith(B[f]) for f in fs) for b in dom])
    R = np.array(J['wrist_on_gun']['R']); t = np.array(J['wrist_on_gun']['t']); d = np.array(J['wrist_on_gun']['shift'])
    def X(q, fingers):
        m = fm(fingers); return (to_g(solve.hand_X(ctx, np.array(q))[0]) + np.where(m[:, None], 0, delta)) @ R.T + t + d
    return X(J['q_trigger'], J['solved_fingers']), X(J['q_squeeze'], J['solved_fingers'] + J['squeeze_fingers']), ctx, x, Xf
def rebuild_hv(J):
    """r11: the heavies / fit-farm pose JSON (heavies/poses_hv.py: poses.trigger / poses.squeeze pose_vector + solved_fingers, wrist R, t,
    shift_cm), rebuilt exactly as the farm's curl (fit_hv.curl: solved fingers carry no per-vertex delta; X @ R^T + t + shift)."""
    (ctx, x, to_g, Xf, delta), B = setup(); dom = ctx.H.dom
    fm = lambda fs: np.array([any(str(b).startswith(B[f]) for f in fs) for b in dom])
    W = J['wrist']; R = np.array(W['R']); t = np.array(W['t']); d = np.array(W['shift_cm'])
    def X(P):
        m = fm(P.get('solved_fingers', 'IMRP')); return (to_g(solve.hand_X(ctx, np.array(P['pose_vector']))[0]) + np.where(m[:, None], 0, delta)) @ R.T + t + d
    return X(J['poses']['trigger']), X(J['poses']['squeeze']), ctx, x, Xf
def rebuild_sg(J):
    """the shotguns lane's pose JSON (shotguns/poses_sg.py: joints.trigger / joints.squeeze full vectors, wrist R, t, gun_shift_cm), rebuilt
    exactly as fit_sg.curl: the solved fingers carry no per-vertex delta (IMRP when the index was re-solved, i.e. joints.trigger[6:9] differs
    from joints.pistol[6:9], else MRP; the squeeze adds I), X @ R^T + t + gun_shift."""
    (ctx, x, to_g, Xf, delta), B = setup(); dom = ctx.H.dom
    fm = lambda fs: np.array([any(str(b).startswith(B[f]) for f in fs) for b in dom])
    W = J['wrist']; R = np.array(W['R']); t = np.array(W['t']); d = np.array(W['gun_shift_cm']); j = J['joints']
    sf = J.get('solved_fingers', 'IMRP' if list(j['trigger'][6:9]) != list(j['pistol'][6:9]) else 'MRP')
    def X(q, fs): m = fm(fs); return (to_g(solve.hand_X(ctx, np.array(q))[0]) + np.where(m[:, None], 0, delta)) @ R.T + t + d
    return X(j['trigger'], sf), X(j['squeeze'], sf + 'I'), ctx, x, Xf
SHIPPED = os.path.join(REPO, 'src', 'models', 'rsq', 'fbx')
def refs(J):
    """the md3s this pose must reproduce: the committed bake (fits/, batch 4/5) and the shipped one (src/models/rsq/fbx)."""
    out = []
    if J.get('bake_md3'): out.append(('committed bake', os.path.join(HERE, J['bake_md3'])))
    name = J.get('baked') or J.get('baked_md3') or (os.path.basename(J['bake_md3']) if J.get('bake_md3') else None)
    if name: out.append(('shipped', os.path.join(SHIPPED, name)))
    return out
MD3_CM = 1.02	# 1 md3 unit drawn = 1.02 cm (hudrender.to_local ws, the hook chain is a rotation; hook.PL scale +-1)
def compare(new, ref):
    a = scene.md3_full(new)[0]['xyz']; b = scene.md3_full(ref)[0]['xyz']; n = min(len(a), len(b))
    same = open(new, 'rb').read() == open(ref, 'rb').read(); dv = float(np.abs(a[:n] - b[:n]).max()) if a.shape[1] == b.shape[1] else float('nan')
    return dict(bytes_identical=same, frames_new=len(a), frames_ref=len(b), max_md3=dv, max_cm=dv * MD3_CM)
def rebake(path, out):
    J = json.load(open(path)); Xt, Xs, ctx, x, Xf = (rebuild_hv if 'poses' in J else rebuild_sg if 'joints' in J else rebuild)(J); Rg, tg = solve.gun_T(ctx, x); to_c = lambda X: solve.gmove(ctx, Rg, tg, X)
    ent = [dict(name=J['cls'] + '_trg', side='R', X=to_c(Xt)), dict(name=J['cls'] + '_sqz', side='R', X=to_c(Xs)), dict(name='PISTOL_chk', side='R', X=to_c(Xf))]
    for e in ent: e['cuff_ref'] = e['X'][ctx.cuff]
    rows, paths, _ = bake.bake(ent, out + '.md3'); print(paths['R'])
    res = {}
    for what, ref in refs(J):
        if not os.path.exists(ref): print('vs %s: %s missing' % (what, ref)); continue
        c = compare(paths['R'], ref); res[what] = c
        print('vs %s %s: %s, max %.4f md3 units (%.4f cm) over %d of %d frames' % (what, os.path.relpath(ref, REPO), 'bytes identical' if c['bytes_identical'] else 'bytes differ',
              c['max_md3'], c['max_cm'], min(c['frames_new'], c['frames_ref']), c['frames_ref']))
    return res
def _port():
    sys.path.insert(0, HERE); import port_gun as pg
    pg.SRC = os.environ.get('RSQ_SRC', os.path.join(REPO, 'src'))
    for d, m in (('shotguns', 'port_sg'), ('heavies', 'port_hv')):	# hv last: its SSG entry is the one the r11 port used
        sys.path.insert(0, os.path.join(HERE, '..', d)); __import__(m)
    return pg
def place_of(J):
    g = J['gun_move']
    if 'place' in g: return np.array(g['place'])
    if 'modeldef_place' in g: return np.array(g['modeldef_place'])
    return np.array([g[k] for k in ['Offset_x', 'Offset_y', 'ZOffset', 'AngleOffset', 'PitchOffset', 'RollOffset']])
def place(cls):
    """the placement numbers regenerated from poses/<Class>.json with the port tools' own functions (port_gun.rigid_move / pivot /
    fire_rows, port_gun.modeldef's %.3f format; registries of port_gun + shotguns/port_sg + heavies/port_hv), compared to src/ MODELDEF and
    gunmoves.zs and to fits/ported_<Class>.json."""
    pg = _port()
    J = json.load(open(os.path.join(POSES, cls + '.json'))); p = place_of(J); out = dict(cls=cls)
    P = json.load(open(os.path.join(HERE, 'fits', 'ported_%s.json' % cls)))
    out['pose_vs_ported_place'] = float(np.abs(np.array(P['place']) - p).max())
    G = dict(pg.GUNS[cls], cls=cls); G['md3'] = os.path.join(pg.SRC, G['md3'])
    R, t = pg.rigid_move(G, p); out['Rt_vs_ported'] = float(max(np.abs(R - np.array(P['R'])).max(), np.abs(t - np.array(P['t'])).max()))
    if 'R' in J['gun_move']: out['Rt_vs_pose'] = float(max(np.abs(R - np.array(J['gun_move']['R'])).max(), np.abs(t - np.array(J['gun_move']['t'])).max()))
    # MODELDEF: every block drawing this gun's meshes that carries a moved placement (AngleOffset present + the port's tag)
    exp = ['%.3f' % v for v in p]; ok = bad = 0; badl = []
    names = G['names'] + G.get('names_extra', [])
    for f in sorted(glob.glob(os.path.join(pg.SRC, 'MODELDEF*'))):
        tx = open(f, encoding='latin1').read()
        for m in pg.BLK.finditer(tx):
            b = m.group(0)
            if not any('"%s"' % n in b for n in names) or 'gun to the FBX hand' not in b: continue
            o = re.search(r'(?m)^\s*Offset\s+(\S+)\s+(\S+)', b); z = re.search(r'(?m)^\s*ZOffset\s+(\S+)', b)
            a = [re.search(r'(?m)^\s*%sOffset\s+(\S+)' % k, b) for k in ('Angle', 'Pitch', 'Roll')]
            got = [o.group(1), o.group(2), z.group(1)] + [x.group(1) if x else None for x in a]
            if got == exp: ok += 1
            else: bad += 1; badl.append('%s %s %s' % (os.path.basename(f), m.group(1), got))
    nmoved = sum(int(s.rsplit('x', 1)[1]) for s in P['moved'] if s.startswith('MODELDEF '))
    out.update(modeldef_match=ok, modeldef_mismatch=bad, modeldef_ported_count=nmoved, mismatches=badl[:4])
    # gunmoves: Pivot row + fire rows
    if G.get('row') is not None and G.get('bdblock'):
        tx = open(os.path.join(pg.SRC, 'zscript/rsq/gunmoves.zs'), encoding='latin1').read(); row = G['row']
        i0 = tx.index('clearscope static Vector3 Pivot'); i1 = tx.index('};', i0); vals = [float(s.strip()) for s in tx[i0:i1].split('{ ', 1)[1].split(',')]
        if 3 * row + 2 >= len(vals): out['gunmoves'] = 'row %d not in gunmoves.zs (port: nothing moved)' % row; return out
        new = pg.pivot(p[:2], p[2]); out['pivot_diff'] = float(np.abs(np.round(new, 3) - np.array(vals[3 * row:3 * row + 3])).max())
        spr = re.findall(r'"([^"]+)"', re.search(r'static const String spr\[\] = \{([^}]*)\}', tx).group(1))
        key = [int(v) for v in re.search(r'static const int key\[\] = \{([^}]*)\}', tx).group(1).split(',')]
        frows = {}
        for k in range(len(spr)):
            if key[2 * k] == row and key[2 * k + 1] not in frows: frows[key[2 * k + 1]] = spr[k]
        f, c = G['bdblock']; b = [m.group(0) for m in pg.BLK.finditer(open(os.path.join(pg.SRC, f), encoding='latin1').read()) if m.group(1) == c and '"%s"' % G['names'][0] in m.group(0)][0]
        fi = {(a, cc): int(n) for a, cc, n in re.findall(r'FrameIndex\s+(\S+)\s+(\S)\s+\d+\s+(\d+)', b)}
        order = sorted(frows); frames = [fi[(frows[r][:4], frows[r][4])] for r in order]
        r1 = pg.fire_rows(G, p[:3], p[3:], frames) if order else []
        lines = tx[tx.index('static Vector3, Vector3 Frame('):].split('\n'); rx = re.compile(r'^(\s*)(-?\d+\.\d+(?:, -?\d+\.\d+){5}),?(.*)$'); idx = [n for n, l in enumerate(lines) if rx.match(l)]
        dmax = 0.0; txt_ok = 0
        for r, v in zip(order, r1):
            shipped = np.array([float(x) for x in rx.match(lines[idx[r]]).group(2).split(',')]); regen = np.array([float('%.2f' % pg.z0(x, 0.005)) for x in v])
            dmax = max(dmax, float(np.abs(shipped - regen).max())); txt_ok += rx.match(lines[idx[r]]).group(2) == ', '.join('%.2f' % pg.z0(x, 0.005) for x in v)
        out.update(fire_rows=len(order), fire_rows_text_identical=txt_ok, fire_rows_max_diff=dmax)
    else: out['gunmoves'] = 'no handtable row / bd block (port_gun moves no gunmoves rows for this gun)'
    return out
def check(classes):
    """bake every pose (or the named ones) to a temp dir, compare to the committed + shipped md3, and regenerate its placement."""
    import tempfile, glob
    classes = classes or sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(POSES, '*.json'))); tmp = tempfile.mkdtemp(prefix='rebake_')
    for g in classes:
        print('== %s' % g); r = rebake(os.path.join(POSES, g + '.json'), os.path.join(tmp, g)); print('placement:', json.dumps(place(g)))
if __name__ == '__main__':
    if sys.argv[1] == 'export':
        for g in sys.argv[2:]: export(g)
    elif sys.argv[1] == 'place':
        for g in sys.argv[2:]: print(json.dumps(place(g)))
    elif sys.argv[1] == 'check': check(sys.argv[2:])
    else: rebake(sys.argv[2], sys.argv[3])
