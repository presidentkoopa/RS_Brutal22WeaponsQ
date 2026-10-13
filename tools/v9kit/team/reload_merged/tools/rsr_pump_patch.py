"""RSR-PUMP: the weapon-file side of hand-loaded shells and a hand-worked pump (zscript/rsr/rsr_pump.zs).

BD22 actors/Weapons/Shotgun.dec: BD22's original + tool/weapon_patch.py's edits for it (first-pickup
skip) WITHOUT its old immersive gates, + the RSP states.
V+ Decorate/shotty.txt: the set's original; in VR_Shotgun the default weapon-switch fix (FIX_SWITCH,
tool/vplus/vplus_patch.py) + the RSP states. VR_SuperShotgun is left as the set ships it (no old gates).

What the RSP states change: only what happens after the gun's own checks, at its own pump (after a
shot, after loading an empty gun) and at its own loading loop. A 0-tic check asks the script; when the
hand is not on the pump, or not in VR, or with Stock reloading, it goes straight on into the set's own
states, unchanged. The shot itself (damage, spread, sound, flash, recoil frames) is never touched.
Ammo moves only through copies of the set's own per-shell step and checks, with its own items.
Every anchor is checked to occur exactly once; every numeric "Goto Label+N" is checked against the
state it lands on (count_states), so a different BD22 / V+ file stops the build.

usage: rsr_pump_patch.py <out dir>     (writes actors/Weapons/Shotgun.dec and Decorate/shotty.txt)
"""
import os, re, sys, importlib.util

S = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
BD_SRC = S + '/bd22src/actors/Weapons/'
VP_SRC = '/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/'


def load_weapon_patch():
    spec = importlib.util.spec_from_file_location('weapon_patch', S + '/tool/weapon_patch.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------- DECORATE states
STATE_RE = re.compile(r'^\s*("[^"]*"|\S{4})\s+("[^"]*"|\S+)\s+(-?\d+)\b(.*)$')


def parse_states(lines):
    """[(label list, sprite, frame, tics, rest, line index)] for an actor's States block, one entry per
    state (a multi-frame line is several states); labels attach to the next state"""
    out = []
    pend = []
    for i, raw in enumerate(lines):
        l = raw.split('//')[0].strip()
        if not l or l in ('{', '}') or l.lower() == 'states':
            continue
        while True:
            m = re.match(r'^([A-Za-z_][\w.]*)\s*:\s*(.*)$', l)
            if not m or m.group(1).lower() in ('goto', 'stop', 'loop', 'wait', 'fail'):
                break
            pend.append(m.group(1))
            l = m.group(2).strip()
        if not l:
            continue
        low = l.lower()
        if low.startswith(('goto', 'stop', 'loop', 'wait', 'fail')):
            continue
        m = STATE_RE.match(l)
        if not m:
            continue
        spr, frames, tics, rest = m.group(1), m.group(2).strip('"'), int(m.group(3)), m.group(4)
        for k, fr in enumerate(frames):
            out.append((pend if k == 0 else [], spr.strip('"'), fr, tics, rest.strip(), i))
        pend = []
    return out


def state_at(states, label, n):
    idx = [k for k, s in enumerate(states) if label in s[0]]
    if len(idx) != 1:
        raise SystemExit('label %s: found %d times' % (label, len(idx)))
    return states[idx[0] + n]


def check_goto(states, label, n, spr, frame, tics, act):
    s = state_at(states, label, n)
    if (s[1], s[2], s[3]) != (spr, frame, tics) or act not in s[4]:
        raise SystemExit('%s+%d is %r, expected %s %s %d [%s]' % (label, n, s[:5], spr, frame, tics, act))


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


def once(lines, a, b, pred, what):
    hits = [i for i in range(a, b) if pred(i)]
    if len(hits) != 1:
        raise SystemExit('%s: found %d times' % (what, len(hits)))
    return hits[0]


def after_label(lines, a, b, label, text, what):
    """the first line equal to text (stripped) after the line 'label:' in [a, b)"""
    k = once(lines, a, b, lambda i: lines[i].strip() == label + ':', what + ' label')
    for i in range(k + 1, b):
        if lines[i].strip() == text:
            return i
        if re.match(r'^\s*[A-Za-z_]\w*\s*:\s*$', lines[i]):
            break
    raise SystemExit('%s: %r not found after %s:' % (what, text, label))


def states_brace(lines, a, b, name):
    i = once(lines, a, b, lambda k: lines[k].strip().lower() == 'states' and lines[k + 1].strip() == '{', name + ' States {')
    return i + 1


# ---------------------------------------------------------------------------- BD22 Shot_Gun
def pump_block(tag, spr, minimum, stock, back, fwd, ready, auto, restore):
    """one of BD22's pumps, hooked after its own checks: the hand works it when it is on the pump.
    restore: states that put BD22's own sprite back (the script draws the gun without its pump)"""
    w = '"####" "#"'
    res = lambda k: [x.replace('@', 'RSP_%s%s2' % (tag, k)) for x in restore]
    b = ['\tRSP_%s:\t\t// %s' % (tag, stock[1]),
         '\t\t%s 0 A_TakeInventory("RSP_Go", 1)' % spr,
         '\t\t%s 0 A_GiveInventory("RSP_PumpStart", %d)\t// %d: BD22\'s own tics from here to its refire' % (spr, minimum, minimum),
         '\t\t%s 0 A_JumpIfInventory("RSP_Go", 1, "RSP_%sGo")' % (spr, tag),
         '\t\tGoto %s' % stock[0],
         '\tRSP_%sGo:' % tag,
         '\t\t%s 0 A_TakeInventory("RSP_Go", 1)' % w,
         '\tRSP_%sWait:\t// the hand works the pump (rsr_pump.zs moves it); switching is allowed, as BD22\'s pump allows' % tag,
         '\t\t%s 1 A_WeaponReady(WRF_NOFIRE|WRF_NOBOB|WRF_NOSECONDARY)' % w,
         '\t\t%s 0 A_GiveInventory("RSP_PTick", 1)' % w,
         '\t\t%s 0 A_JumpIfInventory("RSP_Back", 1, "RSP_%sBack")' % (w, tag),
         '\t\t%s 0 A_JumpIfInventory("RSP_Fwd", 1, "RSP_%sFwd")' % (w, tag),
         '\t\t%s 0 A_JumpIfInventory("RSP_Auto", 1, "RSP_%sAuto")' % (w, tag),
         '\t\t%s 0 A_JumpIfInventory("RSP_Ready", 1, "RSP_%sReady")' % (w, tag),
         '\t\tGoto RSP_%sWait' % tag,
         '\tRSP_%sBack:\t// all the way back: %s' % (tag, back[0]),
         '\t\t%s 0 A_TakeInventory("RSP_Back", 1)' % w] + ['\t\t%s 0 %s' % (w, x) for x in back[1:]] + [
         '\t\tGoto RSP_%sWait' % tag,
         '\tRSP_%sFwd:\t// forward again: %s' % (tag, fwd[0]),
         '\t\t%s 0 A_TakeInventory("RSP_Fwd", 1)' % w] + ['\t\t%s 0 %s' % (w, x) for x in fwd[1:]] + [
         '\t\t%s 0 A_JumpIfInventory("RSP_Ready", 1, "RSP_%sReady")' % (w, tag),
         '\t\tGoto RSP_%sWait\t// ready once BD22\'s own refire time is up (RSP_Ready)' % tag,
         '\tRSP_%sReady:' % tag,
         '\t\t%s 0 A_TakeInventory("RSP_Ready", 1)' % w] + res('R') + (
        ['\t\t"####" A 0 A_JumpIfInventory("Reloading", 1, "ReloadFromPumping")\t// as BD22\'s pump frames do'] if ready[1] else []) + [
         '\t\tGoto %s' % ready[0],
         '\tRSP_%sAuto:\t// the hand left the pump before working it: BD22\'s own pump' % tag,
         '\t\t%s 0 A_TakeInventory("RSP_Auto", 1)' % w] + res('A') + [
         '\t\tGoto %s' % auto]
    return b


PURIST = ['\t\t2HTN A 0 A_JumpIfInventory("IsPlayingAsPurist", 1, "@")\t// BD22\'s own sprite choice', '\t\tSHTN A 0', '\t@:', '\t\t"####" A 0']


def bd_block():
    eject = 'A_FireCustomMissile("ShotCaseSpawn",40,0,-8,-26)'
    L = [
        '\t// RSR-PUMP: hand-loaded shells and a hand-worked pump (zscript/rsr/rsr_pump.zs, tools/rsr_pump_patch.py).',
        '\t// Not in VR, with Stock reloading, or with the off hand not on the pump, every hook goes',
        '\t// straight on into BD22\'s own states. The shot itself is never touched.',
        '\tRSP_Load:\t\t// ReloadNormally, after BD22\'s own checks (before its loading animation)',
        '\t\tSHTN A 0 A_TakeInventory("RSP_Go", 1)',
        '\t\tSHTN A 0 A_GiveInventory("RSP_LoadStart", 1)',
        '\t\tSHTN A 0 A_JumpIfInventory("RSP_Go", 1, "RSP_LoadGo")',
        '\t\tGoto RSP_LoadStock',
        '\tRSP_Load2:\t\t// InsertingShells (after ReloadFromPumping, Pump2 with reload pressed, a kick)',
        '\t\tSHTN A 0 A_TakeInventory("RSP_Go", 1)',
        '\t\tSHTN A 0 A_GiveInventory("RSP_LoadStart", 1)',
        '\t\tSHTN A 0 A_JumpIfInventory("RSP_Go", 1, "RSP_LoadGo")',
        '\t\tGoto RSP_InsStock',
        '\tRSP_LoadGo:',
        '\t\tSHTN A 0 A_TakeInventory("RSP_Go", 1)',
        '\t\tSHTN A 0 A_GiveInventory("Pumping", 1)\t\t// BD22: the player sprite\'s reload',
        '\t\tSHTN A 0 A_TakeInventory("Reloading", 1)',
        '\tRSP_Next:\t\t// BD22\'s own InsertingShells / CheckIfFinishReload checks: room for another shell?',
        '\t\tSHTN A 0 A_JumpIfInventory("AmmoShell", 1, "RSP_Next1")',
        '\t\tGoto Pump2\t\t\t\t// out of shells: BD22 pumps',
        '\tRSP_Next1:',
        '\t\tSHTN A 0 A_JumpIfInventory("ShotgunAmmo", 8, "RSP_Next8")',
        '\t\tGoto RSP_LoadWait',
        '\tRSP_Next8:\t\t// an empty gun stops at 8 (its pump chambers one); a chambered round takes a 9th',
        '\t\tSHTN A 0 A_JumpIfInventory("ShotgunWasEmpty", 1, "RSP_LoadEnd")',
        '\t\tGoto RSP_LoadWait',
        '\tRSP_LoadWait:\t// the hand loads shells (rsr_pump.zs); fire ends the reload, as in BD22\'s insert frames',
        '\t\tSHTN A 1 A_WeaponReady(WRF_NOBOB|WRF_ALLOWZOOM)',
        '\t\tSHTN A 0 A_GiveInventory("RSP_LTick", 1)',
        '\t\tSHTN A 0 A_JumpIfInventory("RSP_ShellIn", 1, "RSP_Shell")',
        '\t\tSHTN A 0 A_JumpIfInventory("RSP_Back", 1, "RSP_LBack")',
        '\t\tSHTN A 0 A_JumpIfInventory("RSP_Fwd", 1, "RSP_LFwd")',
        '\t\tSHTN A 0 A_JumpIfInventory("Reloading", 1, "RSP_LoadEnd")\t// BD22: reload again finishes',
        '\t\tSHTN A 0 A_JumpIfInventory("Kicking", 1, "RSP_Kick")',
        '\t\tSHTN A 0 A_JumpIfInventory("IsRunning", 1, "StartSprint")',
        '\t\tGoto RSP_LoadWait',
        '\tRSP_Shell:\t\t// a shell pushed home: BD22\'s own step, one shell from the reserve into the tube',
        '\t\tSHTN A 0 A_TakeInventory("RSP_ShellIn", 1)',
        '\t\tSHTN A 0 A_Giveinventory("ShotgunAmmo", 1)',
        '\t\tSHTN A 0 A_Takeinventory("AmmoShell", 1, TIF_NOTAKEINFINITE)',
        '\t\tSHTN A 0 A_JumpIfInventory("ShotgunAmmo", 0, "RSP_LoadEnd")\t// full (InsertShellAnimation\'s own check)',
        '\t\tGoto RSP_Next',
        '\tRSP_LoadEnd:\t// FinishedInsertingShells, without its lowering frames (the gun never tilted)',
        '\t\tSHTN A 0 A_Takeinventory("Reloading", 1)',
        '\t\tSHTN A 0 A_JumpIfInventory("ShotgunWasEmpty", 1, "Pump2")',
        '\t\tGoto ReadyToFireAgain',
        '\tRSP_Kick:\t\t// DoKickReloading, the gun held (the hand keeps what it has)',
        '\t\tSHTN A 0 A_GunFlash("ReloadingKickFlash")',
        '\t\tSHTN AAAAAAAAAAAAAA 1 A_GiveInventory("RSP_LTick", 1)',
        '\t\tGoto RSP_LoadWait',
        '\tRSP_LBack:\t\t// the hand has the pump back while loading: a spent shell comes out as in Pump2',
        '\t\tSHTN A 0 A_TakeInventory("RSP_Back", 1)',
        '\t\tSHTN A 0 A_JumpIfInventory("ShotgunWasEmpty", 1, "RSP_LBack1")',
        '\t\tGoto RSP_LoadWait\t\t\t// a live round in: BD22\'s inspect pump, nothing comes out',
        '\tRSP_LBack1:',
        '\t\tSHTN A 0 A_JumpIfInventory("HasUnloadedShotgun", 1, "RSP_LoadWait")',
        '\t\tSHTN A 0 ' + eject,
        '\t\tGoto RSP_LoadWait',
        '\tRSP_LFwd:\t\t// forward again: the reload ends, chambered (Pump2 N)',
        '\t\tSHTN A 0 A_TakeInventory("RSP_Fwd", 1)',
        '\t\tSHTN A 0 A_Takeinventory("Reloading", 1)',
        '\t\tSHTN A 0 A_Takeinventory("ShotgunWasEmpty", 1)',
        '\t\tSHTN A 0 A_Takeinventory("HasUnloadedShotgun", 1)',
        '\t\tGoto ReadyToFireAgain',
    ]
    L += pump_block('P1', '"####" A', 20, ('Pump1+8', 'Pump1, after a shot, after BD22\'s own checks'),
                    ['BD22\'s own Pump1 G..J: the spent shell out', 'A_Takeinventory("ShotgunWasEmpty", 1)', eject,
                     'A_Giveinventory("ShotgunWasEmpty", 1)\t// (BD22: until the pump is forward again)'],
                    ['BD22\'s own Pump1 N', 'A_Takeinventory("ShotgunWasEmpty", 1)'],
                    ('Pump1+38', True), 'Pump1+8', PURIST)
    L += pump_block('P2', 'SHTN A', 17, ('Pump2+9', 'Pump2 (loaded empty, or fired with a spent shell in), after BD22\'s own checks'),
                    ['BD22\'s own Pump2 H..J', 'A_JumpIfInventory("HasUnloadedShotgun", 1, "RSP_P2Wait")', eject],
                    ['BD22\'s own Pump2 N', 'A_Takeinventory("ShotgunWasEmpty", 1)', 'A_Takeinventory("HasUnloadedShotgun", 1)'],
                    ('Pump2+32', True), 'Pump2+9', ['\t\tSHTN A 0'])
    L += pump_block('P3', 'SHT8 C', 11, ('Pump3+3', 'Pump3, after an aimed (zoomed) shot, after BD22\'s own checks'),
                    ['BD22\'s own Pump3 J', 'A_TakeInventory("ShotgunWasEmpty", 1)', 'A_FireCustomMissile("ShotCaseSpawn",40,0,14,0)'],
                    ['BD22\'s own Pump3 (its frames back)'],
                    ('Pump3+20', False), 'Pump3+3', ['\t\tSHT8 C 0'])
    return L


def bd_shotgun():
    wp = load_weapon_patch()
    wp.GATES = [g for g in wp.GATES if g[0] != 'Shotgun.dec']       # the old pauses: gone on this gun
    names = sorted({e[0] for e in wp.EDITS} | {i[0] for i in wp.INSERTS} | {g[0] for g in wp.GATES} | {'Shotgun.dec'})
    files = {n: open(BD_SRC + n, 'rb').read().decode('latin-1') for n in names}
    out = wp.patch(files)
    text = out['Shotgun.dec']
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, 'Shot_Gun')
    orig = parse_states(lines[a:b])
    # the numeric Gotos land where BD22's own jumps land (checked on BD22's own states)
    check_goto(orig, 'Pump1', 8, '####', 'B', 1, '')
    check_goto(orig, 'Pump1', 38, '####', 'A', 0, 'A_JumpIfInventory("ShotgunAmmo",1,2)')
    check_goto(orig, 'Pump2', 9, 'SHTN', 'S', 1, '')
    check_goto(orig, 'Pump2', 32, 'SHTN', 'A', 0, 'A_JumpIfInventory("FiredSecondary",1,"AltFire")')
    check_goto(orig, 'Pump3', 3, 'SHT8', 'C', 0, 'A_GiveInventory ("Pumping", 1)')
    check_goto(orig, 'Pump3', 20, 'SHT8', 'C', 0, '')
    check_goto(orig, 'Pump3', 21, 'SHTN', 'A', 0, 'A_JumpIfInventory("FiredPrimary",1,"Fire")')
    # BD22's own jump offsets these hooks replace land on the same states
    check_goto(orig, 'Pump1', 5, '####', 'A', 0, 'A_JumpIfInventory("ShotgunAmmo",1,3)')
    check_goto(orig, 'Pump2', 6, '####', 'A', 0, 'A_JumpIfInventory("ShotgunAmmo",1,3)')
    check_goto(orig, 'Pump3', 1, 'SHT8', 'C', 0, 'A_JumpIfInventory("ShotgunAmmo", 1, 2)')
    n0 = len(orig)
    # hooks (no state is added or removed in BD22's own states, so its relative jumps still land)
    for lab, old, new in (('Pump1', '"####" A 0 A_JumpIfInventory("ShotgunAmmo",1,3)', '"####" A 0 A_JumpIfInventory("ShotgunAmmo",1,"RSP_P1")'),
                          ('Pump2', '"####" A 0 A_JumpIfInventory("ShotgunAmmo",1,3)', '"####" A 0 A_JumpIfInventory("ShotgunAmmo",1,"RSP_P2")'),
                          ('Pump3', 'SHT8 C 0 A_JumpIfInventory("ShotgunAmmo", 1, 2)', 'SHT8 C 0 A_JumpIfInventory("ShotgunAmmo", 1, "RSP_P3")')):
        k = after_label(lines, a, b, lab, old, 'Shot_Gun ' + lab + ' hook')
        lines[k] = lines[k].replace(old, new + '\t// RSR-PUMP (was: A_Jump' + old.split('A_Jump')[1] + ')')
    k = once(lines, a, b, lambda i: lines[i].strip() == 'SHTN A 0 A_Takeinventory("ZoomHold",1)'
             and lines[i + 1].strip() == 'SHTN A 1 A_GiveInventory ("Pumping", 1)', 'ReloadNormally hook')
    lines[k + 1:k + 1] = ['\t\tGoto RSP_Load\t// RSR-PUMP: hand-loaded shells (zscript/rsr/rsr_pump.zs)', '\tRSP_LoadStock:']
    a, b = actor_span(lines, 'Shot_Gun')
    k = once(lines, a, b, lambda i: lines[i].strip() == 'InsertingShells:' and lines[i + 1].strip() == 'SHTN A 0', 'InsertingShells hook')
    lines[k + 2:k + 2] = ['\t\tGoto RSP_Load2\t// RSR-PUMP', '\tRSP_InsStock:']
    a, b = actor_span(lines, 'Shot_Gun')
    sb = states_brace(lines, a, b, 'Shot_Gun')
    blk = bd_block()
    lines[sb + 1:sb + 1] = blk
    a, b = actor_span(lines, 'Shot_Gun')
    new = parse_states(lines[a:b])
    if len(new) - len(parse_states(blk)) != n0:
        raise SystemExit('Shot_Gun: BD22\'s own state count changed')
    hdr = '// RSR-PUMP: hand-loaded shells and a hand-worked pump (team/reload_pump/tools/rsr_pump_patch.py); first-pickup skip (tool/weapon_patch.py); no old immersive gates; otherwise BD22\'s own file.'
    return hdr + nl + nl.join(lines)


# ---------------------------------------------------------------------------- V+ VR_Shotgun
VP_BLOCK = [
    '\t// RSR-PUMP: hand-loaded shells and a hand-worked pump (zscript/rsr/rsr_pump.zs, tools/rsr_pump_patch.py).',
    '\t// Not in VR, with Stock reloading, or with the off hand not on the pump, every hook goes',
    '\t// straight on into the set\'s own states. The shot itself is never touched.',
    '\tRSP_Load:\t\t// Reload, after the set\'s own checks (not full, shells left)',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Go", 1)',
    '\t\tSHTG A 0 A_GiveInventory("RSP_LoadStart", 1)',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Go", 1, "RSP_LoadGo")',
    '\t\tGoto StartReload',
    '\tRSP_LoadGo:',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Go", 1)',
    '\tRSP_LoadWait:\t// ReloadLoop: the hand loads shells (rsr_pump.zs); fire ends the reload, as in the set',
    '\t\tSHTG A 1 A_WeaponReady',
    '\t\tSHTG A 0 A_GiveInventory("RSP_LTick", 1)',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_ShellIn", 1, "RSP_Shell")',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Back", 1, "RSP_LBack")',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Fwd", 1, "RSP_LFwd")',
    '\t\tGoto RSP_LoadWait',
    '\tRSP_Shell:\t\t// a shell pushed home: the set\'s own InsertShell step',
    '\t\tSHTG A 0 A_TakeInventory("RSP_ShellIn", 1)',
    '\t\tSHTG A 0 A_GiveInventory("VR_ShotLoaded", 1)',
    '\t\tSHTG A 0 A_TakeInventory("VR_Shell", 1)',
    '\t\tSHTG A 0 A_JumpIfInventory("VR_ShotLoaded", 8, "ReloadEnd")\t// ReloadLoop\'s own checks',
    '\t\tSHTG A 0 A_JumpIfInventory("VR_Shell", 1, "RSP_LoadWait")',
    '\t\tGoto OutOfAmmo',
    '\tRSP_LBack:\t\t// the hand has the pump back while loading (the set never pumps in its reload)',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Back", 1)',
    '\t\tGoto RSP_LoadWait',
    '\tRSP_LFwd:\t\t// forward again: the reload ends (ReloadEnd)',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Fwd", 1)',
    '\t\tGoto ReloadEnd',
    '\tRSP_Pump:\t\t// after the shot\'s frames (BCDEFG HI), before the set\'s pump (J-Z)',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Go", 1)',
    '\t\tSHTG A 0 A_GiveInventory("RSP_PumpStart", 17)\t// 17: the set\'s own J-Z, to its refire',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Go", 1, "RSP_PGo")',
    '\t\tGoto RSP_PumpStock',
    '\tRSP_PGo:',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Go", 1)',
    '\tRSP_PWait:\t\t// the hand works the pump (rsr_pump.zs moves it, plays shotpump and ejects the shell)',
    '\t\tSHTG A 1 A_WeaponReady(WRF_NOFIRE|WRF_NOBOB|WRF_NOSECONDARY)',
    '\t\tSHTG A 0 A_GiveInventory("RSP_PTick", 1)',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Back", 1, "RSP_PBack")',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Fwd", 1, "RSP_PFwd")',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Auto", 1, "RSP_PAuto")',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Ready", 1, "RSP_PReady")',
    '\t\tGoto RSP_PWait',
    '\tRSP_PBack:',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Back", 1)',
    '\t\tGoto RSP_PWait',
    '\tRSP_PFwd:',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Fwd", 1)',
    '\t\tSHTG A 0 A_JumpIfInventory("RSP_Ready", 1, "RSP_PReady")',
    '\t\tGoto RSP_PWait\t\t// ready once the set\'s own refire time is up (RSP_Ready)',
    '\tRSP_PReady:',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Ready", 1)',
    '\t\tGoto Ready',
    '\tRSP_PAuto:\t\t// the hand left the pump before working it: the set\'s own pump',
    '\t\tSHTG A 0 A_TakeInventory("RSP_Auto", 1)',
    '\t\tGoto RSP_PumpStock',
]


def vp_shotty(text=None):
    """the set's shotty.txt (or another patcher's version of it, e.g. the break-open reload's VR_SuperShotgun
    edits): only the VR_Shotgun actor is changed"""
    if text is None:
        text = open(VP_SRC + 'shotty.txt', 'rb').read().decode('latin-1')
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    a, b = actor_span(lines, 'VR_Shotgun')
    n0 = len(parse_states(lines[a:b]))
    # FIX_SWITCH (tool/vplus/vplus_patch.py): the slow lower / raise the fast-switch jump expects
    for old in ('    SHTG A 1 A_Lower(60)', '    SHTG A 1 A_Raise(60)'):
        k = once(lines, a, b, lambda i: lines[i] == old, 'FIX_SWITCH ' + old.strip())
        lines[k + 1:k + 1] = ['    Loop', old.replace('(60)', '')]
        a, b = actor_span(lines, 'VR_Shotgun')
    # the pump: after the shot's frames
    k = once(lines, a, b, lambda i: lines[i] == '    SHTG HI 1', 'VR_Shotgun pump hook')
    if lines[k + 1].strip() != 'SHTG A 0 A_PlaySound("shotpump", CHAN_WEAPON)':
        raise SystemExit('VR_Shotgun: shotpump not after SHTG HI')
    lines[k + 1:k + 1] = ['\t\tGoto RSP_Pump\t// RSR-PUMP: a hand-worked pump (zscript/rsr/rsr_pump.zs)', '\tRSP_PumpStock:']
    # the reload: after its own checks
    old = '    TNT1 A 0 A_JumpIfInventory("VR_Shell", 1, "StartReload")'
    k = once(lines, a, b, lambda i: lines[i] == old, 'VR_Shotgun reload hook')
    lines[k] = old.replace('"StartReload")', '"RSP_Load")\t// RSR-PUMP: hand-loaded shells (was: StartReload)')
    a, b = actor_span(lines, 'VR_Shotgun')
    sb = states_brace(lines, a, b, 'VR_Shotgun')
    lines[sb + 1:sb + 1] = VP_BLOCK
    a, b = actor_span(lines, 'VR_Shotgun')
    if len(parse_states(lines[a:b])) - len(parse_states(VP_BLOCK)) != n0 + 2:      # FIX_SWITCH adds the two slow states
        raise SystemExit('VR_Shotgun: the set\'s own state count changed')
    hdr = ('// RSR-PUMP: hand-loaded shells and a hand-worked pump on VR_Shotgun (team/reload_pump/tools/rsr_pump_patch.py),'
           ' and its default weapon-switch crash fixed (tool/vplus/vplus_patch.py FIX_SWITCH); otherwise the set\'s own file'
           ' (VR_SuperShotgun as the set ships it).')
    return hdr + nl + nl.join(lines)


def main(out):
    os.makedirs(out + '/actors/Weapons', exist_ok=True)
    os.makedirs(out + '/Decorate', exist_ok=True)
    t = bd_shotgun()
    open(out + '/actors/Weapons/Shotgun.dec', 'wb').write(t.encode('latin-1'))
    t2 = vp_shotty()
    open(out + '/Decorate/shotty.txt', 'wb').write(t2.encode('latin-1'))
    print('Shotgun.dec', len(t), 'shotty.txt', len(t2))


if __name__ == '__main__':
    main(sys.argv[1])
