"""TEST ONLY (rig, never ships): the same Unmaker hand reload in RS VR Weapons Vanilla Plus on the rig.

python3 rig_plus.py <RSQ_plus.pk3> <logdir> [hmd pose]
Load order doom2 -> RSQ_plus.pk3 (the Depot's dist/RSQ_plus.pk3 = sets/plus_0.7, Vanilla Plus for
QZD 17.3; same unmaker_wm.md3 bytes as RS_VR_Weapons_Plus.pk3). No probe (it knows BD22's classes),
so the off-hand poses come from Plus's own RSR_Guns row 1 (WM_VP_Unmaker), parsed here.
Same driver as rig_reload.py: pouch -> clear carry pose -> 3 cm above the mouth -> half in -> seated.
Env: RIGD (Depot tools/rig), FRAMES (dump dir), HOLD, CARRYP.
"""
import os, sys, re, subprocess, zipfile
PK3, OUT = os.path.abspath(sys.argv[1]), sys.argv[2]
HMD = sys.argv[3] if len(sys.argv) > 3 else '0 1.6 0 0 0 0'
RIGD = os.environ.get('RIGD', '/home/claude/rsq_weapondepot/tools/rig')
sys.path.insert(0, RIGD)
import rig, mags
zs = zipfile.ZipFile(PK3).read('zscript/rsr/rsr_guns.zs').decode('latin-1')
def row(name):
    m = re.search(r'static \w+ %s\(int i\)\s*\{(.*?)\n\t\}' % name, zs, re.S)
    v = re.search(r'case 1:\s*return \(?([^;]*?)\)?;', m.group(1)).group(1)
    v = [float(x) for x in v.split(',')]
    return tuple(v) if len(v) > 1 else v[0]
g = dict(W=row('Well'), A=row('Axis'), M=row('Mouth'), T=row('TopInHand'))
print('Plus row 1:', g)
H = int(os.environ.get('HOLD', '15'))
CARRYP = os.environ.get('CARRYP')
extra = ('echo UNM CLEAR; qz_lhand "%s"; wait %d; ' % (rig.lpose(*[float(x) for x in CARRYP.split()]), 2 * H)) if CARRYP else ''
reload = ('qz_ltrigger 1; wait 12; %secho UNM CARRY; qz_lhand "%s"; wait %d; echo UNM HALF; qz_lhand "%s"; wait %d; echo UNM SEAT; qz_lhand "%s"; wait %d; '
          'qz_ltrigger 0; wait 30; ' % (extra, mags.at(g, g['M'] + 3), 2 * H if CARRYP else H, mags.at(g, g['M'] * 0.5), H, mags.at(g, 0), H + 10))
reload = mags.with_pouch(reload)
s = ('wait 100; god; notarget; screenblocks 12; crosshair 0; qz_hmd "%s"; rsr_reload 1; rsr_grab_with 0; rsr_debug 1; '
     'give WM_VP_Unmaker; give Cell 300; use WM_VP_Unmaker; wait 150; take WMQ_Mag_WM_VP_Unmaker 999; wait 5; '
     'echo UNM RELOAD; +reload; wait 4; -reload; wait 20; echo UNM HANDRELOAD; %s echo UNM FIRE2; +attack; wait 40; -attack; wait 20; echo UNM END; quit' % (HMD, reload))
os.makedirs(OUT, exist_ok=True)
env = dict(os.environ, QZ_RES='320', EGL_PLATFORM='surfaceless', LIBGL_ALWAYS_SOFTWARE='1')
if os.environ.get('FRAMES'):
    os.makedirs(os.environ['FRAMES'], exist_ok=True)
    env.update(QZ_DUMP_EVERY=os.environ.get('EVERY', '1'), QZ_DUMP_DIR=os.environ['FRAMES'])
log = OUT + '/unm_plus.log'
cmd = ['timeout', '400', rig.RIG + '/qz', '-iwad', '/home/claude/gamedata/doom2.wad', '-file', PK3, '-nosound', '-warp', '1', '-skill', '3', '+logfile', log, '+' + s]
rc = subprocess.run(cmd, cwd=rig.RIG, env=env, stdout=open(log + '.out', 'w'), stderr=subprocess.STDOUT).returncode
t = open(log, errors='replace').read()
print('rc', rc)
for l in t.splitlines():
    if re.match(r'UNM |rsr t\d+ gun 1:', l):
        print(l)
print('ERRORS:', [l for l in t.splitlines() if re.search(r'Script error|VM abort|exception', l, re.I)][:10] or 'none')
