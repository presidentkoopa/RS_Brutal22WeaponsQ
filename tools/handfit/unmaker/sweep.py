"""TEST ONLY (rig): select, fire, alt-fire and reload the Unmaker and its neighbours on the pack.
python3 sweep.py <pack.pk3> [Class,...]   (load order doom2 -> brutal22test6 -> BD_VoxelPack -> pack + probe)
Per gun: the probe's 'B22 S' line names the weapon in the main hand after `use`; ammo spent on fire is
read from the 'rsq' / 'B22 W' lines; script errors from the whole run are listed."""
import os, sys, re
PK3 = os.path.abspath(sys.argv[1])
GUNS = (sys.argv[2] if len(sys.argv) > 2 else 'Unmaker,Devastator,Plasma_Gun,RailGun,Flamethrower2,IncendiaryLauncher,NukeLauncher,Minigun,Machinegun').split(',')
RIGD = os.environ.get('RIGD', '/home/claude/rsq_weapondepot/tools/rig')
os.environ.update(B22_IWAD='/home/claude/gamedata/doom2.wad', B22_BD22='/home/claude/gamedata/brutal22test6.pk3',
                  B22_VOX='/home/claude/gamedata/BD_VoxelPack.pk3', B22_PK3=PK3)
sys.path.insert(0, RIGD)
import rig
s = 'wait 100; god; notarget; rsq_extra_weapons 1; rsr_reload 1; rsr_debug 1; give all; give Backpack; '
for g in GUNS:
    s += ('give %s; use %s; wait 150; echo SWEEP %s SEL; +attack; wait 40; -attack; wait 20; echo SWEEP %s ALT; +altattack; wait 20; -altattack; wait 30; '
          'echo SWEEP %s RELOAD; +reload; wait 4; -reload; wait 60; ' % (g, g, g, g, g))
s += 'echo SWEEP END; quit'
rc, t = rig.run('sweep', s, 200 + 300 * len(GUNS))
cur = None; seen = {}
for l in t.splitlines():
    m = re.match(r'SWEEP (\S+) (\S+)', l)
    if m:
        cur = (m.group(1), m.group(2)); seen.setdefault(cur, set()); continue
    if cur:
        m = re.match(r'B22 S \d+ main (\S+)', l)
        if m: seen[cur].add('main=' + m.group(1))
        if re.match(r'B22 W \d+ mag \d+ -> \d+ fp 1', l): seen[cur].add('fired')
        if re.match(r'rsr t\d+ gun \d+: \w+ -> \w+', l): seen[cur].add('reload:' + l.split(': ')[1])
for k, v in seen.items():
    print(k, sorted(v)[:8])
errs = [l for l in t.splitlines() if re.search(r'Script error|VM abort|exception|Unknown (class|actor)', l, re.I) and 'voxeldef' not in l.lower()]
print('rc', rc, 'ERRORS:', errs[:10] or 'none')
