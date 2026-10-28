"""Hands r4: finish a farm fit whose curl is saved (curl3_<Gun>.json + st2_<Gun>.npy) but whose bake did not run
(r4b 'wrap' jobs: fit_batch's log line crashed on padI_trig = None after the curl was written; fixed in fit_batch.py).
Runs exactly fit_batch._fit's tail: fit_hv.bake_it (gun-hand md3 frames + the RQFS B palm-under at the SupportPoint) and
writes <Gun>_hv.json (port_gun.py's fit json) and bake.json, in the result dir. Baking is not fitting (no solve).
usage: python3 bake_r4.py <Gun> <resultdir>"""
import os, sys, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fit_hv_env as E
def main(g, D):
    H = E.H; H.RUN = D.replace('\\', '/'); H.FITS = D; os.makedirs(os.path.join(D, 'bake'), exist_ok=True)
    J = json.load(open(os.path.join(D, 'curl3_%s.json' % g))); o2 = {k: v for k, v in J.items() if k not in ('Xt', 'Xs', 'R', 't')}
    o3, sup, md3 = H.bake_it(g); name = 'fbx_hv_%s_R.md3' % g; shutil.copyfile(md3, os.path.join(D, name))
    job = json.load(open(os.path.join(D, 'job.json')))
    F = dict(shift=o2['shift'], hand=dict(md3=name, md3_name=name, sprite=None, label=None, squeeze='false', squeeze_note='no trigger on this mesh: the squeeze frame = the hold' if J.get('wrap') else 'fullbright (firing) frames',
             support=sup, support_note="the FBX palm-under (RQFS B) under the gun at its SupportPoint, moved with the gun (fit_hv.py)"),
             metrics=dict(stage2=None, curl={k: v for k, v in o2.items() if k != 'shift'}, bake=o3), baked_by='r4/bake_r4.py (cloud; farm curl)')
    json.dump(F, open(os.path.join(D, '%s_hv.json' % g), 'w'), indent=1, default=float); json.dump(o3, open(os.path.join(D, 'bake.json'), 'w'), indent=1, default=float)
    print(json.dumps({k: v for k, v in o3.items() if k != 'rows'}, default=float))
if __name__ == '__main__': main(*sys.argv[1:3])
