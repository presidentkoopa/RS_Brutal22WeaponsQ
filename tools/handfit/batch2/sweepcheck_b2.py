import re, os
def read(p): return open(p, errors='replace').read() if os.path.exists(p) else ''
W = "Melee_Attacks BrutalAxe Chain_Saw DSweap BrutalPistol BrutalSMG MP40 Revolver Revolver2 Shot_Gun AssaultShotgun SSG Sniper Rifle Minigun MG42 Machinegun IncendiaryLauncher GrenadeLauncher Rocket_Launcher Devastator Plasma_Gun RailGun NukeLauncher BFG10k BIG_FUCKING_GUN HellishMissileLauncher Unmaker FlameCannon Flamethrower2 HandGrenades BrutalRevolver".split()
bad = 0
for w in W:
    out = []
    for tag, d in (('r4', '/home/claude/lane_b_r4/logs/sw_r4_%s.log'), ('b1', '/home/claude/lane_b_b1run/logs/sw_b1_%s.log'), ('b2', '/home/claude/lane_b_b2run/logs/sw_b2_%s.log')):
        t = read(d % w) + read(d % w + '.out')
        if not t: out.append('%s -' % tag); continue
        errs = [l for l in re.findall(r'Script error, "([^"]+)"', t) if 'BD_VoxelPack' not in l]
        vm = len(re.findall(r'VM execution aborted|Unhandled exception|Segmentation|signal 11', t))
        held = set(re.findall(r'B22 S \d+ main (\S+)', t))
        shots = len(re.findall(r'B22 SHOT', t))
        ph = sorted(set(re.findall(r'B22 T \d+ gun \d+ (\S+)', t)))
        out.append('%s err %d vm %d held %s shots %d phases %s' % (tag, len(errs), vm, w in held, shots, ','.join(ph) or '-'))
        if tag == 'b2' and (errs or vm or w not in held): bad += 1
    print('%-24s | %s' % (w, ' | '.join(out)))
print('b2 problems:', bad)
