"""TEST ONLY (never ships): fix-accuracy range on the Depot rig.
acc.py pack <out.pk3>                   build the test pack: probe/ + maps/RSQACC.wad (one 3584 x 3072 room, target wall x = 3072)
acc.py run <name> <gun.pk3> <mode 0|1> <scope table 0|1> <Gun,Gun,...>
    one engine run on doom2 -> brutal22test6 -> BD_VoxelPack -> gun pack -> test pack (the Depot's tools/int20_rig/run.sh:
    exclusive rig lock, fresh default ini). Per gun: select, place the muzzle 256 units from the wall down the drawn bore,
    mark, fire 3 bursts; then 1024. mode = sv_rsq_player_ballistics (0 Hitscan, 1 Bullet).
acc.py table <log> [<log> ...]          mean impact offset per gun, kind and distance
Env: RSQ_DEPOT (default /home/claude/rsq_weapondepot), ACC_EXTRA (console before the guns), ACC_FIRE (the firing script)."""
import os, re, sys, struct, zipfile, subprocess, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.environ.get('RSQ_DEPOT', '/home/claude/rsq_weapondepot')
WORK = os.environ.get('RSQ_WORK', DEPOT + '/work') + '/int20_rig'

def wad():
    verts = [(-512, 1536), (3072, 1536), (3072, -1536), (-512, -1536)]	# clockwise: the room is on each line's front (right) side
    t = ['namespace = "zdoom";',
         'thing { x = 0.0; y = 0.0; angle = 0; type = 1; skill1 = true; skill2 = true; skill3 = true; skill4 = true; skill5 = true; single = true; }']
    t += ['vertex { x = %.1f; y = %.1f; }' % v for v in verts]
    t += ['linedef { v1 = %d; v2 = %d; sidefront = %d; blocking = true; }' % (i, (i + 1) % 4, i) for i in range(4)]
    t += ['sidedef { sector = 0; texturemiddle = "STARTAN3"; }' for i in range(4)]
    t += ['sector { heightfloor = 0; heightceiling = 768; texturefloor = "FLOOR4_8"; textureceiling = "CEIL3_5"; lightlevel = 255; }']
    lumps = [('RSQACC', b''), ('TEXTMAP', '\n'.join(t).encode()), ('ENDMAP', b'')]
    data = b''; dirs = []; off = 12
    for n, d in lumps:
        dirs.append((off, len(d), n)); data += d; off += len(d)
    out = b'PWAD' + struct.pack('<ii', len(lumps), off) + data
    for o, s, n in dirs:
        out += struct.pack('<ii8s', o, s, n.encode())
    return out

def pack(out):
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in ('zscript.txt', 'MAPINFO.txt', 'CVARINFO.txt'):
            z.write(os.path.join(HERE, 'probe', f), f)
        z.writestr('maps/RSQACC.wad', wad())
    return out

FIRE = os.environ.get('ACC_FIRE', 'qz_rtrigger 1; wait 12; qz_rtrigger 0; wait 40; qz_rtrigger 1; wait 12; qz_rtrigger 0; wait 40; qz_rtrigger 1; wait 12; qz_rtrigger 0; wait 60; ')

def script(mode, table, guns):
    s = ('wait 100; map RSQACC; wait 70; god; notarget; rsq_extra_weapons 1; sv_rsq_player_ballistics %s; %s '
         'qz_rhand "0.25 1.3 -0.3 30 0 0"; qz_hmd "0 1.6 0 0 0 0"; netevent acc_scope %s; give ammo; ' % (mode, os.environ.get('ACC_EXTRA', ''), table))
    for g in guns:
        s += 'give %s; wait 2; use %s; wait 120; ' % (g, g)
        for d in (256, 1024):
            s += 'netevent acc_place %d; wait 8; netevent acc_mark; wait 2; %s' % (d, FIRE)
    return s + 'wait 10; quit'

def run(name, gunpk3, mode, table, guns):
    os.makedirs(WORK + '/logs', exist_ok=True); tp = pack(os.path.join(WORK, 'acc_probe.pk3'))
    env = dict(os.environ, B22_NOPROBE='1')
    subprocess.run([DEPOT + '/tools/int20_rig/run.sh', name, os.path.abspath(gunpk3), str(120 + 60 * len(guns)), script(mode, table, guns), tp], env=env)
    return WORK + '/logs/%s.log' % name

def table(logs):
    rows = collections.OrderedDict()
    for lg in logs:
        tag = os.path.basename(lg).replace('.log', '')
        for m in re.finditer(r'RSQACC HIT (\S+) (\S+) D (\d+) right (\S+) up (\S+) deg_right (\S+) deg_up (\S+) scope_right (\S+) scope_up (\S+) start_cm (\S+)', open(lg, errors='replace').read()):
            g, k, d = m.group(1), (m.group(2) if m.group(2).startswith('missile') else m.group(2).split(':')[0]), int(m.group(3))
            if re.search(r'(?i)case|brass|clip|ammospawn|links|alerter|particles', k): continue	# casing / magazine spawners, noise probes, spark debris: not shots
            rows.setdefault((tag, g, k, d), []).append([float(x) for x in m.groups()[3:]])
    print('%-22s %-15s %-30s %5s %3s | %8s %8s | %8s %8s | %8s %8s | %7s' % ('run', 'gun', 'kind', 'D', 'n', 'right', 'up', 'deg_R', 'deg_U', 'scope_R', 'scope_U', 'start'))
    for (tag, g, k, d), v in rows.items():
        mean = [statistics.mean(c) for c in zip(*v)]
        st = [x[6] for x in v if x[6] >= 0]
        print('%-22s %-15s %-30s %5d %3d | %8.2f %8.2f | %8.3f %8.3f | %8.2f %8.2f | %7s' % (tag, g, k, d, len(v), *mean[:6], ('%.1f' % statistics.mean(st)) if st else '-'))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'pack': print(pack(a[1]))
    elif a[0] == 'run': print(run(a[1], a[2], a[3], a[4], a[5].split(',')))
    elif a[0] == 'table': table(a[1:])
