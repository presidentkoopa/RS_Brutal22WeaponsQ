"""Batch 2: the MODELDEF placement that puts a gun at  M_pistol(p + d)  (the pistol's r5 move, after a translation d
in the original frame), solved over the QZD 17.3 MODELDEF chain (gunmove.chain). Prints the offsets and the residual."""
import sys, json, numpy as np
import os as _fl_os; FITTER_LIB = _fl_os.environ.get('RS_FITTER_LIB', _fl_os.path.join(_fl_os.path.dirname(_fl_os.path.abspath(__file__)), '..', 'fitter_lib'))	# the batch 1-4 fitter modules (were /home/claude/lane_b_b*run/tools)
sys.path.insert(0, '/home/claude/lane_c/hands_tool'); sys.path.insert(0, '/home/claude/lane_b1run_tools'); sys.path.insert(0, FITTER_LIB)
from scipy.optimize import least_squares
import gunmove, scene
def place(it, d):
    R, t = gunmove.move('BrutalPistol')
    V0 = np.concatenate([v for _, v in scene.item_verts(it)])
    # frame check: the chain with the original offsets reproduces the scene frame
    import gunplace, gunview
    raw = np.concatenate([s['xyz'][it['frame']] for s in scene.md3_full(it['path'])])
    ch0 = gunmove.chain(list(it['off']), (0, 0, 0))(raw)
    chk = float(np.abs(ch0 - V0).max())
    target = V0 @ R.T + (R @ np.asarray(d) + t)
    def res(p): return (gunmove.chain(list(p[:3]), tuple(p[3:]))(raw) - target).ravel()
    m = gunmove.MOVES['BrutalPistol']; p0 = np.r_[m['off'], m['ao']]
    s = least_squares(res, p0)
    return s.x, float(np.abs(res(s.x)).max()), chk, R, R @ np.asarray(d) + t
if __name__ == '__main__':
    J = json.load(open(sys.argv[1]))
    sys.path.insert(0, FITTER_LIB); import revlm
    for g, o in J.items():
        p, r, chk, R, tt = place(revlm.GUNS[g]['it'], o['shift'])
        print(g, 'off %.3f %.3f  zoff %.3f  angle %.3f pitch %.3f roll %.3f' % tuple(p), 'residual %.4f cm' % r, 'frame check %.4f' % chk)
        print('  R', R.round(6).tolist(), 't', tt.round(4).tolist())
