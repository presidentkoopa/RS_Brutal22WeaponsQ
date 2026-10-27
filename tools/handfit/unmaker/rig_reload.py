"""TEST ONLY (rig, never ships): the Unmaker's hand reload on the Depot's QZD 17.3 rig.

python3 rig_reload.py <pack.pk3> <tag> [hmd pose]
Load order doom2 -> brutal22test6 -> BD_VoxelPack -> pack (+ the rig's probe). Boots once to read
the pack's own RSR tables (probe 'B22 GUN' lines), then: Unmaker with a 200 magazine and SoulAmmo in
the pouch, fire held until the magazine is empty, trigger once more on empty, then the by-hand reload
with the off-hand driver (Depot mags.with_pouch / mags.at at the pack's Well/Axis/Mouth/TopInHand):
pouch -> CARRY (3 cm above the mouth) -> half way in -> seated -> fire again. Frames every 3 tics.
Env: B22_BUILD (build dir with probe.pk3), RIGD (Depot tools/rig), FRAMES (dir for frame dumps).
"""
import os, sys, glob, re
PK3, TAG = sys.argv[1], sys.argv[2]
HMD = sys.argv[3] if len(sys.argv) > 3 else '0 1.6 0 0 0 0'
RIGD = os.environ.get('RIGD', '/home/claude/rsq_weapondepot/tools/rig')
os.environ.update(B22_IWAD='/home/claude/gamedata/doom2.wad', B22_BD22='/home/claude/gamedata/brutal22test6.pk3',
                  B22_VOX='/home/claude/gamedata/BD_VoxelPack.pk3', B22_PK3=os.path.abspath(PK3))
sys.path.insert(0, RIGD)
import rig, mags
rig.run('boot', 'wait 100; quit', 120)
ROW = int(os.environ.get('ROW', '13')); GUN = os.environ.get('GUN', 'Unmaker'); AMMO = os.environ.get('AMMO', 'SoulAmmo 450')	# r9: other magazine guns (e.g. ROW=17 GUN=Minigun AMMO='Clip2 400')
g = mags.tables()[ROW]
print('tables row %d:' % ROW, g)
H = int(os.environ.get('HOLD', '15'))	# FRAMES runs hold each pose longer, so the dumps catch it
CARRYP = os.environ.get('CARRYP')		# optional: an extra carry pose, held clear of the gun (F L U cm)
extra = ('echo UNM CLEAR; qz_lhand "%s"; wait %d; ' % (rig.lpose(*[float(x) for x in CARRYP.split()]), 2 * H)) if CARRYP else ''
reload = ('qz_ltrigger 1; wait 12; %secho UNM CARRY; qz_lhand "%s"; wait %d; echo UNM HALF; qz_lhand "%s"; wait %d; echo UNM SEAT; qz_lhand "%s"; wait %d; '
          'qz_ltrigger 0; wait 30; ' % (extra, mags.at(g, g['M'] + 3), 2 * H if CARRYP else H, mags.at(g, g['M'] * 0.5), H, mags.at(g, 0), H + 10))
reload = mags.with_pouch(reload)
s = ('wait 100; god; notarget; screenblocks 12; crosshair 0; qz_hmd "%s"; rsq_extra_weapons 1; rsr_reload 1; rsr_grab_with 0; rsr_debug 1; rsq_reload_nonstd 1; '
     'take %s 999; give %s; give %s; use %s; wait 150; '
     '%secho UNM FIRE1; +attack; wait %d; -attack; wait 20; echo UNM TRYFIRE_EMPTY; +attack; wait 30; -attack; wait 20; '
     'echo UNM HANDRELOAD; %s echo UNM FIRE2; +attack; wait 80; -attack; wait 30; echo UNM END; quit' % (HMD, AMMO.split()[0], AMMO, GUN, GUN, 'take RSQ_Mag_%s 999; wait 10; ' % GUN if os.environ.get('TAKE') else '', int(os.environ.get('FIRE', '900')), reload))
fr = os.environ.get('FRAMES')
if fr:
    os.makedirs(fr, exist_ok=True)
    os.environ.update(QZ_RES=os.environ.get('RES', '320'), QZ_DUMP_EVERY=os.environ.get('EVERY', '3'), QZ_DUMP_DIR=fr)
rc, t = rig.run('unm_' + TAG, s, 700, [x for x in os.environ.get('EXTRA', '').split() if x])	# EXTRA: test-only pk3s after the pack
print('rc', rc)
for l in t.splitlines():
    if re.search(r'UNMP |UNM |rsr t\d+ gun %d|' % ROW + r'RSQ|counter|mag ', l) and 'B22 T' not in l:
        print(l)
errs = [l for l in t.splitlines() if re.search(r'Script error|VM abort|exception', l, re.I) and 'voxeldef' not in l.lower()]
print('ERRORS:', errs[:10] or 'none')
