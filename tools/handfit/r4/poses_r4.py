"""Hands r4: a finished farm fit as DATA, tools/handfit/poses/<Class>.json (same layout as heavies/poses_hv.py).
Gun hand (fit_batch 'dense' / 'wrap' jobs, farm/dense_hv.py): the curl stores the solved parameters, so no FK re-fit is needed:
  trigger = revindex.setup x with x[6:18] = q_curl ; squeeze = that with x[6:9] = q_index_squeeze ('wrap': squeeze = the hold).
Support: a sup_r4.py result (solved FBX pose + its baked frame and row) or the fit's RQFS B placement (fit_hv bake).
Gun move: port_gun.place(G, shift) (MODELDEF numbers) and port_gun.rigid_move.
usage: python3 poses_r4.py gun <Class> <resultdir> <md3 name> [--sup <sup_r4 json>] [--out DIR]
       python3 poses_r4.py cannon <fc_place.json> <sup_r4 json> [--out DIR]   (FlameCannon: no gun hand, placement + support)
       python3 poses_r4.py support <Class> <sup_r4 json> [--out DIR]          (support only, gun hand unchanged)"""
import os, sys, json, argparse, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'port'))
import common_r4 as C
OUT = os.path.join(HERE, '..', 'poses')
FBX = "hand_final.fbx (DXR models/hands, never shipped); approved pistol hand = lane_c results/round4_final.json BrutalPistol (fbx_b1_R frame 0); FBX hand only (never the DXR IQM hands, never Ermac's glove)"
def sup_block(S):
    return dict(source='sup_r4.py: FBX left hand SOLVED for this gun (hold %s), baked %s frame %d with the wrist where RQFS B has it' % (S['hold'], S['md3'], S['frame']),
                hook=S['sup_hook'], rot=S['sup_rot'], point_m=S['sup_point_m'], pose_vector=S['q'], pose_params='handmodel.FbxHand q (18): I/M/R/P curl_base, curl_dist, spread; thumb curl_base, curl_dist, spread, twist; wrist flex, dev',
                placement=dict(R=S['R'], t=S['t'], scale=S['scale']), metrics=S['metrics'], bake_check_max_cm=S['bake_check_max_cm'], minutes=S.get('minutes'))
def gun(a):
    import fit_hv_env as E	# fit_hv with guns.json (farm add_guns rule)
    H = E.H; g = a.cls; D = a.res
    J = json.load(open(os.path.join(D, 'curl3_%s.json' % g))); F = json.load(open(os.path.join(D, '%s_hv.json' % g))); job = json.load(open(os.path.join(D, 'job.json')))
    st = np.load(os.path.join(D, 'st2_%s.npy' % g)); ctx, x, to_g, Xf, delta = H.revindex.setup()
    xt = x.copy(); xt[6:18] = J['q_curl'][-12:] if len(J['q_curl']) >= 12 else xt[6:18]
    if len(J['q_curl']) == 9: xt[9:18] = J['q_curl']
    xs = xt.copy()
    if not J.get('wrap'): xs[6:9] = J['q_index_squeeze']
    c = H.HV[g]; it = c['it']; G = dict(md3=it['path'], ready=it['frame'], scale=it['scale'], off=it['off'])
    import port_gun as PG
    p, res, R0, t0 = PG.place(G, F['shift']); Rm, tm = PG.rigid_move(G, p)
    o = dict(cls=g, fbx_source=FBX, pose_params='handmodel.FbxHand pose vector (revindex.setup x layout: 0-5 wrist/gun, 6-17 I/M/R/P, 18-21 thumb); bounds handmodel.QLO/QHI',
             poses=dict(trigger=dict(pose_vector=xt.tolist(), solved_params='x[6:18]' if len(J['q_curl']) == 12 else 'x[9:18] (M/R/P)'),
                        squeeze=dict(pose_vector=xs.tolist(), solved_params='hold (no trigger: wrap)' if J.get('wrap') else 'x[6:9] (index squeeze 0.6 cm along the bore)')),
             wrist=dict(R=st[:9].reshape(3, 3).tolist(), t=st[9:12].tolist(), shift_cm=F['shift'], note='hand placed X = X_pistol R^T + t in the pistol gun frame; the wrist stays pinned, the gun moves by shift'),
             gun_move=dict(modeldef_place=[float(v) for v in p], place_residual_cm=res, R=Rm.tolist(), t=tm.tolist(), note='controller-frame point -> drawn point after the move'),
             baked=a.md3, metrics=dict(curl={k: J[k] for k in ('rigid_only', 'trigger', 'squeeze', 'squeeze_travel')}, stage2=job.get('metrics', {}).get('stage2'), mode=('wrap' if J.get('wrap') else 'dense'), thr=J.get('thr')),
             farm=dict(job=job['job']['token'], status=job.get('status'), note=F.get('baked_by'), minutes=job['minutes'], batch_dir=os.path.basename(os.path.normpath(D))))
    o['poses']['support'] = sup_block(json.load(open(a.sup))) if a.sup else dict(source='fbx_b1_L.md3 frame 1 (RQFS B, FBX open palm-under; shipped), placed by fit_hv bake', hook=F['hand']['support']['sup_hook'],
                                                                                   rot=F['hand']['support']['sup_rot'], point_m=F['hand']['support']['sup_point_m'], joint_angles='those of the source pose (not re-solved for this gun)',
                                                                                   metrics={k: F['metrics']['bake'].get(k) for k in ('sup_pen', 'sup_gap', 'sup_dz')})
    return g, o
def cannon(a):
    FC = json.load(open(a.fc)); S = json.load(open(a.sup))
    o = dict(cls='FlameCannon', fbx_source=FBX, gun_hand='none drawn (owner 2026-10-27 18:46-18:48: the arm goes inside; the rear has a flesh slit)',
             gun_move=dict(modeldef_place=FC['place'], place_note=FC['place_note'], place_residual_cm=FC['place_residual_cm'], R=FC['R'], t=FC['t'], method=FC['method'], measured=FC['measured'],
                           slit_after=FC['slit_after'], muzzle_after=FC['muzzle_after'], hand_in_housing=FC['hand_in_housing']),
             poses=dict(support=sup_block(S)))
    return 'FlameCannon', o
def support(a):
    return a.cls, dict(cls=a.cls, fbx_source=FBX, gun_hand='unchanged (see the port lane rows)', poses=dict(support=sup_block(json.load(open(a.sup)))))
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd')
    p1 = sp.add_parser('gun'); p1.add_argument('cls'); p1.add_argument('res'); p1.add_argument('md3'); p1.add_argument('--sup')
    p2 = sp.add_parser('cannon'); p2.add_argument('fc'); p2.add_argument('sup')
    p3 = sp.add_parser('support'); p3.add_argument('cls'); p3.add_argument('sup')
    for p_ in (p1, p2, p3): p_.add_argument('--out', default=OUT)
    a = ap.parse_args(); g, o = dict(gun=gun, cannon=cannon, support=support)[a.cmd](a)
    os.makedirs(a.out, exist_ok=True); json.dump(o, open(os.path.join(a.out, g + '.json'), 'w'), indent=1, default=float); print('wrote', os.path.join(a.out, g + '.json'))
