"""Real VR reload (zscript/rsr/vreload.zs): the weapon-file side, for each gun.

BD22 Rifle.dec: BD22's original + tool/weapon_patch.py's edits for it (gun kept on screen,
first-pickup skip) WITHOUT its old immersive gates, + the RSR states.
V+ rifle.txt: the set's original + FIX_SWITCH (tool/vplus/vplus_patch.py) + the RSR states.

What the RSR states change: only what happens after the gun's own Reload has passed all its
own checks. There a 0-tic check (RSR_Start) asks the script; when the real reload does not
apply it goes straight on into the set's own reload (RSR_Stock), unchanged. Firing, ammo
items, limits and sounds are the set's own: the fill / unload loops are the set's own loops
with its own items. Each anchor is checked to occur exactly once.

usage: rsr_patch.py <out dir>     (writes actors/Weapons/Rifle.dec and Decorate/rifle.txt)
"""
import os, sys, json, importlib.util
sys.dont_write_bytecode = True        # never write __pycache__ into tool/

S = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
BD_SRC = S + '/bd22src/actors/Weapons/'
VP_SRC = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/'


def load_weapon_patch():
    spec = importlib.util.spec_from_file_location('weapon_patch', S + '/tool/weapon_patch.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


WAIT = [
    '\tRSR_Wait:\t\t// the gun as the script shows it ("####" "#"); the script runs every tic',
    '\t\t"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE)',
    '\t\t"####" "#" 0 A_GiveInventory("RSR_Tick", 1)',
    '\t\t"####" "#" 0 A_JumpIfInventory("RSR_Seated", 1, "RSR_Fill")',
    '\t\t"####" "#" 0 A_JumpIfInventory("RSR_Done", 1, "RSR_Done")',
    '\t\tGoto RSR_Wait',
]


def fill_loop(spr, label, ammo, full, reserve, extra_give=(), take_flags='', per=1):
    """a copy of the set's own 'one round from the reserve into the gun' loop
    (full: its own limit, 0 = the item's maximum; per: reserve units a round)"""
    t = ', %s' % take_flags if take_flags else ''
    out = ['\t%s:' % label,
           '\t\t%s 0 A_JumpIfInventory("%s", %s, "RSR_Filled")' % (spr, ammo, full),
           '\t\t%s 0 A_JumpIfInventory("%s", %d, "%sa")' % (spr, reserve, per, label),
           '\t\tGoto RSR_Filled',
           '\t%sa:' % label,
           '\t\t%s 0 A_GiveInventory("%s", 1)' % (spr, ammo)]
    out += ['\t\t%s 0 A_GiveInventory("%s", 1)' % (spr, g) for g in extra_give]
    out += ['\t\t%s 0 A_TakeInventory("%s", %d%s)' % (spr, reserve, per, t),
            '\t\tGoto %s' % label]
    return out


BD_BLOCK = [
    '\t// posefix rsr: real VR reload (zscript/rsr/vreload.zs, team/reload/tools/rsr_patch.py).',
    '\t// Not in VR, or with Real reload off, RSR_Start goes straight on into BD22\'s own reload.',
    '\tRSR_Start:',
    '\t\tRIFG A 0 A_TakeInventory("RSR_Go", 1)',
    '\t\tRIFG A 0 A_GiveInventory("RSR_Start", 1)',
    '\t\tRIFG A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out")',
    '\t\tGoto RSR_Stock',
    '\tRSR_Out:',
    '\t\tRIFG A 0 A_TakeInventory("RSR_Go", 1)',
    '\t\tRIFG A 0 A_Takeinventory("Reloading", 1)',
    '\t\tRIFG A 0 A_GiveInventory("Pumping", 1)\t\t// BD22: the player sprite\'s reload',
    '\t\tRIFG A 0 A_JumpIfInventory("HasUnloadedRifle", 1, "RSR_Wait")\t// no magazine in the gun',
    '\t\tRIFG A 0 A_GiveInventory("RSR_MagOut", 1)\t// the magazine drops out (Rifle/Reload1)',
    '\tRSR_Unload:\t\t// its rounds are held aside (a chambered round stays); they come back when a magazine is home,',
    '\t\t\t\t// so the count ends where BD22\'s own top-up reload ends (30 + 1), and the reserve\'s cap loses none',
    '\t\tRIFG A 0 A_JumpIfInventory("RifleAmmo", 2, "RSR_Unload1")',
    '\t\tRIFG A 0 A_GiveInventory("HasUnloadedRifle", 1)',
    '\t\tRIFG A 0 A_GiveInventory("HasUnloadedDualRifles", 1)',
    '\t\tGoto RSR_Wait',
    '\tRSR_Unload1:',
    '\t\tRIFG A 0 A_TakeInventory("RifleAmmo", 1)',
    '\t\tRIFG A 0 A_TakeInventory("DoubleRifleAmmo", 1)',
    '\t\tRIFG A 0 A_GiveInventory("RSR_Held_Rifle", 1)',
    '\t\tGoto RSR_Unload',
] + WAIT + [
    '\tRSR_Fill:\t\t// the magazine is home: BD22\'s own InsertBullets / InsertBullets2',
    '\t\tRIFG A 0 A_TakeInventory("RSR_Seated", 1)',
    '\t\tRIFG A 0 A_TakeInventory("HasUnloadedRifle", 1)',
    '\t\tRIFG A 0 A_TakeInventory("HasUnloadedDualRifles", 1)',
    '\tRSR_Return:\t\t// the held rounds first',
    '\t\tRIFG A 0 A_JumpIfInventory("RSR_Held_Rifle", 1, "RSR_Return1")',
    '\t\tGoto RSR_FillGo',
    '\tRSR_Return1:',
    '\t\tRIFG A 0 A_TakeInventory("RSR_Held_Rifle", 1)',
    '\t\tRIFG A 0 A_GiveInventory("RifleAmmo", 1)',
    '\t\tRIFG A 0 A_GiveInventory("DoubleRifleAmmo", 1)',
    '\t\tGoto RSR_Return',
    '\tRSR_FillGo:',
    '\t\tRIFG A 0 A_JumpIfInventory("RifleAmmo", 1, "RSR_Fill31")',
    '\t\tRIFG A 0 A_GiveInventory("RifleReloadToken", 1)\t// no round chambered: the handle (BD22: FinishReloading)',
] + fill_loop('RIFG A', 'RSR_Fill30', 'RifleAmmo', '30', 'Clip2', ['DoubleRifleAmmo'], 'TIF_NOTAKEINFINITE') \
  + fill_loop('RIFG A', 'RSR_Fill31', 'RifleAmmo', '0', 'Clip2', ['DoubleRifleAmmo'], 'TIF_NOTAKEINFINITE') + [
    '\tRSR_Filled:',
    '\t\tRIFG A 0 A_GiveInventory("RSR_Filled", 1)\t// the script: the handle if RifleReloadToken, else done',
    '\t\tGoto RSR_Wait',
    '\tRSR_Done:',
    '\t\tRIFG A 0 A_TakeInventory("RSR_Done", 1)',
    '\t\tRIFG A 0 A_TakeInventory("RifleReloadToken", 1)',
    '\t\tRIFG A 0 A_Takeinventory("Reloading", 1)',
    '\t\tGoto ReloadConcluded\t\t// BD22\'s own end of a reload',
]

VP_BLOCK = [
    '\t// RS real VR reload (zscript/rsr/vreload.zs, team/reload/tools/rsr_patch.py). Not in VR,',
    '\t// or with Real reload off, RSR_Start goes straight on into the set\'s own reload.',
    '\tRSR_Start:',
    '\t\tRIFL A 0 A_TakeInventory("RSR_Go", 1)',
    '\t\tRIFL A 0 A_GiveInventory("RSR_Start", 1)',
    '\t\tRIFL A 0 A_JumpIfInventory("RSR_Go", 1, "RSR_Out")',
    '\t\tGoto RSR_Stock',
    '\tRSR_Out:',
    '\t\tRIFL A 0 A_TakeInventory("RSR_Go", 1)',
    '\t\tRIFL A 0 A_JumpIfInventory("RSR_NoMag_VR_Rifle", 1, "RSR_Wait")\t// no magazine in the gun',
    '\t\tRIFL A 0 A_takeinventory("RifleFired", 100)\t// as the set\'s own reload does',
    '\t\tRIFL A 0 A_GiveInventory("RSR_MagOut", 1)\t// the magazine drops out (weapons/9mmclip1)',
    '\tRSR_Unload:\t\t// its rounds are held aside and come back when a magazine is home (the set tops up)',
    '\t\tRIFL A 0 A_JumpIfInventory("VR_RifleLoaded", 1, "RSR_Unload1")',
    '\t\tRIFL A 0 A_GiveInventory("RSR_NoMag_VR_Rifle", 1)',
    '\t\tGoto RSR_Wait',
    '\tRSR_Unload1:',
    '\t\tRIFL A 0 A_TakeInventory("VR_RifleLoaded", 1)',
    '\t\tRIFL A 0 A_GiveInventory("RSR_Held_VR_Rifle", 1)',
    '\t\tGoto RSR_Unload',
] + WAIT + [
    '\tRSR_Fill:\t\t// the magazine is home: the set\'s own Bulletin loop (20 rounds)',
    '\t\tRIFL A 0 A_TakeInventory("RSR_Seated", 1)',
    '\t\tRIFL A 0 A_TakeInventory("RSR_NoMag_VR_Rifle", 1)',
    '\tRSR_Return:\t\t// the held rounds first',
    '\t\tRIFL A 0 A_JumpIfInventory("RSR_Held_VR_Rifle", 1, "RSR_Return1")',
    '\t\tGoto RSR_Fill1',
    '\tRSR_Return1:',
    '\t\tRIFL A 0 A_TakeInventory("RSR_Held_VR_Rifle", 1)',
    '\t\tRIFL A 0 A_GiveInventory("VR_RifleLoaded", 1)',
    '\t\tGoto RSR_Return',
] + fill_loop('RIFL A', 'RSR_Fill1', 'VR_RifleLoaded', '20', 'Clip') + [
    '\tRSR_Filled:',
    '\t\tRIFL A 0 A_GiveInventory("RSR_Filled", 1)\t// the script: the charging handle',
    '\t\tGoto RSR_Wait',
    '\tRSR_Done:',
    '\t\tRIFL A 0 A_TakeInventory("RSR_Done", 1)',
    '\t\tRIFL A 0 A_giveinventory("RifleFull", 1)\t// as the set\'s own reload does',
    '\t\tGoto Ready',
]


# ---------------------------------------------------------------------------
# The rest of BD22's magazine guns: one entry each, one generator (bd_block). What each
# entry copies from BD22's own file is named in it: the hook goes after the gun's own
# Reload checks (anchor lines, matched exactly once), the fill loop is the gun's own
# InsertBullets with its own items, the end is the gun's own end of a reload.
#   chamber: BD keeps a round in the chamber (its "+1 effect"): it stays in the gun when
#     the magazine drops, and a gun with it fills to its maximum (BD's second loop); an
#     empty one fills to fill_empty (BD's first loop) and its handle is due
#   charge: 'empty' (the handle only when the gun was empty, BD's rule), 'always' (BD's
#     canned reload always works it), 'never' (no handle)
#   per: reserve units per round (the railgun takes 10 cells a shot)
#   end: the lines after the takes; end_label: (anchor lines, index) a label RSR_End put
#     into BD's own end of a reload, before that anchor line (a label adds no state)
BD_GUNS = {
    'BrutalPistol': dict(
        file='Pistol.dec', spr='PIST E',
        hook=(['PIST E 0 A_GiveInventory ("Pumping", 1)', 'PIST E 0 A_Takeinventory("Reloading",1)',
               'PIST E 0 A_JumpIfInventory("HasUnloadedPistol", 1, 3)'], 1),
        nomag=['HasUnloadedPistol', 'HasUnloadedDualPistols'], ammo='BDPistolAmmo', ammo_extra=['BDDualPistolAmmo'],
        reserve='Clip1', chamber=True, fill_empty='15', fill_full='0', charge='empty', charge_token='RSR_Charge',
        end=['"####" "#" 0 A_ReFire', 'Goto Ready']),                          # FinishReload2
    'BrutalSMG': dict(
        file='SubMachinegun.dec', spr='SMGR A',
        hook=(['SMGR A 0 A_GiveInventory ("Pumping", 1)', 'SMGR A 0 A_Takeinventory("Reloading",1)',
               'SMGR A 0 A_JumpIfInventory("HasUnloadedSMG", 1, "ReloadEmpty")'], 1),
        nomag=['HasUnloadedSMG', 'HasUnloadedDualSMG'], ammo='BDSMGAmmo', ammo_extra=['BDDualSMGAmmo'],
        reserve='Clip1', chamber=True, fill_empty='40', fill_full='0', charge='always', charge_token='RSR_Charge',
        end=['"####" "#" 0 A_ReFire', 'Goto Ready']),                          # FinishReload
    'MP40': dict(
        file='Mp40.dec', spr='MP40 A',
        hook=(['MP40 A 0 A_GiveInventory ("Pumping", 1)', 'MP40 A 0 A_Takeinventory("Reloading",1)',
               'MP40 A 0 A_JumpIfInventory("HasUnloadedMP40", 1, "ReloadAfterUnload")'], 1),
        nomag=['HasUnloadedMP40', 'HasUnloadedDualMP40'], ammo='MP40Ammo', ammo_extra=['DualMP40Ammo'],
        reserve='Mauser9mm', chamber=False, fill_empty='0', fill_full='0', charge='empty', charge_token='MP40ReloadToken',
        end=['"####" "#" 0 A_ReFire', 'Goto Ready3']),                         # FullReload
    'AssaultShotgun': dict(
        file='AssaultShotgun.dec', spr='USAS A',
        hook=(['USAS A 0 A_GiveInventory ("Pumping", 1)', 'USAS A 0 A_Takeinventory("Reloading",1)',
               'USAS A 0 A_JumpIfInventory("TurboReload", 1, "InsertBullets")'], 1),
        nomag=['HasUnloadedASG'], ammo='AssaultShotgunAmmo', ammo_extra=[],
        reserve='AmmoShell', chamber=False, fill_empty='0', fill_full='0', charge='empty', charge_token='ASGReloadToken',
        end=['Goto ReloadConcluded']),
    'RailGun': dict(
        file='Railgun.dec', spr='RAIL A',
        hook=(['RAIL A 0 A_Takeinventory("ZoomHold",1)', 'RAIL A 0 A_JumpIfInventory("HasUnloadedRailgun",1, 3)'], 0),
        nomag=['HasUnloadedRailgun'], ammo='RailgunAmmo', ammo_extra=[], per=10,
        reserve='AmmoCell', chamber=False, fill_empty='0', fill_full='0', charge='never', charge_token='',
        # BD22's own power-up after the cell is in: Plasma/Beep, Railgun/Recharge (gun at its ready frame)
        end_label=(['RAR2 ABCDDEF 1 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)', 'TNT1 A 0 A_PlaySound("Plasma/Beep", 5)'], 1),
        end=['Goto RSR_End']),
    'Plasma_Gun': dict(
        file='Plasma.dec', spr='PRSG F',
        hook=(['PRSG F 0 A_JumpIfInventory("TurboReload",1,"TurboReload")', 'TNT1 A 0 A_JumpIfInventory("HasUnloadedPlasma",1,3)'], 0),
        nomag=['HasUnloadedPlasma', 'HasUnloadedDualPlasmas'], ammo='PlasmaAmmo', ammo_extra=['DoublePlasmaAmmo'],
        reserve='AmmoCell', chamber=False, fill_empty='0', fill_full='0', charge='never', charge_token='',
        # BD22's own end of FinishReload: the gun at its ready frame (PRSG IFI), the takes, A_ReFire
        end_label=(['PRSR CZAA 1 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)', 'tnt1 a 0 A_Takeinventory("Reloading",1)'], 1),
        end=['Goto RSR_End']),
    'Sniper': dict(
        file='Sniper.dec', spr='X21G A',
        hook=(['X21G A 0 A_Takeinventory("Reloading",1)', 'X21G A 0 A_ZoomFactor(1.0)', 'X21G A 0', 'X21R AB 1'], 1),
        nomag=['HasUnloadedSniper'], ammo='xm21Ammo', ammo_extra=[],
        reserve='SniperAmmo', chamber=True, fill_empty='10', fill_full='0', charge='empty', charge_token='SniperReloadToken',
        end=['Goto ReloadConcluded']),
    'Rocket_Launcher': dict(
        file='RocketLauncher.dec', spr='MISG A',
        hook=(['TNT1 A 0 A_SetCrosshair(CallACS("GetCrosshair", 8))', 'MISG A 0 A_JumpIfInventory("HasUnloadedRL", 1, "ReloadUnloaded")'], 0),
        nomag=['HasUnloadedRL'], ammo='RocketRounds', ammo_extra=[],
        reserve='AmmoRocket', chamber=False, fill_empty='0', fill_full='0', charge='never', charge_token='',
        end=['"####" "#" 0 A_ReFire', 'Goto Ready']),                          # FinishReloadAnim
}


def bd_block(cls, c):
    """the RSR states of one BD22 gun (see BD_GUNS)"""
    sp = c['spr']
    S0 = lambda s: '\t\t%s 0 %s' % (sp, s)
    keep = 2 if c['chamber'] else 1
    ct = c['charge_token']
    L = ['\t// posefix rsr: real VR reload (zscript/rsr/vreload.zs, team/reload/tools/rsr_patch.py BD_GUNS).',
         '\t// Not in VR, or with Real reload off, RSR_Start goes straight on into BD22\'s own reload.',
         '\tRSR_Start:',
         S0('A_TakeInventory("RSR_Go", 1)'),
         S0('A_GiveInventory("RSR_Start", 1)'),
         S0('A_JumpIfInventory("RSR_Go", 1, "RSR_Out")'),
         '\t\tGoto RSR_Stock',
         '\tRSR_Out:',
         S0('A_TakeInventory("RSR_Go", 1)'),
         S0('A_JumpIfInventory("%s", 1, "RSR_Wait")\t// no magazine in the gun' % c['nomag'][0])]
    if ct == 'RSR_Charge':
        L.append(S0('A_JumpIfInventory("RSR_Charge", 1, "RSR_Filled")\t// a magazine in, the handle still to pull'))
    L += [S0('A_GiveInventory("RSR_MagOut", 1)\t// the magazine drops out (its own sound)'),
          '\tRSR_Unload:\t\t// its rounds are held aside%s; they come back when a magazine is home,' % (' (a chambered round stays)' if c['chamber'] else ''),
          '\t\t\t\t// so the count ends where BD22\'s own top-up reload ends, and the reserve\'s cap loses none',
          S0('A_JumpIfInventory("%s", %d, "RSR_Unload1")' % (c['ammo'], keep))]
    L += [S0('A_GiveInventory("%s", 1)' % n) for n in c['nomag']]
    L += ['\t\tGoto RSR_Wait', '\tRSR_Unload1:', S0('A_TakeInventory("%s", 1)' % c['ammo'])]
    L += [S0('A_TakeInventory("%s", 1)' % n) for n in c['ammo_extra']]
    L += [S0('A_GiveInventory("RSR_Held_%s", 1)' % cls), '\t\tGoto RSR_Unload']
    L += WAIT
    L += ['\tRSR_Fill:\t\t// the magazine is home: BD22\'s own fill loop (InsertBullets), its own items',
          S0('A_TakeInventory("RSR_Seated", 1)')]
    L += [S0('A_TakeInventory("%s", 1)' % n) for n in c['nomag']]
    L += ['\tRSR_Return:\t\t// the held rounds first',
          S0('A_JumpIfInventory("RSR_Held_%s", 1, "RSR_Return1")' % cls),
          '\t\tGoto RSR_FillGo', '\tRSR_Return1:', S0('A_TakeInventory("RSR_Held_%s", 1)' % cls),
          S0('A_GiveInventory("%s", 1)' % c['ammo'])]
    L += [S0('A_GiveInventory("%s", 1)' % n) for n in c['ammo_extra']]
    L += ['\t\tGoto RSR_Return', '\tRSR_FillGo:']
    tok = lambda: [S0('A_GiveInventory("%s", 1)\t// the handle is due (vreload.zs: ChargeToken)' % ct)] if ct else []
    if c['chamber']:
        L.append(S0('A_JumpIfInventory("%s", 1, "RSR_FillB")\t// a round chambered: BD22\'s second loop, to the maximum' % c['ammo']))
    else:
        L.append(S0('A_JumpIfInventory("%s", 1, "RSR_FillB")\t// the gun was not empty: no handle' % c['ammo']))
    if c['charge'] in ('empty', 'always'):
        L += tok()
    L.append('\t\tGoto RSR_FillA')
    L.append('\tRSR_FillB:')
    if c['charge'] == 'always':
        L += tok()
    L.append('\t\tGoto RSR_FillB1')
    per = c.get('per', 1)
    L += fill_loop(sp, 'RSR_FillA', c['ammo'], c['fill_empty'], c['reserve'], c['ammo_extra'], 'TIF_NOTAKEINFINITE', per)
    L += fill_loop(sp, 'RSR_FillB1', c['ammo'], c['fill_full'], c['reserve'], c['ammo_extra'], 'TIF_NOTAKEINFINITE', per)
    L += ['\tRSR_Filled:',
          S0('A_GiveInventory("RSR_Filled", 1)\t// the script: the handle if it is due, else done'),
          '\t\tGoto RSR_Wait',
          '\tRSR_Done:',
          S0('A_TakeInventory("RSR_Done", 1)')]
    if ct:
        L.append(S0('A_TakeInventory("%s", 1)' % ct))
    L.append(S0('A_TakeInventory("Reloading", 1)'))
    L += ['\t\t' + e for e in c['end']]
    return L


def bd_gun(cls, wp):
    c = BD_GUNS[cls]
    name = c['file']
    wp.GATES = [g for g in wp.GATES if g[0] != name]        # the old pauses: gone on this gun
    names = sorted({e[0] for e in wp.EDITS} | {i[0] for i in wp.INSERTS} | {g[0] for g in wp.GATES} | {name})
    files = {n: open(BD_SRC + n, 'rb').read().decode('latin-1') for n in names}
    text = wp.patch(files).get(name, files[name])
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, cls)
    anchor, at = c['hook']
    n = len(anchor)
    k = once(lines, a, b, lambda i: i + n <= len(lines) and [lines[i + j].strip() for j in range(n)] == anchor, cls + ' Reload hook')
    lines[k + at + 1:k + at + 1] = ['\t\tGoto RSR_Start\t// posefix rsr: real VR reload (zscript/rsr/vreload.zs)', '\tRSR_Stock:']
    if c.get('end_label'):
        a, b = actor_span(lines, cls)
        anchor, at = c['end_label']
        n = len(anchor)
        k = once(lines, a, b, lambda i: i + n <= len(lines) and [lines[i + j].strip() for j in range(n)] == anchor, cls + ' end label')
        lines[k + at:k + at] = ['\tRSR_End:\t\t// posefix rsr: the real VR reload ends here (a label: no state added)']
    a, b = actor_span(lines, cls)
    sb = states_brace(lines, a, b, cls)
    lines[sb + 1:sb + 1] = bd_block(cls, c)
    if 'posefix:' not in lines[0]:
        lines.insert(0, '// posefix: BD22 brutal22test6 file; lines marked "posefix" are the only changes.')
    lines[0] = lines[0].replace('"rsq gate": optional immersive reload pauses', '"rsr": real VR reload (no gates on this gun)')
    return nl.join(lines)


def once(lines, i0, i1, pred, what):
    hits = [i for i in range(i0, i1) if pred(i)]
    if len(hits) != 1:
        raise SystemExit('%s: found %d times' % (what, len(hits)))
    return hits[0]


def actor_span(lines, name):
    import re
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


def states_brace(lines, a, b, name):
    i = once(lines, a, b, lambda k: lines[k].strip().lower() == 'states' and lines[k + 1].strip() == '{', name + ' States {')
    return i + 1


def bd_rifle():
    wp = load_weapon_patch()
    wp.GATES = [g for g in wp.GATES if g[0] != 'Rifle.dec']        # the old pauses: gone on this gun
    names = sorted({e[0] for e in wp.EDITS} | {i[0] for i in wp.INSERTS} | {g[0] for g in wp.GATES} | {'Rifle.dec'})
    files = {n: open(BD_SRC + n, 'rb').read().decode('latin-1') for n in names}
    out = wp.patch(files)
    text = out['Rifle.dec']
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, 'Rifle')
    # the hook: in Reload, after all of BD22's own checks, before its animation starts
    k = once(lines, a, b, lambda i: lines[i].strip() == 'RIFG A 0 A_Takeinventory("ZoomHold",1)'
             and lines[i + 1].strip() == 'RIFG A 0 A_JumpIfInventory("HasUnloadedRifle", 1, 2)'
             and lines[i + 2].strip() == 'RIFG A 0 A_PlaySound("Rifle/Reload1", 5)', 'Rifle Reload hook')
    lines[k + 1:k + 1] = ['\t\tGoto RSR_Start\t// posefix rsr: real VR reload (zscript/rsr/vreload.zs)', '\tRSR_Stock:']
    sb = states_brace(lines, a, b, 'Rifle')
    lines[sb + 1:sb + 1] = BD_BLOCK
    lines[0] = lines[0].replace('"rsq gate": optional immersive reload pauses', '"rsr": real VR reload (no gates on this gun)')
    return nl.join(lines)


def vp_rifle():
    text = open(VP_SRC + 'rifle.txt', 'rb').read().decode('latin-1')
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, 'VR_Rifle')
    # FIX_SWITCH (tool/vplus/vplus_patch.py): the slow lower the fast-switch jump expects
    k = once(lines, a, b, lambda i: lines[i] == '\t\tRIFL A 1 A_Lower(60)', 'FIX_SWITCH')
    lines[k + 1:k + 1] = ['\t\tLoop', '\t\tRIFL A 1 A_Lower']
    a, b = actor_span(lines, 'VR_Rifle')
    k = once(lines, a, b, lambda i: lines[i].strip() == 'ReloadA:' and lines[i + 1].strip() == 'RIFL LMN 2', 'ReloadA hook')
    lines[k + 1:k + 1] = ['\t\tRIFL A 0 A_Jump(256, "RSR_Start")\t// RS real VR reload (zscript/rsr/vreload.zs)', '\tRSR_Stock:']
    sb = states_brace(lines, a, b + 3, 'VR_Rifle')
    lines[sb + 1:sb + 1] = VP_BLOCK
    hdr = ('// RS real VR reload states added (team/reload/tools/rsr_patch.py), and the default'
           ' weapon-switch crash fixed (tool/vplus/vplus_patch.py FIX_SWITCH); otherwise the set\'s own file.')
    return hdr + nl + nl.join(lines)


def main(out, only=None):
    os.makedirs(out + '/actors/Weapons', exist_ok=True)
    os.makedirs(out + '/Decorate', exist_ok=True)
    # the weapon files each set's pack gets (build_proto.py)
    man = {'bd': {}, 'vp': {}}
    if not only or 'Rifle' in only:
        t = bd_rifle()
        open(out + '/actors/Weapons/Rifle.dec', 'wb').write(t.encode('latin-1'))
        man['bd']['actors/Weapons/Rifle.dec'] = out + '/actors/Weapons/Rifle.dec'
    if not only or 'VR_Rifle' in only:
        t = vp_rifle()
        open(out + '/Decorate/rifle.txt', 'wb').write(t.encode('latin-1'))
        man['vp']['Decorate/rifle.txt'] = out + '/Decorate/rifle.txt'
    for cls, c in BD_GUNS.items():
        if only and cls not in only:
            continue
        t = bd_gun(cls, load_weapon_patch())
        open(out + '/actors/Weapons/' + c['file'], 'wb').write(t.encode('latin-1'))
        man['bd']['actors/Weapons/' + c['file']] = out + '/actors/Weapons/' + c['file']
    json.dump(man, open(out + '/rsr_weapons.json', 'w'), indent=1)
    print(json.dumps(man, indent=1))


if __name__ == '__main__':
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    main(sys.argv[1], only)
