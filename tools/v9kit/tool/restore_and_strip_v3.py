#!/usr/bin/env python3
"""Fix RS_BD22_Models.pk3 as a models-only pack. Writes a NEW pk3; never edits the old one.

  1. Restore the authored poses on AssaultShotgun, Plasma_Gun, GrenadeLauncher,
     FlameCannon (pose_tables.py). FlameCannon also gets its eight fire frames
     keyed (they were never keyed, so it vanished whenever it fired).
  2. Remove every TNT1 FrameIndex line (TNT1 is BD22's "draw nothing").
  3. MP40 back on MP40.md3 (it was drawing Dual_MP40.md3) and Chain_saw back on
     Chain_saw.png (it was skinned with BloodB.png). Both were first-file-in-folder
     picks by the generator; fixing them first is what makes step 4 drop the
     right files.
  4. Ship only the meshes and skins MODELDEF references, and in each mesh only
     the frames some FrameIndex line uses; FrameIndex numbers are remapped.

    python restore_and_strip.py OLD.pk3 NEW.pk3
"""
import io, re, sys, zipfile, hashlib, json
from md3strip import strip, verify, parse
from pose_tables import TABLES, FLAMECANNON_ADD
from hands_blocks import keys as hand_keys, block_text

FI = re.compile(r'^(\s*FrameIndex\s+)(\S+)(\s+)(\S+)(\s+)(\d+)(\s+)(\d+)(.*)$', re.I)
BLOCK = re.compile(r'^Model\s+(\S+)\s*$')


def split_blocks(text):
    """[(name or None, [lines])] keeping every line, in order."""
    lines = text.split('\n')
    starts = []                       # (first line of block incl. its comments, name)
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


def block_path(lines):
    for ln in lines:
        m = re.match(r'^\s*Path\s+"([^"]+)"', ln, re.I)
        if m:
            return m.group(1)
    return None


def main(src, dst):
    zin = zipfile.ZipFile(src)
    files = {n: zin.read(n) for n in zin.namelist() if not n.endswith('/')}
    text = files['MODELDEF.bd.txt'].decode('latin-1')
    blocks = split_blocks(text)
    report = {'removed_tnt1': {}, 'pose_changes': {}, 'added_keys': {}, 'fixes': []}

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
                if table is not None:
                    key = (spr, fr.upper())
                    if key not in table:
                        raise SystemExit('no authored pose for %s %s %s' % (name, spr, fr))
                    newpose = table[key]
                    if newpose != pose:
                        report['pose_changes'].setdefault(name, 0)
                        report['pose_changes'][name] += 1
                    ln = '%s%s%s%s%s%s%s%d%s' % (m.group(1), m.group(2), m.group(3), m.group(4),
                                                 m.group(5), m.group(6), m.group(7), newpose, m.group(9))
                out.append(ln)
                continue
            # per-block text fixes
            if name == 'MP40' and re.match(r'^\s*Model\s+0\s+"Dual_MP40\.md3"', ln):
                ln = ln.replace('Dual_MP40.md3', 'MP40.md3')
                report['fixes'].append('MP40: Model 0 Dual_MP40.md3 -> MP40.md3 (authored mesh)')
            if name == 'Chain_saw' and re.match(r'^\s*Skin\s+0\s+"BloodB\.png"', ln):
                ln = ln.replace('BloodB.png', 'Chain_saw.png')
                report['fixes'].append('Chain_saw: Skin 0 BloodB.png -> Chain_saw.png (authored skin)')
            if re.match(r'^// NOTE the authored block.s mesh was MP40\.md3; we ship Dual_MP40\.md3\.', ln):
                continue
            if re.match(r'^// Pose: ', ln) and table is not None:
                ln = ('// Pose: restored 2026-10-10 -- each BD22 sprite frame takes the authored\n'
                      '// BD21 pose for the same moment of the animation (tools/pose_tables.py).')
            if re.match(r'^// within their action, ', ln) and table is not None:
                continue
            out.append(ln)
        if name == 'FlameCannon':
            last = max(i for i, l in enumerate(out) if FI.match(l))
            add = ['   FrameIndex\t%s\t%s\t0\t%d' % (s, f, TABLES['FlameCannon'][(s, f)]) for s, f in FLAMECANNON_ADD]
            out[last + 1:last + 1] = add
            report['added_keys'][name] = ['%s %s' % k for k in FLAMECANNON_ADD]
        new_blocks.append((name, out))

    # ---------------------------------------------------------------- step 3b
    # The authored BD21 boot / fist / grenade blocks, on every gun class.
    guns = [n for n, _ in new_blocks if n]
    for cls in guns:
        for spec, km in hand_keys():
            new_blocks.append((cls, [''] + block_text(cls, spec, km)))
    report['fixes'].append('boot, fist and grenade blocks restored on %d guns' % len(guns))

    # ---------------------------------------------------------------- step 4
    # referenced files and the frames each mesh needs
    used = {}          # mesh zip path -> set(frames)
    skins = set()
    for name, lines in new_blocks:
        if name is None:
            continue
        path = block_path(lines).rstrip('/')
        mesh = path + '/' + block_attr(lines, 'Model')
        skin = block_attr(lines, 'Skin')
        if skin:
            skins.add(path + '/' + skin)
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
            raise SystemExit('referenced file missing from pk3: ' + p)
        return k

    remap, newmesh, mesh_report = {}, {}, {}
    for mesh, frs in used.items():
        k = real(mesh)
        data = files[k]
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

    # renumber FrameIndex
    final_blocks = []
    for name, lines in new_blocks:
        if name is None:
            final_blocks.append(lines)
            continue
        path = block_path(lines).rstrip('/')
        mesh = (path + '/' + block_attr(lines, 'Model')).lower()
        rm = remap[mesh]
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
        '// PATCHED 2026-10-10 by restore_and_strip.py (models-only, no code):',
        '//   - authored poses restored on AssaultShotgun, Plasma_Gun, GrenadeLauncher,',
        '//     FlameCannon, and the eight FlameCannon fire frames keyed',
        '//   - TNT1 keys removed (TNT1 means "draw nothing" in BD22)',
        '//   - authored BD21 boot (kick), fist (taunt) and grenade blocks restored',
        '//     on every gun, so those moves draw models, not flat sprites',
        '//   - MP40 on MP40.md3, Chain_saw skinned Chain_saw.png (authored files)',
        '//   - meshes carry only the frames used below; FrameIndex numbers are',
        '//     indices into those stripped meshes, NOT into the source meshes.',
        '// Re-running gen_bd22_modeldef.py over this file would undo all of this.',
        '// ---------------------------------------------------------------------------',
    ]
    out_text = '\n'.join(sum(final_blocks, []))
    # insert the note right after the generator's banner
    bannerend = out_text.find('// ===========================================================================', 10)
    bannerend = out_text.find('\n', bannerend) + 1
    out_text = out_text[:bannerend] + '\n'.join(header_note) + '\n' + out_text[bannerend:]

    keepfiles = {'MODELDEF.bd.txt': out_text.encode('latin-1')}
    for k, v in newmesh.items():
        keepfiles[k] = v
    for s in skins:
        k = real(s)
        keepfiles[k] = files[k]

    dropped = sorted(set(files) - set(keepfiles))
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # same order as the source pk3, MODELDEF first
        for n in zin.namelist():
            if n in keepfiles:
                zi = zipfile.ZipInfo(n, date_time=zin.getinfo(n).date_time)
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = zin.getinfo(n).external_attr
                z.writestr(zi, keepfiles[n], compresslevel=9)

    report['meshes'] = mesh_report
    report['dropped_files'] = dropped
    report['kept_files'] = sorted(keepfiles)
    return report


if __name__ == '__main__':
    rep = main(sys.argv[1], sys.argv[2])
    json.dump(rep, open(sys.argv[2] + '.report.json', 'w'), indent=1, default=list)
    print(json.dumps({k: rep[k] for k in ('removed_tnt1', 'pose_changes', 'added_keys', 'fixes')}, indent=1))
    print('dropped', len(rep['dropped_files']), 'files')
