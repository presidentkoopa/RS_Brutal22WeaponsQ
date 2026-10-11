"""The authored BD21 boot, fist and grenade blocks, put back on every BD22 gun.

The authored set gives EVERY gun class three extra blocks (Modeldef.<gun>.def):
  nade.md3        GRTH A-M -> 3-15                 (grenade toss)
  Boot.md3        KIK1/KIK2 A-E, KICK A-U, STOM A-E (kick, stomp)
  fistclosed.md3  FUCK A-O -> 61-74                 (taunt)
They are identical for all 21 guns and copied verbatim here; only Path changes.

BD22 additions, held on the authored poses so no flat sprite shows:
  GRTH N O P   -> 16 17 18  the mesh's own follow-through after the release (15)
  KICK V-]     -> 40        BD22's air kick runs past the authored U; held on U
  1ICK 2ICK 3ICK -> as KICK (BD22's bloody-boot copies of the same frames)
  1TOM 2TOM 3TOM -> as STOM A
  SLID 1LID 2LID 3LID -> 24 (leg extended, KICK E) for the whole slide
  VUCK -> as FUCK (the same taunt, other player class)
Dropped: KIKF (BD22 ships no art for it; keying it is fatal, and it cannot
show as a sprite either).
"""
GRENADE = dict(path='models/bd/Grenade', mesh='nade.md3', skin='nade.png',
               placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'NoInterpolation', 'ZOffset -5'])
BOOT = dict(path='models/bd/Boot', mesh='Boot.md3', skin='Boot.png',
            placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'NoInterpolation', 'ZOffset -5'])
FIST = dict(path='models/bd/FIST', mesh='fistclosed.md3', skin='fist.png',
            placement=['Scale -1.0 1.0 1.0', 'Offset 0.0 0.0 0.0', 'ZOffset -5'])

KICK_LETTERS = 'ABCDEFGHIJKLMNOPQRSTU'
KICK_EXTRA = 'VWXYZ[]'


def keys():
    g = {('GRTH', c): 3 + i for i, c in enumerate('ABCDEFGHIJKLM')}
    g.update({('GRTH', 'N'): 16, ('GRTH', 'O'): 17, ('GRTH', 'P'): 18})

    b = {}
    for i, c in enumerate('ABCDE'):
        b[('KIK1', c)] = 5 + i
        b[('KIK2', c)] = 10 + i
        b[('STOM', c)] = 53 + i
    kick = {c: 20 + i for i, c in enumerate(KICK_LETTERS)}
    kick.update({c: 40 for c in KICK_EXTRA})
    for spr in ('KICK', '1ICK', '2ICK', '3ICK'):
        for c, p in kick.items():
            b[(spr, c)] = p
    for spr in ('1TOM', '2TOM', '3TOM'):
        b[(spr, 'A')] = 53
    for spr in ('SLID', '1LID', '2LID', '3LID'):
        for c in 'ABCDEFGHIJKLMN':
            b[(spr, c)] = 24

    fuck = dict(zip('ABCDEFGHIJKLMNO', [61, 62, 63, 64, 64, 66, 67, 68, 69, 69, 71, 72, 73, 74, 74]))
    f = {}
    for spr in ('FUCK', 'VUCK'):
        for c, p in fuck.items():
            f[(spr, c)] = p
    return [(GRENADE, g), (BOOT, b), (FIST, f)]


def block_text(cls, spec, keymap):
    out = ['// %s -- authored BD21 %s block, verbatim placement (posefix/hands_blocks.py)' % (cls, spec['mesh']),
           'Model %s' % cls, '{',
           '   Path "%s"' % spec['path'],
           '   Model 0 "%s"' % spec['mesh'],
           '   Skin 0 "%s"' % spec['skin']]
    out += ['   ' + p for p in spec['placement']]
    out.append('')
    for (s, f), p in sorted(keymap.items()):
        out.append('   FrameIndex\t%s\t%s\t0\t%d' % (s, f, p))
    out.append('}')
    return out
