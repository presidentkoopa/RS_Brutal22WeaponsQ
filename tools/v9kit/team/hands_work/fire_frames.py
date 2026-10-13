"""Which (sprite, frame)s each hand-table gun shows while firing: the states reached from
Fire / AltFire / Hold / AltHold before the gun is back at Ready (or goes to reload,
select, zoom, ...). Uses tool/decsim.py's DECORATE state model.

usage: fire_frames.py bd22|vplus  -> fire_<set>.json {class: ["SPRT F", ...]}
"""
import sys, os, re, json, zipfile
from collections import deque

S = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
W = S + '/team/hands_work'
sys.path.insert(0, S + '/tool')
import decsim

ROOTS = ('Fire', 'AltFire', 'Hold', 'AltHold')
STOP_ROOTS = ('Ready', 'Select', 'Deselect', 'Reload', 'Zoom', 'User1', 'User2', 'User3', 'User4', 'Spawn', 'NoAmmo')
STOP_WORDS = re.compile(r'(?<!no)reload|unload|select|ready|inspect|sprint|zoom|pickup|kick|melee|taunt|salute|grenade|throw|switch', re.I)

BD22_FILES = {'AssaultShotgun': 'AssaultShotgun.dec', 'BFG10k': 'BFG10k.dec', 'BIG_FUCKING_GUN': 'BFG.dec',
              'BrutalPistol': 'Pistol.dec', 'BrutalSMG': 'SubMachinegun.dec', 'Devastator': 'Devastator.dec',
              'Flamethrower2': 'Flamethrower.dec', 'GrenadeLauncher': 'GrenadeLaunch.dec',
              'HellishMissileLauncher': 'HellishMissile.dec', 'IncendiaryLauncher': 'IncendiaryLauncher.dec',
              'MG42': 'MG42.dec', 'MP40': 'Mp40.dec', 'Minigun': 'Minigun.dec', 'NukeLauncher': 'NukeLauncher.dec',
              'Plasma_Gun': 'Plasma.dec', 'RailGun': 'Railgun.dec', 'Revolver': 'Revolver.dec', 'Rifle': 'Rifle.dec',
              'Rocket_Launcher': 'RocketLauncher.dec', 'SSG': 'SSG.dec', 'Shot_Gun': 'Shotgun.dec',
              'Sniper': 'Sniper.dec', 'Unmaker': 'Unmaker.dec'}
VP_FILES = {'VR_Revolver': 'revolver.txt', 'VR_Revolver2': 'revolver.txt', 'VR_Rifle': 'rifle.txt',
            'VR_Shotgun': 'shotty.txt', 'VR_SuperShotgun': 'shotty.txt', 'Vanilla_BFG9000': 'bfg9000.txt',
            'Vanilla_Chaingun': 'chaingun.txt', 'Vanilla_Chainsaw': 'chainsaw.txt',
            'Vanilla_PlasmaRifle': 'plasmarifle.txt', 'Vanilla_RocketLauncher': 'rocketlauncher.txt'}


def block_from_text(text, actor):
    p = W + '/_dec_tmp.txt'
    open(p, 'w').write(text)
    return decsim.actor_states_block(p, actor)


def weapon(which, cls):
    if which == 'bd22':
        parent = decsim.actor_states_block(S + '/bd22src/actors/Weapons/DEFAULTWEAPON.dec', 'BrutalWeapon')
        f = BD22_FILES[cls]
        p = W + '/v8/actors/Weapons/' + f        # the pack's patched copy when there is one
        if not os.path.exists(p):
            p = S + '/bd22src/actors/Weapons/' + f
        return decsim.Weapon(parent, decsim.actor_states_block(p, cls), cls)
    f = VP_FILES[cls]
    z = zipfile.ZipFile(S + '/team/vplus/RS_VanillaVRPlus_VR_v9_sharedhands.pk3')
    if 'Decorate/' + f in z.namelist():
        child = block_from_text(z.read('Decorate/' + f).decode('latin-1'), cls)
    else:
        child = decsim.actor_states_block('/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2/FILTER/DOOM/Decorate/' + f, cls)
    return decsim.Weapon([], child, cls)


def fire_keys(w, start=('?', '?')):
    """start: the (sprite, frame) the gun shows when it fires (its ready key), for \"####\" states"""
    # a stop label stops the whole run of states up to the next label (so "Goto Ready+6" stops too)
    starts = sorted({v for tab in (w.ptab, w.ctab) for v in tab.values() if isinstance(v, int)} | {len(w.states), w.off})
    stops = set()
    for tab in (w.ptab, w.ctab):
        for lab in tab:
            if lab in [r.lower() for r in STOP_ROOTS] or STOP_WORDS.search(lab):
                j = w.resolve(tab, lab)
                if j is not None:
                    end = min(x for x in starts if x > j) if any(x > j for x in starts) else len(w.states)
                    stops.update(range(j, end))
    for r in ROOTS:
        j = w.resolve(w.ctab, r)
        if j is not None:
            stops.discard(j)
    shown = {}
    seen = set()
    q = deque()
    for r in ROOTS:
        j = w.resolve(w.ctab, r)
        if j is not None:
            q.append((j, start[0], start[1]))
    while q:
        node = q.popleft()
        if node in seen:
            continue
        seen.add(node)
        i, cs, cf = node
        if i is None or i < 0 or i >= len(w.states) or i in stops:
            continue
        st = w.states[i]
        spr = st['spr'] if st['spr'] != '####' else cs
        fr = st['fr'] if st['fr'] != '#' else cf
        succ, always = w.successors(i)
        if st['tics'] != 0 and not always and spr != '?' and fr != '?':
            shown.setdefault('%s %s' % (spr, fr), st['line'][:50])
        for j, kind in succ:
            if kind in ('weaponready', 'raise'):
                continue
            q.append((j, spr, fr))
        if len(seen) > 100000:
            break
    return shown


def main(which):
    files = BD22_FILES if which == 'bd22' else VP_FILES
    out = {}
    for cls in files:
        try:
            w = weapon(which, cls)
        except KeyError as e:
            print(cls, 'not found', e)
            continue
        ks = fire_keys(w)
        out[cls] = sorted(ks)
        print('%-24s %s' % (cls, ' '.join(k.replace(' ', '') for k in sorted(ks))))
    json.dump(out, open(W + '/fire_%s.json' % which, 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
