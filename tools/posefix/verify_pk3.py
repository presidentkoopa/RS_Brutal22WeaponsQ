#!/usr/bin/env python3
"""Independent offline check of the built pk3 (v4).

Checks by CONTENT: every FrameIndex line's vertex data in the new pk3 is
compared with the vertex data of the frame it is meant to show in the SOURCE
mesh (old pk3, or the source pack for the new models). Coverage is checked by
re-running the DECORATE explorer: every (sprite, frame) BD22 can put on a
weapon or flash layer, and has art for, must have a model key.

    python verify_pk3.py OLD.pk3 NEW.pk3 bd22_lumps.txt BD22_DECORATE_DIR WEAPONSETS_DIR
"""
import re, sys, zipfile, struct, os, glob
from md3strip import parse
from pose_tables import TABLES, FLAMECANNON_ADD
import fill_tables as FT
from restore_and_strip import HAND, AUTHORED_HAND, source_files

FI = re.compile(r'^\s*FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', re.I)


def blocks(text):
    out = []
    for m in re.finditer(r'^Model (\S+)\s*\{(.*?)^\}', text, re.M | re.S):
        body = m.group(2)
        keys = {}
        for l in body.splitlines():
            f = FI.match(l)
            if f:
                k = (f.group(1).upper(), f.group(2).upper())
                assert k not in keys, ('duplicate key in block', m.group(1), k)
                assert f.group(3) == '0', ('model index', m.group(1), k)
                keys[k] = int(f.group(4))
        other = [l.strip() for l in body.splitlines()
                 if l.strip() and not FI.match(l) and not l.strip().startswith('//') and l.strip() != '{']
        out.append(dict(cls=m.group(1), keys=keys, other=other,
                        path=re.search(r'Path\s+"([^"]+)"', body).group(1).rstrip('/'),
                        mesh=re.search(r'Model\s+0\s+"([^"]+)"', body).group(1),
                        skins=re.findall(r'(?:Skin\s+0|SurfaceSkin\s+0\s+\d+)\s+"([^"]+)"', body)))
    return out


def frame_blob(m, f):
    return m['frames'][f][:40] + b''.join(s['xyz'][f] for s in m['surfs'])


def main(old_pk3, new_pk3, lumps_txt, decorate_dir, weaponsets):
    zo, zn = zipfile.ZipFile(old_pk3), zipfile.ZipFile(new_pk3)
    assert zn.testzip() is None, 'zip CRC failure'
    oldb = {b['cls']: b for b in blocks(zo.read('MODELDEF.bd.txt').decode('latin-1'))}
    newb = blocks(zn.read('MODELDEF.bd.txt').decode('latin-1'))
    problems = []
    src = {n.lower(): zo.read(n) for n in zo.namelist() if not n.endswith('/')}
    src.update({k.lower(): v for k, v in source_files(weaponsets).items()})
    names_new = {n.lower(): n for n in zn.namelist()}

    # art and coverage, recomputed here (not read from the builder's json)
    art = set()
    for l in open(lumps_txt):
        l = l.strip().upper()
        if len(l) >= 6 and l[5].isdigit():
            art.add(l[:4])
    # sprite names DECORATE states use: the engine registers these before it
    # reads MODELDEF (info.cpp GetSpriteIndex), so keying them is legal even
    # with no art; an unregistered name is fatal ("Unknown sprite", models.cpp)
    registered = set(art) | {'PLAY', 'CSAW'}
    for p in glob.glob(os.path.join(decorate_dir, '**', '*'), recursive=True):
        if os.path.isfile(p):
            for m in re.finditer(r'^\s*"?([A-Za-z0-9_]{4})"?\s+"?[A-Za-z\[\]\\#^]+"?\s+-?\d+',
                                 open(p, errors='replace').read(), re.M):
                registered.add(m.group(1).upper())
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import decsim
    decsim.D = decorate_dir
    decsim.CLASSES.update({'MG42': 'MG42.dec', 'BFG10k': 'BFG10k.dec', 'Sniper': 'Sniper.dec',
                           'IncendiaryLauncher': 'IncendiaryLauncher.dec', 'NukeLauncher': 'NukeLauncher.dec',
                           'Devastator': 'Devastator.dec', 'Melee_Attacks': 'Melee.dec', 'HandGrenades': 'Grenades.dec'})

    per = {}
    for b in newb:
        per.setdefault(b['cls'], []).append(b)
    for cls, bl in per.items():
        seen = {}
        for b in bl:
            for k in b['keys']:
                if k in seen:
                    problems.append('%s: %s%s keyed in two blocks (%s, %s)' % (cls, k[0], k[1], seen[k], b['mesh']))
                seen[k] = b['mesh']

    # 1. coverage: nothing BD22 can show stays a flat sprite
    uncovered = {}
    for cls in list(FT.WORLD):
        if cls not in per:
            problems.append('no model blocks for ' + cls)
    for cls in decsim.CLASSES:
        if cls not in per:
            problems.append('no model blocks for ' + cls)
            continue
        d = decsim.explore(decsim.load(cls))
        keyed = set().union(*[set(b['keys']) for b in per[cls]])
        for s, f in set(d['weapon']) | set(d['flash']):
            if s in ('TNT1', '?') or len(s) != 4:
                continue
            if (s, f) not in keyed:
                uncovered.setdefault(cls, []).append(s + f)
    for cls, v in uncovered.items():
        problems.append('%s shows flat sprites: %s' % (cls, ' '.join(sorted(v))))

    # 2. expected source frame for every key
    def expect_old(cls, b):
        old = oldb[cls]
        exp = {}
        for k, p in old['keys'].items():
            if k[0] == 'TNT1' or FT.hand_mesh_for(k[0]):
                continue
            if any(k in sp['keys'] for sp in FT.WORLD.get(cls, [])):
                continue    # moved to the class's world block
            if cls in TABLES:
                exp[k] = TABLES[cls][k]
            elif k in FT.GUN_TABLES.get(cls, {}):
                exp[k] = FT.GUN_TABLES[cls][k]
            elif cls == 'BIG_FUCKING_GUN':
                exp[k] = FT.BFG_LEVEL[k]
            elif cls == 'RailGun':
                exp[k] = FT.railgun_level(k[0], k[1], p)
            else:
                exp[k] = p
        if cls == 'FlameCannon':
            for k in FLAMECANNON_ADD:
                exp[k] = TABLES[cls][k]
        for k in b['keys']:
            if k not in exp and k in FT.GUN_TABLES.get(cls, {}):
                exp[k] = FT.GUN_TABLES[cls][k]
            if k not in exp:
                base = FT.SIBLING.get(cls, {}).get(k[0], 'none')
                if base == 'none':
                    problems.append('%s: unexpected key %s%s' % (cls, k[0], k[1]))
                    continue
                v = exp.get((base, k[1])) if base else None
                exp[k] = FT.READY[cls] if v is None else v
        missing = set(exp) - set(b['keys'])
        if missing:
            problems.append('%s lost keys %s' % (cls, sorted(missing)))
        return exp

    checked = 0
    new_specs = {}
    for cls, specs in list(FT.NEW.items()) + list(FT.WORLD.items()):
        for sp in specs:
            new_specs.setdefault(cls, []).append(sp)
    for b in newb:
        cls, mesh = b['cls'], b['mesh']
        world = [s for s in FT.WORLD.get(cls, []) if set(s['keys']) == set(b['keys'])]
        if world:
            sp = world[0]
            exp = sp['keys']
            if b['path'] != sp['path'] or b['mesh'] != sp['mesh'] or b['skins'] != [v for _, v in sorted(sp['skins'].items())]:
                problems.append('%s: files %s %s %s' % (cls, b['path'], b['mesh'], b['skins']))
            if [x for x in b['other'] if not re.match(r'(Path|Model|Skin|SurfaceSkin)\b', x)] != sp['placement']:
                problems.append('%s: placement %s' % (cls, b['other']))
        elif mesh in HAND:
            path, skin, placement = HAND[mesh]
            fams = FT.HAND_SPECS[mesh]
            exp = {k: FT.family_pose(fams, *k) for k in b['keys']}
            if any(v is None for v in exp.values()):
                problems.append('%s %s: key outside the family maps' % (cls, mesh))
            if not set(AUTHORED_HAND[mesh]) <= set(b['keys']):
                problems.append('%s %s: authored keys missing' % (cls, mesh))
            wantpl = FT.HAND_WEAPONS[cls][1] if FT.HAND_WEAPONS.get(cls, (None,))[0] == mesh else placement
            if b['other'][3:] != wantpl or b['path'] != path or b['skins'] != [skin]:
                problems.append('%s %s: placement %s' % (cls, mesh, b['other']))
        elif cls in FT.NEW or (cls in FT.WORLD and cls not in oldb):
            sp = [s for s in new_specs[cls] if set(s['keys']) == set(b['keys'])]
            if len(sp) != 1:
                problems.append('%s: block keys match no spec' % cls)
                continue
            sp = sp[0]
            exp = sp['keys']
            if b['path'] != sp['path'] or b['mesh'] != sp['mesh'] or b['skins'] != [v for _, v in sorted(sp['skins'].items())]:
                problems.append('%s: files %s %s %s' % (cls, b['path'], b['mesh'], b['skins']))
            if [x for x in b['other'] if not re.match(r'(Path|Model|Skin|SurfaceSkin)\b', x)] != sp['placement']:
                problems.append('%s: placement %s' % (cls, b['other']))
        elif cls in oldb:
            a = list(oldb[cls]['other'])
            if cls == 'MP40':
                a = [x.replace('Dual_MP40.md3', 'MP40.md3') for x in a]
            if cls == 'Chain_saw':
                a = [x.replace('BloodB.png', 'Chain_saw.png') for x in a]
            if a != b['other']:
                problems.append('placement changed in %s: %s -> %s' % (cls, a, b['other']))
            exp = expect_old(cls, b)
        else:
            problems.append('unknown class block ' + cls)
            continue
        mp = (b['path'] + '/' + mesh).lower()
        if mp not in names_new:
            problems.append('missing mesh ' + mp)
            continue
        for s in b['skins']:
            if (b['path'] + '/' + s).lower() not in names_new:
                problems.append('missing skin %s/%s' % (b['path'], s))
        if mp.endswith('.iqm'):
            from restore_and_strip import iqm_frames
            n_new, n_src = iqm_frames(zn.read(names_new[mp])), iqm_frames(src[mp])
            if zn.read(names_new[mp]) != src[mp]:
                problems.append('%s: shipped IQM differs from source' % mp)
            for k, pose in b['keys'].items():
                if pose >= n_new or exp.get(k) != pose:
                    problems.append('%s %s%s: IQM frame %d wrong (want %s of %d)' % (cls, k[0], k[1], pose, exp.get(k), n_new))
                checked += 1
            continue
        mn, ms = parse(zn.read(names_new[mp])), parse(src[mp])
        for k, pose in b['keys'].items():
            want = exp.get(k)
            if want is None:
                continue
            if pose >= mn['nfr'] or want >= ms['nfr']:
                problems.append('%s %s%s: frame out of range' % (cls, k[0], k[1]))
            elif frame_blob(mn, pose) != frame_blob(ms, want):
                problems.append('%s %s %s%s: draws wrong geometry' % (cls, mesh, k[0], k[1]))
            checked += 1

    # 3. no stray files; every md3 sane
    referenced = {'modeldef.bd.txt'}
    for b in newb:
        referenced.add((b['path'] + '/' + b['mesh']).lower())
        referenced |= {(b['path'] + '/' + s).lower() for s in b['skins']}
    import weapon_patch as WP
    wfiles = {(WP.PK3_DIR + n).lower() for n in {e[0] for e in WP.EDITS} | {i[0] for i in WP.INSERTS}}
    for n in zn.namelist():
        if n.lower() in wfiles:
            mine = open(os.path.join(decorate_dir, os.path.basename(n)), encoding='latin-1', newline='').read()
            if zn.read(n).decode('latin-1') != mine:
                problems.append('shipped weapon file differs from the one checked: ' + n)
    if len([n for n in zn.namelist() if n.lower() in wfiles]) != len(wfiles):
        problems.append('weapon files missing from pk3')
    from restore_and_strip import vrmelee_files
    vfiles = vrmelee_files()
    for n, data in vfiles.items():
        if n not in zn.NameToInfo:
            problems.append('VR melee file missing: ' + n)
        elif zn.read(n) != data:
            problems.append('VR melee file differs from tool/vrmelee: ' + n)
    vlow = {n.lower() for n in vfiles}
    stray = [n for n in zn.namelist() if n.lower() not in referenced and n.lower() not in wfiles
             and n.lower() not in vlow and not n.endswith('/')]
    if stray:
        problems.append('unreferenced files shipped: %s' % stray)
    for n in zn.namelist():
        if n.lower().endswith('.iqm'):
            from restore_and_strip import iqm_frames
            iqm_frames(zn.read(n))
        if n.lower().endswith('.md3'):
            d = zn.read(n)
            ident, ver = struct.unpack_from('<4si', d, 0)
            nfr, ntag, nsurf, nskin, ofr, otag, osurf, oend = struct.unpack_from('<8i', d, 76)
            if ident != b'IDP3' or ver != 15 or oend != len(d) or nfr < 1:
                problems.append('bad md3 header ' + n)

    # 4. every keyed sprite is registered (an unknown sprite in MODELDEF is fatal)
    noart = set()
    for b in newb:
        for s, f in b['keys']:
            if s not in registered:
                problems.append('%s keys unregistered sprite %s (fatal)' % (b['cls'], s))
            elif s not in art and s not in ('PLAY', 'CSAW'):
                noart.add(s)
    print('keyed sprites with no art (registered by DECORATE, legal):', sorted(noart))

    # 5. every class exists in BD22 DECORATE
    classes = set()
    for p in glob.glob(os.path.join(decorate_dir, '**', '*'), recursive=True):
        if os.path.isfile(p):
            for m in re.finditer(r'^\s*actor\s+([A-Za-z0-9_]+)', open(p, errors='replace').read(), re.I | re.M):
                classes.add(m.group(1).lower())
    for c in per:
        if c.lower() not in classes:
            problems.append('class not in BD22: ' + c)

    # 6. the new weapons' world pickups: which keys also draw the dropped item
    for cls in FT.NEW:
        sp = decsim.spawn_pairs(cls)
        hit = sorted(set().union(*[set(b['keys']) for b in per[cls]]) & sp)
        if hit:
            print('note: %s pickup sprite %s is keyed (pickup draws the model)' % (cls, hit))

    print('classes:', len(per), ' blocks:', len(newb), ' frame lines checked by geometry:', checked)
    print('problems:', len(problems))
    for p in problems:
        print('  ', p)
    return not problems


if __name__ == '__main__':
    sys.exit(0 if main(*sys.argv[1:6]) else 1)
