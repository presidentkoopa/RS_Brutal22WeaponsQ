#!/usr/bin/env python3
"""Build the BD22 models pack from RS_BD22_Models.pk3. Writes a NEW pk3; never
edits the old one. Models only: no DECORATE, ZScript or ACS.

  1. Authored poses on AssaultShotgun, Plasma_Gun, GrenadeLauncher, FlameCannon
     (pose_tables.py); FlameCannon's eight fire frames keyed.
  2. TNT1 keys removed (TNT1 is BD22's "draw nothing"). Empty-hand frames a
     gun block had on the gun (BrutalAxe throw, Rifle knuckle crack) move to
     the fist block.
  3. MP40 on MP40.md3, Chain_saw skinned Chain_saw.png (authored files).
  4. BIG_FUCKING_GUN and RailGun put on their level poses (fill_tables.py).
  5. Every frame BD22 can show on a gun that had no key gets one: colour,
     purist and dual copies take their base sprite's pose for the same letter,
     anything else the gun's ready pose.
  6. Boot, fist and grenade blocks on every weapon, covering every kick, slide,
     stomp, taunt, punch, execution, grab and grenade frame BD22 can show.
  7. Models for the eight weapons that had none: Melee_Attacks (fists),
     HandGrenades, MG42, BFG10k, Sniper, IncendiaryLauncher, NukeLauncher,
     Devastator.
  9. Replacement copies of five BD22 weapon files (weapon_patch.py) so the gun
     stays on screen where BD22 blanked it mid-use. LOAD THIS PK3 AFTER BD22.
  8. Ship only referenced files, and in each mesh only the frames used;
     FrameIndex numbers are remapped.

    python restore_and_strip.py OLD.pk3 NEW.pk3 WEAPONSETS_DIR bd22_displayed.json BD22.pk3 [--deflate-only]

Meshes are stored with zip LZMA (method 14), which QuestZDoom 17.3 reads
(src/common/filesystem/source/file_zip.cpp); it halves the pack.

WEAPONSETS_DIR is VR_WeaponSetRebuild\\WeaponSets (source of the new models).
bd22_displayed.json lists, per class, every (sprite, frame) BD22's DECORATE can
put on the weapon or flash layer (made by decsim.py from brutal22test6.pk3).
"""
import io, os, re, sys, zipfile, json, struct
from md3strip import strip, verify, parse
from pose_tables import TABLES, FLAMECANNON_ADD
import fill_tables as FT
import weapon_patch as WP

DEFLATE_ONLY = False      # --deflate-only: every entry deflate (bigger file)

FI = re.compile(r'^(\s*FrameIndex\s+)(\S+)(\s+)(\S+)(\s+)(\d+)(\s+)(\d+)(.*)$', re.I)
BLOCK = re.compile(r'^Model\s+(\S+)\s*$')

HAND = {   # mesh -> (path, skin, placement)  authored BD21 hand blocks
    'nade.md3': ('models/bd/Grenade', 'nade.png',
                 ['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'NoInterpolation', 'ZOffset -5']),
    'Boot.md3': ('models/bd/Boot', 'Boot.png',
                 ['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'NoInterpolation', 'ZOffset -5']),
    'fistclosed.md3': ('models/bd/FIST', 'fist.png',
                       ['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'ZOffset -5']),
}
# authored BD21 keys every gun carries (Modeldef.<gun>.def); KIKF has no BD22 art
AUTHORED_HAND = {
    'nade.md3': [('GRTH', c) for c in 'ABCDEFGHIJKLM'],
    'Boot.md3': ([('KIK1', c) for c in 'ABCDE'] + [('KIK2', c) for c in 'ABCDE'] +
                 [('KICK', c) for c in 'ABCDEFGHIJKLMNOPQRSTU'] + [('STOM', c) for c in 'ABCDE']),
    'fistclosed.md3': [('FUCK', c) for c in 'ABCDEFGHIJKLMNO'],
}


def split_blocks(text):
    """[(name or None, [lines])] keeping every line, in order."""
    lines = text.split('\n')
    starts = []
    for i, ln in enumerate(lines):
        m = BLOCK.match(ln)
        if m:
            j = i
            while j > 0 and lines[j - 1].startswith('//') and not lines[j - 1].startswith('// ====='):
                j -= 1
            starts.append((j, m.group(1)))
    out = [(None, lines[:starts[0][0]])]
    for k, (j, name) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        out.append((name, lines[j:end]))
    assert sum(len(ls) for _, ls in out) == len(lines)
    return out


def block_attr(lines, key):
    for ln in lines:
        m = re.match(r'^\s*' + key + r'\s+0\s+"([^"]+)"', ln, re.I)
        if m:
            return m.group(1)
    return None


def block_skins(lines):
    out = []
    for ln in lines:
        m = re.match(r'^\s*(?:Skin\s+0|SurfaceSkin\s+0\s+\d+)\s+"([^"]+)"', ln, re.I)
        if m:
            out.append(m.group(1))
    return out


def block_path(lines):
    for ln in lines:
        m = re.match(r'^\s*Path\s+"([^"]+)"', ln, re.I)
        if m:
            return m.group(1)
    return None


def block_keys(lines):
    return {(m.group(2).upper(), m.group(4).upper()): int(m.group(8)) for m in map(FI.match, lines) if m}


def emit(cls, comment, path, mesh, skins, placement, keys):
    out = ['', '// %s -- %s' % (cls, comment), 'Model %s' % cls, '{',
           '   Path "%s"' % path, '   Model 0 "%s"' % mesh]
    if list(skins) == [0]:
        out.append('   Skin 0 "%s"' % skins[0])
    else:
        out += ['   SurfaceSkin 0 %d "%s"' % (i, s) for i, s in sorted(skins.items())]
    out += ['   ' + p for p in placement]
    out.append('')
    for (s, f), p in sorted(keys.items()):
        out.append('   FrameIndex\t%s\t%s\t0\t%d' % (s, f, p))
    out.append('}')
    return out


def iqm_frames(data):
    if data[:16] != b'INTERQUAKEMODEL\0':
        raise ValueError('not an IQM')
    return struct.unpack_from('<I', data, 16 + 4 * 19)[0]      # header field num_frames


def source_files(weaponsets):
    """target zip path -> bytes, for the meshes/skins not in the old pk3."""
    out = {}
    for cls, specs in FT.NEW.items():
        for sp in specs:
            if sp['src'] == 'pk3':
                continue
            names = [sp['mesh']] + sorted(set(sp['skins'].values()))
            if sp['src'].startswith('b35:'):
                z = zipfile.ZipFile(os.path.join(weaponsets, 'UNUSED', '_zips', 'BR_VR__B35_Quest.zip'))
                low = {n.lower(): n for n in z.namelist()}
                for n in names:
                    out[sp['path'] + '/' + n] = z.read(low['models/weapons/hud/hitlersbuzzsaw/' + n.lower()])
            else:
                d = os.path.join(weaponsets, *sp['src'].split('/'))
                low = {n.lower(): n for n in os.listdir(d)}
                assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
                for n in names:
                    if n.lower() in low:
                        out[sp['path'] + '/' + n] = open(os.path.join(d, low[n.lower()]), 'rb').read()
                    else:   # our own file (tool/assets): the transparent skin
                        out[sp['path'] + '/' + n] = open(os.path.join(assets, n), 'rb').read()
    return out


VRMELEE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vrmelee')


def vrmelee_files():
    """pk3 path -> bytes: the VR melee scripts (tool/vrmelee), shipped as they are"""
    out = {}
    for root, _, fs in os.walk(VRMELEE):
        for f in sorted(fs):
            full = os.path.join(root, f)
            out[os.path.relpath(full, VRMELEE).replace(os.sep, '/')] = open(full, 'rb').read()
    return out


def main(src, dst, weaponsets, displayed_json, bd22_pk3):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist() if not n.endswith('/')}
    extra = source_files(weaponsets)
    files.update(extra)
    info = json.load(open(displayed_json))
    shown = {c: [tuple(p) for p in v] for c, v in info['displayed'].items()}
    # Every shown sprite is named by a DECORATE state, so the engine registers
    # it (info.cpp GetSpriteIndex) before MODELDEF is read; models.cpp only
    # rejects names it never saw. Sprites with no art (SALU, VGRN, ...) are
    # keyed too: in flat BD22 they draw nothing, here they draw the model.

    text = files['MODELDEF.bd.txt'].decode('latin-1')
    blocks = split_blocks(text)
    report = {'removed_tnt1': {}, 'pose_changes': {}, 'added_keys': {}, 'fixes': [], 'new_classes': {}}

    # ------------------------------------------------------------- steps 1-4
    new_blocks = []
    for name, lines in blocks:
        if name is None:
            new_blocks.append((name, lines))
            continue
        out = []
        table = TABLES.get(name)
        for ln in lines:
            m = FI.match(ln)
            if m:
                spr, fr, pose = m.group(2).upper(), m.group(4), int(m.group(8))
                if spr == 'TNT1':
                    report['removed_tnt1'].setdefault(name, []).append(fr)
                    continue
                if any((spr, fr.upper()) in sp['keys'] for sp in FT.WORLD.get(name, [])):
                    # the item in the world (fill_tables.WORLD) has its own block
                    report.setdefault('moved_to_world', {}).setdefault(name, []).append(spr + fr)
                    continue
                if FT.hand_mesh_for(spr):
                    # an empty-hand frame (axe thrown, knuckle crack): the hand
                    # block draws it, not the gun at its ready pose
                    report.setdefault('moved_to_hand', {}).setdefault(name, []).append(spr + fr)
                    continue
                newpose = pose
                if table is not None:
                    if (spr, fr.upper()) not in table:
                        raise SystemExit('no authored pose for %s %s %s' % (name, spr, fr))
                    newpose = table[(spr, fr.upper())]
                elif name in FT.GUN_TABLES and (spr, fr.upper()) in FT.GUN_TABLES[name]:
                    newpose = FT.GUN_TABLES[name][(spr, fr.upper())]
                elif name == 'BIG_FUCKING_GUN':
                    newpose = FT.BFG_LEVEL[(spr, fr.upper())]
                elif name == 'RailGun':
                    newpose = FT.railgun_level(spr, fr.upper(), pose)
                if newpose != pose:
                    report['pose_changes'][name] = report['pose_changes'].get(name, 0) + 1
                out.append('%s%s%s%s%s%s%s%d%s' % (m.group(1), m.group(2), m.group(3), m.group(4),
                                                   m.group(5), m.group(6), m.group(7), newpose, m.group(9)))
                continue
            if name == 'MP40' and re.match(r'^\s*Model\s+0\s+"Dual_MP40\.md3"', ln):
                ln = ln.replace('Dual_MP40.md3', 'MP40.md3')
                report['fixes'].append('MP40: Model 0 Dual_MP40.md3 -> MP40.md3 (authored mesh)')
            if name == 'Chain_saw' and re.match(r'^\s*Skin\s+0\s+"BloodB\.png"', ln):
                ln = ln.replace('BloodB.png', 'Chain_saw.png')
                report['fixes'].append('Chain_saw: Skin 0 BloodB.png -> Chain_saw.png (authored skin)')
            if re.match(r'^// NOTE the authored block.s mesh was MP40\.md3; we ship Dual_MP40\.md3\.', ln):
                continue
            if re.match(r'^// Pose: ', ln) and (table is not None or name in FT.GUN_TABLES or name in ('BIG_FUCKING_GUN', 'RailGun')):
                ln = ('// Pose: restored 2026-10-10 -- each BD22 sprite frame takes the authored\n'
                      '// BD21 pose for the same moment (tools/pose_tables.py, fill_tables.py).')
            if re.match(r'^// within their action, ', ln) and (table is not None or name in FT.GUN_TABLES or name in ('BIG_FUCKING_GUN', 'RailGun')):
                continue
            out.append(ln)
        if name == 'FlameCannon':
            last = max(i for i, l in enumerate(out) if FI.match(l))
            add = ['   FrameIndex\t%s\t%s\t0\t%d' % (s, f, TABLES['FlameCannon'][(s, f)]) for s, f in FLAMECANNON_ADD]
            out[last + 1:last + 1] = add
            report['added_keys'][name] = ['%s %s' % k for k in FLAMECANNON_ADD]
        new_blocks.append((name, out))

    # ---------------------------------------------------------------- step 5
    old_guns = [n for n, _ in new_blocks if n]
    for i, (name, lines) in enumerate(new_blocks):
        if name is None:
            continue
        keyed = block_keys(lines)
        add = {}
        for spr, fr in shown[name]:
            if FT.hand_mesh_for(spr) or (spr, fr) in keyed:
                continue
            if (spr, fr) in FT.GUN_TABLES.get(name, {}):
                add[(spr, fr)] = FT.GUN_TABLES[name][(spr, fr)]
                continue
            if spr not in FT.SIBLING.get(name, {}):
                raise SystemExit('%s: no rule for shown frame %s %s' % (name, spr, fr))
            base = FT.SIBLING[name][spr]
            pose = keyed.get((base, fr)) if base else None
            add[(spr, fr)] = FT.READY[name] if pose is None else pose
        if add:
            last = max(j for j, l in enumerate(lines) if FI.match(l))
            lines[last + 1:last + 1] = (['   // v4: frames BD22 shows that had no key (fill_tables.py SIBLING/READY)'] +
                                        ['   FrameIndex\t%s\t%s\t0\t%d' % (s, f, p) for (s, f), p in sorted(add.items())])
            report['added_keys'][name] = report['added_keys'].get(name, []) + ['%s %s' % k for k in sorted(add)]

    # ---------------------------------------------------------------- step 7
    for cls, specs in FT.NEW.items():
        need = {(s, f) for s, f in shown[cls] if not FT.hand_mesh_for(s)}
        have = set()
        for sp in specs:
            have |= set(sp['keys'])
        if need - have:
            raise SystemExit('%s: shown frames with no pose: %s' % (cls, sorted(need - have)))
        for n, sp in enumerate(specs):
            new_blocks.append((cls, emit(cls, 'new in v4: %s (fill_tables.NEW)' % sp['mesh'], sp['path'],
                                         sp['mesh'], sp['skins'], sp['placement'], sp['keys'])))
        report['new_classes'][cls] = [sp['mesh'] for sp in specs]

    for cls, specs in FT.WORLD.items():
        for sp in specs:
            new_blocks.append((cls, emit(cls, sp.get('comment', 'world model'), sp['path'],
                                         sp['mesh'], sp['skins'], sp['placement'], sp['keys'])))

    # ---------------------------------------------------------------- step 6
    # each weapon's hand blocks: the authored BD21 keys plus every hand frame
    # that weapon can show (keys for frames a weapon never shows are dead weight)
    def hand_keys(cls, mesh):
        want = set(AUTHORED_HAND[mesh])
        want |= {(s, f) for s, f in shown[cls] if FT.hand_mesh_for(s) == mesh}
        km = {}
        for s, f in want:
            p = FT.family_pose(FT.HAND_SPECS[mesh], s, f)
            if p is None:
                raise SystemExit('no %s pose for %s %s' % (mesh, s, f))
            km[(s, f)] = p
        report['hand_keys'][cls + ' ' + mesh] = len(km)
        return km
    report['hand_keys'] = {}
    for cls in old_guns + list(FT.NEW) + list(FT.HAND_WEAPONS):
        for mesh, (path, skin, placement) in HAND.items():
            comment = 'authored BD21 %s block (posefix/fill_tables.py)' % mesh
            if FT.HAND_WEAPONS.get(cls, (None,))[0] == mesh:
                placement = FT.HAND_WEAPONS[cls][1]
                comment = 'new in v4: the %s weapon itself, authored placement' % mesh
                report['new_classes'][cls] = [mesh]
            new_blocks.append((cls, emit(cls, comment, path, mesh, {0: skin}, placement, hand_keys(cls, mesh))))

    # ---------------------------------------------------------------- step 8
    used, skins = {}, set()
    for name, lines in new_blocks:
        if name is None:
            continue
        path = block_path(lines).rstrip('/')
        mesh = path + '/' + block_attr(lines, 'Model')
        skins |= {path + '/' + s for s in block_skins(lines)}
        fr = used.setdefault(mesh, set())
        for l in lines:
            m = FI.match(l)
            if m:
                if int(m.group(6)) != 0:
                    raise SystemExit('model index other than 0 in %s' % name)
                fr.add(int(m.group(8)))

    lower = {k.lower(): k for k in files}

    def real(p):
        k = lower.get(p.lower())
        if not k:
            raise SystemExit('referenced file missing: ' + p)
        return k

    remap, newmesh, mesh_report = {}, {}, {}
    for mesh, frs in used.items():
        k = real(mesh)
        data = files[k]
        if k.lower().endswith('.iqm'):
            # skeletal (Breach): shipped whole, FrameIndex = the IQM's own frame numbers
            nfr = iqm_frames(data)
            bad = [f for f in frs if f >= nfr]
            if bad:
                raise SystemExit('%s: frame(s) %s out of range (%d frames)' % (mesh, bad, nfr))
            newmesh[k] = data
            remap[mesh.lower()] = {f: f for f in frs}
            mesh_report[k] = dict(frames_before=nfr, frames_after=nfr, bytes_before=len(data), bytes_after=len(data))
            continue
        nfr = parse(data)['nfr']
        bad = [f for f in frs if f >= nfr]
        if bad:
            raise SystemExit('%s: frame(s) %s out of range (%d frames)' % (mesh, bad, nfr))
        keep = sorted(frs)
        new = strip(data, keep)
        verify(data, new, keep)
        newmesh[k] = new
        remap[mesh.lower()] = {old: i for i, old in enumerate(keep)}
        mesh_report[k] = dict(frames_before=nfr, frames_after=len(keep), bytes_before=len(data), bytes_after=len(new))

    final_blocks = []
    for name, lines in new_blocks:
        if name is None:
            final_blocks.append(lines)
            continue
        path = block_path(lines).rstrip('/')
        rm = remap[(path + '/' + block_attr(lines, 'Model')).lower()]
        out = []
        for l in lines:
            m = FI.match(l)
            if m:
                l = '%s%s%s%s%s%s%s%d%s' % (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5),
                                            m.group(6), m.group(7), rm[int(m.group(8))], m.group(9))
            out.append(l)
        final_blocks.append(out)

    header_note = [
        '// ---------------------------------------------------------------------------',
        '// PATCHED 2026-10-10 by restore_and_strip.py (models-only, no code), v4:',
        '//   - authored poses on AssaultShotgun, Plasma_Gun, GrenadeLauncher,',
        '//     FlameCannon; FlameCannon fire frames keyed',
        '//   - BIG_FUCKING_GUN and RailGun on their level (authored) poses',
        '//   - TNT1 keys removed (TNT1 means "draw nothing" in BD22)',
        '//   - every frame BD22 can show on a weapon is keyed: no flat sprites',
        '//   - boot / fist / grenade blocks on every weapon: kicks, slides, taunts,',
        '//     punches, executions, grabs, grenade toss',
        '//   - new: Melee_Attacks (fistclosed), HandGrenades (nade), MG42',
        '//     (HitlersBuzzsaw), BFG10k (BFG_10k), Sniper (Kar98),',
        '//     IncendiaryLauncher (M32), NukeLauncher (Nuker), Devastator (Sidewinder)',
        '//   - MP40 on MP40.md3, Chain_saw skinned Chain_saw.png (authored files)',
        '//   - meshes carry only the frames used below; FrameIndex numbers are',
        '//     indices into those stripped meshes, NOT into the source meshes.',
        '// Re-running gen_bd22_modeldef.py over this file would undo all of this.',
        '// ---------------------------------------------------------------------------',
    ]
    out_text = '\n'.join(sum(final_blocks, []))
    bannerend = out_text.find('// ===========================================================================', 10)
    bannerend = out_text.find('\n', bannerend) + 1
    out_text = out_text[:bannerend] + '\n'.join(header_note) + '\n' + out_text[bannerend:]

    keepfiles = {'MODELDEF.bd.txt': out_text.encode('latin-1')}
    # replacement weapon files (weapon_patch.py): same paths as BD22's, so
    # BD22's #include picks ours when this pk3 loads after BD22
    zb = zipfile.ZipFile(bd22_pk3)
    names = {e[0] for e in WP.EDITS} | {i[0] for i in WP.INSERTS}
    for n, t in WP.patch({n: zb.read(WP.PK3_DIR + n).decode('latin-1') for n in names}).items():
        keepfiles[WP.PK3_DIR + n] = t.encode('latin-1')
    report['weapon_files'] = sorted(WP.PK3_DIR + n for n in names)
    keepfiles.update(vrmelee_files())
    report['vr_melee_files'] = sorted(vrmelee_files())
    keepfiles.update(newmesh)
    for s in skins:
        k = real(s)
        keepfiles[k] = files[k]

    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        order = [n for n in zin.namelist() if n in keepfiles] + sorted(n for n in keepfiles if n not in zin.NameToInfo)
        for n in order:
            if n in zin.NameToInfo:
                zi = zipfile.ZipInfo(n, date_time=zin.getinfo(n).date_time)
                zi.external_attr = zin.getinfo(n).external_attr
            else:
                zi = zipfile.ZipInfo(n, date_time=(2026, 10, 10, 12, 0, 0))
                zi.external_attr = 0o644 << 16
            # meshes LZMA (QZD reads zip method 14: file_zip.cpp / DecompressorLZMA),
            # roughly halving them; everything else deflate
            if n.lower().endswith('.md3') and not DEFLATE_ONLY:
                zi.compress_type = zipfile.ZIP_LZMA
                z.writestr(zi, keepfiles[n])
            else:
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, keepfiles[n], compresslevel=9)

    report['meshes'] = mesh_report
    report['dropped_files'] = sorted(set(zin.namelist()) - set(keepfiles))
    report['kept_files'] = sorted(keepfiles)
    return report


if __name__ == '__main__':
    if '--deflate-only' in sys.argv:
        sys.argv.remove('--deflate-only')
        DEFLATE_ONLY = True
    rep = main(*sys.argv[1:6])
    json.dump(rep, open(sys.argv[2] + '.report.json', 'w'), indent=1, default=list)
    print(json.dumps({k: rep.get(k) for k in ('removed_tnt1', 'moved_to_hand', 'pose_changes', 'fixes', 'new_classes', 'weapon_files')}, indent=1))
    print('added keys:', {k: len(v) for k, v in rep['added_keys'].items()})
    print('dropped', len(rep['dropped_files']), 'files')
