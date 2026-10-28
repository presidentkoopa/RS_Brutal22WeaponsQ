"""TEST ONLY (2.0.2 options/melee lane). One rig run of the OM driver (driver/) on the owner's load order through the
Depot's tools/int20_rig/run.sh (exclusive rig lock, fresh default ini). Never ships.
usage: run.py <pk3> <name> <test,test,...> [frames: hmd pose "x y z p y r"] [extra console before the tests]
  --base  the pack predates 2.0.2 (no off-hand melee, no sword gate): the driver's new-API reads become constants
Env: RSQ_WORK (default <depot>/work), DEPOT (default /home/claude/rsq_weapondepot), QZ_RES (frames, default 480).
Prints the OM summary lines and pack script errors; with a hmd pose, dumps every 2nd frame to <work>/optmelee/<name>/
as PNG (the .ppm are deleted as they are converted)."""
import os, re, sys, glob, shutil, subprocess, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.environ.get('DEPOT', '/home/claude/rsq_weapondepot')
args = [a for a in sys.argv[1:] if a != '--base']
base = '--base' in sys.argv
pk3, name, tests = os.path.abspath(args[0]), args[1], args[2]
hmd = args[3] if len(args) > 3 and args[3] else ''
pre = args[4] if len(args) > 4 else ''
WORK = os.environ.get('RSQ_WORK', os.path.join(DEPOT, 'work'))
OUT = os.path.join(WORK, 'optmelee', name)
os.makedirs(OUT, exist_ok=True)
drv = os.path.join(OUT, 'omdriver.pk3')
z = open(os.path.join(HERE, 'driver', 'zscript.txt')).read()
if base:
    for a, b in [('RSVR_MeleeHandler.HandOf(mo, true)', 'null'), ('h.swings', '-1'), ('h.armed', '0'), ('h.arc', '0.0'),
                 ("RSVR_MeleeHandler.Inv('RSQ_Off_BrutalAxe')", "'RSVR_Token'"), ('RSVR_Hand.KindOfOff(mo)', '0')]:
        z = z.replace(a, b)
with zipfile.ZipFile(drv, 'w') as zf:
    zf.writestr('zscript.txt', z)
    for f in ('CVARINFO.txt', 'MAPINFO.txt'):
        zf.write(os.path.join(HERE, 'driver', f), f)
wait = int(os.environ.get('WAIT', str(150 + 420 * len(tests.split(',')))))
script = 'wait 100; god; notarget; screenblocks 12; crosshair 0; %s qzt_test "%s"; wait %d; quit' % (pre, tests, wait)
env = dict(os.environ)
dump = os.path.join(OUT, 'ppm')
if hmd:
    shutil.rmtree(dump, ignore_errors=True); os.makedirs(dump)
    env.update(QZ_RES=env.get('QZ_RES', '480'), QZ_DUMP_EVERY='2', QZ_DUMP_DIR=dump, QZ_HMD=hmd)
secs = env.get('SECS', '420')
subprocess.run(['bash', os.path.join(DEPOT, 'tools', 'int20_rig', 'run.sh'), 'om_' + name, pk3, secs, script, drv],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
log = os.path.join(WORK, 'int20_rig', 'logs', 'om_%s.log' % name)
t = open(log, errors='replace').read() + open(log + '.out', errors='replace').read()
shutil.copy(log, os.path.join(OUT, 'run.log'))
pk = os.path.basename(pk3)
err = sorted(set(l for l in t.splitlines() if re.search(r'Script error|VM execution aborted|exception', l) and 'voxeldef' not in l.lower()))
print('pack loaded:', ('adding ' in t and pk in t), '| MAP01:', 'MAP01' in t, '| errors (not BD_VoxelPack):', err or 'none')
for l in t.splitlines():
    if l.startswith('OM SUM') or l.startswith('OM FX') or l.startswith('OM test') or l.startswith('OM done') or l.startswith('OM THROW') or l.startswith('OM t') and ('dual key' in l or 'pickup' in l):
        print(l)
if hmd:
    fr = sorted(glob.glob(dump + '/*.ppm'))
    from PIL import Image
    for f in fr:
        Image.open(f).save(f[:-4] + '.png'); os.remove(f)
    print('frames:', len(fr), '->', dump)
