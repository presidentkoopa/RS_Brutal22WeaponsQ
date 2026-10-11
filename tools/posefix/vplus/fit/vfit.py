"""Hands for Vanilla VR Plus. Shared meshes take BD22's fits (moved by the placement
difference); the set's own guns are fitted the same way BD22's were (fitall.run)."""
import sys, json
import numpy as np
import vplus, guns
sys.path.insert(0, vplus.H)
import align, handfit, support, handtable, fitall, ermac
OUT = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/vplus/'
TABLE = {
    'VR_Rifle': ('plasma', 'shotgun', ('wrap', 28)),
    'VR_Revolver': ('pistol', 'pistol', ('same',)),
    'VR_Shotgun': ('shotgun', 'shotgun', ('wrap', 35)),
    'VR_SuperShotgun': ('ssg', 'ssg', ('wrap', 16)),
}
handtable.TABLE.update(TABLE)

def shared(v, b, bd):
    """the same mesh drawn by a different placement: move every hand by the gun's move"""
    it_v, it_b = guns.item(v), guns.item(b)
    import gunview, hudrender
    pv = gunview.to_fl(hudrender.to_local(np.asarray(gunview.item_mesh(it_v)[0][1], float), it_v))
    pb = gunview.to_fl(hudrender.to_local(np.asarray(gunview.item_mesh(it_b)[0][1], float), it_b))
    dflu = (pv - pb).mean(0)
    r = json.loads(json.dumps(bd))
    r['gun_shift'] = (np.array(r['gun_shift']) + dflu).round(2).tolist()
    r['target'] = (np.array(r['target']) + dflu).round(2).tolist()
    if 'sup_hook' in r:   # rotated support: the hook sits inside the rotation
        R = support.rot(r['sup_rot'])
        dl = np.array([-dflu[1], dflu[2], -dflu[0]])      # FLU -> local
        dl = dl * np.array([-1, 1, 1])                    # Scale x -1
        r['sup_hook'] = (np.array(r['sup_hook']) + np.linalg.inv(R) @ dl).round(2).tolist()
    else:
        r['sup_shift'] = (np.array(r['sup_shift']) + dflu).round(2).tolist()
    r['from'] = b
    return r, dflu

if __name__ == '__main__':
    bdfits = json.load(open(vplus.H + '/fits.json'))
    res = {}
    try:
        res = json.load(open(OUT + 'vfits.json'))
    except Exception:
        pass
    only = sys.argv[1:]
    for v, b in vplus.SHARED.items():
        if only and v not in only: continue
        r, d = shared(v, b, bdfits[b])
        res[v] = r
        print(v, 'from', b, 'moved', d.round(2), r)
    for c in TABLE:
        if only and c not in only: continue
        r, t, t2 = fitall.run(c)
        res[c] = r
        print(c, r, flush=True)
    json.dump(res, open(OUT + 'vfits.json', 'w'), indent=1)
