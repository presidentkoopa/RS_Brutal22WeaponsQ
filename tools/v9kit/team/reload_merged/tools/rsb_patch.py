"""RSR-BREAK: the break-open / revolver real VR reload (zscript/rsr/rsr_break.zs): the weapon-file side.

BD22 SSG.dec, Revolver.dec, GrenadeLaunch.dec: BD22's original + tool/weapon_patch.py's edits for
them (gun kept on screen, first-pickup skip) WITHOUT their old immersive gates, + the RSB states.
V+ revolver.txt: the set's original + FIX_SWITCH (tool/vplus/vplus_patch.py) + the RSB states.
V+ shotty.txt: the set's original + FIX_SWITCH on VR_Shotgun (the base pack's fix, kept so the pump
gun does not crash) + the RSB states on VR_SuperShotgun ONLY. patch_shotty_ssg() applies just the
VR_SuperShotgun part to any shotty.txt (the pump work's), anchored inside that actor.

What the RSB states change: only what happens after the gun's own Reload has passed all its own
checks. There a 0-tic check (RSB_Start) asks the script; when the break reload does not apply it
goes straight on into the set's own reload (RSB_Stock), unchanged. Firing states are untouched.
The ammo moves only in copies of the set's own steps, with its own items. Each anchor is checked
to occur exactly once.

usage: rsb_patch.py <out dir>   (writes actors/Weapons/{SSG,Revolver,GrenadeLaunch}.dec,
                                 Decorate/{revolver,shotty}.txt)
"""
import os, sys, re, importlib.util

S = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
BD_SRC = S + '/bd22src/actors/Weapons/'
VP_SRC = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/'
MINE = ('SSG.dec', 'Revolver.dec', 'GrenadeLaunch.dec')
TAG = '// RSR-BREAK'


def load_weapon_patch():
    spec = importlib.util.spec_from_file_location('weapon_patch', S + '/tool/weapon_patch.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def once(lines, i0, i1, pred, what):
    hits = [i for i in range(i0, i1) if pred(i)]
    if len(hits) != 1:
        raise SystemExit('%s: found %d times' % (what, len(hits)))
    return hits[0]


def actor_span(lines, name):
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


def start_block(spr, stocks):
    """RSB_Start (and RSB_Start2 for a second way in): ask the script; the set's own reload if not"""
    out = ['\t%s: real VR reload, break-open / revolver (zscript/rsr/rsr_break.zs, team/reload_break/tools/rsb_patch.py).' % TAG,
           '\t// Not in VR, or with Real reload off, RSB_Start goes straight on into the set\'s own reload.']
    for lab, stock in stocks:
        out += ['\t%s:' % lab,
                '\t\t%s 0 A_TakeInventory("RSB_Go", 1)' % spr,
                '\t\t%s 0 A_GiveInventory("RSB_Start", 1)' % spr,
                '\t\t%s 0 A_JumpIfInventory("RSB_Go", 1, "RSB_Open")' % spr,
                '\t\tGoto %s' % stock]
    return out


def wait_block(topup=False):
    out = ['\tRSB_Wait:\t\t// the gun as the script shows it ("####" "#"); the script runs every tic',
           '\t\t"####" "#" 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE)',
           '\t\t"####" "#" 0 A_GiveInventory("RSB_Tick", 1)',
           '\t\t"####" "#" 0 A_JumpIfInventory("RSB_EjectT", 1, "RSB_Eject")',
           '\t\t"####" "#" 0 A_JumpIfInventory("RSB_LoadT", 1, "RSB_Load")']
    if topup:
        out.append('\t\t"####" "#" 0 A_JumpIfInventory("RSB_TopUpT", 1, "RSB_TopUp")')
    out += ['\t\t"####" "#" 0 A_JumpIfInventory("RSB_Done", 1, "RSB_Done")',
            '\t\tGoto RSB_Wait']
    return out


H = '"####" "#"'

BD_SSG = start_block(H, [('RSB_Start', 'RSB_Stock'), ('RSB_Start2', 'RSB_Stock2')]) + [
    '\tRSB_Open:',
    '\t\t%s 0 A_TakeInventory("RSB_Go", 1)' % H,
    '\t\t%s 0 A_TakeInventory("Reloading", 1)' % H,
    '\t\t%s 0 A_GiveInventory("Pumping", 1)\t\t// BD22: the player sprite\'s reload' % H,
] + wait_block() + [
    '\tRSB_Eject:\t\t// BD22\'s own casings: one SSGCaseSpawner per fired barrel (its RaiseReloading / Reload2)',
    '\t\t%s 0 A_TakeInventory("RSB_EjectT", 1)' % H,
    '\t\t%s 0 A_FireCustomMissile("SSGCaseSpawner",0,0,-10, -20)' % H,
    '\t\t%s 0 A_JumpIfInventory("RSB_EjectT", 1, "RSB_Eject")' % H,
    '\t\tGoto RSB_Wait',
    '\tRSB_Load:\t\t// one shell pushed home in a barrel: BD22\'s own step (its Reload2, one shell)',
    '\t\t%s 0 A_TakeInventory("RSB_LoadT", 1)' % H,
    '\t\t%s 0 A_TakeInventory("HasUnloadedSSG", 1)' % H,
    '\t\t%s 0 A_GiveInventory("SSGAmmo", 1)' % H,
    '\t\t%s 0 A_JumpIfInventory("NoReloading",1,2)' % H,
    '\t\t%s 0 A_TakeInventory("AmmoShell", 1,TIF_NOTAKEINFINITE)' % H,
    '\t\t%s 0' % H,
    '\t\tGoto RSB_Wait',
    '\tRSB_Done:\t\t// shut (weapons/sshotc, SSG/Lever1): BD22\'s own end of a reload',
    '\t\tSHTZ A 0 A_TakeInventory("RSB_Done", 1)',
    '\t\tGoto Ready',
]

BD_GL = start_block(H, [('RSB_Start', 'RSB_Stock'), ('RSB_Start2', 'RSB_Stock2')]) + [
    '\tRSB_Open:',
    '\t\t%s 0 A_TakeInventory("RSB_Go", 1)' % H,
    '\t\t%s 0 A_TakeInventory("Reloading", 1)' % H,
] + wait_block() + [
    '\tRSB_Eject:\t\t// BD22\'s own: the empty and its smoke (its RaiseReloading), once',
    '\t\t%s 0 A_TakeInventory("RSB_EjectT", 1)' % H,
    '\t\t%s 0 A_JumpIfInventory("GLReloadToken",1,3)' % H,
    '\t\t%s 0 A_FireCustomMissile("GrenadeCasingSpawner",0,0,8, -14)' % H,
    '\t\t%s 0 A_FireCustomMissile("SmokeSpawner",0,0,0,5)' % H,
    '\t\t%s 0 A_GiveInventory("GLReloadToken", 1)' % H,
    '\t\tGoto RSB_Wait',
    '\tRSB_Load:\t\t// the grenade pushed home: BD22\'s own step (its RaiseReloading)',
    '\t\t%s 0 A_TakeInventory("RSB_LoadT", 1)' % H,
    '\t\t%s 0 A_GiveInventory("GLAmmo", 1)' % H,
    '\t\t%s 0 A_GiveInventory("GLLoaded",1)' % H,
    '\t\t%s 0 A_JumpIfInventory("NoReloading",1,2)' % H,
    '\t\t%s 0 A_TakeInventory("AmmoRocket", 1,TIF_NOTAKEINFINITE)' % H,
    '\t\t%s 0 A_TakeInventory("GLReloadToken", 1)' % H,
    '\t\tGoto RSB_Wait',
    '\tRSB_Done:\t\t// shut (GrenadeLauncher/Close): BD22\'s own end of a reload',
    '\t\tGRLN A 0 A_TakeInventory("RSB_Done", 1)',
    '\t\tGoto Ready',
]

BD_REV = start_block(H, [('RSB_Start', 'RSB_Stock')]) + [
    '\tRSB_Open:',
    '\t\t%s 0 A_TakeInventory("RSB_Go", 1)' % H,
    '\t\t%s 0 A_TakeInventory("Reloading", 1)' % H,
    '\t\t%s 0 A_GiveInventory("Pumping", 1)\t\t// as BD22\'s reload' % H,
] + wait_block(topup=True) + [
    '\tRSB_Eject:\t\t// BD22\'s own casings: one SSGCaseSpawner per spent round (its InsertingShells)',
    '\t\t%s 0 A_TakeInventory("RSB_EjectT", 1)' % H,
    '\t\t%s 0 A_FireCustomMissile("SSGCaseSpawner",0,0,-10, -20)' % H,
    '\t\t%s 0 A_JumpIfInventory("RSB_EjectT", 1, "RSB_Eject")' % H,
    '\t\tGoto RSB_Wait',
    '\tRSB_Load:\t\t// one round pushed home in a chamber: BD22\'s own pass (its InsertingShells)',
    '\t\t%s 0 A_TakeInventory("RSB_LoadT", 1)' % H,
    '\t\t%s 0 A_JumpIfInventory("RevolverAmmo",0,"RSB_Wait")' % H,
    '\t\t%s 0 A_Giveinventory("RevolverAmmo",1)' % H,
    '\t\t%s 0 A_JumpIfInventory("NoReloading",1,2)' % H,
    '\t\t%s 0 A_Takeinventory("AmmoShell",1,TIF_NOTAKEINFINITE)' % H,
    '\t\t%s 0' % H,
    '\t\tGoto RSB_Wait',
    '\tRSB_TopUp:\t\t// every chamber loaded: BD22\'s own InsertBullets to its 6 (its cylinder mesh has 5 chambers)',
    '\t\t%s 0 A_TakeInventory("RSB_TopUpT", 1)' % H,
    '\tRSB_TopUp1:',
    '\t\t%s 0 A_JumpIfInventory("RevolverAmmo",0,"RSB_Wait")' % H,
    '\t\t%s 0 A_JumpIfInventory("AmmoShell",1,1)' % H,
    '\t\tGoto RSB_Wait',
    '\t\t%s 0 A_Giveinventory("RevolverAmmo",1)' % H,
    '\t\t%s 0 A_Takeinventory("AmmoShell",1,TIF_NOTAKEINFINITE)' % H,
    '\t\tGoto RSB_TopUp1',
    '\tRSB_Done:\t\t// shut (Revolver/Close): BD22\'s own end of a reload (its FinishedInsertingShells)',
    '\t\tREVO A 0 A_TakeInventory("RSB_Done", 1)',
    '\t\tREVO A 0 A_JumpIfInventory("NeedToHammer",1,"Hammering")',
    '\t\tGoto Ready',
]


def vp_ssg_block():
    return start_block('SHT2 A', [('RSB_Start', 'RSB_Stock')]) + [
        '\tRSB_Open:',
        '\t\tSHT2 A 0 A_TakeInventory("RSB_Go", 1)',
    ] + wait_block() + [
        '\tRSB_Eject:\t\t// (its spent shells are thrown out by the script, as its own frames throw them)',
        '\t\t%s 0 A_TakeInventory("RSB_EjectT", 8)' % H,
        '\t\tGoto RSB_Wait',
        '\tRSB_Load:\t\t// one shell pushed home in a barrel: the set\'s own count (VR_SSGAlt, the loaded barrels; its reload gives 2)',
        '\t\t%s 0 A_TakeInventory("RSB_LoadT", 1)' % H,
        '\t\t%s 0 A_GiveInventory("VR_SSGAlt", 1)' % H,
        '\t\tGoto RSB_Wait',
        '\tRSB_Done:\t\t// shut (weapons/sshotc): the set\'s own end of a reload',
        '\t\tSHT2 A 0 A_TakeInventory("RSB_Done", 1)',
        '\t\tGoto Ready',
    ]


def vp_rev_block(loaded):
    held = 'RSB_Held_' + {'VR_RevLoaded': 'VR_Revolver', 'VR_RevLoaded2': 'VR_Revolver2'}[loaded]
    return start_block('REVL A', [('RSB_Start', 'RSB_Stock')]) + [
        '\tRSB_Open:',
        '\t\tREVL A 0 A_TakeInventory("RSB_Go", 1)',
    ] + wait_block() + [
        '\tRSB_Eject:\t\t// the ejector threw all six (the set\'s own frames): the live ones are held until a loader is home',
        '\t\t%s 0 A_TakeInventory("RSB_EjectT", 1)' % H,
        '\tRSB_Eject1:',
        '\t\t%s 0 A_JumpIfInventory("%s", 1, 1)' % (H, loaded),
        '\t\tGoto RSB_Wait',
        '\t\t%s 0 A_TakeInventory("%s", 1)' % (H, loaded),
        '\t\t%s 0 A_GiveInventory("%s", 1)' % (H, held),
        '\t\tGoto RSB_Eject1',
        '\tRSB_Load:\t\t// the speedloader pushed home: the held rounds back, then the set\'s own Bulletin loop',
        '\t\t%s 0 A_TakeInventory("RSB_LoadT", 1)' % H,
        '\tRSB_Return:',
        '\t\t%s 0 A_JumpIfInventory("%s", 1, 1)' % (H, held),
        '\t\tGoto RSB_Bulletin',
        '\t\t%s 0 A_TakeInventory("%s", 1)' % (H, held),
        '\t\t%s 0 A_GiveInventory("%s", 1)' % (H, loaded),
        '\t\tGoto RSB_Return',
        '\tRSB_Bulletin:',
        '\t\t%s 0 A_JumpIfInventory("%s",6,"RSB_Wait")' % (H, loaded),
        '\t\t%s 0 A_JumpIfInventory("Clip",1,"RSB_Bulletin2")' % H,
        '\t\tgoto RSB_Wait',
        '\tRSB_Bulletin2:',
        '\t\t%s 0 A_Giveinventory("%s",1)' % (H, loaded),
        '\t\t%s 0 A_Takeinventory("Clip",1)' % H,
        '\t\tGoto RSB_Bulletin',
        '\tRSB_Done:\t\t// shut (weapons/9mmslide): the set\'s own end of a reload',
        '\t\tREVL A 0 A_TakeInventory("RSB_Done", 1)',
        '\t\tGoto Ready',
    ]


def hook_after(lines, a, b, anchor_pred, what, new):
    k = once(lines, a, b, anchor_pred, what)
    lines[k + 1:k + 1] = new
    return k


def bd_files():
    wp = load_weapon_patch()
    wp.GATES = [g for g in wp.GATES if g[0] not in MINE]        # the old pauses: gone on these guns
    names = sorted({e[0] for e in wp.EDITS} | {i[0] for i in wp.INSERTS} | {g[0] for g in wp.GATES} | set(MINE))
    files = {n: open(BD_SRC + n, 'rb').read().decode('latin-1') for n in names}
    out = wp.patch(files)
    res = {}
    for n in MINE:
        text = out[n]
        nl = '\r\n' if '\r\n' in text else '\n'
        lines = text.split(nl)
        if n == 'SSG.dec':
            a, b = actor_span(lines, 'SSG')
            # Reload: after its own checks (full -> Inspect, SSGLoaded -> Ready, no shells -> Ready),
            # before it picks one barrel (Reload2) or both
            k = once(lines, a, b, lambda i: lines[i].strip().startswith('"####" A 0 A_JumpIfInventory("SSGAlt", 1, "Reload2")'),
                     'SSG Reload hook')
            lines[k:k] = ['\t\t"####" A 0 A_Jump(256, "RSB_Start")\t%s: real VR reload (zscript/rsr/rsr_break.zs)' % TAG, '\tRSB_Stock:']
            # RaiseReloading (an empty gun selected): after its own shells check
            k = once(lines, a, b, lambda i: lines[i].strip() == 'Goto ResumeNormalRaise'
                     and lines[i + 1].strip().startswith('"####" A 0 A_JumpIfInventory("AmmoShell", 2, 1)'), 'SSG RaiseReloading hook')
            lines[k + 1:k + 1] = ['\t\t"####" A 0 A_Jump(256, "RSB_Start2")\t%s' % TAG, '\tRSB_Stock2:']
            blk = BD_SSG
            cls = 'SSG'
        elif n == 'GrenadeLaunch.dec':
            a, b = actor_span(lines, 'GrenadeLauncher')
            k = once(lines, a, b, lambda i: lines[i].strip() == 'Goto Ready'
                     and lines[i + 1].strip().startswith('"####" FGHII 1 A_WEAPONREADY'), 'GL Reload hook')
            lines[k + 1:k + 1] = ['\t\t"####" A 0 A_Jump(256, "RSB_Start")\t%s: real VR reload (zscript/rsr/rsr_break.zs)' % TAG, '\tRSB_Stock:']
            k = once(lines, a, b, lambda i: lines[i].strip() == 'Goto ResumeNormalRaise'
                     and lines[i + 1].strip().startswith('"####" J 1 A_PlaySound("GrenadeLauncher/Open", 5)'), 'GL RaiseReloading hook')
            lines[k + 1:k + 1] = ['\t\t"####" A 0 A_Jump(256, "RSB_Start2")\t%s' % TAG, '\tRSB_Stock2:']
            blk = BD_GL
            cls = 'GrenadeLauncher'
        else:
            a, b = actor_span(lines, 'Revolver')
            # Reload: after its own checks (no shells -> Ready, inspect, full -> Inspect), before
            # its unloaded / turbo / animated ways
            k = once(lines, a, b, lambda i: lines[i].strip() == 'REVO A 0 A_JumpIfInventory("RevolverAmmo",0,"Inspect")'
                     and lines[i + 1].strip().startswith('REVO A 0 A_JumpIfInventory("HasUnloadedRevolver", 1, "ReloadUnloaded")'),
                     'Revolver Reload hook')
            lines[k + 1:k + 1] = ['\t\tGoto RSB_Start\t%s: real VR reload (zscript/rsr/rsr_break.zs)' % TAG, '\tRSB_Stock:']
            blk = BD_REV
            cls = 'Revolver'
        a, b = actor_span(lines, cls)
        sb = states_brace(lines, a, b, cls)
        lines[sb + 1:sb + 1] = blk
        lines[0] = lines[0].replace('"rsq gate": optional immersive reload pauses',
                                    '"RSR-BREAK": real VR reload (rsr_break.zs; no gates on this gun)')
        res[n] = nl.join(lines)
    return res


def fix_switch(lines, cls, old, new):
    a, b = actor_span(lines, cls)
    k = once(lines, a, b, lambda i: lines[i] == old, cls + ' FIX_SWITCH')
    lines[k + 1:k + 1] = new


def vp_revolver():
    text = open(VP_SRC + 'revolver.txt', 'rb').read().decode('latin-1')
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    for cls, loaded in (('VR_Revolver', 'VR_RevLoaded'), ('VR_Revolver2', 'VR_RevLoaded2')):
        # FIX_SWITCH (tool/vplus/vplus_patch.py): the slow lower the fast-switch jump expects
        fix_switch(lines, cls, '\t\tREVL A 1 A_Lower(60)', ['\t\tLoop', '\t\tREVL A 1 A_Lower'])
        a, b = actor_span(lines, cls)
        # ReloadA: after its own checks (full -> Ready, no Clip -> OutOfAmmo)
        k = once(lines, a, b, lambda i: lines[i].strip() == 'ReloadA:', cls + ' ReloadA hook')
        lines[k + 1:k + 1] = ['\t\tREVL A 0 A_Jump(256, "RSB_Start")\t%s: real VR reload (zscript/rsr/rsr_break.zs)' % TAG, '\tRSB_Stock:']
        a, b = actor_span(lines, cls)
        sb = states_brace(lines, a, b, cls)
        lines[sb + 1:sb + 1] = vp_rev_block(loaded)
    hdr = ('// RSR-BREAK: real VR reload states added (team/reload_break/tools/rsb_patch.py), and the default'
           ' weapon-switch crash fixed (tool/vplus/vplus_patch.py FIX_SWITCH); otherwise the set\'s own file.')
    return hdr + nl + nl.join(lines)


def patch_shotty_ssg(text):
    """the VR_SuperShotgun part only, anchored inside that actor (merges onto any shotty.txt)"""
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, 'VR_SuperShotgun')
    # Reload: after its own checks (loaded -> Ready, A_CheckReload)
    k = once(lines, a, b, lambda i: lines[i].strip() == 'SHT2 I 0 A_CheckReload'
             and lines[i + 1].strip() == 'SHT2 I 2 A_OpenShotgun2', 'VR_SuperShotgun Reload hook')
    lines[k + 1:k + 1] = ['    SHT2 I 0 A_Jump(256, "RSB_Start")\t%s: real VR reload (zscript/rsr/rsr_break.zs)' % TAG, '  RSB_Stock:']
    a, b = actor_span(lines, 'VR_SuperShotgun')
    sb = states_brace(lines, a, b, 'VR_SuperShotgun')
    lines[sb + 1:sb + 1] = vp_ssg_block()
    return nl.join(lines)


def vp_shotty():
    text = open(VP_SRC + 'shotty.txt', 'rb').read().decode('latin-1')
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    # the base pack's FIX_SWITCH on the pump shotgun (not this work's gun; kept so it does not crash)
    fix_switch(lines, 'VR_Shotgun', '    SHTG A 1 A_Lower(60)', ['    Loop', '    SHTG A 1 A_Lower'])
    fix_switch(lines, 'VR_Shotgun', '    SHTG A 1 A_Raise(60)', ['    Loop', '    SHTG A 1 A_Raise'])
    text = nl.join(lines)
    text = patch_shotty_ssg(text)
    hdr = ('// RSR-BREAK: real VR reload states added to VR_SuperShotgun (team/reload_break/tools/rsb_patch.py);'
           ' VR_Shotgun: the default weapon-switch crash fixed (tool/vplus/vplus_patch.py FIX_SWITCH); otherwise the set\'s own file.')
    return hdr + nl + text


def main(out):
    os.makedirs(out + '/actors/Weapons', exist_ok=True)
    os.makedirs(out + '/Decorate', exist_ok=True)
    for n, t in bd_files().items():
        open(out + '/actors/Weapons/' + n, 'wb').write(t.encode('latin-1'))
    open(out + '/Decorate/revolver.txt', 'wb').write(vp_revolver().encode('latin-1'))
    open(out + '/Decorate/shotty.txt', 'wb').write(vp_shotty().encode('latin-1'))
    print('rsb_patch: written')


if __name__ == '__main__':
    main(sys.argv[1])
