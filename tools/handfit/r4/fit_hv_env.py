"""fit_hv with the farm's guns.json added (fit_batch.add_guns rule), for the cloud-side r4 tools (poses_r4.py)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'heavies'))
os.environ.setdefault('HV_RUN', os.path.join(os.environ.get('TMPDIR', '/tmp'), 'hv_run_r4'))
# the batch run dirs fit_hv imports (/home/claude/lane_b_b1run..b4run/tools) may be gone from this box: RSQ_RUNS_HOME = a mirror
# of them (e.g. the fit farm's home/ with its farmpaths.py), put ahead of the cloud paths
RH = os.environ.get('RSQ_RUNS_HOME')
if RH:
    for p in (RH, RH + '/lane_b_b1run/tools', RH + '/lane_b_b2run/tools', RH + '/lane_b_b3run/tools', RH + '/lane_b_b4run/tools'): sys.path.insert(0, p)
import fit_hv as H
for k, v in json.load(open(os.path.join(HERE, '..', 'farm', 'guns.json'))).items():
    if k.startswith('_'): continue
    it = dict(v['it']); it['path'] = H.M(it['path']); it.pop('crop', None)
    H.HV[k] = dict(cls=v.get('cls', k), row=v['row'], it=it, trig_surf=v['trig_surf'], bore_surf=v['bore_surf'], src192=v.get('src192', k))
    H.revlm.GUNS[k] = dict(it=it, grip_surf=v.get('grip_surf', [v['bore_surf']]), trig_surf=v['trig_surf'], fmax=None, bore_surf=v['bore_surf'])
