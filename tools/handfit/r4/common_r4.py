"""Hands round 4: shared helpers. Every frame is the controller frame, cm, F forward / L left / U up (gunview.to_fl).
  pinned_hand(): the approved FBX pistol hand (fbx_b1_R.md3 frame 0, hook 0) = where the drawn wrist sits on the controller
  gun(path, frame, scale, off): a BD22 mesh at its shipped MODELDEF placement (scene.merged)
  fbx_index(): md3 vertex k <-> FBX vertex src[k] (md3write.split_uv), bones per FBX vertex, landmarks"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
def _tool():
    if os.environ.get('RSQ_HANDS_TOOL'): return os.environ['RSQ_HANDS_TOOL']
    d = HERE	# on the fit farm the r4 tree sits under work/fitfarm/: find farmpaths.py upward
    for _ in range(6):
        d = os.path.dirname(d)
        if os.path.exists(os.path.join(d, 'farmpaths.py')): sys.path.insert(0, d); break
    try:	# on the fit farm: the packed fitter under farmpaths.HOME
        import farmpaths; return farmpaths.HOME + '/lane_c/hands_tool'
    except ImportError: return '/home/claude/lane_c/hands_tool'
TOOL = _tool(); sys.path.insert(0, TOOL)
import scene, hudrender, hook, md3write, handmodel, exactpen
SRC = os.environ.get('RSQ_SRC', os.path.join(REPO, 'src')); FBXDIR = os.path.join(SRC, 'models/rsq/fbx')
LANE = os.path.dirname(TOOL)
def md3_hand(path, frame):
    s = scene.md3_full(path)[0]; return 100 * (hudrender.to_local(s['xyz'][frame], dict(hook=[0, 0, 0], rot=[0, 0, 0], **hook.PL)) @ hook.P.T), s['tris']
def pinned_hand(): return md3_hand(os.path.join(FBXDIR, 'fbx_b1_R.md3'), 0)
_IDX = {}
def fbx_index(side='R'):
    if side not in _IDX:
        H = handmodel.FbxHand(side); T, src, uv = md3write.split_uv(H.h.F, H.h.Fc, H.h.uv_corner)
        L = json.load(open(os.path.join(LANE, 'landmarks_fbx.json')))[side]
        _IDX[side] = dict(H=H, T=T, src=src, L=L, dom=np.asarray([str(b) for b in H.dom]))
    return _IDX[side]
def md3_sel(fbx_ids, side='R'):
    """md3 vertex indices whose FBX source vertex is in fbx_ids"""
    return np.where(np.isin(fbx_index(side)['src'], np.asarray(fbx_ids)))[0]
def gun(path, frame=0, scale=(-1, 1, 1), off=(0, 0, -5)):
    it = dict(path=os.path.join(SRC, 'models/bd', path), frame=frame, scale=list(scale), off=list(off)); F, V = scene.merged(it); return np.asarray(F), V, it
def rot_a_to_b(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = float(a @ b)
    if np.linalg.norm(v) < 1e-12: return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K * (1 / (1 + c))
