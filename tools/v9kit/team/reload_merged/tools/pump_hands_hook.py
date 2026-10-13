"""RSR-PUMP: the small hooks hand-loaded shells and the hand-worked pump (zscript/rsr/rsr_pump.zs) need
in rsq/hands.zs. Applied after tools/hands_hook.py (the real reload's hooks), anchors checked, to
the team's hands.zs or the v8 one.

  1. A_RSQ_Layers: while the pump shotguns' loading has the off hand, RSP_Handler.FreeHand() says
     what the free hand shows (Ermac's one-shell hold, or a closed hand on the pump), and the
     support-hand hold is off then (the real reload's "rsr" string carries it).
  2. ModifyBobLayer3D: the pump shotguns' layers (2120-2123 on the gun, 2210 in the off hand) are
     placed by RSP_Handler.Place (and the free hand in the desktop test).
  3. ModifyBobLayer3D: the support hand (layer 2101) rides the pump while the hand works it
     (RSP_Handler.SupportShift: the pump's offset, in the hand model's units).
  4. States: RspShell (Ermac's ammo_hand frame 1 without his shell: MODELDEF.rsrpump.hands RQUN A).

usage: pump_hands_hook.py <hands.zs in> <hands.zs out>
"""
import sys

EDITS = [
    ('\t\tString rsr = RSR_Handler.FreeHand(mo);\n',
     '\t\tString rsr = RSR_Handler.FreeHand(mo);\n'
     '\t\tif (rsr == "")\n'
     '\t\t\trsr = RSP_Handler.FreeHand(mo);\t// RSR-PUMP: the pump shotguns\' loading and pump (rsr/rsr_pump.zs)\n'),
    ('\t\t// the real reload\'s layers (rsr/vreload.zs)\n',
     '\t\t// RSR-PUMP: the pump shotguns\' layers (rsr/rsr_pump.zs)\n'
     '\t\tif (RSP_Handler.Places(Owner, layer))\n'
     '\t\t{\n'
     '\t\t\tVector3 pt, pr;\n'
     '\t\t\t[pt, pr] = RSP_Handler.Place(Owner, translation, rotation, layer, ticfrac);\n'
     '\t\t\treturn pt, pr;\n'
     '\t\t}\n'
     '\t\t// the real reload\'s layers (rsr/vreload.zs)\n'),
    # (team hands.zs) the gun's model-frame move / (v8 hands.zs) the support hook
    [('\t\tVector3 t, r;\n\t\t[t, r] = RSQ_Turn.Place(',
      '\t\tif (!gunHand)\n'
      '\t\t\tframeMove += RSP_Handler.SupportShift(Owner, ticfrac);\t// RSR-PUMP: the support hand rides the pump\n'
      '\t\tVector3 t, r;\n\t\t[t, r] = RSQ_Turn.Place('),
     ('\t\treturn translation + RSQ_HandTable.SupportHook(i), rotation + RSQ_HandTable.SupportRot(i);\n',
      '\t\treturn translation + RSQ_HandTable.SupportHook(i) + RSP_Handler.SupportShift(Owner, ticfrac), rotation + RSQ_HandTable.SupportRot(i);'
      '\t// RSR-PUMP: the support hand rides the pump\n')],
    ('\tRsrHold: RQHN I -1; Stop;',
     '\tRspShell: RQUN A -1; Stop;\t// RSR-PUMP: Ermac\'s one-shell hold (ammo_hand frame 1), round the gun\'s own shell\n'
     '\tRsrHold: RQHN I -1; Stop;'),
]


def main(src, dst):
    t = open(src).read()
    for e in EDITS:
        alts = e if isinstance(e, list) else [e]
        hits = [(o, nw) for o, nw in alts if t.count(o) == 1]
        if len(hits) != 1:
            raise SystemExit('pump_hands_hook: no single anchor for %r' % (alts[0][0][:80],))
        t = t.replace(hits[0][0], hits[0][1])
    open(dst, 'w').write(t)
    print('hands.zs pump-hooked:', dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
