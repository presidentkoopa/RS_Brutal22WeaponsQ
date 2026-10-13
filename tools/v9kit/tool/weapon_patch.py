"""Replacement copies of BD22 weapon files, shipped inside our pk3 at the same
paths so they override BD22's (the br_vr way). Load our pk3 AFTER BD22.

The only changes: where BD22 blanks the gun (TNT1) in the middle of normal
use, the gun stays on screen. State counts are unchanged, so every relative
jump in the files still lands where it did. Each edit names the exact original
line; if BD22's file differs, the build stops.
"""

# (file, line number in BD22's file, original line stripped, replacement)
EDITS = [
    # grenade launcher: reload, inspect, unload, first pickup -- hold the frame before the gap
    ('GrenadeLaunch.dec', 262, 'TNT1 A 4 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)',
     '"####" "#" 4 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'),
    ('GrenadeLaunch.dec', 51, 'TNT1 A 4 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)',
     'GRL3 D 4 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'),
    ('GrenadeLaunch.dec', 292, 'TNT1 A 12 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)',
     'GRLN K 12 A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'),
    ('GrenadeLaunch.dec', 141, 'TNT1 AAAA 1 A_WeaponReady(WRF_ALLOWZOOM)',
     'GRLN YYYY 1 A_WeaponReady(WRF_ALLOWZOOM)'),
    # super shotgun: reload, single-shell reload, unload
    ('SSG.dec', 425, 'TNT1 A 4 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)',
     '"####" "#" 4 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'),
    ('SSG.dec', 465, 'TNT1 A 3 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)',
     'SHZ3 E 3 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'),
    ('SSG.dec', 506, 'TNT1 A 16 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)',
     'SHZ3 E 16 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'),
    # axe: end of the swing (keeps the blood-colour sprite via ####)
    ('Axe.dec', 246, 'TNT1 AA 1 A_SetPitch(pitch+2)', '"####" LL 1 A_SetPitch(pitch+2)'),
    ('Axe.dec', 247, 'TNT1 A 2', '"####" L 2'),
    ('Axe.dec', 248, 'TNT1 AAAAA 1 A_SetPitch(pitch-2)', '"####" LLLLL 1 A_SetPitch(pitch-2)'),
    ('Axe.dec', 324, 'TNT1 A 3', 'AXEA L 3'),
    ('Axe.dec', 325, 'TNT1 AAAAAAAA 1 A_SetAngle(angle-2)', 'AXEA LLLLLLLL 1 A_SetAngle(angle-2)'),
    # chainsaw: the 2-tic gap at the start of firing
    ('Saw.dec', 182, 'TNT1 A 2', '"####" "#" 2'),
    ('Saw.dec', 234, 'TNT1 A 2', '"####" "#" 2'),
    # dragonslayer: after the swing the sword comes back at its return pose
    # instead of vanishing (BD22 slides it 620 px off screen first)
    ('Dragonslayer.dec', 81, 'TNT1 AA 1 A_SetAngle(angle+8)', 'DSLC DD 1 Offset(-64, 128) A_SetAngle(angle+8)'),
    ('Dragonslayer.dec', 82, 'TNT1 AA 1 A_SetAngle(angle+4)', 'DSLC DD 1 A_SetAngle(angle+4)'),
    ('Dragonslayer.dec', 83, 'TNT1 AA 1 A_SetAngle(angle+2)', 'DSLC DD 1 A_SetAngle(angle+2)'),
    ('Dragonslayer.dec', 85, 'TNT1 A 5', 'DSLC D 5'),
    ('Dragonslayer.dec', 86, 'TNT1 AAAAAAAA 1 A_JumpIfInventory("FiredPrimary", 1, "Attack2")',
     'DSLC DDDDDDDD 1 A_JumpIfInventory("FiredPrimary", 1, "Attack2")'),
    ('Dragonslayer.dec', 112, 'TNT1 AA 1 A_SetAngle(angle-8)', 'DSLC DD 1 Offset(64, 128) A_SetAngle(angle-8)'),
    ('Dragonslayer.dec', 113, 'TNT1 AA 1 A_SetAngle(angle-4)', 'DSLC DD 1 A_SetAngle(angle-4)'),
    ('Dragonslayer.dec', 114, 'TNT1 AA 1 A_SetAngle(angle-2)', 'DSLC DD 1 A_SetAngle(angle-2)'),
]


# first pickup: every gun goes straight to its normal raise. The jump into the
# first-pickup animation becomes "take the never-selected token" (same state
# count, so nothing else moves); the rifle's game-start warm-up likewise.
EDITS += [
    ('AssaultShotgun.dec', 44, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedASG", 1, "FirstSelectAnimation")', 'TNT1 A 0 A_TakeInventory("NeverSelectedASG", 1)'),
    ('GrenadeLaunch.dec', 104, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedGL",1,"FirstSelectAnim")', 'TNT1 A 0 A_TakeInventory("NeverSelectedGL", 1)'),
    ('Minigun.dec', 105, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedMinigun", 1,"FirstSelectAnimation")', 'TNT1 A 0 A_TakeInventory("NeverSelectedMinigun", 1)'),
    ('Mp40.dec', 112, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedMP40", 1, "FirstSelectAnimation")', 'TNT1 A 0 A_TakeInventory("NeverSelectedMP40", 1)'),
    ('Pistol.dec', 89, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedPistol", 1,2)', 'TNT1 A 0 A_TakeInventory("NeverSelectedPistol", 1)'),
    ('Plasma.dec', 123, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedPlasma", 1, "FirstSelectAnimation")', 'TNT1 A 0 A_TakeInventory("NeverSelectedPlasma", 1)'),
    ('Railgun.dec', 106, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedRailgun",1,"FirstSelectAnim")', 'TNT1 A 0 A_TakeInventory("NeverSelectedRailgun", 1)'),
    ('Revolver.dec', 148, 'SHTN A 0 A_JumpIfInventory("NeverSelectedRevolver", 1, "FirstSelectAnimation")', 'SHTN A 0 A_TakeInventory("NeverSelectedRevolver", 1)'),
    ('Rifle.dec', 123, 'TNT1 A 0 A_JumpIfInventory("JustStartedGame",1,"WarmUp")', 'TNT1 A 0 A_TakeInventory("JustStartedGame", 1)'),
    ('Rifle.dec', 129, 'TNT1 A 0 A_JumpIfInventory("JustStartedGame", 1,"warmUp")', 'TNT1 A 0 A_TakeInventory("JustStartedGame", 1)'),
    ('Rifle.dec', 130, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedRifle", 1,2)', 'TNT1 A 0 A_TakeInventory("NeverSelectedRifle", 1)'),
    ('RocketLauncher.dec', 81, 'MISG A 0 A_JumpIfInventory("NeverSelectedRL", 1, "FirstSelectAnimation")', 'MISG A 0 A_TakeInventory("NeverSelectedRL", 1)'),
    ('Shotgun.dec', 107, 'SHTN A 0 A_JumpIfInventory("NeverSelectedShotgun", 1, "FirstSelectAnimation")', 'SHTN A 0 A_TakeInventory("NeverSelectedShotgun", 1)'),
    ('Sniper.dec', 61, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedSniper",1,"FirstSelectAnimation")', 'TNT1 A 0 A_TakeInventory("NeverSelectedSniper", 1)'),
    ('SubMachinegun.dec', 44, 'TNT1 A 0 A_JumpIfInventory("NeverSelectedSMG", 1, "FirstSelectAnimation")', 'TNT1 A 0 A_TakeInventory("NeverSelectedSMG", 1)'),
]

# chainsaw: after each sweep BD22 parks the saw on a frame with no art for 8
# tics ("[" -- off screen left after one sweep, right after the other). Hold the
# last frame of the sweep instead, so the saw stays where the swing ended.
EDITS += [('Saw.dec', n, '"####" "[" 8 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB)',
           '"####" "#" 8 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB)') for n in (216, 267, 331, 397)]


def _kickflash(spr, fr):
    """Same timing as BrutalWeapon's KickFlash family, gun at its ready frame
    (every other BD22 gun keeps itself on screen this way while kicking)."""
    s = '%s %s' % (spr, fr)
    return ['\t// kick / slide: keep the weapon on screen (posefix weapon_patch.py)',
            '\tKickFlash:', '\t\t%s%s 1' % (spr + ' ', fr * 4), '\t\t%s 10' % s, '\t\t%s%s 1' % (spr + ' ', fr * 4), '\t\tstop',
            '\tSlideFlash:', '\t\t%s%s 1' % (spr + ' ', fr * 4), '\t\t%s 35' % s, '\t\tstop',
            '\tSlideFlashEnd:', '\t\t%s 5' % s, '\t\t%s%s 1' % (spr + ' ', fr * 4), '\t\tstop',
            '\tSlideFlashEndEarly:', '\t\t%s 2' % s, '\t\t%s%s 1' % (spr + ' ', fr * 4), '\t\tstop']


# VR melee (zscript/rsvr/melee.zs): the axe's alt-fire holds the axe; swing and
# let go to throw it. RSVR_AxeGrip reads the button and the hand each tic. Not
# in VR, alt-fire goes to BD22's own sideways swing, kept whole as "SideSwing".
EDITS += [('Axe.dec', 282, 'AltFire:', 'SideSwing:')]

AXE_VR_ALT = [
    '\t// VR (posefix weapon_patch.py + zscript/rsvr/melee.zs): alt-fire holds the axe;',
    '\t// swing and let go to throw it. Not in VR: BD22\'s sideways swing (SideSwing).',
    '\tAltFire:',
    '\t\t4XEG A 0 A_JumpIfInventory("IsPlayingAsPurist", 1, 6)',
    '\t\t1XEG A 0 A_JumpIfInventory("PowerBloodOnVisor", 1, 5)',
    '\t\t2XEG A 0 A_JumpIfInventory("PowerBlueBloodOnVisor", 1, 4)',
    '\t\t3XEG A 0 A_JumpIfInventory("PowerGreenBloodOnVisor", 1, 3)',
    '\t\t5XEG A 0 A_JumpIfInventory("PowerAlienBloodOnVisor", 1, 2)',
    '\t\tAXEG A 0',
    '\t\t"####" A 0 A_TakeInventory("RSVR_AxeThrown", 1)',
    '\tAltGrip:',
    '\t\t"####" A 0 A_GiveInventory("RSVR_AxeGrip", 1)',
    '\t\t"####" A 0 A_JumpIfInventory("RSVR_NotVR", 1, "SideSwing")',
    '\t\t"####" A 0 A_JumpIfInventory("RSVR_AxeThrown", 1, "AxeThrown")',
    '\t\t"####" A 0 A_JumpIfInventory("RSVR_AxeHolding", 1, "AltGripHold")',
    '\t\tGoto Ready',
    '\tAltGripHold:',
    '\t\t"####" A 1',
    '\t\tGoto AltGrip',
    '\tAxeThrown:',
    '\t\tTHRW F 0 A_TakeInventory("RSVR_AxeThrown", 1)',
    '\t\tTHRW F 0 A_TakeInventory("RSVR_AxeHolding", 1)',
    '\t\tTHRW FGHIJ 1',
    '\t\tTHRW J 0 A_TakeInventory("PowerBloodOnVisor", 1)',
    '\t\tTHRW J 0 A_TakeInventory("PowerBlueBloodOnVisor", 1)',
    '\t\tTHRW J 0 A_TakeInventory("PowerGreenBloodOnVisor", 1)',
    '\t\tTHRW J 0 A_TakeInventory("PowerAlienBloodOnVisor", 1)',
    '\t\tTHRW J 2',
    '\t\tPONG RQP 1',
    '\t\tPONG P 1 ACS_NamedExecuteAlways("FistSelect", 0, 0, 0, 0)',
    '\t\tPONG P 5',
    '\t\tGoto Ready',
]

# (file, line number of the weapon actor's 'States' opening brace, lines to insert after it)
INSERTS = [
    ('Dragonslayer.dec', 16, _kickflash('DSLA', 'A')),
    ('IncendiaryLauncher.dec', 13, _kickflash('M202', 'A')),
    ('Axe.dec', 12, AXE_VR_ALT),
]


# ---------------------------------------------------------------------------
# Immersive reload (zscript/rsq/reload.zs). Each gate is a pause in BD22's own
# reload animation: after the named line the gun asks RSQ_Gate whether the step
# is done (hand away for a magazine, hand at the magazine well, slide / bolt /
# pump pulled, a shell at the loading port). With rsq_reload 0, or not in VR,
# the answer is always yes and the gate costs no time: its states are all
# 0 tics, and the first of them shows exactly what BD22's next state shows, so
# even the model's frame blending is unchanged. Gates add no states inside
# BD22's sequences (a Goto and a label take no state), so every relative jump
# still lands where it did; the gate's own states sit at the top of States.
#
# (file, gun id, kind, line in BD22's file, that line stripped, frame held
#  while waiting, split) -- split = (first part, second part) cuts one line of
# frames in two without changing its state count; the gate goes between them.
FETCH, INSERT, RACK, SHELL = 1, 2, 3, 4
GUN_IDS = {'Rifle': 1, 'BrutalPistol': 2, 'BrutalSMG': 3, 'MP40': 4, 'Sniper': 5,
           'AssaultShotgun': 6, 'Shot_Gun': 7, 'Revolver': 8, 'SSG': 9,
           'Rocket_Launcher': 10, 'RailGun': 11, 'Plasma_Gun': 12, 'GrenadeLauncher': 13}
_WR = 'A_WEAPONREADY(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)'
GATES = [
    # assault rifle: magazine out / in, then the bolt on an empty gun
    ('Rifle.dec', 1, FETCH, 699, 'RIFR H 3 ' + _WR, 'RIFR H', None),
    ('Rifle.dec', 1, INSERT, 700, 'RIFR IJKLMNNO 1 ' + _WR, 'RIFR O', None),
    ('Rifle.dec', 1, RACK, 714, '2IFR H 3 ' + _WR, '2IFR H', None),
    # pistol: empty (slide) and with a round chambered
    ('Pistol.dec', 2, FETCH, 376, '2ISR ABCDEFGG 1 ' + _WR, '2ISR G', None),
    ('Pistol.dec', 2, INSERT, 378, '2ISR MNO 1 ' + _WR, '2ISR O', None),
    ('Pistol.dec', 2, RACK, 400, '2ISR PQRSS 1 ' + _WR, '2ISR S', None),
    ('Pistol.dec', 2, FETCH, 411, 'PISR ABCDEFGG 1 ' + _WR, 'PISR G', None),
    ('Pistol.dec', 2, INSERT, 413, 'PISR MNO 1 ' + _WR, 'PISR O', None),
    # SMG
    ('SubMachinegun.dec', 3, FETCH, 386, 'SMGR O 1 A_FireCustomMissile("EmptyClip2Spawn",-5,0,8,-4)', 'SMGR O', None),
    ('SubMachinegun.dec', 3, INSERT, 388, 'SMGR PPPQRSTUUUUV 1 ' + _WR, 'SMGR V', None),
    # MP40: empty, then charge; and with a round chambered
    ('Mp40.dec', 4, FETCH, 394, 'MP4R "[\\]" 1 ' + _WR, 'MP4R ]', None),
    ('Mp40.dec', 4, INSERT, 397, '2P4R CCCCCCDEFGHHH 1 ' + _WR, '2P4R H', None),
    ('Mp40.dec', 4, RACK, 402, '2P4R IJKL 1 ' + _WR, '2P4R L', None),
    ('Mp40.dec', 4, FETCH, 424, 'MP40 A 0 A_FireCustomMissile("EmptyClip2Spawn",-5,0,8,-4)', '2P4R ]', None),
    ('Mp40.dec', 4, INSERT, 425, '3P4R ABCDEEEEEEEFGHIIJJJ 1 ' + _WR, '3P4R J', None),
    # sniper: magazine, then the bolt on an empty gun
    ('Sniper.dec', 5, FETCH, 515, 'X21G A 0 A_FireCustomMissile("EmptySniperAmmoSpawn",-5,0,8,-4)', 'X21R M', None),
    ('Sniper.dec', 5, INSERT, 518, 'X21R RSTU 1 ' + _WR, 'X21R U', None),
    ('Sniper.dec', 5, RACK, 563, 'X22R K 5 ' + _WR, 'X22R K', None),
    # assault shotgun: drum, then the bolt on an empty gun
    ('AssaultShotgun.dec', 6, FETCH, 411, 'USAS A 0 A_GiveInventory("HasUnloadedASG",1)', 'USAR O', None),
    ('AssaultShotgun.dec', 6, INSERT, 414, 'USAR TUVW 1 ' + _WR, 'USAR W', None),
    ('AssaultShotgun.dec', 6, RACK, 438, '2SAR M 3 ' + _WR, '2SAR M', None),
    # pump shotgun: one shell per pass (can still fire), the pump after loading
    ('Shotgun.dec', 7, SHELL, 573, 'SHTN AA 0 A_JumpIfInventory("ShotgunAmmo",8,"CheckIfFinishReload")', 'SHTN T', None),
    ('Shotgun.dec', 7, SHELL, 595, 'SHTN A 0 A_Giveinventory("ShotgunAmmo",1)', 'SHTN T', None),   # the 9th shell
    ('Shotgun.dec', 7, RACK, 290, 'SHTN TSFG 1', 'SHTN G', None),
    # revolver: one round per pass
    ('Revolver.dec', 8, SHELL, 339, 'REVO A 0 A_Takeinventory("AmmoShell",1,TIF_NOTAKEINFINITE)', 'REVR Q', None),
    # super shotgun: two shells, and one
    ('SSG.dec', 9, FETCH, 411, '"####" A 0 A_GiveInventory("SSGReloadToken", 1)', '"####" K', None),
    ('SSG.dec', 9, INSERT, 415, '"####" OPQSTTU 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)\t//removed u frame', '"####" U', None),
    ('SSG.dec', 9, FETCH, 452, 'TNT1 A 0 A_GunFlash("ReloadSmoke2",GFF_NOEXTCHANGE)', 'SHZ3 K', None),
    ('SSG.dec', 9, INSERT, 456, 'SHZ2 XXYY 1 A_WeaponReady(WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM)', 'SHZ2 Y', None),
    # rocket launcher
    ('RocketLauncher.dec', 10, FETCH, 532, 'MISR FGH 1 ' + _WR, 'MISR H', None),
    ('RocketLauncher.dec', 10, INSERT, 535, 'MISR N 3 ' + _WR, 'MISR N', None),
    # railgun: the cell comes out during one long line of frames
    ('Railgun.dec', 11, FETCH, 541, 'RAIR ABCDEFGHHIIIIIIIIII 1 ' + _WR, 'RAIR I',
     ('RAIR ABCDEFGHHI 1 ' + _WR, 'RAIR IIIIIIIII 1 ' + _WR)),
    ('Railgun.dec', 11, INSERT, 541, None, 'RAIR I', None),
    # plasma rifle
    ('Plasma.dec', 12, FETCH, 581, 'PRSR AAZBCDEFGHH 1 ' + _WR, 'PRSR H', None),
    ('Plasma.dec', 12, INSERT, 582, 'PRSR I 10 ' + _WR, 'PRSR I', None),
    # grenade launcher
    ('GrenadeLaunch.dec', 13, FETCH, 251, '"####" A 0 A_GiveInventory("GLReloadToken", 1)', '"####" K', None),
    ('GrenadeLaunch.dec', 13, INSERT, 253, '"####" QRTTUU 1 ' + _WR, '"####" U', None),
]
GATE_WAIT = {FETCH: 'WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM', INSERT: 'WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM',
             RACK: 'WRF_NOBOB|WRF_NOFIRE|WRF_ALLOWZOOM', SHELL: 'WRF_NOBOB|WRF_ALLOWZOOM'}

PK3_DIR = 'actors/Weapons/'


def _first_state(line):
    """sprite and first frame of the first state on a line of frames, written so
    DECORATE reads them back the same ('"####" "#"', 'RIFR I', 'MP4R "["')"""
    s = line.strip()
    toks = []
    i = 0
    while len(toks) < 2:
        while s[i] in ' \t':
            i += 1
        if s[i] == '"':
            j = s.index('"', i + 1)
            toks.append(s[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < len(s) and s[j] not in ' \t':
                j += 1
            toks.append(s[i:j])
            i = j
    spr, frames = toks
    fr = frames.strip('"')[0]
    if fr == '\\':
        raise SystemExit('gate next frame is a backslash: %r' % line)
    if not fr.isalpha() and fr not in '[]#':
        raise SystemExit('unexpected frame %r in %r' % (fr, line))
    return '%s %s' % (spr, fr if fr.isalpha() else '"%s"' % fr)


def _gate_block(tag, nxt, hold, code, kind):
    """the gate's own states. The first three show what BD22's next state shows
    (so the frame before the gate blends exactly as it did); waiting shows the
    frame the gun stopped on and re-asks every tic."""
    return [
        '\t// posefix rsq gate %s (zscript/rsq/reload.zs): passes at once with stock reloading' % tag,
        '\tRSQ_%s_G:' % tag,
        '\t\t%s 0 A_TakeInventory("RSQ_Pass", 1)' % nxt,
        '\t\t%s 0 A_GiveInventory("RSQ_Gate", %d)' % (nxt, code),
        '\t\t%s 0 A_JumpIfInventory("RSQ_Pass", 1, "RSQ_%s_R")' % (nxt, tag),
        '\tRSQ_%s_W:' % tag,
        '\t\t%s 1 A_WeaponReady(%s)' % (hold, GATE_WAIT[kind]),
        '\t\t%s 0 A_GiveInventory("RSQ_Gate", %d)' % (hold, code),
        '\t\t%s 0 A_JumpIfInventory("RSQ_Pass", 1, "RSQ_%s_R")' % (hold, tag),
        '\t\tGoto RSQ_%s_W' % tag,
    ]


def _apply_gates(name, lines, orig):
    """lines: the file after EDITS (same line numbers as BD22's); orig: BD22's
    lines. Returns the lines with the gates in."""
    gates = [g for g in GATES if g[0] == name]
    if not gates:
        return lines
    after = {}         # original line -> lines to put after it
    splits = {}        # original line -> (first part, lines between, second part)
    blocks = {}        # States brace line -> gate blocks
    for k, (f, gun, kind, n, text, hold, split) in enumerate(gates):
        tag = '%d%s' % (gun, 'abcdefghij'[k])
        code = kind * 100 + gun
        if text is not None and orig[n - 1].strip() != text:
            raise SystemExit('%s:%d is %r, expected %r' % (f, n, orig[n - 1].strip(), text))
        if lines[n - 1] != orig[n - 1]:
            raise SystemExit('%s:%d gate on an edited line' % (f, n))
        indent = orig[n - 1][:len(orig[n - 1]) - len(orig[n - 1].lstrip())]
        goto = [indent + 'Goto RSQ_%s_G\t// posefix rsq gate' % tag, '\tRSQ_%s_R:' % tag]
        if split:
            a, b = split
            if (a.split()[0], len(a.split()[1]) + len(b.split()[1]), a.split()[2:]) != \
                    (text.split()[0], len(text.split()[1]), text.split()[2:]) or b.split()[2:] != text.split()[2:]:
                raise SystemExit('%s:%d split changes the states' % (f, n))
            splits[n] = (indent + a + '\t// posefix rsq: one line split in two, same states', goto, indent + b)
            nxt = _first_state(b)
        else:
            after.setdefault(n, []).extend(goto)
            m = n
            while True:      # BD22's next state: skip labels, comments, blanks
                s = orig[m].split('//')[0].strip()
                if s and not s.endswith(':'):
                    break
                m += 1
            if s.lower().startswith(('goto', 'stop', 'loop', 'wait')):
                raise SystemExit('%s:%d gate before a jump' % (f, n))
            nxt = _first_state(orig[m])
        b = n
        while not (orig[b - 1].strip() == '{' and orig[b - 2].strip().lower() == 'states'):
            b -= 1
        blocks.setdefault(b, []).extend(_gate_block(tag, nxt, hold, code, kind))
    # later lines first, so earlier line numbers stay valid
    for n in sorted(set(after) | set(splits) | set(blocks), reverse=True):
        if n in splits:
            a, mid, b = splits[n]
            lines[n - 1:n] = [a] + mid + [b] + after.get(n, [])
        else:
            lines[n:n] = after.get(n, []) + blocks.get(n, [])
    return lines


def patch(files):
    """files: {basename: text} of BD22's originals -> {basename: patched text}"""
    out = {}
    for name in sorted({e[0] for e in EDITS} | {i[0] for i in INSERTS} | {g[0] for g in GATES}):
        text = files[name]
        nl = '\r\n' if '\r\n' in text else '\n'
        lines = text.split(nl)
        orig = list(lines)
        for f, n, old, new in EDITS:
            if f != name:
                continue
            got = lines[n - 1].strip()
            if got != old:
                raise SystemExit('%s:%d is %r, expected %r' % (f, n, got, old))
            indent = lines[n - 1][:len(lines[n - 1]) - len(lines[n - 1].lstrip())]
            lines[n - 1] = indent + new + '\t// posefix: was ' + old
        lines = _apply_gates(name, lines, orig)
        for f, n, add in sorted(INSERTS, key=lambda x: -x[1]):
            if f != name:
                continue
            if lines[n - 1].strip() != '{' or lines[n - 2].strip().lower() != 'states':
                raise SystemExit('%s:%d is not the States brace' % (f, n))
            lines[n:n] = add
        header = ('// posefix: BD22 brutal22test6 file. Lines marked "posefix" are the only changes '
                  '(gun kept on screen where BD22 blanked it; first-pickup animation skipped; '
                  'Axe.dec: VR axe throw on alt-fire; "rsq gate": optional immersive reload pauses).')
        out[name] = header + nl + nl.join(lines)
    return out
