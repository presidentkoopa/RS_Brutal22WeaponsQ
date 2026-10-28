"""BUILD helper (2.0.2, owner r3 item 37: dual axes). Writes src/MODELDEF.rsqaxedual from the pack's own blocks:
block 1 = MODELDEF.bd.txt's first `Model BrutalAxe` block (the held axe) with the class renamed RSQ_Off_BrutalAxe;
blocks 2-3 = MODELDEF.rsq's BrutalAxe FBX gun hand (RQVI) as `Model RSQ_Off_BrutalAxe` and `Model BrutalAxe`
(dualhands.zs draws the hand as a layer called by each axe). Run from anywhere: python3 tools/optmelee/axe_dual_modeldef.py"""
import os, re
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src')
bd = open(os.path.join(SRC, 'MODELDEF.bd.txt'), encoding='latin-1').read()
m = re.search(r'^Model BrutalAxe\n\{\n(?:.*\n)*?\}', bd, re.M)
blk = m.group(0).replace('Model BrutalAxe', 'Model RSQ_Off_BrutalAxe', 1)
assert 'AXEG\tA\t0\t5' in blk
rsq = open(os.path.join(SRC, 'MODELDEF.rsq')).read()
i = rsq.index('// r12 port (lane B): BrutalAxe (row 24) holds the FBX gun hand')
hand = rsq[rsq.index('Model RSQ_GunSide', i):rsq.index('Model RSQ_Hands', i)].strip()
assert 'RQVI' in hand
head = '''// 2.0.2 DUAL AXES (owner r3 item 37). MODELDEF blocks are per class, so the off-hand copy RSQ_Off_BrutalAxe
// (Axe.dec) needs its own, as RSQ_Off_BrutalRevolver does (MODELDEF.rsqmoondual).
// Block 1 is MODELDEF.bd.txt's first `Model BrutalAxe` block (the held axe, r12 port placement) COPIED LINE FOR
// LINE with the class renamed (the engine mirrors the off hand itself). RE-COPY IT whenever that block is refitted:
// tools/optmelee/axe_dual_modeldef.py writes this file from MODELDEF.bd.txt and MODELDEF.rsq.
// Blocks 2-3: the dual-wield axe hand (dualhands.zs labels DFbxTrgAxe / DFbxSqzAxe, sprite RQVI), which the axe
// itself calls, so each class needs it: MODELDEF.rsq's BrutalAxe gun hand (fbx_hv_BrutalAxe_R.md3), unchanged.

'''
out = head + blk + '\n\n' + hand.replace('Model RSQ_GunSide', 'Model RSQ_Off_BrutalAxe') + '\n\n' + hand.replace('Model RSQ_GunSide', 'Model BrutalAxe') + '\n'
open(os.path.join(SRC, 'MODELDEF.rsqaxedual'), 'w', encoding='latin-1').write(out)
print('wrote MODELDEF.rsqaxedual', len(out.splitlines()), 'lines')
