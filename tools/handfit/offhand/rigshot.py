"""rigshot.py (off-hand FBX lane, TEST ONLY, never ships): one Depot-rig run (QZD 17.3, doom2 -> brutal22test6 -> BD_VoxelPack ->
pack + the Depot probe), exclusive rig.lock (port/gate_gun.locked: fcntl LOCK_EX on <repo>/../rig.lock, the rig ini restored),
left-eye frame dumps converted to PNG and the .ppm dumps deleted at once.
  shot(pk3, name, script, picks)  picks = {png_name: tics_before_quit} (or a function of the log text returning it): the frame dumped that long before the run's last frame
                                  (the engine keeps 35 tics a second of wall time; the dump mtimes give the time), saved as PNG
Returns the run's log text. extra: test-only pk3s after the pack (e.g. oht_dmg.pk3: the damage log, dmgprobe/). Env: RSQ_GATE (logs, shots; default <repo>/../lane_b_out/offhand_gate)."""
import os, sys, glob, shutil, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
os.environ.setdefault('RSQ_GATE', os.path.join(REPO, '..', 'lane_b_out', 'offhand_gate'))
sys.path.insert(0, os.path.join(HERE, '..', 'port'))
import gate_gun as G
from PIL import Image
SHOTS = os.path.join(G.OUT, 'shots')
def shot(pk3, name, script, picks=None, res='480', every='2', secs=300, probe=True, extra=()):
    d = os.path.join(G.OUT, 'dump_' + name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    G.setpk3(os.path.abspath(pk3))
    env = dict(QZ_RES=res, QZ_DUMP_EVERY=every, QZ_DUMP_DIR=d)
    if not probe: env['B22_NOPROBE'] = '1'
    old = {k: os.environ.get(k) for k in env}; os.environ.update(env)
    try: rc, text = G.locked(G.rig.run, name, script, secs, list(extra))
    finally:
        for k, v in old.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
    fr = sorted(glob.glob(d + '/*.ppm')); out = {}
    if callable(picks): picks = picks(text)	# {png: tics before quit} worked out from the log (e.g. a logged hit's tic)
    if fr and picks:
        mt = [os.path.getmtime(f) for f in fr]; last = mt[-1]
        for png, tics in picks.items():
            t = last - tics / 35.0; k = min(range(len(fr)), key=lambda i: abs(mt[i] - t))
            Image.open(fr[k]).save(os.path.join(SHOTS, png)); out[png] = (k, len(fr))
    shutil.rmtree(d, ignore_errors=True)	# the .ppm dumps deleted right after converting
    return text, out
def errors(text):
    import re
    return [l for l in re.findall(r'Script error, "([^"]+)"[^\n]*', text) if 'BD_VoxelPack' not in l], len(re.findall(r'VM execution aborted|Unhandled exception|Segmentation|signal 11', text))
