"""TEST ONLY (rig, never ships): the revolvers and the Revolver's rounds on the Depot's QZD 17.3 rig.

python3 rig_rev.py <pack.pk3> <outdir>
Load order doom2 -> brutal22test6 -> BD_VoxelPack -> pack (+ the rig's probe). Run it under
`flock -o -x /home/claude/rig.lock`. Jobs (each one engine run, logs in <outdir>/logs):
  roster : idkfa, then which revolvers the player holds (printinv); give / summon Revolver2 (gone)
  cap    : Revolver + 100 rounds (cap 36); a second Revolver picked up off the floor (cap 72); 100 more;
           then a backpack (cap stays 72)
  spawn  : MAP01 reloaded with rsr_debug on: the map's Clip2 and the rounds put beside them
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
    show('cap rc %d' % rc, t, r'REV |RSQ moon|RevolverRounds|BrutalRevolver|RSQ_MoonPair|Backpack|AmmoSuply')

if 'spawn' in JOBS:
    s = PRE + 'map map01; wait 40; map map03; wait 40; map map07; wait 40; map map11; wait 40; echo REV END; quit'
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
