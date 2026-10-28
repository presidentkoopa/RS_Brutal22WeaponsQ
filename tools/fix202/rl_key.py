"""TEST ONLY (2.0.2, owner item 32): the Ruger as played: two single shots, the gun rests in its Ready loop, then the
reload key; then the hand takes a magazine from the pouch, seats it, racks the handle, and the gun fires.
usage (RSQ_WORK set; a boot.log on a pack with the same Sniper rows): rl_key.py <pk3> <tag> [Gun]"""
import os, re, subprocess, sys
DEPOT = os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot')
sys.path.insert(0, DEPOT + '/tools'); import depot as DP
R = DP.WORK + '/int20_rig'
os.environ.update(B22_BUILD=R, B22_RIG=R + '/bin')
sys.path.insert(0, DP.RIG); import rig, mags
pk3, tag = sys.argv[1:3]; c = sys.argv[3] if len(sys.argv) > 3 else 'Sniper'
g = mags.tables(); i = [k for k in g if mags.CLS[k] == c][0]; G = g[i]; tr = G['travel']
s = ('wait 120; god; rsq_extra_weapons 1; rsr_reload 1; rsr_grab_with 0; rsr_debug 1; give %s; give %s 400; wait 20; use %s; wait 80; '
     'echo STEP two_shots; +attack; wait 3; -attack; wait 40; +attack; wait 3; -attack; wait 120; '
     'echo STEP reload_key; +reload; wait 4; -reload; wait 60; '
     'echo STEP grab_insert; qz_lhand "%s"; wait 10; qz_ltrigger 1; wait 12; qz_lhand "%s"; wait 15; qz_lhand "%s"; wait 15; qz_lhand "%s"; wait 25; qz_ltrigger 0; wait 30; '
     'echo STEP handle; qz_lhand "%s"; wait 15; qz_ltrigger 1; wait 12; qz_lhand "%s"; wait 10; qz_lhand "%s"; wait 15; qz_ltrigger 0; wait 30; '
     'echo STEP fire; +attack; wait 3; -attack; wait 30; quit'
     % (c, G['reserve'], c, rig.lpose(0, 40, -30), mags.at(G, G['M'] + 3), mags.at(G, G['M'] * 0.5), mags.at(G, 0),
        mags.handle_at(G, 0), mags.handle_at(G, tr * 0.5), mags.handle_at(G, tr * 1.05)))
subprocess.run([DEPOT + '/tools/int20_rig/run.sh', 'key_%s_%s' % (c, tag), pk3, '300', s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t = open('%s/logs/key_%s_%s.log' % (R, c, tag), errors='replace').read()
for l in t.splitlines():
    if re.match(r'(STEP |rsr t\d+ gun|rsr t\d+: |B22 SHOT)', l) and 'sound' not in l: print('   ', l[:130])
print('   errors:', [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l][:3] or 'none')
