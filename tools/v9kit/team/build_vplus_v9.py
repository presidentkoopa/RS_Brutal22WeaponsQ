#!/usr/bin/env python3
"""Build RS_VanillaVRPlus_VR_v9.pk3 (load it after the Vanilla VR Plus set). One command:

    python3 -I -B team/build_vplus_v9.py [--reload DIR] [--hands team/hands.zs] [--set DIR] [-o OUT]

  --reload DIR   the real VR reload release (default team/reload_release; read only)
  --hands PATH   the hands work's hands.zs (default team/hands.zs)
  --set DIR      the weapon set (default /mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2)
  -o OUT         default team/out_v9/RS_VanillaVRPlus_VR_v9.pk3

v9 = vplus/RS_VanillaVRPlus_VR.pk3 (v8) with (everything else copied from v8 with the same
bytes, zip method and date):
  Decorate/*.txt         the set's own files + FIX_SWITCH only (team/vplus/vplus_patch.py: the
                         default weapon-switch crash fix; no gates). Guns the reload release
                         covers (rifle.txt) come from DIR/src instead, checked to be that same
                         file with only lines inserted.
  zscript/rsq/reload.zs, guns.zs   gone; zscript/rsq/handler.zs (team/v9src) keeps what
                         hands.zs needs.
  zscript/rsq/hands.zs   team/hands.zs + DIR/tools/hands_hook.py + GunH (the BFG's gun hand is
                         letter H) + y = WEAPONTOP for the hand layers - v8's carried-ammo states.
  zscript/rsq/gunmoves.zs  team/gunmoves_vplus.zs.  handtable.zs, hand.md3, hand2.md3: v8's.
  zscript/rsvr/vrhand.zs, zscript/rsr/*, MODELDEF.rsr, CVARINFO.rsr, rsr_clear.png   the reload.
  ZSCRIPT.rsq, MAPINFO.rsq, MENUDEF.rsq, CVARINFO.rsq, README   v9.
  MODELDEF.rsq           v8's minus the carried-ammo blocks; their meshes and skins gone.
"""
import argparse, os, re, sys, zipfile

sys.dont_write_bytecode = True
TEAM = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TEAM)
import v9common as C
sys.path.insert(0, os.path.join(TEAM, 'vplus'))
import vplus_patch                       # team/vplus/vplus_patch.py: FIX_SWITCH only
assert os.path.dirname(os.path.abspath(vplus_patch.__file__)) == os.path.join(TEAM, 'vplus')

S = C.S
V8 = os.path.join(S, 'vplus', 'RS_VanillaVRPlus_VR.pk3')
SET = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2'
GUNMOVES = os.path.join(TEAM, 'gunmoves_vplus.zs')

ZSCRIPT = '''version "4.10"

// RS VR hands, ballistics and real VR reload for Vanilla VR Plus (QuestZDoom 17.x).
// The same scripts as BD22_Models; options in RSQ_Options (MENUDEF.rsq).
#include "zscript/rsvr/vrhand.zs"
#include "zscript/rsvr/common.zs"
#include "zscript/rsq/handler.zs"
#include "zscript/rsq/handtable.zs"
#include "zscript/rsq/gunmoves.zs"
#include "zscript/rsq/hands.zs"
#include "zscript/rsq/ballistics.zs"

// RS real VR reload (zscript/rsr, from the reload release)
%s'''
MAPINFO = '''// RS VR hands and ballistics: zscript/rsq. Real VR reload: zscript/rsr
gameinfo
{
	AddEventHandlers = "RSQ_Handler", "RSQ_Ballistics", %s
}
'''
README = '''RS_VanillaVRPlus_VR v9 -- VR hands, real VR reloading and ballistics for Vanilla VR Plus
(1.0b_Weapons_VanillaVRPlus_v1.2) on stock QuestZDoom 17.x. No engine changes.

Load after the weapon set. Options: Options > RS VR Hands, Reload, Ballistics
(also at the bottom of the set's 3D Weapon Settings).

  VR hands    Ermac's posed hands on every gun; bring your off hand to the front
              of the gun and squeeze the grip to hold it (the engine's own
              two-hand steadying, left as it is).
  Reloading   VR (default) on the %s; every other gun, and Stock, is the
              set's own reload.
%s
  Ballistics  Enhanced: impacts throw dust, sparks and chips by surface.

Files: %s
They replace the set's copies while this pack is loaded.
Do not load together with BD22_Models (they share these scripts).

Hands and poses: Ermac, Rusted Legacy / Force Unleashed (MIT,
models/rsq/LICENSE_RustedLegacy_MIT.txt).
'''


def decorate(setdir, rel, wlog):
    """{pk3 path: bytes}: FIX_SWITCH copies, the reload's guns replaced; checked"""
    src = os.path.join(setdir, 'FILTER', 'DOOM', 'Decorate')
    work = os.path.join(C.OUTDIR, '_work', 'vplus', 'Decorate')
    if os.path.isdir(work):
        for f in os.listdir(work):
            os.remove(os.path.join(work, f))
    written = vplus_patch.main(src, work)
    z8 = zipfile.ZipFile(V8)
    out = {}
    for f in written:
        t = open(os.path.join(work, f), 'rb').read()
        s = t.decode('latin-1')
        if re.search(r'RSQ_|\{G:|rsq gate', s):
            raise SystemExit('%s: old gates left' % f)
        # every FIX_SWITCH line v8 had is still there
        v8 = z8.read('Decorate/' + f).decode('latin-1')
        for ln in v8.split('\r\n'):
            if re.match(r'\s+(\w{4}) A 1 A_(Lower|Raise)$', ln) and ln not in s.split('\r\n'):
                raise SystemExit('%s: v8 FIX_SWITCH line %r missing' % (f, ln))
        out['Decorate/' + f] = t
        wlog.append('  %-14s the set\'s own + FIX_SWITCH (no gates)' % f)
    for k, data in rel['weapons'].items():
        f = os.path.basename(k)
        if k not in out:
            raise SystemExit('reload release ships %s, which is not one of the patched files' % k)
        ours = [l for l in out[k].decode('latin-1').split('\r\n')]
        theirs = data.decode('latin-1')
        nl = '\r\n' if '\r\n' in theirs else '\n'
        theirs = theirs.split(nl)
        while ours and ours[0].startswith('//'):
            ours = ours[1:]
        while theirs and theirs[0].startswith('//'):
            theirs = theirs[1:]
        n = C.check_inserts_only(ours, theirs, k)
        wlog.append('  %-14s <- reload release (= the FIX_SWITCH file + %d inserted lines, nothing else)' % (f, n))
        # Builder workaround: the release's inserted lines repeat two of the set's own calls on
        # classes the set never defines (RifleFired, RifleFull). They do nothing, but each one is a
        # new "Unknown class name" warning at load. Drop them from the inserted lines only.
        data, dropped = drop_inserted_noops(ours, data, k, setdir)
        if dropped:
            wlog.append('  %-14s builder workaround: %d inserted no-op line(s) on undefined classes left out: %s'
                        % (f, len(dropped), '; '.join(d.strip() for d in dropped)))
        out[k] = data
    return out, written


UNDEFINED_IN_SET = ('RifleFired', 'RifleFull')


def drop_inserted_noops(ours, data, what, setdir):
    """the release file minus inserted lines that only give / take a class the set never defines"""
    import difflib
    for root, _, fs in os.walk(setdir):
        for f in fs:
            p = os.path.join(root, f)
            if os.path.getsize(p) < 4000000 and not f.lower().endswith(('.png', '.md3', '.ogg', '.wav', '.jpg', '.iqm', '.flac', '.mp3')):
                t = open(p, 'rb').read().decode('latin-1')
                for c in UNDEFINED_IN_SET:
                    if re.search(r'(?im)^\s*(actor|class)\s+%s\b' % c, t):
                        raise SystemExit('%s defines %s: the no-op workaround is wrong now' % (p, c))
    s = data.decode('latin-1')
    nl = '\r\n' if '\r\n' in s else '\n'
    lines = s.split(nl)
    head = 0
    while head < len(lines) and lines[head].startswith('//'):
        head += 1
    body = lines[head:]
    sm = difflib.SequenceMatcher(None, ours, body, autojunk=False)
    drop = set()
    pat = re.compile(r'^\s*\S+ \S+ 0 A_(take|give)inventory\("(%s)", \d+\)\s*(//.*)?$' % '|'.join(UNDEFINED_IN_SET), re.I)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'insert':
            drop |= {j for j in range(j1, j2) if pat.match(body[j])}
    dropped = [body[j] for j in sorted(drop)]
    body = [l for j, l in enumerate(body) if j not in drop]
    C.check_inserts_only(ours, body, what + ' (after the workaround)')
    return nl.join(lines[:head] + body).encode('latin-1'), dropped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--reload', default=C.RELOAD_DEFAULT)
    ap.add_argument('--hands', default=os.path.join(TEAM, 'hands.zs'))
    ap.add_argument('--set', default=SET)
    ap.add_argument('-o', '--out', default=os.path.join(C.OUTDIR, 'RS_VanillaVRPlus_VR_v9.pk3'))
    a = ap.parse_args()
    work = os.path.join(C.OUTDIR, '_work', 'vplus')
    z8 = zipfile.ZipFile(V8)

    rel = C.read_release(os.path.abspath(a.reload), 'vp')
    wlog = []
    repl, written = decorate(a.set, rel, wlog)
    for n in z8.namelist():
        if n.startswith('Decorate/') and n not in repl:
            raise SystemExit('v8 ships %s, v9 would not replace it' % n)
    hands, steps = C.build_hands(os.path.abspath(a.hands), rel['hooks'], work)
    md_rsq = C.strip_old_carry_blocks(z8.read('MODELDEF.rsq').decode())
    import textwrap
    names = ['Decorate/' + written[0]] + written[1:]
    rfiles = sorted(rel['weapons'])
    files = ('%s %s the set\'s own %s with the default weapon-switch fix (with Weapon switching '
             '"Default", switching away from the M16, a revolver or the pump shotgun crashed QuestZDoom; '
             'they now lower and raise the way the set\'s fist does)%s.' % (
                 ', '.join(names[:-1]) + ' and ' + names[-1] if len(names) > 1 else names[0],
                 'are' if len(names) > 1 else 'is', 'files' if len(names) > 1 else 'file',
                 ('; %s also carries the real VR reload\'s states' % ', '.join(rfiles)) if rfiles else ''))
    rguns = ', '.join(C.GUN_NAMES.get(g, g) for g in rel['guns'])
    helptext = textwrap.fill(' '.join(rel['help']), 64, initial_indent=' ' * 14, subsequent_indent=' ' * 14)
    readme = README % (rguns, helptext, textwrap.fill(files, 84, subsequent_indent=''))
    repl.update({
        'zscript/rsq/hands.zs': hands.encode(),
        'zscript/rsq/handler.zs': open(os.path.join(C.V9SRC, 'handler.zs'), 'rb').read(),
        'zscript/rsq/gunmoves.zs': open(GUNMOVES, 'rb').read(),
        'MODELDEF.rsq': md_rsq.encode(),
        'MENUDEF.rsq': C.menudef('vp', rel['guns'], rel['help']).encode(),
        'CVARINFO.rsq': C.cvarinfo_rsq(rel['files']['CVARINFO.rsr'].decode()).encode(),
        'MAPINFO.rsq': (MAPINFO % ', '.join('"%s"' % h for h in rel['handlers'])).encode(),
        'ZSCRIPT.rsq': (ZSCRIPT % ''.join('#include "zscript/rsr/%s"\n' % f for f in rel['rsr_zs'])).encode(),
        'README_RS_VanillaVRPlus_VR.txt': readme.encode(),
    })
    repl.update(rel['files'])
    remove = ['zscript/rsq/reload.zs', 'zscript/rsq/guns.zs'] + C.OLD_CARRY_FILES
    tmp = C.write_pk3(V8, a.out, repl, set(remove), zipfile.ZIP_DEFLATED)

    C.log('Decorate:')
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
    for l in C.check_pack(tmp, 'vp', rel['guns']):
        C.log(l)
    C.publish(tmp, a.out)
    C.size_report(V8, a.out)
    C.log('wrote', a.out)


if __name__ == '__main__':
    main()
