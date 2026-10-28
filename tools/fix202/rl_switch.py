"""TEST ONLY (2.0.2, owner item 33): a magazine gun's hand reload across a weapon switch, on the Depot rig.
empty -> reload (magazine drops) -> switch away -> switch back -> [variant: press reload again] -> grab from the pouch
-> insert -> handle if needed -> fire. Geometry from the live tables (the probe's B22 GUN lines in a boot.log made on
the same pack). usage (Depot env, RSQ_WORK set): rl_switch.py <pk3> <Gun,...|all> [again 0|1] [tag]"""
import os, re, subprocess, sys
DEPOT = os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot')
sys.path.insert(0, DEPOT + '/tools'); import depot as DP
R = DP.WORK + '/int20_rig'
os.environ.update(B22_BUILD=R, B22_RIG=R + '/bin')
sys.path.insert(0, DP.RIG); import rig, mags
pk3 = sys.argv[1]; which = sys.argv[2]; again = len(sys.argv) > 3 and sys.argv[3] == '1'; tag = sys.argv[4] if len(sys.argv) > 4 else ''
OTHER = 'BrutalPistol'
# empty the gun: hold the trigger (automatics), then single pulls (semi-autos such as the Ruger fire once per pull)
FIRE = '+attack; wait 200; -attack; wait 20; ' + '+attack; wait 3; -attack; wait 10; ' * 16 + 'wait 30; '
def run(name, s, secs=300):
    subprocess.run([DEPOT + '/tools/int20_rig/run.sh', name, pk3, str(secs), s, R + '/int20dump.pk3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return open('%s/logs/%s.log' % (R, name), errors='replace').read()
def errs(t): return [l for l in t.splitlines() if re.search(r'VM abort|Script error|exception', l) and 'voxeldef' not in l]
g = mags.tables()
guns = sorted(g) if which == 'all' else [i for i in g if mags.CLS[i] in which.split(',')]
for i in guns:
    c = mags.CLS[i]; G = g[i]; oth = OTHER if c != OTHER else 'Rifle'
    pouch = 'qz_lhand "%s"; wait 10; ' % rig.lpose(0, 40, -30)
    ins = ('%sqz_ltrigger 1; wait 12; qz_lhand "%s"; wait 15; qz_lhand "%s"; wait 15; qz_lhand "%s"; wait 25; qz_ltrigger 0; wait 30; '
           % (pouch, mags.at(G, G['M'] + 3), mags.at(G, G['M'] * 0.5), mags.at(G, 0)))
    hnd = ''
    if G['handle']:
        tr = G['travel']
        hnd = ('qz_lhand "%s"; wait 15; qz_ltrigger 1; wait 12; qz_lhand "%s"; wait 10; qz_lhand "%s"; wait 15; qz_ltrigger 0; wait 30; '
               % (mags.handle_at(G, 0), mags.handle_at(G, tr * 0.5), mags.handle_at(G, tr * 1.05)))
    s = ('wait 120; god; rsq_extra_weapons 1; rsr_reload 1; rsr_grab_with 0; rsr_debug 1; give %s; wait 10; give %s; give %s 400; wait 30; use %s; wait 80; '
         'echo STEP fire_empty; %s'
         'echo STEP reload; +reload; wait 4; -reload; wait 60; '
         'echo STEP switch_away; use %s; wait 70; echo STEP switch_back; use %s; wait 80; %s'
         'echo STEP grab_insert; %s%s'
         'echo STEP fire; +attack; wait 6; -attack; wait 30; quit'
         % (oth, c, G['reserve'], c, FIRE, oth, c, 'echo STEP reload_again; +reload; wait 4; -reload; wait 40; ' if again else '', ins, hnd))
    t = run('sw_%s%s' % (c, tag), s, 400)
    lines = [l for l in t.splitlines() if re.match(r'(STEP |rsr t\d+|B22 W \d+ mag|B22 SHOT)', l)]
    print('== %s (gun %d, again=%d)' % (c, i, again))
    for l in lines: print('   ', l[:140])
    print('   errors:', errs(t)[:3] or 'none', flush=True)
