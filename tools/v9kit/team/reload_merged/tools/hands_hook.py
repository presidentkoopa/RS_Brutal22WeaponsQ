"""The small hooks the real VR reload needs in rsq/hands.zs. Applied to whatever
hands.zs is current (anchors checked), so it can follow the hands work.

  1. A_RSQ_Layers: while a real reload has the off hand, RSR_Handler.FreeHand() says what
     the free hand shows (open, Ermac's hold round the magazine, a fist on the handle).
     The support hand stays on the engine's own steadying flag (WF_TWOHANDSTABILIZED),
     stock: no grip of the reload's own takes hold of the gun.
  2. ModifyBobLayer3D: the reload's layers (2102-2104 on the gun, 2201 in the off hand)
     are placed by RSR_Handler.Place (and the free hand in the desktop test).
  3. States: RsrHold (Ermac's ammo_hand frame 3 without his magazine: MODELDEF.rsr RQHN I).
  4. Upkeep: the off-hand weapon is given when Real reload is on even with the hands off
     (the magazine in the hand is its layer).

usage: hands_hook.py <hands.zs in> <hands.zs out>
"""
import sys

EDITS = [
    ('\t\tint carry = s ? s.carry : 0;\n',
     '\t\tint carry = s ? s.carry : 0;\n'
     '\t\t// a real reload (rsr/vreload.zs) has the off hand: it says what the free hand shows\n'
     '\t\tString rsr = RSR_Handler.FreeHand(mo);\n'),
    # (v8 hands.zs only) its distance snap is let go while a reload has the off hand. The team
    # hands.zs is left as it is: its support hand follows the engine's own two-hand steadying
    # (WF_TWOHANDSTABILIZED), stock; the reload adds no grip of its own to it.
    [('\t\tif (i > 0 && s && s.kind == 0 && carry == 0)\n',
      '\t\tif (i > 0 && s && s.kind == 0 && carry == 0 && rsr == "")\n'),
     ('\t\tbool hold = i > 0 && (p.WeaponState & WF_TWOHANDSTABILIZED) != 0 && s && s.kind == 0 && carry == 0;\n',
      '\t\tbool hold = i > 0 && (p.WeaponState & WF_TWOHANDSTABILIZED) != 0 && s && s.kind == 0 && carry == 0;\n')],
    ('\t\t\t!on || hold ? "Hidden" : ammo[clamp(carry, 0, 7)]);\n',
     '\t\t\t!on || hold ? "Hidden" : rsr != "" ? rsr : ammo[clamp(carry, 0, 7)]);\n'),
    ('\toverride Vector3, Vector3 ModifyBobLayer3D(Vector3 translation, Vector3 rotation, int layer, double ticfrac)\n\t{\n',
     '\toverride Vector3, Vector3 ModifyBobLayer3D(Vector3 translation, Vector3 rotation, int layer, double ticfrac)\n\t{\n'
     '\t\t// the real reload\'s layers (rsr/vreload.zs)\n'
     '\t\tif (layer >= RSR.LAYER_FIRST && layer <= RSR.LAYER_LAST || layer == RSR.HANDMAG || layer == RSQ_Layers.FREEHAND)\n'
     '\t\t{\n'
     '\t\t\tVector3 t, r;\n'
     '\t\t\t[t, r] = RSR_Handler.Place(Owner, translation, rotation, layer, ticfrac);\n'
     '\t\t\tif (layer != RSQ_Layers.FREEHAND)\n'
     '\t\t\t\treturn t, r;\n'
     '\t\t\ttranslation = t;\n'
     '\t\t\trotation = r;\n'
     '\t\t}\n'),
    ('\tAmmoH: RQHN H -1; Stop;\t\t// a closed hand\n',
     '\tAmmoH: RQHN H -1; Stop;\t\t// a closed hand\n'
     '\tRsrHold: RQHN I -1; Stop;\t// real reload: Ermac\'s hold, round the gun\'s own magazine (rsr)\n'),
    # RSR-BREAK: the break-open / revolver reload (rsr/rsr_break.zs): what the free hand shows while it
    # has the hand, where its layers go, Ermac's holds for a shell and for the speedloader
    ('\t\tString rsr = RSR_Handler.FreeHand(mo);\n',
     '\t\tString rsr = RSR_Handler.FreeHand(mo);\n'
     '\t\tif (rsr == "")\n'
     '\t\t\trsr = RSB_Handler.FreeHand(mo);\t// RSR-BREAK\n'),
    ('\t\t// the real reload\'s layers (rsr/vreload.zs)\n',
     '\t\t// RSR-BREAK: the break-open / revolver reload\'s layers (rsr/rsr_break.zs)\n'
     '\t\tif (RSB_Handler.Owns(Owner, layer))\n'
     '\t\t{\n'
     '\t\t\tVector3 bt, br;\n'
     '\t\t\t[bt, br] = RSB_Handler.Place(Owner, translation, rotation, layer, ticfrac);\n'
     '\t\t\treturn bt, br;\n'
     '\t\t}\n'
     '\t\t// the real reload\'s layers (rsr/vreload.zs)\n'),
    ('\tRsrHold: RQHN I -1; Stop;\t// real reload: Ermac\'s hold, round the gun\'s own magazine (rsr)\n',
     '\tRsrHold: RQHN I -1; Stop;\t// real reload: Ermac\'s hold, round the gun\'s own magazine (rsr)\n'
     '\tRsbShell: RQHN J -1; Stop;\t// RSR-BREAK: Ermac\'s hold of one shell (ammo_hand 1), round the gun\'s own round\n'
     '\tRsbCell: RQHN L -1; Stop;\t// RSR-BREAK: Ermac\'s hold of a cell (ammo_hand 5), round the gun\'s own speedloader\n'),
    ('\t\tif (!p || p.playerstate != PST_LIVE || mo.health <= 0 || !Shown(mo))\n',
     '\t\tif (!p || p.playerstate != PST_LIVE || mo.health <= 0 || !Shown(mo) && !RSR_Handler.WantsHands(mo))\n'),
]


def main(src, dst):
    t = open(src).read()
    for e in EDITS:
        alts = e if isinstance(e, list) else [e]
        hits = [(o, nw) for o, nw in alts if t.count(o) == 1]
        if len(hits) != 1:
            raise SystemExit('hands_hook: no single anchor for %r' % (alts[0][0][:80],))
        t = t.replace(hits[0][0], hits[0][1])
    open(dst, 'w').write(t)
    print('hands.zs hooked:', dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
