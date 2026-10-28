"""TEST ONLY (2.0 int r2, owner job 3): hand reload of the IncendiaryLauncher, NukeLauncher and Minigun with NO backpack.
Real-play order: the gun first, then (3 tics later, as a later pickup) its reserve ammo through the normal pickup cap;
counts (reserve item, magazine) printed before the reload, and after. rl3.py <pk3> [Gun,...]"""
import os, re, subprocess, sys
R = '/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad/int20_rig'
D = '/home/claude/rsq_weapondepot/tools/rig'
os.environ.update(B22_BUILD=R, B22_RIG=R + '/bin', B22_IWAD='/home/claude/gamedata/doom2.wad')
sys.path.insert(0, D)
import rig
rig.OUT = R + '/logs'
import mags
pk3 = sys.argv[1]; only = sys.argv[2].split(',') if len(sys.argv) > 2 else ['IncendiaryLauncher', 'NukeLauncher', 'Minigun']
g = mags.tables()
for i in sorted(g):
    c = mags.CLS[i]
    if c not in only: continue
    res = g[i]['reserve']; cnt = 'netevent int_cnt_%s_RSQ_Mag_%s; wait 2; ' % (res, c)
    s = mags.with_pouch(mags.script(i, g[i]))
    s = s.replace('give %s; give %s 400; use %s; wait 80; ' % (c, res, c),
                  'give %s; wait 3; give %s 400; use %s; wait 80; %s' % (c, res, c, cnt), 1)
    s = s.replace('+reload;', cnt + '+reload;', 1).replace('quit', cnt + 'quit')
    assert s.count('int_cnt') == 3, s
    name = 'r2rl_%s' % c
    subprocess.run([R + '/run.sh', name, pk3, '300', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    ph = re.findall(r'rsr t(\d+) gun %d: (\w+) -> (\w+)' % i, t)
    trail = '>'.join([ph[0][1]] + [b for _, a, b in ph]) if ph else '(never started)'
    cn = re.findall(r'INT CNT t(\d+) (.*?) main state', t)
    er = [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l.lower()]
    print('%-20s trail %s' % (c, trail), flush=True)
    for tt, x in cn: print('    t%s %s' % (tt, x), flush=True)
    print('    errors:', er[:3] or 'none', '| refused:', re.findall(r'rsr t\d+: reload refused.*', t)[:1] or 'no', flush=True)
