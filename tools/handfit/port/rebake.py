"""rebake.py: the solved hand poses as DATA (tools/handfit/poses/<Class>.json), and the MD3 frames rebuilt from them.
  rebake.py export <Class>              fits/curl3_<Class>.json + fits/ported_<Class>.json -> poses/<Class>.json
  rebake.py bake <poses.json> <out>      the FBX hand (env RSQ_FBX, same skeleton) posed by the JSON's joint vectors -> <out>_R.md3
                                         frames 0 trigger, 1 squeeze, 2 the approved pistol check; prints the difference to the
                                         committed bake when `bake_md3` in the JSON exists
The pose JSON: `q_trigger` / `q_squeeze` = the full joint-parameter vector of fbx_fitter's hand model (solve.hand_X order: the r5
pistol pose with the solved fingers replaced), `solved_fingers` (those take the pose as solved; the rest keep the approved pistol
hand's per-vertex correction `delta`, exactly as curl3 did), the wrist placement on the gun (R, t: hand -> gun scene frame; `shift`
d), the gun move (MODELDEF Offset/ZOffset/Angle/Pitch/Roll), and the FBX source + take. The support hand of these guns is not an
FBX pose yet (Ermac's): `support` says which pose and hook the handtable row holds.
Needs RSQ_HANDS_TOOL = a full fitter checkout (lane data) and the FBX (fbx_fitter/handmodel.py FBX, or RSQ_FBX)."""
import sys, os, json, numpy as np
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
def export(g):
    C = json.load(open(os.path.join(HERE, 'fits', 'curl3_%s.json' % g))); P = json.load(open(os.path.join(HERE, 'fits', 'ported_%s.json' % g)))
    (ctx, x, to_g, Xf, delta), B = setup()
    q = np.array(C['q_MRP']); idx = len(q) == 12; sl = list(range(6 if idx else 9, 18))
    xt = x.copy(); xt[sl] = q; xs = xt.copy(); xs[6:9] = C['q_I_sqz']
    out = dict(cls=g, fbx=os.path.basename(handmodel.FBX), fbx_take='the FBX\'s single 1279-frame take: joint LIMITS only; the pose is the parameter vector below (bind pose + these rotations)',
               model='tools/handfit/fbx_fitter/handmodel.py + solve.hand_X (lane_c r5 parameterisation)', q_pistol_r5=x.tolist(), q_trigger=xt.tolist(), q_squeeze=xs.tolist(),
               solved_fingers='IMRP' if idx else 'MRP', squeeze_fingers='I', wrist_on_gun=dict(R=C['R'], t=C['t'], shift=C['shift']),
               gun_move=dict(zip(['Offset_x', 'Offset_y', 'ZOffset', 'AngleOffset', 'PitchOffset', 'RollOffset'], P['place'])),
               fit=dict(trigger=C['trigger'], squeeze=C['squeeze']), bake_md3='fits/bake/fbx_b4_%s_R.md3' % g,
               support=dict(Rifle='Ermac hand2 pose C under the M203 tube, moved with the gun (handtable row 18); NOT an FBX pose yet',
                            Revolver='Ermac cup (handtable row 17, unchanged: it cups the gun hand, which is pinned); NOT an FBX pose yet',
                            BrutalRevolver='Ermac cup (shared row 17); NOT an FBX pose yet').get(g, ''))
    os.makedirs(POSES, exist_ok=True); json.dump(out, open(os.path.join(POSES, '%s.json' % g), 'w'), indent=1); print('poses/%s.json' % g)
def rebuild(J):
    (ctx, x, to_g, Xf, delta), B = setup(); dom = ctx.H.dom
    fm = lambda fs: np.array([any(str(b).startswith(B[f]) for f in fs) for b in dom])
    R = np.array(J['wrist_on_gun']['R']); t = np.array(J['wrist_on_gun']['t']); d = np.array(J['wrist_on_gun']['shift'])
    def X(q, fingers):
        m = fm(fingers); return (to_g(solve.hand_X(ctx, np.array(q))[0]) + np.where(m[:, None], 0, delta)) @ R.T + t + d
    return X(J['q_trigger'], J['solved_fingers']), X(J['q_squeeze'], J['solved_fingers'] + J['squeeze_fingers']), ctx, x, Xf
def rebake(path, out):
    J = json.load(open(path)); Xt, Xs, ctx, x, Xf = rebuild(J); Rg, tg = solve.gun_T(ctx, x); to_c = lambda X: solve.gmove(ctx, Rg, tg, X)
    ent = [dict(name=J['cls'] + '_trg', side='R', X=to_c(Xt)), dict(name=J['cls'] + '_sqz', side='R', X=to_c(Xs)), dict(name='PISTOL_chk', side='R', X=to_c(Xf))]
    for e in ent: e['cuff_ref'] = e['X'][ctx.cuff]
    rows, paths, _ = bake.bake(ent, out + '.md3'); print(paths['R'])
    ref = os.path.join(HERE, J['bake_md3'])
    if os.path.exists(ref):
        a = scene.md3_full(paths['R'])[0]['xyz']; b = scene.md3_full(ref)[0]['xyz']; print('vs committed bake: max %.4f md3 units over %d frames' % (np.abs(a - b).max(), len(a)))
if __name__ == '__main__':
    if sys.argv[1] == 'export':
        for g in sys.argv[2:]: export(g)
    else: rebake(sys.argv[2], sys.argv[3])
