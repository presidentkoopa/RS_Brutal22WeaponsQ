#!/usr/bin/env python3
"""Build BD22_Models_v9.pk3 (load it after brutal22test6.pk3). One command:

    python3 -I -B team/build_bd22_v9.py [--reload DIR] [--hands team/hands.zs] [-o OUT]

  --reload DIR   the real VR reload release (default team/reload_release; read only)
  --hands PATH   the hands work's hands.zs (default team/hands.zs)
  -o OUT         default team/out_v9/BD22_Models_v9.pk3

v9 = out/RS_BD22_Models_v8.pk3 with (everything else copied from v8 with the same bytes,
zip method and date):
  actors/Weapons/*.dec   BD22's originals + tool/weapon_patch.py EDITS and INSERTS (gun kept on
                         screen, first pickup, axe throw) with GATES = [] (no immersive pauses).
                         Guns the reload release covers (Rifle.dec) come from DIR/src instead,
                         checked to be that same file with only lines inserted.
  zscript/rsq/reload.zs  gone; zscript/rsq/handler.zs (team/v9src) keeps what hands.zs needs.
  zscript/rsq/hands.zs   team/hands.zs + DIR/tools/hands_hook.py + GunH + y = WEAPONTOP for the
                         hand layers - v8's carried-ammo states.
  zscript/rsq/handtable.zs, MODELDEF.rsq, models/rsq/hand.md3   team/melee_hands/gen (axe 24,
                         chainsaw 25; guns 1-23 unchanged, checked), minus v8's carried ammo.
  zscript/rsq/gunmoves.zs  team/gunmoves_bd22.zs.
  zscript/rsvr/vrhand.zs, zscript/rsr/*, MODELDEF.rsr, CVARINFO.rsr, rsr_clear.png   the reload.
  ZSCRIPT.rsvr, MAPINFO.rsvr, MENUDEF.rsq, CVARINFO.rsq   v9 (team/v9src).
  models/rsq/ mag / shell / rocket / cell meshes and skins   gone (v8 carried ammo).
"""
import argparse, difflib, importlib.util, os, re, sys, zipfile

sys.dont_write_bytecode = True          # never write __pycache__ into tool/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v9common as C

TEAM, S = C.TEAM, C.S
V8 = os.path.join(S, 'out', 'RS_BD22_Models_v8.pk3')
BD22 = '/mnt/user-data/uploads/DOOMWork/RS_VR_Weapons/bd22/brutal22test6.pk3'
TOOL = os.path.join(S, 'tool')
MELEE_GEN = os.path.join(TEAM, 'melee_hands', 'gen')
GUNMOVES = os.path.join(TEAM, 'v9src', 'gunmoves_bd22.zs')   # team/gunmoves_bd22.zs regenerated against the v9 hand table (v9src/gen_gunmoves_bd22.py)

OLD_HEADER_TAIL = '; "rsq gate": optional immersive reload pauses).'
NEW_HEADER_TAIL = ').'

ZSCRIPT = '''version "4.10"

// RS VR melee (posefix): real axe / Dragonslayer swings and axe throwing in VR
#include "zscript/rsvr/vrhand.zs"
#include "zscript/rsvr/melee.zs"

// RS VR hands and ballistics (zscript/rsq): options in RSQ_Options (MENUDEF.rsq)
#include "zscript/rsq/handler.zs"
#include "zscript/rsq/handtable.zs"
#include "zscript/rsq/gunmoves.zs"
#include "zscript/rsq/hands.zs"
#include "zscript/rsq/ballistics.zs"

// RS real VR reload (zscript/rsr, from the reload release)
%s'''
MAPINFO = '''// RS VR melee (posefix): zscript/rsvr/melee.zs
// RS VR hands and ballistics: zscript/rsq. Real VR reload: zscript/rsr
gameinfo
{
	AddEventHandlers = "RSVR_MeleeHandler", "RSQ_Handler", "RSQ_Ballistics", %s
}
'''


def load_weapon_patch():
    spec = importlib.util.spec_from_file_location('weapon_patch_v9', os.path.join(TOOL, 'weapon_patch.py'))
    wp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wp)
    return wp


def frames_of(line):
    """number of states a DECORATE state line makes (0 for labels / flow / blanks)"""
    s = line.split('//')[0].strip()
    if not s or s.endswith(':') or s.split()[0].lower() in ('goto', 'stop', 'loop', 'wait', 'fail', '{', '}'):
        return 0
    toks, i = [], 0
    while len(toks) < 2 and i < len(s):
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i >= len(s):
            break
        if s[i] == '"':
            j = s.index('"', i + 1)
            toks.append(s[i + 1:j])
            i = j + 1
        else:
            j = i
            while j < len(s) and s[j] not in ' \t':
                j += 1
            toks.append(s[i:j])
            i = j
    return len(toks[1]) if len(toks) == 2 else 0


def states_total(lines):
    """states made by the lines inside States { } blocks"""
    tot, depth, inside, want = 0, 0, False, False
    for ln in lines:
        s = ln.split('//')[0].strip()
        if not inside:
            if s.lower().startswith('states'):
                want = True
                s = s[6:].strip()
            if want and s.startswith('{'):
                inside, want, depth = True, False, 0
            else:
                continue
        depth += s.count('{') - s.count('}')
        if depth <= 0:
            inside = False
            continue
        tot += frames_of(ln)
    return tot


def weapon_files(log):
    """{pk3 path: bytes} of the 18 weapon files without gates, checked"""
    wp = load_weapon_patch()
    gates = list(wp.GATES)
    names = sorted({e[0] for e in wp.EDITS} | {i[0] for i in wp.INSERTS})
    zb = zipfile.ZipFile(BD22)
    orig = {n: zb.read(wp.PK3_DIR + n).decode('latin-1') for n in names}
    z8 = zipfile.ZipFile(V8)
    # provenance: the unmodified patcher (with GATES) reproduces v8's files exactly
    with_gates = wp.patch(dict(orig))
    for n in names:
        if with_gates[n].encode('latin-1') != z8.read(wp.PK3_DIR + n):
            raise SystemExit('%s: weapon_patch.py with GATES does not reproduce v8' % n)
    log.append('  (weapon_patch.py with its GATES reproduces all %d v8 weapon files byte for byte)' % len(names))
    wp.GATES = []                                 # the only change: no immersive reload pauses
    out = wp.patch(dict(orig))
    split_b = {g[6][1] for g in gates if g[6]}
    split_full = {g[4] for g in gates if g[6]}
    waits = {'%s 1 A_WeaponReady(%s)' % (g[5], wp.GATE_WAIT[g[2]]) for g in gates}
    res = {}
    for n in names:
        t = out[n]
        nl = '\r\n' if '\r\n' in orig[n] else '\n'
        head, _, body = t.partition(nl)
        if not head.endswith(OLD_HEADER_TAIL):
            raise SystemExit('%s: unexpected header %r' % (n, head))
        head = head[:-len(OLD_HEADER_TAIL)] + NEW_HEADER_TAIL
        t = head + nl + body
        if re.search('rsq', t, re.I):
            raise SystemExit('%s: still mentions rsq' % n)

        # 1. against BD22's original: only EDITS (same state count) and INSERTS
        ol = orig[n].split(nl)
        nlines = t.split(nl)[1:]
        for f, at, add in wp.INSERTS:
            if f == n:
                if nlines[at:at + len(add)] != add:
                    raise SystemExit('%s: insert not where expected' % n)
                del nlines[at:at + len(add)]
        if len(nlines) != len(ol):
            raise SystemExit('%s: line count %d vs BD22 %d' % (n, len(nlines), len(ol)))
        edits = {e[1]: e for e in wp.EDITS if e[0] == n}
        for k, (a, b) in enumerate(zip(ol, nlines), 1):
            if a == b:
                continue
            if k not in edits:
                raise SystemExit('%s:%d changed but not an EDIT' % (n, k))
            if frames_of(a) != frames_of(b):
                raise SystemExit('%s:%d EDIT changes the state count %d -> %d' % (n, k, frames_of(a), frames_of(b)))
        ins = sum(len(i[2]) for i in wp.INSERTS if i[0] == n)
        ins_states = sum(frames_of(x) for i in wp.INSERTS if i[0] == n for x in i[2])
        tot_o = states_total(ol)
        tot_n = states_total(t.split(nl)[1:])

        # 2. against v8: only gate lines (and the header, and the rejoined split line) differ
        v8l = z8.read(wp.PK3_DIR + n).decode('latin-1').split(nl)
        v9l = t.split(nl)
        removed = added = 0
        sm = difflib.SequenceMatcher(None, v8l, v9l, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal':
                continue
            for x in v8l[i1:i2]:
                if not (re.search('rsq', x, re.I) or x.strip() in split_b | waits or x.startswith('// posefix: BD22')):
                    raise SystemExit('%s: v8 line removed that is not a gate: %r' % (n, x))
                removed += 1
            for x in v9l[j1:j2]:
                if not (x.startswith('// posefix: BD22') or x.strip() in split_full):
                    raise SystemExit('%s: line added vs v8 that is not the header / a rejoined line: %r' % (n, x))
                added += 1
        g8 = sum(1 for g in gates if g[0] == n)
        tot_8 = states_total(v8l)
        if tot_8 != tot_o + ins_states + 6 * g8:
            raise SystemExit('%s: v8 states %d != BD22 %d + inserts %d + 6 x %d gates' % (n, tot_8, tot_o, ins_states, g8))
        log.append('  %-24s edits %2d  inserts %2d lines/%2d states  states BD22 %4d -> v9 %4d (v8 %4d, %d gates)  '
                   'vs v8: -%d +%d lines' % (n, len(edits), ins, ins_states, tot_o, tot_n, tot_8, g8, removed, added))
        if tot_n != tot_o + ins_states:
            raise SystemExit('%s: state total off' % n)
        res[wp.PK3_DIR + n] = t.encode('latin-1')
    return res


def melee_hands(log):
    """handtable.zs, MODELDEF.rsq and hand.md3 from team/melee_hands/gen, checked against v8"""
    z8 = zipfile.ZipFile(V8)
    ht = open(os.path.join(MELEE_GEN, 'zscript/rsq/handtable.zs')).read()
    md = open(os.path.join(MELEE_GEN, 'MODELDEF.rsq')).read()
    h1 = open(os.path.join(MELEE_GEN, 'models/rsq/hand.md3'), 'rb').read()
    h2 = open(os.path.join(MELEE_GEN, 'models/rsq/hand2.md3'), 'rb').read()
    ht8 = z8.read('zscript/rsq/handtable.zs').decode()
    md8 = z8.read('MODELDEF.rsq').decode()
    h1_8 = z8.read('models/rsq/hand.md3')
    if h2 != z8.read('models/rsq/hand2.md3'):
        raise SystemExit('melee gen hand2.md3 differs from v8')
    # guns 1-23 keep their index; the axe is 24, the chainsaw 25
    idx8 = re.findall(r"if \(w is '(\w+)'\)\s*return (\d+);", ht8)
    idx9 = re.findall(r"if \(w is '(\w+)'\)\s*return (\d+);", ht)
    if idx9[:len(idx8)] != idx8 or idx9[len(idx8):] != [('BrutalAxe', '24'), ('Chain_saw', '25')]:
        raise SystemExit('melee handtable: indexes are not v8 1-23 + BrutalAxe 24 + Chain_saw 25: %s' % idx9[len(idx8) - 1:])
    # every v8 row is unchanged (letters, hooks, support): the v9 arrays start with the v8 arrays
    for arr8 in re.findall(r'static const \w+ \w+\[\] = \{ (.*?) \};', ht8):
        if not any(a9.startswith(arr8 + ', ') for a9 in re.findall(r'static const \w+ \w+\[\] = \{ (.*?) \};', ht)):
            raise SystemExit('melee handtable: a v8 row changed: %s...' % arr8[:60])
    # every v8 gun-hand letter shows the same pose (same vertices) in the new hand.md3
    f8 = {L: int(i) for L, i in re.findall(r'FrameIndex RQGS (\w) 0 (\d+)', md8)}
    f9 = {L: int(i) for L, i in re.findall(r'FrameIndex RQGS (\w) 0 (\d+)', md)}
    for L, i8 in f8.items():
        if C.md3_frame_verts(h1_8, i8) != C.md3_frame_verts(h1, f9[L]):
            raise SystemExit('hand.md3: letter %s is not the same pose as in v8' % L)
    new = sorted(set(f9) - set(f8))
    # the rest of MODELDEF.rsq is v8's
    strip = lambda t: [l for l in t.split('\n') if not l.startswith('//') and 'FrameIndex RQGS' not in l]
    if strip(md) != strip(md8):
        raise SystemExit('melee MODELDEF.rsq differs from v8 beyond the RQGS frames')
    log.append('melee hands (team/melee_hands/gen): guns 1-%d unchanged (rows, letters, poses checked), BrutalAxe 24, '
               'Chain_saw 25; hand.md3 %d -> %d frames, new letters %s' % (len(idx8), C.md3_frames(h1_8), C.md3_frames(h1), new))
    return ht, md, h1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--reload', default=C.RELOAD_DEFAULT)
    ap.add_argument('--hands', default=os.path.join(TEAM, 'hands.zs'))
    ap.add_argument('-o', '--out', default=os.path.join(C.OUTDIR, 'BD22_Models_v9.pk3'))
    a = ap.parse_args()
    work = os.path.join(C.OUTDIR, '_work', 'bd22')
    log = []

    # the weapon files: GATES = [], then the reload release's guns
    wlog = []
    repl = weapon_files(wlog)
    rel = C.read_release(os.path.abspath(a.reload), 'bd')
    for k, data in rel['weapons'].items():
        f = os.path.basename(k)
        if k not in repl:
            raise SystemExit('reload release ships %s, which is not one of the patched weapon files' % k)
        ours = repl[k].decode('latin-1')
        theirs = data.decode('latin-1')
        nl = '\r\n' if '\r\n' in ours else '\n'
        n = C.check_inserts_only(ours.split(nl)[1:], theirs.split(nl)[1:], k)
        wlog.append('  %-24s <- reload release (= the GATES=[] file + %d inserted lines, nothing else)' % (f, n))
        repl[k] = data

    # hands
    hands, steps = C.build_hands(os.path.abspath(a.hands), rel['hooks'], work)
    ht, md_rsq, hand_md3 = melee_hands(log)
    md_rsq = C.strip_old_carry_blocks(md_rsq)

    repl.update({
        'zscript/rsq/hands.zs': hands.encode(),
        'zscript/rsq/handtable.zs': ht.encode(),
        'zscript/rsq/handler.zs': open(os.path.join(C.V9SRC, 'handler.zs'), 'rb').read(),
        'zscript/rsq/gunmoves.zs': open(GUNMOVES, 'rb').read(),
        'MODELDEF.rsq': md_rsq.encode(),
        'models/rsq/hand.md3': hand_md3,
        'MENUDEF.rsq': C.menudef('bd', rel['guns'], rel['help']).encode(),
        'CVARINFO.rsq': C.cvarinfo_rsq(rel['files']['CVARINFO.rsr'].decode()).encode(),
        'MAPINFO.rsvr': (MAPINFO % ', '.join('"%s"' % h for h in rel['handlers'])).encode(),
        'ZSCRIPT.rsvr': (ZSCRIPT % ''.join('#include "zscript/rsr/%s"\n' % f for f in rel['rsr_zs'])).encode(),
    })
    repl.update(rel['files'])
    remove = ['zscript/rsq/reload.zs'] + C.OLD_CARRY_FILES

    tmp = C.write_pk3(V8, a.out, repl, set(remove), zipfile.ZIP_LZMA)

    # ------------------------------------------------------------------ report
    C.log('weapon files (tool/weapon_patch.py EDITS + INSERTS, GATES = []):')
    C.log('\n'.join(wlog))
    C.log('reload release: %s (snapshot %s, tree %s; %s)' % (os.path.abspath(a.reload), rel['snap'], rel['hash'][:12], rel['status']))
    C.log('  guns: %s; zscript/rsr: %s; weapon files: %s' % (', '.join(rel['guns']), ', '.join(rel['rsr_zs']), ', '.join(rel['weapons'])))
    for n in rel['notes']:
        C.log('  builder: ' + n)
    for n in C.CHANGED:
        C.log('  reload hook changed a gun line one for one (same state count): ' + n)
    for n in C.regen_check(rel):
        C.log('  ' + n)
    C.log('hands.zs: ' + '; '.join(steps))
    for l in log:
        C.log(l)
    for l in C.check_pack(tmp, 'bd', rel['guns']):
        C.log(l)
    C.publish(tmp, a.out)
    C.size_report(V8, a.out)
    C.log('wrote', a.out)


if __name__ == '__main__':
    main()
