"""Batch 2: gunmoves.zs fire-frame rows (turn, move) and Pivot for a moved gun, computed exactly as the Depot generator
rsq_gunmoves_gen.py does (trimmed rigid fit of each fire frame against the ready frame, controller frame, D / O_H
conventions), but with the gun drawn through the full QZD 17.3 MODELDEF chain (gunmove.chain: Offset, ZOffset and the
Angle/Pitch/RollOffsets).  Self-check: the original placement must give the shipped rows; the pistol's r5 placement must
give b1's refitted rows 15-17."""
import sys, numpy as np
import os as _fl_os; FITTER_LIB = _fl_os.environ.get('RS_FITTER_LIB', _fl_os.path.join(_fl_os.path.dirname(_fl_os.path.abspath(__file__)), '..', 'fitter_lib'))	# the batch 1-4 fitter modules (were /home/claude/lane_b_b*run/tools)
sys.path.insert(0, '/home/claude/lane_c/hands_tool'); sys.path.insert(0, FITTER_LIB)
sys.path.insert(0, '/home/claude/depot_import/rs_questhands/tools/v9kit/team/hands_work')
import gunmove, scene
import kick_measure as km, math, types
# rsq_gunmoves_gen.py's constants and angles() (copied verbatim; the module itself needs decsim, not in this tree)
gg = types.SimpleNamespace(D=np.diag([-1.0, 1.0, 1.0]), O_H=np.array([0.0, -10.0, -24.0]),
    angles=lambda R: np.array([math.degrees(math.atan2(R[0, 2], R[2, 2])), math.degrees(math.asin(max(-1, min(1, -R[1, 2])))), math.degrees(math.atan2(R[1, 0], R[1, 1]))]))
P = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0.]]); SH = np.array([0, 5, 30.])
def frames(path, off, ao, fr):
    S = scene.md3_full(path); raw = np.concatenate([s['xyz'][fr] for s in S])
    X = gunmove.chain(list(off), tuple(ao))(raw)		# FLU cm
    return X @ P - SH						# -> km's controller frame (x right, y up, z back)
def rows(path, off, ao, ready, fire):
    a = frames(path, off, ao, ready); out = []
    for f in fire:
        b = frames(path, off, ao, f); Rw, tw, err = km.rigid(a, b)
        Rk = gg.D @ Rw @ gg.D; bk = Rk @ gg.O_H - gg.O_H + gg.D @ tw; u = Rk.T @ bk
        out.append(np.r_[gg.angles(Rk), u])
    return np.array(out)
def pivot(off, zoff):
    return gg.D @ np.array([off[0], zoff, off[1]]) - gg.O_H
if __name__ == '__main__':
    np.set_printoptions(precision=2, suppress=True)
    SRC = '/home/claude/lane_b_b2/src/models/bd/'
    print('pistol original (shipped 1.99 rows 15-17 were 0 5.00 0 0 -0.15 0.86 / 0 3.79 0 0 -0.13 0.65 / 0 1.21 0 0 -0.05 0.21):')
    print(rows(SRC + 'BrutalPistol/BrutalPistol.md3', [0, 0, -5], (0, 0, 0), 3, (4, 5, 6)))
    m = gunmove.MOVES['BrutalPistol']
    print('pistol r5 (b1 rows 0.97 4.89 0.43 0.15 -0.94 0.47 / 0.73 3.70 0.32 0.11 -0.73 0.35 / 0.23 1.18 0.10 0.04 -0.24 0.11):')
    print(rows(SRC + 'BrutalPistol/BrutalPistol.md3', m['off'], m['ao'], 3, (4, 5, 6)), 'pivot', pivot([0.820, -8.333], -1.408))
    print('SMG original (shipped rows 18-20: 0 0 0 0 0 0.51 / 0 1.16 0 0 -0.03 1.00 / 0 0.58 0 0 -0.02 0.50):')
    print(rows(SRC + 'BrutalSMG/BrutalSMG.md3', [0, 0, -5], (0, 0, 0), 3, (4, 5, 6)))
    off = [float(v) for v in sys.argv[1:4]]; ao = tuple(float(v) for v in sys.argv[4:7])
    print('SMG moved', off, ao); print(rows(SRC + 'BrutalSMG/BrutalSMG.md3', off, ao, 3, (4, 5, 6)), 'pivot', pivot(off[:2], off[2]))
