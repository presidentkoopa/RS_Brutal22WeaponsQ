"""TEST ONLY (2.0 final, owner 05:0x): the Minigun's own ammo pool on the rig. mini20.py <pk3>
Run 1 (rifle cap): Rifle, Clip2 given past the cap, counted; a backpack, again. Run 2 (Minigun): the Minigun picked up (its
starting amount), then RSQ_MinigunAmmo past the cap, a burst, the hand reload (Depot mags.py geometry from this pack's own
probe table), one RSQ_MinigunAmmo box dropped at the player's feet
and walked over right after the gun (a real pickup), then RSQ_MinigunAmmo past the cap, the burst and reload, then a backpack.
Counts: INT CNT (items) and `netevent rsq_ontop` (reserve item / cap / magazine / pouch / HUD mag and reserve)."""
import os, re, subprocess, sys
R = '/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad/int20_rig'
D = '/home/claude/rsq_weapondepot/tools/rig'
os.environ.update(B22_BUILD=R, B22_RIG=R + '/bin', B22_IWAD='/home/claude/gamedata/doom2.wad')
sys.path.insert(0, D)
import rig
rig.OUT = R + '/logs'
import mags
pk3 = sys.argv[1]
def run(name, s):
    subprocess.run([R + '/run.sh', name, pk3, '300', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = open('%s/logs/%s.log' % (R, name), errors='replace').read()
    er = [l for l in t.splitlines() if re.search(r'VM execution aborted|Script error|exception', l) and 'voxeldef' not in l.lower()]
    return t, er
C = "netevent int_cnt_Clip2; netevent int_cnt_Backpack; netevent rsq_ontop; wait 2; "
s = ('wait 100; god; notarget; rsr_debug 1; give Rifle; use Rifle; wait 60; ' + C + 'give Clip2 999; wait 3; ' + C +
     'give Backpack; wait 3; give Clip2 999; wait 3; ' + C + 'quit')
t, er = run('mini_rifle', s)
print('== Rifle / Clip2 (BD22: 200, 400 with a backpack)')
for l in re.findall(r'^(INT CNT t\d+ .*?) main state|^(RSQ ontop .*)$', t, re.M): print('   ', (l[0] or l[1])[:260])
print('    errors:', er[:3] or 'none')
g = mags.tables(); i = 17; c = mags.CLS[i]; res = g[i]['reserve']
print('== Minigun: probe table reserve item:', res)
DROP = 'netevent int_drop_RSQ_MinigunAmmo; wait 15; qz_lstick "0 0.6"; wait 4; qz_lstick "0 -0.6"; wait 4; qz_lstick "0 0"; wait 30; '
s = mags.with_pouch(mags.script(i, g[i]))
s = s.replace('give %s; give %s 400; use %s; wait 80; ' % (c, res, c),
              'give %s; use %s; wait 80; %s%s%sgive %s 999; wait 3; %s' % (c, c, C, DROP, C, res, C), 1)
s = s.replace('+reload;', C + '+reload;', 1)
s = s.replace('quit', C + 'give Backpack; wait 3; give %s 999; wait 3; ' % res + C + 'quit')
t, er = run('mini_minigun', s)
ph = re.findall(r'rsr t(\d+) gun %d: (\w+) -> (\w+)' % i, t)
print('    trail', '>'.join([ph[0][1]] + [b for _, a, b in ph]) if ph else '(never started)')
for l in re.findall(r'^(INT CNT t\d+ .*?) main state|^(RSQ ontop .*)$|^(rsq t\d+ Minigun: RELOAD.*)$|^(INT DROP .*)$|^(Picked up a box of Minigun.*)$', t, re.M):
    print('   ', ''.join(l)[:260])
print('    errors:', er[:3] or 'none')
