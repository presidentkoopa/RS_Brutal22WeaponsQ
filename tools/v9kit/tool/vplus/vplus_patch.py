"""Immersive-reload gates for Vanilla VR Plus (1.0b_Weapons_VanillaVRPlus_v1.2, FILTER/DOOM).

Writes patched copies of Decorate/shotty.txt, rifle.txt and revolver.txt. The add-on pk3
carries them at the same lump names, so the set's own decorate.txt #includes ours.

Every change is a gate (the same as BD22's, tool/weapon_patch.py): at a point in a reload
the gun asks RSQ_Gate whether the off hand has done the step. With stock reloading, or out
of VR, it is told yes at once and costs no time, and the first states of a gate show the
same frame the gun shows next, so stock play is unchanged. Every anchor line is checked to
occur exactly once in its actor before anything is changed.

Gun ids (zscript/rsq/guns.zs): 21 VR_Rifle, 22 VR_Revolver, 23 VR_Revolver2,
24 VR_Shotgun, 25 VR_SuperShotgun.

One fix that is not a gate (FIX_SWITCH): with "Weapon switching: Default" (evw_fastswitch 0)
the set's Deselect / Select jump 2 states ahead to a slow lower / raise that these four guns
never got (Vanilla_Fist has it). The jump lands in Select, whose A_Raise sees the pending
weapon and lowers again, in the same tic, forever: switching away from the M16 or a
revolver overflows the stack and crashes QuestZDoom 17.3 (seen headless; A_Raise ->
DropWeapon -> Deselect -> Select -> A_Raise). On the pump shotgun the jump lands in Fire.
The fix adds the missing slow pair, written the way Vanilla_Fist writes it.
"""
import os, re, sys
FETCH, INSERT, RACK, SHELL = 1, 2, 3, 4
WAIT = {FETCH: 'WRF_NOBOB|WRF_NOFIRE', INSERT: 'WRF_NOBOB|WRF_NOFIRE',
        RACK: 'WRF_NOBOB|WRF_NOFIRE', SHELL: 'WRF_NOBOB'}       # a shell pause can still fire
# (file, actor, gun, [(anchor line, replacement lines with {G:tag} gate markers)], gates)
#   a gate marker '{G:tag}' becomes 'Goto RSQ_tag_G' + 'RSQ_tag_R:'
#   gates: tag -> (kind, next state 'SPR F', hold state 'SPR F')
EDITS = [
    ('shotty.txt', 'VR_Shotgun', 24, [
        # FIX_SWITCH: the slow lower / raise the fast-switch jump expects
        ('    SHTG A 1 A_Lower(60)', ['    SHTG A 1 A_Lower(60)', '    Loop', '    SHTG A 1 A_Lower']),
        ('    SHTG A 1 A_Raise(60)', ['    SHTG A 1 A_Raise(60)', '    Loop', '    SHTG A 1 A_Raise']),
        # the pump after every shot
        ('    SHTG HI 1', ['    SHTG HI 1', '{G:P}']),
        # one shell per pass at the loading port (can still fire)
        ('  InsertShell:', ['  InsertShell:', '{G:S}']),
     ], {'P': (RACK, 'SHTG A', 'SHTG I'), 'S': (SHELL, 'SHTG R', 'SHTG A')}),
    ('shotty.txt', 'VR_SuperShotgun', 25, [
        # open, empties out; hand away for two shells, back to the breech; shells go in
        ('    SHT2 JKLMNOPQR 3 ', ['    SHT2 JKLMNOP 3', '{G:F}', '{G:I}', '    SHT2 QR 3']),
     ], {'F': (FETCH, 'SHT2 Q', 'SHT2 T'), 'I': (INSERT, 'SHT2 Q', 'SHT2 T')}),
    ('rifle.txt', 'VR_Rifle', 21, [
        # FIX_SWITCH (Select already falls through to a slow raise)
        ('\t\tRIFL A 1 A_Lower(60)', ['\t\tRIFL A 1 A_Lower(60)', '\t\tLoop', '\t\tRIFL A 1 A_Lower']),
        # magazine drops out (O-U); hand away for one
        ('\t\tRIFL OPQRSTUVWXYZ 1', ['\t\tRIFL OPQRSTUVWXYZ 1', '{G:F}']),
        # the new one rises into the well from D
        ('\t\tRIFK ABCDEFGHI 2', ['\t\tRIFK ABC 2', '{G:I}', '\t\tRIFK DEFGHI 2']),
        # charging handle (pulled at K)
        ('\t\tRIFK i 0 A_playsound("weapons/9mmclip2", CHAN_AUTO)',
         ['\t\tRIFK i 0 A_playsound("weapons/9mmclip2", CHAN_AUTO)', '{G:R}']),
     ], {'F': (FETCH, 'RIFK A', 'RIFL Z'), 'I': (INSERT, 'RIFK D', 'RIFK C'), 'R': (RACK, 'RIFK J', 'RIFK I')}),
]
for cls, gun in (('VR_Revolver', 22), ('VR_Revolver2', 23)):
    EDITS.append(('revolver.txt', cls, gun, [
        # FIX_SWITCH
        ('\t\tREVL A 1 A_Lower(60)', ['\t\tREVL A 1 A_Lower(60)', '\t\tLoop', '\t\tREVL A 1 A_Lower']),
        # cylinder out and emptied (Q-Z); hand away for rounds, back to the cylinder;
        # then the speedloader goes in (REVO A-E)
        ('\t\tREVL QRSTUVWXYZ 2', ['\t\tREVL QRSTUVWXYZ 2', '{G:F}', '{G:I}']),
     ], {'F': (FETCH, 'REVO A', 'REVL Z'), 'I': (INSERT, 'REVO A', 'REVL Z')}))

def gate_block(tag, kind, code, nxt, hold, ind='\t'):
    return [
        ind + '// rsq gate %s (RS VR reload, zscript/rsq/reload.zs): passes at once with stock reloading' % tag,
        ind + 'RSQ_%s_G:' % tag,
        ind * 2 + '%s 0 A_TakeInventory("RSQ_Pass", 1)' % nxt,
        ind * 2 + '%s 0 A_GiveInventory("RSQ_Gate", %d)' % (nxt, code),
        ind * 2 + '%s 0 A_JumpIfInventory("RSQ_Pass", 1, "RSQ_%s_R")' % (nxt, tag),
        ind + 'RSQ_%s_W:' % tag,
        ind * 2 + '%s 1 A_WeaponReady(%s)' % (hold, WAIT[kind]),
        ind * 2 + '%s 0 A_GiveInventory("RSQ_Gate", %d)' % (hold, code),
        ind * 2 + '%s 0 A_JumpIfInventory("RSQ_Pass", 1, "RSQ_%s_R")' % (hold, tag),
        ind * 2 + 'Goto RSQ_%s_W' % tag,
    ]

def actor_span(lines, name):
    """first and last line index of an actor's block"""
    st = None
    for i, l in enumerate(lines):
        m = re.match(r'\s*actor\s+(\w+)', l, re.I)
        if m:
            if st is not None:
                return st, i
            if m.group(1).lower() == name.lower():
                st = i
    if st is None:
        raise SystemExit('actor %s not found' % name)
    return st, len(lines)

def patch_file(text, edits):
    lines = text.split('\r\n')
    for (fname, actor, gun, subs, gates) in edits:
        a, b = actor_span(lines, actor)
        block = lines[a:b]
        for anchor, repl in subs:
            hits = [i for i, l in enumerate(block) if l == anchor]
            if len(hits) != 1:
                raise SystemExit('%s %s: anchor %r found %d times' % (fname, actor, anchor, len(hits)))
            out = []
            for r in repl:
                m = re.match(r'\{G:(\w+)\}$', r)
                if m:
                    out += ['\t\tGoto RSQ_%s_G' % m.group(1), '\tRSQ_%s_R:' % m.group(1)]
                else:
                    out.append(r)
            i = hits[0]
            block[i:i + 1] = out
        # gate blocks go first inside States { }
        si = [i for i, l in enumerate(block) if l.strip().lower() == 'states']
        if len(si) != 1 or block[si[0] + 1].strip() != '{':
            raise SystemExit('%s: States { not found' % actor)
        gb = []
        for tag, (kind, nxt, hold) in sorted(gates.items()):
            gb += gate_block(tag, kind, kind * 100 + gun, nxt, hold)
        block[si[0] + 2:si[0] + 2] = gb
        lines[a:b] = block
    return '\r\n'.join(lines)

def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    for fname in sorted({e[0] for e in EDITS}):
        text = open(os.path.join(src, fname), 'rb').read().decode('latin-1')
        new = patch_file(text, [e for e in EDITS if e[0] == fname])
        hdr = ('// RS VR reload gates added, and the default weapon-switch crash fixed\r\n'
               '// (tool/vplus/vplus_patch.py); otherwise the set\'s own file.\r\n')
        open(os.path.join(dst, fname), 'wb').write((hdr + new).encode('latin-1'))
        print(fname, len(text), '->', len(new))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
