"""TEST ONLY (2.0.2, owner item 33): the 40 mm round hold (RQ2H A) under several Hand Skin Tones, on the Rifle and the
over-under Machinegun, with the Depot's rig_holds.py M203 job (the hold shown in front of the eye, one frame kept).
usage (RSQ_WORK set): tone_m203.py <pk3> <tag> <Rifle|Machinegun> <tone,...>"""
import os, sys, json
DEPOT = os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot')
sys.path.insert(0, DEPOT + '/tools/handfit/offhand')
import rig_holds as RH
pk3, tag, gun, tones = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(',')]
base = RH.job_m203
def job_gun():
    s, pat = base()
    if gun == 'Machinegun':
        # the over-under: its own tube line (Depot tools/rig/m203.py MG constants) moved by ported_Machinegun.json
        import numpy as np, json as js
        P = js.load(open(os.path.join(RH._DP.FITS, 'ported_Machinegun.json'))); Rm = np.array(P['R']); tm = np.array(P['t'])
        MV = lambda q: tuple(Rm @ np.array(q, float) + tm); MD = lambda v: tuple(Rm @ np.array(v, float))
        L, U, TR, REAR = (-0.068, -1.517, 9.694, 29.272); PALM = (-1.5, 2.0, -4.5); RND, RAX = (-1.930, 4.560, -4.500), (0, 0, 1)
        h = RH.h
        palm_at = lambda x: h.place(PALM, (1, 0, 0), MV((x, L, U - 2.0)), MD((1, 0, 0)))[0]
        round_at = lambda x: h.place(RND, RAX, MV((x, L, U)), MD((1, 0, 0)))[0]
        FAR = '-0.25 1.3 -0.3 30 0 0'
        s = ('wait 100; ' + RH.SET + 'give Machinegun; give Clip2 100; give AmmoRocket 10; use Machinegun; wait 120; +altattack; wait 3; -altattack; wait 60; '
             'qz_lhand "%s"; wait 10; qz_lgrip 1; wait 10; qz_ltrigger 1; wait 6; qz_lhand "%s"; wait 8; qz_lhand "%s"; wait 8; qz_lhand "%s"; wait 10; qz_ltrigger 0; qz_lgrip 0; wait 6; '
             'qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 10; ' % (palm_at(40), palm_at(40 + TR * 0.4), palm_at(40 + TR * 0.75), palm_at(40 + TR + 0.5), FAR) + RH.show() +
             'qz_lhand "%s"; wait 12; qz_lhand "%s"; wait 15; qz_ltrigger 0; wait 8; '
             'qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 8; qz_lhand "%s"; wait 8; qz_lhand "%s"; wait 10; qz_ltrigger 0; wait 8; qz_lhand "%s"; wait 10; +altattack; wait 3; -altattack; wait 40; '
             % (round_at(REAR + 3.5), round_at(REAR + TR + 0.4 + 4.3), palm_at(40 + TR), palm_at(40 + TR / 2), palm_at(39.5), FAR) + RH.END)
    return s, pat
RH.job_m203 = job_gun
set0 = RH.SET
for t in tones:
    RH.SET = set0 + 'rsq_hand_tone %d; ' % t
    r = RH.run(pk3, '%s_%s_tone%02d' % (tag, gun, t), 'm203')
    print(gun, 'tone', t, json.dumps({k: r[k] for k in ('frame', 'errors', 'vm')}), r['log'][-6:], flush=True)
