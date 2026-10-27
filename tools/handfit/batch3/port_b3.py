"""Batch 3: MP40 (handtable row 12) gets the FBX gun hand fitted from 1.92's MP40 hold (m192/rigid3/curl3: 1.92's hand
placement on the MP40, transported to the approved FBX pistol hand, re-placed rigidly onto the grip, M/R/P curls closed,
index squeeze 0.6 cm) and the FBX palm-under (RQFS B) under the barrel at 1.92's SupportPoint. The gun keeps the pistol's
r5 aim and moves to the hand. Every edit asserts the exact text it replaces (port_b2.py's method)."""
import os, re, sys, json, shutil, numpy as np
SRC = '/home/claude/lane_b_b3/src'; RUN = '/home/claude/lane_b_b3run'
def rd(p): return open(os.path.join(SRC, p), encoding='latin1').read()
def wr(p, t): open(os.path.join(SRC, p), 'w', encoding='latin1').write(t)
def sub1(t, a, b, what):
    n = t.count(a); assert n == 1, '%s: %d matches' % (what, n); return t.replace(a, b)
PL_ = json.load(open(RUN + '/place_MP40.json')); B = json.load(open(RUN + '/bake/bake_b3_MP40.json'))
p = PL_['place']; R = np.array(PL_['R']); t = np.array(PL_['t'])	# MP40 point (1.99 scene frame) -> R p + t (controller F L U cm)
OFF = tuple(p[:3]); AO = tuple(p[3:])
shutil.copyfile(RUN + '/bake/fbx_b3_MP40_R.md3', SRC + '/models/rsq/fbx/fbx_b3_R.md3')
# ---- MODELDEF: every block drawing MP40.md3 on the gun controller (not RSQ_Hands RQMP = off hand, not RSR_DroppedMag RQMW)
PL = 'Offset %.3f %.3f 0.0\n{i}ZOffset %.3f\n{i}AngleOffset %.3f\n{i}PitchOffset %.3f\n{i}RollOffset %.3f\t// batch 3 (lane B): gun to the FBX hand fitted from 1.92' % (OFF + AO)
OK = {('MODELDEF.bd.txt', 'MP40'), ('MODELDEF.purist', 'PuristMP40'), ('MODELDEF.rsqoff', 'RSQ_Off_MP40'), ('MODELDEF.rsr', 'MP40'), ('MODELDEF.rsr', 'RSR_GunParts')}
EXPECT = {('MODELDEF.bd.txt', 'MP40'): 1, ('MODELDEF.purist', 'PuristMP40'): 3, ('MODELDEF.rsqoff', 'RSQ_Off_MP40'): 3, ('MODELDEF.rsr', 'MP40'): 2, ('MODELDEF.rsr', 'RSR_GunParts'): 2}
blk = re.compile(r'(?m)^Model[ \t]+(\S+)[ \t]*\n\{.*?\n\}', re.S); count = {}
for f in sorted(set(k[0] for k in OK)):
    tx = rd(f); out = []; last = 0
    for m in blk.finditer(tx):
        body = m.group(0); cls = m.group(1)
        if (f, cls) in OK and '"MP40.md3"' in body and 'RQMW' not in body:
            mm = re.search(r'(?m)^([ \t]*)Offset[ \t]+0\.0+[ \t]+0\.0+[ \t]+0\.0[^\n]*\n', body); assert mm, (f, cls)
            z = re.search(r'(?m)^[ \t]*ZOffset[ \t]+-5(\.0+)?[ \t]*\n', body); assert z, (f, cls)
            assert 'AngleOffset' not in body and 'RollOffset' not in body, (f, cls)
            nb = body[:z.start()] + body[z.end():]; ind = mm.group(1)
            body = nb.replace(mm.group(0), ind + PL.format(i=ind) + '\n', 1); count[(f, cls)] = count.get((f, cls), 0) + 1
        out.append(tx[last:m.start()]); out.append(body); last = m.end()
    out.append(tx[last:]); wr(f, ''.join(out))
assert count == EXPECT, count
# ---- hand blocks: RQFI (new sprite; free in the pack, BD22 and BD_VoxelPack): A MP40 trigger, B squeeze
FR = '\tFrameIndex RQFI A 0 0\t// MP40, finger on the trigger\n\tFrameIndex RQFI B 0 1\t// MP40, squeezed\n'
def hblock(cls): return 'Model %s\n{\n\tPath "models/rsq/fbx"\n\tModel 0 "fbx_b3_R.md3"\n\tSkin 0 "fbx_hand.png"\n\tScale -1.0 1.0 1.0\n\tOffset 0.0 -24.0 -10.0\n%s}\n' % (cls, FR)
H = '\n// batch 3 (lane B): MP40 (row 12) holds the FBX gun hand fitted from 1.92\'s MP40 hold (frames baked in place, hook 0)\n'
wr('MODELDEF.rsq', rd('MODELDEF.rsq').rstrip('\n') + '\n' + H + hblock('RSQ_GunSide') + hblock('RSQ_Hands'))
for f, cls in (('MODELDEF.rsqdual', 'MP40'), ('MODELDEF.rsqoff', 'RSQ_Off_MP40'), ('MODELDEF.purist', 'PuristMP40')):
    wr(f, rd(f).rstrip('\n') + '\n' + H.replace('(row 12)', '(row 12), dual wield') + hblock(cls))
# ---- hands.zs / dualhands.zs
tx = rd('zscript/rsq/hands.zs')
tx = sub1(tx, '\tFbxSqzS: RQFH B -1; Stop;\n', '\tFbxSqzS: RQFH B -1; Stop;\n\t// batch 3: MP40 (row 12)\n\tFbxTrgM: RQFI A -1; Stop;\n\tFbxSqzM: RQFI B -1; Stop;\n', 'states')
A = '\t\tif (i == 5)\t// batch 2: BrutalSMG squeezes'
tx = sub1(tx, A, '''		if (i == 12)	// batch 3: MP40 squeezes on its FIRE frames (gunmoves rows 42-45: MP40 B D E Q R S, PP40 B D E) or fullbright, trigger otherwise
		{
			bool msq = false;
			let mgp = p.FindPSprite(PSP_WEAPON);
			if (mgp && mgp.CurState)
			{
				int mf = mgp.Frame;
				msq = mgp.CurState.bFullbright || (mgp.Sprite == Actor.GetSpriteIndex('MP40') && (mf == 1 || mf == 3 || mf == 4 || (mf >= 16 && mf <= 18))) || (mgp.Sprite == Actor.GetSpriteIndex('PP40') && (mf == 1 || mf == 3 || mf == 4));
			}
			gl = msq ? "FbxSqzM" : "FbxTrgM";
		}
''' + A, 'gun label')
S = '\t\tif (i == 5)\n\t\t\tspl = "FbxSupF";'
tx = sub1(tx, S, '\t\tif (i == 12)\n\t\t\tspl = "FbxSupF";\t// batch 3: MP40, the FBX open palm under its barrel (handtable SupportHook / SupportRot row 12)\n' + S, 'support label')
tx = sub1(tx, '\tDFbxSqzS: RQFH B -1; Stop;\n', '\tDFbxSqzS: RQFH B -1; Stop;\n\tDFbxTrgM: RQFI A -1; Stop;\t// batch 3: dual wield, MP40\n\tDFbxSqzM: RQFI B -1; Stop;\n', 'dual states')
wr('zscript/rsq/hands.zs', tx)
tx = rd('zscript/rsq/dualhands.zs')
DL = '\t\t\t\tif (i == 5)\t// batch 2: BrutalSMG\n'
tx = sub1(tx, DL, '\t\t\t\tif (i == 12)\t// batch 3: MP40\n\t\t\t\t\tlabel = firing ? "DFbxSqzM" : "DFbxTrgM";\n' + DL, 'dual label')
wr('zscript/rsq/dualhands.zs', tx)
# ---- handtable row 12
tx = rd('zscript/rsq/handtable.zs')
def setrow(tx, fn, vals, row=12, fmt='%.3f'):
    i0 = tx.index('static Vector3 %s(int i)' % fn); i1 = tx.index('}', tx.index('return', i0)); seg = tx[i0:i1]; k = [0]
    def z(m):
        v = [s.strip() for s in m.group(2).split(',')]; v[row] = fmt % vals[k[0]]; k[0] += 1
        return m.group(1) + ', '.join(v) + m.group(3)
    seg2, n = re.subn(r'(static const double [xyz]\[\] = \{ )([^}]*)( \};)', z, seg); assert n == 3, fn
    return tx[:i0] + seg2 + tx[i1:]
tx = setrow(tx, 'GunHook', (0, 0, 0)); tx = setrow(tx, 'GunHookTwo', (0, 0, 0))
tx = setrow(tx, 'SupportHook', B['sup_hook']); tx = setrow(tx, 'SupportRot', B['sup_rot']); tx = setrow(tx, 'SupportPoint', B['sup_point_m'])
tx = sub1(tx, '\t// batch 2: row 5 (BrutalSMG)', '\t// batch 3: row 12 (MP40) = the FBX palm-under (RQFS B) under the MP40 barrel at 1.92\'s SupportPoint, moved with the gun (bake_b3.py)\n\t// batch 2: row 5 (BrutalSMG)', 'comment')
wr('zscript/rsq/handtable.zs', tx)
# ---- gunmoves: pivot row 12 and fire rows 42-45 (follow_b2.rows at the moved placement; the original placement reproduces the shipped rows)
tx = rd('zscript/rsq/gunmoves.zs')
i0 = tx.index('clearscope static Vector3 Pivot'); i1 = tx.index('};', i0); seg = tx[i0:i1]
pre, body = seg.split('{ ', 1); vals = [s.strip() for s in body.split(',')]
assert vals[36:39] == ['0.000', '5.000', '24.000'], vals[36:39]
vals[36:39] = ['%.3f' % v for v in PL_['pivot']]; tx = tx[:i0] + pre + '{ ' + ', '.join(vals) + ' ' + tx[i1:]
OLD = ['0.00, 0.85, 0.00, 0.00, -0.05, 1.01', '0.00, 1.28, 0.00, 0.00, -0.07, 1.53', '0.00, 0.41, 0.00, 0.00, -0.03, 0.49', '0.00, 1.69, 0.00, 0.00, -0.07, 2.01']
for k, (o, r) in enumerate(zip(OLD, PL_['rows'])):
    new = ', '.join('%.2f' % (0.0 if abs(v) < 0.005 else v) for v in r)
    tx = sub1(tx, '\t\t\t' + o + ',\n', '\t\t\t' + new + ',\t// batch 3: row %d MP40, refitted for the moved gun\n' % (42 + k), 'row %d' % (42 + k))
wr('zscript/rsq/gunmoves.zs', tx)
# ---- reload table case 4 (MP40), moved with the gun (TopInHand / HandHook are hand-frame: kept, as b1/b2)
tx = rd('zscript/rsr/rsr_guns.bd.zs')
v3 = lambda q: '(%.3f, %.3f, %.3f)' % tuple(0.0 if abs(x) < 5e-4 else x for x in q)
def setcase(tx, fn, case, old, new):
    i0 = tx.index(' %s(int i)' % fn); i1 = tx.index('\n\t}', i0); seg = tx[i0:i1]
    a = '\t\tcase %d:\treturn %s;' % (case, old); b = '\t\tcase %d:\treturn %s;\t// batch 3: moved with the gun to the FBX hand (was %s)' % (case, new, old)
    assert seg.count(a) == 1, (fn, case, a); return tx[:i0] + seg.replace(a, b) + tx[i1:]
pt = lambda q: R @ np.array(q) + t; dr = lambda v: R @ np.array(v)
ax = dr([0.0, -0.001, 1.0]); pu = dr([-1.0, 0.0, 0.0])
C4 = {'Well': ('(31.400, -0.000, 1.800)', v3(pt([31.4, 0, 1.8]))), 'Axis': ('(0.000, -0.001, 1.000)', v3(ax)),
      'MagCentre': ('(31.339, -0.015, -4.664)', v3(pt([31.339, -0.015, -4.664]))), 'WellHook': ('(0.001, -1.000, 0.000)', v3([-ax[1], -ax[2], ax[0]])),
      'Grab': ('(22.700, 1.200, 3.200)', v3(pt([22.7, 1.2, 3.2]))), 'Pull': ('(-1.000, 0.000, 0.000)', v3(pu)),
      'HandleHook': ('(0.000, 0.000, 1.000)', v3([pu[1], pu[2], -pu[0]])), 'Offset': ('(0.000, 0.000, -5.000)', '(%.3f, %.3f, %.3f)' % OFF)}
for fn, (a, b) in C4.items(): tx = setcase(tx, fn, 4, a, b)
wr('zscript/rsr/rsr_guns.bd.zs', tx); print('case 4:', {k: v[1] for k, v in C4.items()})
# ---- casing port
port = pt([34.7, -2.2, 3.3])
tx = rd('zscript/rsq/casings.zs')
tx = sub1(tx, "\t\tif (w is 'MP40')\t\t\t\treturn (34.7, -2.2, 3.3);", "\t\tif (w is 'MP40')\t\t\t\treturn (%.1f, %.1f, %.1f);\t// batch 3: moved with the gun to the FBX hand (was 34.7, -2.2, 3.3)" % tuple(port), 'port')
wr('zscript/rsq/casings.zs', tx); print('port', port.round(2), 'place', np.round(p, 3))
