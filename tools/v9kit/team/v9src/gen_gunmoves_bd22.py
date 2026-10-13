"""gunmoves_bd22 against the v9 hand table (team/melee_hands/gen: + BrutalAxe 24, Chain_saw 25).
Runs team/hands_work/rsq_gunmoves_gen.py unchanged (read only); only its inputs are pointed at the
v9 table: the hand-table order, the axe / chainsaw ready frames (AXEG A, SAWG A) and their files.
    python3 -I -B gen_bd22_v9.py <out.zs>"""
import sys, os
sys.dont_write_bytecode = True
S = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
sys.path.insert(0, S + '/team/hands_work')
import kick_measure as km, fire_frames as ff, rsq_gunmoves_gen as gen
HT = S + '/team/melee_hands/gen/zscript/rsq/handtable.zs'
orig_sets = km.sets

def sets(which):
    blocks, root, ready, order = orig_sets(which)
    if which == 'bd22':
        ready = dict(ready, BrutalAxe=('AXEG', 'A'), Chain_saw=('SAWG', 'A'))
        order = km.handtable_order(open(HT).read())
    return blocks, root, ready, order

km.sets = sets
ff.BD22_FILES.update({'BrutalAxe': 'Axe.dec', 'Chain_saw': 'Saw.dec'})
gen.main('bd22', sys.argv[1])
