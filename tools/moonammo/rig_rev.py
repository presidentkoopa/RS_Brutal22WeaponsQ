"""TEST ONLY (rig, never ships): the revolvers and the Revolver's rounds on the Depot's QZD 17.3 rig.

python3 rig_rev.py <pack.pk3> <outdir>
Load order doom2 -> brutal22test6 -> BD_VoxelPack -> pack (+ the rig's probe). Run it under
`flock -o -x /home/claude/rig.lock`. Jobs (each one engine run, logs in <outdir>/logs):
  roster : idkfa, then which revolvers the player holds (printinv); give / summon Revolver2 (gone)
  cap    : Revolver + 100 rounds (cap 36); a second Revolver picked up off the floor (dual.zs gives the off-hand
           copy: cap 72); 100 more; then a backpack (cap stays 72)
  spawn  : MAP01/03/07/11 with rsq_moonlight_pistol 0 and then 1: the map's Clip2 and the rounds put beside them
  combos : a new game (map map01) for each of Moonlight Replaces Pistol x Start With Two: the weapons, cylinders
           and the RevolverRounds cap (printinv), the counts
  drops  : with Moonlight Replaces Pistol 0 and 1: 10 PistolSpawner summoned (a map pistol), 5 PistolZombie summoned
           and killed (their PistolDrop flies and lands as a PistolSpawner), then what is in the world
  slug   : the Shotvolver (BD22 Revolver) with rsa_rev_magnum 1: alt fire, then fire; the test-only slugprobe.pk3
           (tools/moonammo/slugprobe) counts the bullets' puffs per tic: the slug is one bullet, the shell 35
  menu   : the BD22 VR WEAPONS menu opened, frames dumped
  dual   : one Moonlight, a second picked up, the Dual key: both held; fire main, off, both; flick the off hand,
           then the main hand (reloads); printinv after each; frames dumped
  frame  : MAP07, the player warped onto open floor by one of its bullet pickups (-1090 -1138, where a run put
           rounds), facing west; a RevolverRounds summoned 56 units ahead; frames dumped
"""
import os, re, sys, glob, shutil, subprocess
PK3, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
JOBS = sys.argv[3].split(',') if len(sys.argv) > 3 else ['roster', 'cap', 'spawn', 'frame']
RIGD = os.environ.get('RIGD', '/home/claude/rsq_weapondepot/tools/rig')
os.makedirs(OUT + '/build', exist_ok=True)
shutil.copy(RIGD + '/build/probe.pk3', OUT + '/build/probe.pk3')
os.environ.update(B22_IWAD='/home/claude/gamedata/doom2.wad', B22_BD22='/home/claude/gamedata/brutal22test6.pk3',
                  B22_VOX='/home/claude/gamedata/BD_VoxelPack.pk3', B22_PK3=PK3, B22_BUILD=OUT + '/build')
sys.path.insert(0, RIGD)
import rig

PRE = 'wait 100; god; notarget; screenblocks 12; crosshair 0; rsq_extra_weapons 1; rsr_debug 1; '


def errs(t):
    return [l for l in t.splitlines() if re.search(r'Script error|VM abort|exception|Execution could not continue', l, re.I)
            and 'voxeldef' not in l.lower()]


def show(tag, t, pat):
    print('=== %s' % tag)
    for l in t.splitlines():
        if re.search(pat, l):
            print('   ', l.strip())
    e = errs(t)
    print('    script errors (not BD_VoxelPack voxeldef):', e[:8] or 'none')


def restore_ini():
    subprocess.run(['git', '-C', RIGD, 'checkout', '--', 'bin/config/qzdoom.ini'], check=False)


if 'roster' in JOBS:
    s = PRE + ('take BrutalRevolver; take Revolver; idkfa; wait 20; echo REV PRINTINV; printinv; wait 5; '
               'echo REV GIVE_REVOLVER2; give Revolver2; wait 5; echo REV SUMMON_REVOLVER2; summon Revolver2; wait 5; '
               'echo REV GIVE_SLUGCVAR; rsq_slug_replaces_shotvolver; wait 5; echo REV END; quit')
    rc, t = rig.run('rev_roster', s, 200); restore_ini()
    show('roster rc %d' % rc, t, r'REV |[Rr]evolver|Shotvolver|[Uu]nknown|rsq_slug')

if 'cap' in JOBS:
    # the second Revolver: summon puts it 56 units ahead of the player; the rig's player walks with the left
    # stick (qz_lstick; +forward does not move it), and a pickup needs the walk (a warp onto it touches nothing)
    s = PRE + ('take RevolverRounds 999; give BrutalRevolver; wait 5; give RevolverRounds 100; wait 3; echo REV ONE_GUN; printinv; '
               'summon BrutalRevolver; wait 3; qz_lstick "0 1"; wait 15; qz_lstick "0 0"; wait 5; echo REV AFTER_SECOND; '
               'give RevolverRounds 100; wait 3; echo REV TWO_GUNS; printinv; '
               'give Backpack; wait 3; give RevolverRounds 100; wait 3; echo REV BACKPACK; printinv; echo REV END; quit')
    rc, t = rig.run('rev_cap', s, 200); restore_ini()
    show('cap rc %d' % rc, t, r'REV |RSQ moon|RevolverRounds|BrutalRevolver|Backpack|AmmoSuply')

if 'spawn' in JOBS:
    s = PRE + ''.join('rsq_moonlight_pistol %d; echo REV MOONLIGHT_PISTOL %d; map map01; wait 40; map map03; wait 40; map map07; wait 40; map map11; wait 40; ' % (m, m)
                      for m in (0, 1)) + 'rsq_moonlight_pistol 0; echo REV END; quit'
    rc, t = rig.run('rev_spawn', s, 200); restore_ini()
    show('spawn rc %d' % rc, t, r'REV |RSQ moon')

if 'frame' in JOBS:
    fr = OUT + '/frames_pickup'
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    os.environ.update(QZ_RES='480', QZ_DUMP_EVERY='10', QZ_DUMP_DIR=fr)
    s = PRE + ('map map07; wait 20; warp -1010 -1138; qz_hmd "0 1.6 0 -35 0 0"; qz_rhand "0.4 0.6 0.4 30 0 0"; qz_lhand "-0.4 0.6 0.4 30 0 0"; '
               'summon RevolverRounds; wait 60; echo REV SHOT; wait 30; echo REV END; quit')
    rc, t = rig.run('rev_frame', s, 200); restore_ini()
    for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
        os.environ.pop(k)
    show('frame rc %d' % rc, t, r'REV ')
    print('    frames:', len(glob.glob(fr + '/*')), fr)

if 'combos' in JOBS:
    # the rig's ini plays the Rifle class (starts with the Rifle); the pistol start is BD22's Pistol class (Doomer2)
    s = PRE + 'playerclass "$TAGBD_CLASS_PISTOL"; ' + ''.join('rsq_moonlight_pistol %d; rsq_moonlight_two %d; map map01; wait 120; echo REV COMBO pistol %d two %d; printinv; '
                      'netevent rsq_moon_count; wait 5; ' % (a, b, a, b) for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)))
    s += 'rsq_moonlight_pistol 0; rsq_moonlight_two 0; playerclass "$TAGBD_CLASS_RIFLE"; quit'
    rc, t = rig.run('rev_combos', s, 300); restore_ini()
    log = OUT + '/build/logs/rev_combos.log'
    show('combos rc %d (from %s)' % (rc, log), open(log, errors='replace').read(),
         r'REV COMBO|RSQ moon|BrutalPistol|RSQ_Off_BrutalPistol|BrutalRevolver|RSQ_Off_BrutalRevolver|Cylinder|RevolverRounds|Clip1 ')

if 'drops' in JOBS:
    s = PRE + ''.join('rsq_moonlight_pistol %d; map map01; wait 30; echo REV DROPS pistol %d; %s %s wait 5; kill monsters; wait 200; '
                      'netevent rsq_moon_count; wait 5; ' % (a, a, 'summon PistolSpawner; ' * 10, 'summon PistolZombie; ' * 5) for a in (0, 1))
    s += 'rsq_moonlight_pistol 0; quit'
    rc, t = rig.run('rev_drops', s, 300); restore_ini()
    log = OUT + '/build/logs/rev_drops.log'
    show('drops rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV DROPS|RSQ moon: map|monsters')

if 'slug' in JOBS:
    probe = os.environ.get('SLUGPROBE', os.path.join(OUT, '..', 'slugprobe.pk3'))
    s = PRE + ('rsa_rev_magnum 1; give Revolver; give AmmoShell 50; use Revolver; wait 150; echo REV ALTFIRE; +altattack; wait 40; '
               '-altattack; wait 60; echo REV FIRE; +attack; wait 4; -attack; wait 60; echo REV ALTFIRE2; +altattack; wait 40; -altattack; '
               'wait 60; echo REV END; quit')
    rc, t = rig.run('rev_slug', s, 240, [os.path.abspath(probe)]); restore_ini()
    log = OUT + '/build/logs/rev_slug.log'
    show('slug rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV |SLUGPROBE|rsa_rev_magnum')

if 'menu' in JOBS:
    fr = OUT + '/frames_menu'
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    os.environ.update(QZ_RES='480', QZ_DUMP_EVERY='10', QZ_DUMP_DIR=fr)
    s = PRE + 'wait 20; openmenu RSQ_Options; wait 60; echo REV MENU; wait 20; quit'
    rc, t = rig.run('rev_menu', s, 200); restore_ini()
    for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
        os.environ.pop(k)
    show('menu rc %d' % rc, t, r'REV |Unknown menu|openmenu')
    print('    frames:', len(glob.glob(fr + '/*')), fr)

if 'dual' in JOBS:
    fr = OUT + '/frames_dual'
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    os.environ.update(QZ_RES='320', QZ_DUMP_EVERY='4', QZ_DUMP_DIR=fr)
    R, L = '0.22 1.3 -0.35 %d 0 0', '-0.22 1.3 -0.35 %d 0 0'
    s = PRE + ('rsr_reload 1; qz_hmd "0 1.6 0 -20 0 0"; qz_rhand "%s"; qz_lhand "%s"; take RevolverRounds 999; give BrutalRevolver; '
               'use BrutalRevolver; wait 120; echo REV ONE; printinv; summon BrutalRevolver; wait 3; qz_lstick "0 1"; wait 15; '
               'qz_lstick "0 0"; wait 5; echo REV PICKED; printinv; give StartDualWield; wait 80; echo REV DUAL_HELD; printinv; '
               'echo REV FIRE_MAIN; +attack; wait 3; -attack; wait 25; echo REV FIRE_OFF; qz_ltrigger 1; wait 3; qz_ltrigger 0; wait 25; '
               'echo REV FIRE_BOTH; +attack; qz_ltrigger 1; wait 3; -attack; qz_ltrigger 0; wait 25; echo REV AFTER_FIRE; printinv; '
               'echo REV FLICK_OFF; qz_lhand "%s"; wait 8; qz_lhand "%s"; wait 60; echo REV AFTER_FLICK_OFF; printinv; '
               'echo REV FLICK_MAIN; qz_rhand "%s"; wait 8; qz_rhand "%s"; wait 90; echo REV AFTER_FLICK_MAIN; printinv; echo REV END; quit'
               % (R % 30, L % 30, L % -70, L % 30, R % -70, R % 30))
    rc, t = rig.run('rev_dual', s, 300); restore_ini()
    for k in ('QZ_DUMP_EVERY', 'QZ_DUMP_DIR'):
        os.environ.pop(k)
    log = OUT + '/build/logs/rev_dual.log'
    show('dual rc %d (from %s)' % (rc, log), open(log, errors='replace').read(), r'REV |RSQ moon|Revolver|Cylinder|B22 SHOT')
    print('    frames:', len(glob.glob(fr + '/*')), fr)
