"""Regenerate tool/bd22_displayed.json 'displayed' from a patched BD22 DECORATE dir
(keeps art_sprites / art_frames, which describe BD22's art and do not change)."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tool'))
import decsim

def displayed(decorate_dir):
    decsim.D = decorate_dir
    decsim.CLASSES.update({'MG42': 'MG42.dec', 'BFG10k': 'BFG10k.dec', 'Sniper': 'Sniper.dec',
                           'IncendiaryLauncher': 'IncendiaryLauncher.dec', 'NukeLauncher': 'NukeLauncher.dec',
                           'Devastator': 'Devastator.dec', 'Melee_Attacks': 'Melee.dec', 'HandGrenades': 'Grenades.dec'})
    out = {}
    for cls in sorted(decsim.CLASSES):
        d = decsim.explore(decsim.load(cls))
        out[cls] = sorted([list(k) for k in set(d['weapon']) | set(d['flash']) if k[0] not in ('TNT1', '?') and len(k[0]) == 4 and k[1] != '?'])
    return out

if __name__ == '__main__':
    src, ddir, dst = sys.argv[1:4]
    j = json.load(open(src))
    new = displayed(ddir)
    old = j['displayed']
    for c in sorted(set(old) | set(new)):
        a = {tuple(x) for x in old.get(c, [])}; b = {tuple(x) for x in new.get(c, [])}
        if a != b:
            print(c, 'added', sorted(b - a)[:40], 'removed', sorted(a - b)[:40])
    j['displayed'] = new
    if dst != '-':
        json.dump(j, open(dst, 'w'))
