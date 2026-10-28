"""TEST ONLY (2.0.2, owner item 34): the Moonlight on the Depot rig, frames dumped every rendered frame, each labelled
with the mesh frame the weapon layer shows (moonprobe), kept as PNG strips; every .ppm deleted.
usage (RSQ_WORK set): moon_rig.py <pk3> <tag> <fire|stock|hand> [res]"""
import os, re, sys, glob, shutil, subprocess, zipfile
from PIL import Image, ImageDraw
DEPOT = os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot')
sys.path.insert(0, DEPOT + '/tools'); import depot as DP
HERE = os.path.dirname(os.path.abspath(__file__))
R = DP.WORK + '/int20_rig'
pk3, tag, mode = sys.argv[1:4]; res = sys.argv[4] if len(sys.argv) > 4 else '240'
probe = DP.WORK + '/moonprobe.pk3'
with zipfile.ZipFile(probe, 'w') as z:
    for f in ('zscript.txt', 'MAPINFO.txt'):
        z.write(os.path.join(HERE, 'moonprobe', f), f)
d = DP.WORK + '/moon_' + tag; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
SIDE = os.environ.get('MOON_SIDE', '-0.12 1.60 -0.36 20 -80 0')		# the held gun side-on in front of the left eye
pre = ('wait 100; god; notarget; screenblocks 12; crosshair 0; qz_lhand "-0.5 0.8 0.2 0 0 0"; rsq_extra_weapons 1; rsr_debug 1; give BrutalRevolver; give Clip1 60; give BrutalRevolverCylinder 6; '
       'wait 10; use BrutalRevolver; wait 60; qz_rhand "%s"; wait 15; echo MOONSTART; ' % SIDE)
if mode == 'fire':
    body = 'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 30; qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 30; '
elif mode == 'stock':
    body = 'rsr_reload 0; ' + 'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 9; ' * 7 + 'qz_rtrigger 1; wait 4; qz_rtrigger 0; wait 120; '
else:
    body = ''
s = pre + body + 'echo MOONEND; wait 5; quit'
env = dict(os.environ, QZ_RES=res, QZ_DUMP_EVERY='1', QZ_DUMP_DIR=d)
subprocess.run([DEPOT + '/tools/int20_rig/run.sh', 'moon_' + tag, pk3, '400', s, R + '/int20dump.pk3', probe], env=env,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
log = open('%s/logs/moon_%s.log' % (R, tag), errors='replace').read()
mp = re.findall(r'^MP (\d+) t (\d+) (\w+) (-?\d+) mesh (-?\d+) tics (-?\d+)', log, re.M)
ppm = sorted(glob.glob(d + '/*.ppm'))
print('rendered (probe) %d, dumped %d' % (len(mp), len(ppm)))
lines = log.splitlines()
st = [i for i, l in enumerate(lines) if 'MOONSTART' in l]; en = [i for i, l in enumerate(lines) if 'MOONEND' in l]
first = int(re.findall(r'^MP (\d+)', '\n'.join(lines[st[0]:]), re.M)[0]) if st else 0
last = int(re.findall(r'^MP (\d+)', '\n'.join(lines[:en[0]]), re.M)[-1]) if en else len(mp)
off = len(ppm) - len(mp)		# frames dumped before the level drew its first overlay (title, wipe); one overlay per frame
keep = []
for n, t, nm, fr, mesh, tics in mp:
    n = int(n)
    if n < first or n > last:
        continue
    k = n + off
    if k < len(ppm):
        keep.append((ppm[k], int(t), nm, int(mesh), int(tics)))
out = DP.WORK + '/moon_png/' + tag; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
prev = None; sel = []
for f, t, nm, mesh, tics in keep:
    if (t, mesh) == prev: continue
    prev = (t, mesh)
    im = Image.open(f).convert('RGB'); dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, im.width, 14], fill=(0, 0, 0)); dr.text((2, 1), 't%d %s mesh %d' % (t, nm, mesh), fill=(255, 255, 0))
    p = '%s/t%04d_%s_m%02d.png' % (out, t, nm, mesh); im.save(p); sel.append(p)
for f in ppm: os.remove(f)
shutil.rmtree(d, ignore_errors=True)
print('kept %d labelled PNG in %s (all .ppm deleted)' % (len(sel), out))
errs = [l for l in lines if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l]
print('errors:', errs[:3] or 'none')
for l in lines:
    if re.match(r'(rsb t\d+|B22 SHOT|B22 W \d+ mag)', l): print('  ', l[:120])
