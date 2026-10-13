"""Generate zscript/rsq/gunmoves.zs for a set: how each hand-table gun's model moves under
the gun hand and the support hand (rsq/hands.zs keeps both on it).

  python3 rsq_gunmoves_gen.py bd22  <out.zs>
  python3 rsq_gunmoves_gen.py vplus <out.zs>

Per gun:   Pivot   where the gun model turns when its layer is offset (raise, lower, a
                   kick by Offset / A_WeaponOffset), relative to where the hand models turn
           Mirrored  the gun model's MODELDEF Scale x has the other sign from the hands'
                   (Vanilla VR Plus's own guns), so a sideways turn of its layer goes the other way
           Blends  the engine blends this gun's model frames (no NoInterpolation)
Per fire frame (sprite, frame) whose model frame moves the gun body off the ready frame
(the recoil is in the meshes): the turn (ModifyBobLayer3D angles: yaw about y, pitch about x,
roll about z) and the move, both in the hand models' frame (cm: x left, y up, z back) the
way hands.zs uses them.

The frames are the ones fire_frames.py finds (Fire / AltFire / Hold / AltHold until the gun
is back at Ready). The move of the body is a trimmed rigid fit (kick_measure.py), so a bolt,
magazine or trigger moving on its own does not count.
"""
import sys, os, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kick_measure as km
import fire_frames as ff

D = np.diag([-1.0, 1.0, 1.0])
O_H = np.array([0.0, -10.0, -24.0])      # the hand models' Offset 0 -24 -10 (Scale -1 1 1), pre-scale
MIN_MOVE = 0.3                           # cm at the gun body: smaller is not worth a row
MIN_TURN = 0.4                           # degrees


def rot_y(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rot_x(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def rot_z(a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def turn(e):
    return rot_y(e[0]) @ rot_x(e[1]) @ rot_z(e[2])


def angles(R):
    return np.array([math.degrees(math.atan2(R[0, 2], R[2, 2])), math.degrees(math.asin(max(-1, min(1, -R[1, 2])))),
                     math.degrees(math.atan2(R[1, 0], R[1, 1]))])


def place(hook, hook_rot, gun_angles, k_turn, k_move, pivot):
    """the runtime math of hands.zs (RSQ_Follow.Place): what ModifyBobLayer3D gives a hand layer"""
    Q, K, H = turn(gun_angles), turn(k_turn), turn(hook_rot)
    E = angles(Q @ K @ H)
    v = k_move + K.T @ (Q.T @ pivot - pivot)
    return hook + H.T @ v, E


def gun_blocks(blocks, cls, rk):
    first = next((b for b in blocks if b['cls'].lower() == cls.lower() and rk in b['keys']), None)
    if not first:
        return None
    keys, nointerp = {}, {}
    for b in blocks:
        if b['cls'].lower() == cls.lower() and b['path'].lower() == first['path'].lower() and b['mesh'].lower() == first['mesh'].lower():
            for k, f in b['keys'].items():
                keys.setdefault(k, f)
                nointerp.setdefault(k, b['nointerp'])
    return dict(first, keys=keys, nointerp_keys=nointerp)


def find_mesh(roots, blk):
    for r in roots:
        p = km.find_file(r, blk['path'] + '/' + blk['mesh'])
        if p:
            return p
    return None


def build(which):
    blocks, root, ready, order = km.sets(which)
    roots = [root] if which == 'bd22' else [root, root + '/FILTER/DOOM']
    guns, rows, report = [], [], []
    for cls, idx in order:
        idx = int(idx)
        rk = ready.get(cls)
        blk = gun_blocks(blocks, cls, rk) if rk else None
        path = find_mesh(roots, blk) if blk else None
        if not path:
            report.append('%s: no model found, left out' % cls)
            guns.append((idx, cls, np.zeros(3), False, False))
            continue
        xs, ys, zs = blk['scale']
        xo, yo, zo = blk['off']
        pivot = D @ np.array([xo, zo, yo]) - O_H
        mirrored = xs > 0
        blends = not blk['nointerp_keys'].get(rk, blk['nointerp'])
        guns.append((idx, cls, pivot, mirrored, blends))
        try:
            fire = ff.fire_keys(ff.weapon(which, cls), rk)
        except KeyError:
            fire = {}
        get, nfr = (km.iqm_frames if path.lower().endswith('.iqm') else km.md3_frames)(path)
        rf = blk['keys'][rk]
        a = km.to_ctrl(get(rf), blk)
        cache = {}
        n = 0
        for key in sorted(fire):
            spr, fr = key.split()
            f = blk['keys'].get((spr, fr))
            if f is None or f == rf or f >= nfr:
                continue
            if f not in cache:
                b = km.to_ctrl(get(f), blk)
                Rw, tw, err = km.rigid(a, b)
                d = np.linalg.norm(a @ Rw.T + tw - a, axis=1)
                cache[f] = (Rw, tw, float(np.percentile(d, 95)), km.angle_of(Rw), err)
            Rw, tw, move95, ang, err = cache[f]
            if move95 < MIN_MOVE and ang < MIN_TURN:
                continue
            Rk = D @ Rw @ D
            bk = Rk @ O_H - O_H + D @ tw
            u = Rk.T @ bk
            rows.append(dict(gun=idx, cls=cls, spr=spr, fr=ord(fr) - ord('A'), frl=fr, turn=angles(Rk), move=u,
                             f=f, move95=move95, ang=ang, err=err))
            n += 1
        report.append('%-24s pivot %s mirrored %d blends %d  %d fire frames, %d move the gun' % (
            cls, np.round(pivot, 2), mirrored, blends, len(fire), n))
    return guns, rows, report


def selftest(which, guns, rows):
    """drive the runtime math through RenderHUDModel's chain and check the hand stays on the gun"""
    rng = np.random.default_rng(1)
    blocks, root, ready, order = km.sets(which)
    worst = 0.0
    for (idx, cls, pivot, mirrored, blends) in guns:
        rk = ready.get(cls)
        blk = gun_blocks(blocks, cls, rk) if rk else None
        if not blk:
            continue
        xs, ys, zs = blk['scale']
        xo, yo, zo = blk['off']
        Sg = np.array([xs, zs, ys]); offg = np.array([xo, zo, yo])
        mine = [r for r in rows if r['gun'] == idx] or [None]
        for r in mine[:3]:
            for gx, gy in ((0, 32), (6, 40), (-9, 70), (3, 128)):
                hook = rng.normal(0, 8, 3); hrot = rng.normal(0, 30, 3) if rng.random() < 0.5 else np.zeros(3)
                y = rng.normal(0, 10, 3)
                kt = r['turn'] if r else np.zeros(3); kmv = r['move'] if r else np.zeros(3)
                a = gx / 4.0; b = (gy - 32) / -4.0
                T, E = place(hook, hrot, np.array([-a if mirrored else a, b, 0.0]), kt, kmv, pivot)
                # the hand as the engine draws it (controller frame, cm)
                w_hand = D @ (O_H + turn(E) @ (T + y))
                # the same point at rest, carried along by the gun: kick (mesh frame) then layer turn
                w0 = D @ (O_H + turn(hrot) @ (hook + y))
                if r:
                    Rk = turn(kt); bk = Rk @ kmv
                    Rw = D @ Rk @ D; tw = D @ (bk - Rk @ O_H + O_H)
                    w1 = Rw @ w0 + tw
                else:
                    w1 = w0
                x = (w1 - offg) / Sg                     # the gun's own pre-scale frame
                w2 = Sg * (turn((a, b, 0)) @ x) + offg   # its layer turn about its origin
                worst = max(worst, float(np.linalg.norm(w2 - w_hand)))
    return worst


def emit(which, guns, rows, out):
    n = max(g[0] for g in guns)
    piv = [np.zeros(3)] * (n + 1)
    mir = [0] * (n + 1)
    ble = [0] * (n + 1)
    names = [''] * (n + 1)
    for idx, cls, pivot, mirrored, blends in guns:
        piv[idx] = pivot; mir[idx] = int(mirrored); ble[idx] = int(blends); names[idx] = cls
    L = ['// generated by rsq_gunmoves_gen.py (%s) -- do not edit by hand' % which,
         '// How each gun\'s model moves under the gun hand and the support hand (rsq/hands.zs keeps',
         '// both on it). Indexed like RSQ_HandTable. Units are ModifyBobLayer3D\'s in the hand models\'',
         '// frame: centimetres, x left, y up, z back; angles yaw about y, pitch about x, roll about z.',
         '', 'class RSQ_GunMoves abstract play', '{']
    L += ['\t// where the gun model turns when its layer is offset (raise, lower, a kick by Offset),',
          '\t// from where the hand models turn',
          '\tclearscope static Vector3 Pivot(int i)', '\t{']
    L.append('\t\tstatic const double v[] = { %s };' % ', '.join('%.3f, %.3f, %.3f' % tuple(p) for p in piv))
    L += ['\t\tif (i <= 0 || 3 * i + 2 >= v.Size())', '\t\t\treturn (0, 0, 0);', '\t\treturn (v[3 * i], v[3 * i + 1], v[3 * i + 2]);', '\t}', '']
    L += ['\t// the gun model is mirrored left-right against the hands (its Scale x is positive),',
          '\t// so a sideways turn of its layer turns the other way',
          '\tclearscope static bool Mirrored(int i)', '\t{',
          '\t\tstatic const int v[] = { %s };' % ', '.join(str(x) for x in mir),
          '\t\treturn i > 0 && i < v.Size() && v[i] != 0;', '\t}', '']
    L += ['\t// the engine blends this gun\'s model frames from one state to the next (no NoInterpolation)',
          '\tclearscope static bool Blends(int i)', '\t{',
          '\t\tstatic const int v[] = { %s };' % ', '.join(str(x) for x in ble),
          '\t\treturn i > 0 && i < v.Size() && v[i] != 0;', '\t}', '']
    # one move per (gun, model frame); the sprite frames that show it grouped per sprite
    moves, mindex, groups = [], {}, {}
    for r in rows:
        mk = (r['gun'], r['f'])
        if mk not in mindex:
            mindex[mk] = len(moves)
            moves.append(r)
        groups.setdefault((r['gun'], r['spr'], mindex[mk]), []).append(r['frl'])
    def num(v):
        t = '%.2f' % v
        return '0.00' if t == '-0.00' else t
    # One table per kind, declared first: this VM indexes a function's constant table wrongly
    # once it starts past entry 255 of its kind (codegen.cpp FxArrayElement::Emit adds the
    # start to the index register in place), so x[], y[], z[] of 100 rows each would break.
    L += ['\t// how the model frame shown for (sprite, frame) has turned and moved the gun off its ready',
          '\t// frame (the recoil is in the meshes): the turn, and the move in the turned frame.',
          '\t// Only the fire frames that move it are listed. key: gun, row in v; spr: the sprite, then',
          '\t// its frames that show that row; v: turn x y z, move x y z. (One table of each kind:',
          '\t// the VM gets a function\'s constant tables wrong past 255 entries of one kind.)',
          '\tstatic Vector3, Vector3 Frame(int i, int sprite, int frame)', '\t{']
    if rows:
        gk = sorted(groups)
        L.append('\t\tstatic const int key[] = { %s };' % ', '.join('%d, %d' % (g[0], g[2]) for g in gk))
        L.append('\t\tstatic const String spr[] = { %s };' % ', '.join(
            '"%s%s"' % (g[1], ''.join(sorted(set(groups[g]))).replace('\\', '\\\\')) for g in gk))
        L.append('\t\tstatic const double v[] = {')
        for m in moves:
            L.append('\t\t\t%s,' % ', '.join(num(x) for x in list(m['turn']) + list(m['move'])))
        L[-1] = L[-1].rstrip(',')
        L.append('\t\t};')
        L += ['\t\tString f = String.Format("%c", 65 + frame);',
              '\t\tfor (int k = 0; k < spr.Size(); k++)', '\t\t{',
              '\t\t\tif (key[2 * k] == i && spr[k].IndexOf(f, 4) >= 0 && Actor.GetSpriteIndex(spr[k].Left(4)) == sprite)',
              '\t\t\t{', '\t\t\t\tint b = key[2 * k + 1] * 6;',
              '\t\t\t\treturn (v[b], v[b + 1], v[b + 2]), (v[b + 3], v[b + 4], v[b + 5]);', '\t\t\t}', '\t\t}']
    L += ['\t\treturn (0, 0, 0), (0, 0, 0);', '\t}', '}', '']
    open(out, 'w').write('\n'.join(L))


def main(which, out):
    guns, rows, report = build(which)
    for line in report:
        print(line)
    for r in rows:
        print('   %-16s %s%s -> f%-3d move95 %5.2f cm turn %5.2f  -> turn %s move %s' % (
            r['cls'], r['spr'], r['frl'], r['f'], r['move95'], r['ang'], np.round(r['turn'], 2), np.round(r['move'], 2)))
    print('rows', len(rows), 'moves', len({(r['gun'], r['f']) for r in rows}), 'groups', len({(r['gun'], r['spr'], r['f']) for r in rows}))
    print('selftest: worst hand-to-gun error %.4f cm' % selftest(which, guns, rows))
    emit(which, guns, rows, out)
    json.dump([dict(r, turn=list(r['turn']), move=list(r['move'])) for r in rows], open(out + '.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
