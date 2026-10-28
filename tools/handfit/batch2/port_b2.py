"""Batch 2 (lane B hands lane): BrutalSMG gets the pistol's approved FBX gun hand (lane_c r5 trigger pose, only the index
re-solved to this trigger: revindex.py) and the existing FBX palm-under support pose (RQFS B) under its forend.
Every edit asserts the exact text it replaces.  Numbers: revindex_BrutalSMG.json (index), move_b2.py (placement),
bake_b2.json (frames + support row), follow_b2.py (gunmoves rows, self-checked against shipped and b1 rows)."""
import os, re, sys, json, shutil, numpy as np
import os as _fl_os; FITTER_LIB = _fl_os.environ.get('RS_FITTER_LIB', _fl_os.path.join(_fl_os.path.dirname(_fl_os.path.abspath(__file__)), '..', 'fitter_lib'))	# the batch 1-4 fitter modules (were /home/claude/lane_b_b*run/tools)
sys.path.insert(0, FITTER_LIB); sys.path.insert(0, '/home/claude/lane_c/hands_tool')
import gunmove
SRC = '/home/claude/lane_b_b2/src'
RUN = '/home/claude/lane_b_b2run'
def rd(p): return open(os.path.join(SRC, p), encoding='latin1').read()
def wr(p, t): open(os.path.join(SRC, p), 'w', encoding='latin1').write(t)
def sub1(t, a, b, what):
    n = t.count(a); assert n == 1, '%s: %d matches' % (what, n); return t.replace(a, b)
J = json.load(open(RUN + '/revindex_BrutalSMG.json'))['BrutalSMG']; B = json.load(open(RUN + '/bake/bake_b2.json'))
OFF = (0.908, -4.560, -3.413); AO = (3.854, 3.363, 10.974)		# move_b2.py: residual 0.0000 cm
Rm, tm = gunmove.move('BrutalPistol'); d = np.array(J['shift']); R = Rm; t = Rm @ d + tm	# SMG point p -> R p + t (controller F L U cm)
# ---- 1. hand mesh (frames 0 SMG trigger, 1 SMG squeeze; frame 2 = the pistol re-bake check, identical to fbx_b1_R frame 0, unused)
shutil.copyfile(RUN + '/bake/fbx_b2_R.md3', SRC + '/models/rsq/fbx/fbx_b2_R.md3')
# ---- 2. gun MODELDEF placement: every block drawing BrutalSMG.md3 on the gun controller (not RSQ_Hands = off hand, not RQBW = dropped)
PL = 'Offset %.3f %.3f 0.0\n{i}ZOffset %.3f\n{i}AngleOffset %.3f\n{i}PitchOffset %.3f\n{i}RollOffset %.3f\t// batch 2 (lane B): gun to the FBX pistol hand' % (OFF[0], OFF[1], OFF[2], AO[0], AO[1], AO[2])
BLOCKS = [('MODELDEF.bd.txt', 'BrutalSMG', 'VSMG'), ('MODELDEF.purist', 'PuristSMG', 'VSMG'), ('MODELDEF.purist', 'PuristSMG', 'RQBM'),
          ('MODELDEF.rsqoff', 'RSQ_Off_BrutalSMG', 'VSMG'), ('MODELDEF.rsqoff', 'RSQ_Off_BrutalSMG', 'RQBM'),
          ('MODELDEF.rsr', 'BrutalSMG', 'RQBM'), ('MODELDEF.rsr', 'RSR_GunParts', 'RQBP')]
EXPECT = {('MODELDEF.bd.txt', 'VSMG'): 1, ('MODELDEF.purist', 'VSMG'): 1, ('MODELDEF.purist', 'RQBM'): 2, ('MODELDEF.rsqoff', 'VSMG'): 1,
          ('MODELDEF.rsqoff', 'RQBM'): 3, ('MODELDEF.rsr', 'RQBM'): 3, ('MODELDEF.rsr', 'RQBP'): 2}
blk = re.compile(r'(?m)^Model[ \t]+(\S+)[ \t]*\n\{.*?\n\}', re.S); count = {}
for f in sorted(set(b[0] for b in BLOCKS)):
    tx = rd(f); out = []; last = 0
    for m in blk.finditer(tx):
        body = m.group(0); cls = m.group(1); hit = None
        for (ff, c, spr) in BLOCKS:
            if ff == f and c == cls and '"BrutalSMG.md3"' in body and re.search(r'FrameIndex\s+%s\s' % spr, body): hit = spr
        if hit:
            mm = re.search(r'(?m)^([ \t]*)Offset[ \t]+0\.0+[ \t]+0\.0+[ \t]+0\.0[^\n]*\n', body); assert mm, (f, cls)
            z = re.search(r'(?m)^[ \t]*ZOffset[ \t]+-5(\.0+)?[ \t]*\n', body); assert z, (f, cls)
            assert 'AngleOffset' not in body and 'RollOffset' not in body, (f, cls)
            nb = body[:z.start()] + body[z.end():]; ind = mm.group(1)
            body = nb.replace(mm.group(0), ind + PL.format(i=ind) + '\n', 1); count[(f, hit)] = count.get((f, hit), 0) + 1
        out.append(tx[last:m.start()]); out.append(body); last = m.end()
    out.append(tx[last:]); wr(f, ''.join(out))
assert count == EXPECT, count
# ---- 3. hand blocks: RQFH (new sprite, free in the pack, BD22 and BD_VoxelPack): A SMG trigger, B SMG squeeze
FR = '\tFrameIndex RQFH A 0 0\t// BrutalSMG, finger on the trigger\n\tFrameIndex RQFH B 0 1\t// BrutalSMG, squeezed\n'
def hblock(cls): return 'Model %s\n{\n\tPath "models/rsq/fbx"\n\tModel 0 "fbx_b2_R.md3"\n\tSkin 0 "fbx_hand.png"\n\tScale -1.0 1.0 1.0\n\tOffset 0.0 -24.0 -10.0\n%s}\n' % (cls, FR)
H = '\n// batch 2 (lane B): BrutalSMG (row 5) holds the pistol\'s FBX gun hand, index re-solved to its trigger (frames baked in place, hook 0)\n'
wr('MODELDEF.rsq', rd('MODELDEF.rsq').rstrip('\n') + '\n' + H + hblock('RSQ_GunSide') + hblock('RSQ_Hands'))
for f, cls in (('MODELDEF.rsqdual', 'BrutalSMG'), ('MODELDEF.rsqoff', 'RSQ_Off_BrutalSMG'), ('MODELDEF.purist', 'PuristSMG')):
    wr(f, rd(f).rstrip('\n') + '\n' + H.replace('(row 5)', '(row 5), dual wield') + hblock(cls))
# ---- 4. hands.zs / dualhands.zs (separate blocks after b1's)
tx = rd('zscript/rsq/hands.zs')
tx = sub1(tx, '\tFbxSupF: RQFS B -1; Stop;\n', '\tFbxSupF: RQFS B -1; Stop;\n\t// batch 2: BrutalSMG (row 5), the pistol\'s FBX hand with the index on the SMG trigger\n\tFbxTrgS: RQFH A -1; Stop;\n\tFbxSqzS: RQFH B -1; Stop;\n', 'states')
A = '\t\tinvoker.SetLayer(p, RSQ_Layers.GUNHAND, gs, own != "" ? own : i > 0 && g != "" ? gl : "Hidden");\n'
tx = sub1(tx, A, '''		if (i == 5)	// batch 2: BrutalSMG squeezes on its FIRE frames (BD22 SMG.dec Fire: SMGF / 2MGF A-C, zoomed SMGZ G-I), trigger otherwise
		{
			bool ssq = false;
			let sgp = p.FindPSprite(PSP_WEAPON);
			if (sgp && sgp.CurState)
			{
				int sf = sgp.Frame;
				ssq = sgp.CurState.bFullbright || ((sgp.Sprite == Actor.GetSpriteIndex('SMGF') || sgp.Sprite == Actor.GetSpriteIndex('2MGF')) && sf <= 2) || (sgp.Sprite == Actor.GetSpriteIndex('SMGZ') && sf >= 6 && sf <= 8);
			}
			gl = ssq ? "FbxSqzS" : "FbxTrgS";
		}
''' + A, 'gun label')
S = '\t\tinvoker.SetLayer(p, RSQ_Layers.SUPPORT, gs, hold && sp != "" ? spl : "Hidden");\n'
tx = sub1(tx, S, '\t\tif (i == 5)\n\t\t\tspl = "FbxSupF";\t// batch 2: BrutalSMG, the FBX open palm under its forend (handtable SupportHook / SupportRot row 5)\n' + S, 'support label')
tx = sub1(tx, '\tDFbxSqzF: RQFG D -1; Stop;\n', '\tDFbxSqzF: RQFG D -1; Stop;\n\tDFbxTrgS: RQFH A -1; Stop;\t// batch 2: dual wield, BrutalSMG\n\tDFbxSqzS: RQFH B -1; Stop;\n', 'dual states')
wr('zscript/rsq/hands.zs', tx)
tx = rd('zscript/rsq/dualhands.zs')
DL = '\t\t\t\t\tlabel = (firing ? "DFbxSqz" : "DFbxTrg") .. (i == 4 ? "P" : "F");\n'
tx = sub1(tx, DL, DL + '\t\t\t\tif (i == 5)\t// batch 2: BrutalSMG\n\t\t\t\t\tlabel = firing ? "DFbxSqzS" : "DFbxTrgS";\n', 'dual label')
wr('zscript/rsq/dualhands.zs', tx)
# ---- 5. handtable row 5: gun hooks 0 (baked in place); support hook/rot = bake_b2; support point moved with the gun
tx = rd('zscript/rsq/handtable.zs')
def setrow(tx, fn, vals, fmt='%.3f'):
    i0 = tx.index('static Vector3 %s(int i)' % fn); i1 = tx.index('}', tx.index('return', i0)); seg = tx[i0:i1]; k = [0]
    def z(m):
        v = [s.strip() for s in m.group(2).split(',')]; v[5] = fmt % vals[k[0]]; k[0] += 1
        return m.group(1) + ', '.join(v) + m.group(3)
    seg2, n = re.subn(r'(static const double [xyz]\[\] = \{ )([^}]*)( \};)', z, seg); assert n == 3, fn
    return tx[:i0] + seg2 + tx[i1:]
tx = setrow(tx, 'GunHook', (0, 0, 0)); tx = setrow(tx, 'GunHookTwo', (0, 0, 0))
tx = setrow(tx, 'SupportHook', B['sup_hook']); tx = setrow(tx, 'SupportRot', B['sup_rot']); tx = setrow(tx, 'SupportPoint', B['sup_point_m'])
tx = sub1(tx, '\tclearscope static Vector3 SupportHook(int i)\n', '\t// batch 2: row 5 (BrutalSMG) = the FBX palm-under (RQFS B) moved under the SMG forend (bake_b2.py)\n\tclearscope static Vector3 SupportHook(int i)\n', 'comment')
wr('zscript/rsq/handtable.zs', tx)
# ---- 6. gunmoves: pivot row 5 and fire rows 18-20 (follow_b2.py)
tx = rd('zscript/rsq/gunmoves.zs')
tx = sub1(tx, '15.667, 0.000, 5.000, 24.000, 0.000, 10.000, 11.000,', '15.667, -0.908, 6.587, 19.440, 0.000, 10.000, 11.000,', 'pivot')
tx = sub1(tx, '\t\t\t0.00, 0.00, 0.00, 0.00, 0.00, 0.51,\n\t\t\t0.00, 1.16, 0.00, 0.00, -0.03, 1.00,\n\t\t\t0.00, 0.58, 0.00, 0.00, -0.02, 0.50,\n',
          '\t\t\t-0.00, 0.00, -0.00, -0.03, -0.03, 0.51,\t// batch 2: rows 18-20 BrutalSMG, refitted for the moved gun (follow_b2.py)\n\t\t\t0.22, 1.14, 0.09, -0.04, -0.19, 0.94,\n\t\t\t0.11, 0.57, 0.05, -0.02, -0.10, 0.47,\n', 'smg rows')
wr('zscript/rsq/gunmoves.zs', tx)
# ---- 7. reload table case 3 (BrutalSMG), moved with the gun
tx = rd('zscript/rsr/rsr_guns.bd.zs')
v3 = lambda p: '(%.3f, %.3f, %.3f)' % tuple(0.0 if abs(x) < 5e-4 else x for x in p)
def setcase(tx, fn, case, old, new):
    i0 = tx.index(' %s(int i)' % fn); i1 = tx.index('\n\t}', i0); seg = tx[i0:i1]
    a = '\t\tcase %d:\treturn %s;' % (case, old); b = '\t\tcase %d:\treturn %s;\t// batch 2: moved with the gun to the FBX hand (was %s)' % (case, new, old)
    assert seg.count(a) == 1, (fn, case, a); return tx[:i0] + seg.replace(a, b) + tx[i1:]
pt = lambda p: R @ np.array(p) + t; dr = lambda v: R @ np.array(v)
well = pt([17.8, 0, -4.8]); ax = dr([0.299, 0.001, 0.954]); mc = pt([13.292, -0.026, -14.492]); gr = pt([22.4, 2.4, -2.7]); pu = dr([-0.960, 0.279, 0.0])
C3 = {'Well': ('(17.800, -0.000, -4.800)', v3(well)), 'Axis': ('(0.299, 0.001, 0.954)', v3(ax)), 'MagCentre': ('(13.292, -0.026, -14.492)', v3(mc)),
      'WellHook': ('(-0.001, -0.954, 0.299)', v3([-ax[1], -ax[2], ax[0]])), 'Grab': ('(22.400, 2.400, -2.700)', v3(gr)),
      'Pull': ('(-0.960, 0.279, 0.000)', v3(pu)), 'HandleHook': ('(0.279, 0.000, 0.960)', v3([pu[1], pu[2], -pu[0]])),
      'Offset': ('(0.000, 0.000, -5.000)', '(%.3f, %.3f, %.3f)' % OFF)}
for fn, (a, b) in C3.items(): tx = setcase(tx, fn, 3, a, b)
wr('zscript/rsr/rsr_guns.bd.zs', tx); print('case 3:', {k: v[1] for k, v in C3.items()})
# ---- 8. casing port
port = pt([14.0, -3.1, -1.0])
tx = rd('zscript/rsq/casings.zs')
tx = sub1(tx, "\t\tif (w is 'BrutalSMG')\t\t\treturn (14.0, -3.1, -1.0);", "\t\tif (w is 'BrutalSMG')\t\t\treturn (%.1f, %.1f, %.1f);\t// batch 2: moved with the gun to the FBX hand (was 14.0, -3.1, -1.0)" % tuple(port), 'port')
wr('zscript/rsq/casings.zs', tx); print('port', port.round(2))
