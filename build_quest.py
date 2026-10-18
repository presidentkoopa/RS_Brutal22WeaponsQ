"""Build the Quest (QuestZDoom on Meta Quest) edition of the pack from src/.

WHY A SEPARATE EDITION
The Quest runs QuestZDoom 1.6 = LZDoom 3.88b underneath, which compiles ZScript only up to
4.6.1. The PC build is a newer engine, and the pack is written for it. On Quest the scripts
do not compile, so the pack never loaded there (every release from 1.0 to 1.90).

This script does not keep a second copy of the source. It takes src/ and rewrites the few
things the Quest engine lacks, each patch asserting it matched exactly what it expects, so a
source change that moves one of them breaks this build loudly instead of shipping a pack
that does not compile:

  version "4.10"                 -> "4.6"
  Actor.FindStateByString(s)     -> RSQ_StateMap.Find(actor, s): a generated table of every
                                    state label the pack defines, each looked up with a
                                    constant label (the only kind the old compiler accepts)
  RS ballistics                  -> removed (owner's call): stock BD22 impacts/projectiles
  player.PlayInVR                -> dropped (Quest is always VR; OverrideAttackPosDir stays)
  Voxel Options                  -> removed (needs A_ChangeModel). The BD voxel pack still
                                    works on its own, always on, with its own VOXELDEF.

Usage: python3 build_quest.py 1.91   -> BD22_VR-Reloaded_1.91_Quest.pk3
"""
import os, re, sys, zipfile, glob

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, 'src')
ver = sys.argv[1] if len(sys.argv) > 1 else 'dev'
out = os.path.join(here, f'BD22_VR-Reloaded_{ver}_Quest.pk3')

# files and folders left out of the Quest edition
DROP = {'MENUDEF.rsqvox', 'MODELDEF.rsqvox', 'CVARINFO.rsqvox', 'Voxeldef.txt', 'Voxeldef.cruel.txt',
        'zscript/rsq/voxels.zs', 'zscript/rsq/voxtable.zs',
        'zscript/rsq/ballistics.zs', 'SURFACES.rsq'}
DROP_DIRS = ('rsqvox/', 'models/rsq/debris/')

files = {}
for root, _, fs in os.walk(src):
    for f in sorted(fs):
        p = os.path.join(root, f)
        rel = os.path.relpath(p, src).replace(os.sep, '/')
        if rel in DROP or rel.startswith(DROP_DIRS):
            continue
        files[rel] = open(p, 'rb').read()

def patch(rel, old, new, count=1, regex=False):
    t = files[rel].decode('latin-1')
    n = len(re.findall(old, t)) if regex else t.count(old)
    if n != count:
        sys.exit(f'build_quest: {rel}: expected {count} of {old!r}, found {n}')
    t = re.sub(old, new, t) if regex else t.replace(old, new)
    files[rel] = t.encode('latin-1')

# ---- version
for rel in ('ZSCRIPT.rsvr', 'ZSCRIPT.nosniper'):
    patch(rel, 'version "4.10"', 'version "4.6"')

# ---- voxels out
patch('ZSCRIPT.rsvr', '#include "zscript/rsq/voxtable.zs"\n', '')
patch('ZSCRIPT.rsvr', '#include "zscript/rsq/voxels.zs"\n', '#include "zscript/quest/quest.zs"\n')
patch('MAPINFO.rsvr', ', "RSQ_Voxels"', '')
patch('MENUDEF.rsq', r'\n[ \t]*Submenu "Voxel Options", "RSQ_VoxelOptions"[^\n]*', '', regex=True)

# ---- PlayInVR
patch('zscript/rsvr/vrhand.zs', 'mo.player.PlayInVR && ', '')

# ---- FindStateByString
patch('zscript/rsq/dualhands.zs', 'gs.FindStateByString(label)', 'RSQ_StateMap.Find(gs, label)')
patch('zscript/rsq/hands.zs', 'caller.FindStateByString(label)', 'RSQ_StateMap.Find(caller, label)')
patch('zscript/rsr/rsr_pump.zs', 'w.FindStateByString(list[k], true)', 'RSQ_StateMap.Find(w, list[k], true)')

# ---- RS ballistics out: Quest gets stock BD22 impacts and projectiles (owner, 2026-10-18)
patch('ZSCRIPT.rsvr', '#include "zscript/rsq/ballistics.zs"\n', '')
patch('MAPINFO.rsvr', '"RSQ_Ballistics", ', '')
patch('MENUDEF.rsq', r'\nOptionValue "RSQ_Ballistics"\n\{[^}]*\}\n', '\n', regex=True)
patch('MENUDEF.rsq', r'\n[ \t]*Option "Ballistics", "rsq_ballistics"[^\n]*', '', regex=True)
patch('CVARINFO.rsq', r'\nserver bool rsq_ballistics[^\n]*', '', regex=True)
patch('MODELDEF.rsq', r'\n// debris: A-D chips[^\n]*\n(?:\nModel RSQ_Debris\n\{[^}]*\}\n)+', '\n', regex=True)

# anything left that the Quest engine cannot compile -> stop here
left = []
for rel, b in files.items():
    if rel.endswith('.zs') or rel.upper().startswith('ZSCRIPT'):
        t = b.decode('latin-1')
        for k in ('FindStateByString', 'SpawnParticle(p', 'FSpawnParticleParams', 'PlayInVR', 'Map<', 'A_ChangeModel', 'version "4.1'):
            if k in t:
                left.append(f'{rel}: {k}')
if left:
    sys.exit('build_quest: still in the Quest edition:\n  ' + '\n  '.join(left))

# ---- generated: every state label the pack defines
labels = set()
for rel, b in files.items():
    if not (rel.endswith('.zs') or rel.upper().startswith(('DECORATE', 'ZSCRIPT')) or rel.startswith('actors/')):
        continue
    t = b.decode('latin-1')
    t = re.sub(r'//.*', '', t)
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    for m in re.finditer(r'\bstates\b[^{;]*\{', t, re.I):
        i = j = m.end(); d = 1
        while d and j < len(t):
            d += t[j] == '{'; d -= t[j] == '}'; j += 1
        body = t[i:j - 1]
        for lm in re.finditer(r'(?:^|[;}])\s*([A-Za-z_][\w.]*)\s*:(?!:)', body, re.M):
            labels.add(lm.group(1))
labels = sorted(labels, key=str.lower)
# a Name switch is case-insensitive, so one case per label regardless of spelling
seen = {}
for l in labels:
    seen.setdefault(l.lower(), l)
labels = sorted(seen.values(), key=str.lower)

q = ['// GENERATED by build_quest.py for the Quest edition. Do not edit.', '',
     '// FindStateByString does not exist on the Quest engine, and its compiler only takes a',
     '// state label as a constant. So: one constant lookup per label the pack defines.',
     'class RSQ_StateMap play', '{',
     '\tstatic State Find(Actor a, String label, bool exact = false)', '\t{',
     '\t\tif (!a || label == "")', '\t\t\treturn null;',
     '\t\tName n = label;', '\t\tswitch (n)', '\t\t{']
for l in labels:
    q.append(f"\t\tcase '{l}':\treturn a.FindState('{l}', exact);")
q += ['\t\tdefault:', '\t\t\tbreak;', '\t\t}',
      '\t\tif (developer)', '\t\t\tConsole.Printf("RSQ_StateMap: no label %s", label);',
      '\t\treturn null;', '\t}', '}', '',
      '// kept from voxels.zs (the rest of it is the Voxel Options, not in this edition)',
      'class DeathSphere : Inventory {}', '']
files['zscript/quest/quest.zs'] = '\n'.join(q).encode('latin-1')

# models as LZMA like the PC release (the Quest engine reads LZMA zip entries), the rest deflate
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for rel in sorted(files):
        z.writestr(rel, files[rel], zipfile.ZIP_LZMA if rel.lower().endswith('.md3') else zipfile.ZIP_DEFLATED)
print(out, len(files), 'files,', len(labels), 'state labels')
