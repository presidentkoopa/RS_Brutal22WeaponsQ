"""TEST ONLY (never ships): frames THROUGH the scope at the accuracy range (acc.py's map and probe).
scopeshot.py <name> <gun.pk3> <Sniper|RailGun> <scope table 0|1> <D> <out dir> [mode 0|1]
The gun is held level (qz_rhand pitch 30 = level with vr_weaponRotate -30), the muzzle put D units from the wall down
the drawn bore, a green dot on the wall where the bore meets it and a red dot where the scope camera's centre line meets
it; the LEFT eye is put on the scope's axis 8 cm behind the lens (scope3x/drive.py's placement), then one shot (the eye is placed first: the head moves the pawn, room scale).
Frames: QZ_RES 960 left eye every 2nd frame; the ones from the tic before the shot ... no: frames 20 to 40 tics after the shot are kept (the puff has gone; the blue dot stays where the shot landed), each also as a 4x crop of the lens as PNG
(<out>/<name>_t<tic>.png) and every .ppm is deleted."""
import os, re, sys, glob, shutil, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import acc
name, pk3, gun, table, D, out = sys.argv[1:7]
mode = sys.argv[7] if len(sys.argv) > 7 else '0'
LENS = {'RailGun': (2.756, 0.416, 16.469), 'Sniper': (5.843, 1.237, 10.244)}[gun]
AXIS = {('RailGun', '0'): (0.9940, 0.0787, 0.0764), ('Sniper', '0'): (0.9962, 0.0624, 0.0616)}.get((gun, table), (0.99602, 0.06710, 0.05866))
RH = (0.25, 1.3, -0.3)
CROP = tuple(int(v) for v in os.environ.get('ACC_CROP', '340 340 540 540').split())	# the lens in a 960 frame (rig, this placement)
ipd = 0.064
eye = [LENS[i] - 8.0 * AXIS[i] for i in range(3)]
eye[1] -= ipd * 100 / 2		# the left eye is ipd/2 left of the head's centre: the centre goes right of the axis
hmd = '%.4f %.4f %.4f 0 0 0' % (RH[0] - eye[1] / 100, RH[1] + eye[2] / 100, RH[2] - eye[0] / 100)
s = ('wait 100; map RSQACC; wait 70; god; notarget; rsq_extra_weapons 1; sv_rsq_player_ballistics %s; screenblocks 12; crosshair 0; '
     'show_messages 0; con_notifytime 0.05; acc_hitdots 1; qz_rhand "%.2f %.2f %.2f 30 0 0"; qz_hmd "0 1.6 0 0 0 0"; netevent acc_scope %s; give ammo; give %s; wait 2; use %s; wait 120; '
     'qz_hmd "%s"; wait 30; netevent acc_place %s; wait 8; netevent acc_mark; wait 100; qz_rtrigger 1; wait 12; qz_rtrigger 0; wait 60; quit'
     % (mode, RH[0], RH[1], RH[2], table, gun, gun, hmd, D))
d = os.path.join(acc.WORK, 'dump_' + name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
os.makedirs(acc.WORK + '/logs', exist_ok=True); tp = acc.pack(os.path.join(acc.WORK, 'acc_probe.pk3'))
env = dict(os.environ, B22_NOPROBE='1', QZ_RES='960', QZ_DUMP_EVERY='2', QZ_DUMP_DIR=d)
subprocess.run([acc.DEPOT + '/tools/int20_rig/run.sh', name, os.path.abspath(pk3), '400', s, tp], env=env)
log = open(acc.WORK + '/logs/%s.log' % name, errors='replace').read()
fr = {int(a): int(b) for a, b in re.findall(r'RSQACC FRAME (\d+) t (\d+)', log)}
shot = re.search(r'RSQACC SHOT t (\d+)', log)
os.makedirs(out, exist_ok=True); kept = []
for f in sorted(glob.glob(d + '/*.ppm')):
    n = int(re.search(r'(\d+)', os.path.basename(f)).group(1)) + 1	# f00000 is the first rendered frame
    t = fr.get(n)
    if shot and t is not None and int(shot.group(1)) + 20 <= t <= int(shot.group(1)) + 40:
        p = os.path.join(out, '%s_t%d_f%d.png' % (name, t, n)); im = Image.open(f); im.save(p); kept.append(p)
        im.crop(CROP).resize(((CROP[2] - CROP[0]) * 4, (CROP[3] - CROP[1]) * 4), Image.NEAREST).save(p[:-4] + '_lens.png')
shutil.rmtree(d, ignore_errors=True)	# no .ppm left behind
print('shot tic', shot and shot.group(1), 'kept', len(kept))
for l in log.splitlines():
    if l.startswith(('RSQACC REF', 'RSQACC SCOPE', 'RSQACC HIT')): print(l)
print('pack script errors:', [l for l in re.findall(r'Script error, "([^"]+)"', log) if 'BD_VoxelPack' not in l])
