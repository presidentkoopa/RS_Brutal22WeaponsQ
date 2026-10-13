#!/usr/bin/env python3
"""DECORATE weapon state-machine explorer (BD22 BrutalWeapon + one subclass).

Finds every (sprite, frame) a psprite layer can actually DISPLAY (state tics != 0
and not an always-taken A_Jump), resolving "####"/"#" along real paths, on the
weapon layer and on the flash layer (A_GunFlash targets).

Semantics modelled (GZDoom):
  - static Goto/Loop/Wait/Stop resolve against the DEFINING class's labels
    (inherited BrutalWeapon states keep BrutalWeapon's targets)
  - string targets of A_Jump* resolve at runtime against the SUBCLASS labels
  - integer jump targets are offsets from the current state
  - "####" / "#" keep the psprite's current sprite / frame, which 0-tic states
    passed through also set
"""
import re, os, sys
from collections import deque

STATE = re.compile(r'^\s*(?P<spr>"####"|####|"[A-Za-z0-9_]{4}"|[A-Za-z0-9_]{4})\s+'
                   r'(?P<fr>"[^"]+"|[A-Za-z0-9\[\]\\_#^]+)\s+'
                   r'(?P<tics>-?\d+|random\s*\([^)]*\))(?P<rest>.*)$', re.I)
LABEL = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*:(?!:)\s*(?P<after>.*)$')
FLOW = re.compile(r'^\s*(goto)\s+([A-Za-z0-9_.:]+)\s*(?:\+\s*(\d+))?|^\s*(loop|stop|wait|fail)\b', re.I)


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), text, flags=re.S)
    return '\n'.join(l.split('//')[0] for l in text.split('\n'))


def actor_states_block(path, actor):
    text = strip_comments(open(path, errors='replace').read())
    m = re.search(r'^\s*actor\s+' + re.escape(actor) + r'\b[^\n]*', text, re.I | re.M)
    if not m:
        raise KeyError(actor)
    i = text.index('{', m.end() - 1 if text[m.end() - 1] == '{' else m.end())
    depth = 0
    j = i
    while True:
        c = text[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = text[i + 1:j]
    s = re.search(r'\bstates\b\s*\{', body, re.I)
    if not s:
        return []
    k = s.end()
    depth = 1
    e = k
    while depth:
        if body[e] == '{':
            depth += 1
        elif body[e] == '}':
            depth -= 1
        e += 1
    return body[k:e - 1].split('\n')


def split_args(s):
    out, depth, cur, q = [], 0, '', False
    for c in s:
        if c == '"':
            q = not q
        if not q and c == '(':
            depth += 1
        if not q and c == ')':
            depth -= 1
        if not q and depth == 0 and c == ',':
            out.append(cur.strip())
            cur = ''
            continue
        cur += c
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_action(rest):
    # strip keywords
    r = re.sub(r'\b(bright|fast|slow|nodelay|canraise)\b', ' ', rest, flags=re.I)
    r = re.sub(r'\b(offset|light)\s*\([^)]*\)', ' ', r, flags=re.I)
    m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*(\((.*)\))?\s*$', r.strip())
    if not m:
        return None, []
    name = m.group(1)
    args = split_args(m.group(3)) if m.group(3) is not None else []
    return name, args


class Block:
    def __init__(self, lines, owner):
        self.owner = owner
        self.states = []      # dicts
        self.labels = {}      # lower -> index or ('alias', label, off)
        pending = []
        last_seq_label = None
        for raw in lines:
            line = raw.strip()
            while True:
                m = LABEL.match(line)
                if m and not STATE.match(line):
                    pending.append(m.group(1))
                    line = m.group('after').strip()
                    continue
                break
            if not line:
                continue
            f = FLOW.match(line)
            if f:
                if f.group(1):
                    tgt = (f.group(2), int(f.group(3) or 0))
                    kind = 'goto'
                else:
                    kind = f.group(4).lower()
                    tgt = None
                if pending:
                    # label directly followed by a flow keyword: alias
                    for p in pending:
                        self.labels[p.lower()] = ('alias', kind, tgt, len(self.states))
                    pending = []
                    if kind == 'goto':
                        continue
                if self.states:
                    st = self.states[-1]
                    if kind == 'goto':
                        st['next'] = ('goto', tgt[0], tgt[1])
                    elif kind == 'loop':
                        st['next'] = ('index', last_seq_label)
                    elif kind == 'wait':
                        st['next'] = ('index', len(self.states) - 1)
                    else:
                        st['next'] = ('stop',)
                continue
            m = STATE.match(line)
            if not m:
                continue
            spr = m.group('spr').strip('"').upper()
            frs = m.group('fr').strip('"')
            t = m.group('tics')
            tics = 1 if t.lower().startswith('random') else int(t)
            name, args = parse_action(m.group('rest'))
            for n, fch in enumerate(frs):
                idx = len(self.states)
                if pending:
                    for p in pending:
                        self.labels[p.lower()] = idx
                    last_seq_label = idx
                    pending = []
                self.states.append(dict(spr=spr, fr=fch.upper() if fch != '#' else '#',
                                        tics=tics, act=name, args=args, next=('fall',),
                                        owner=owner, line=raw.strip()))
        for p in pending:
            self.labels[p.lower()] = len(self.states)


class Weapon:
    def __init__(self, parent_lines, child_lines, child_name):
        self.P = Block(parent_lines, 'BrutalWeapon')
        self.C = Block(child_lines, child_name)
        self.off = len(self.P.states)
        self.states = self.P.states + self.C.states
        self.ptab = self._table(self.P, 0)
        self.ctab = dict(self.ptab)
        self.ctab.update(self._table(self.C, self.off))

    def _table(self, blk, base):
        t = {}
        for k, v in blk.labels.items():
            if isinstance(v, int):
                t[k] = base + v
        # aliases
        for k, v in blk.labels.items():
            if not isinstance(v, int):
                _, kind, tgt, at = v
                t[k] = ('alias', kind, tgt, base + at)
        return t

    def resolve(self, table, label, off=0):
        lab = label.lower()
        if '::' in lab:
            lab = lab.split('::')[-1]
            table = self.ptab
        v = table.get(lab)
        seen = 0
        while isinstance(v, tuple) and seen < 10:
            seen += 1
            _, kind, tgt, at = v
            if kind == 'goto':
                lab2, off2 = tgt
                v2 = table.get(lab2.lower())
                if isinstance(v2, int):
                    return v2 + off2 + off
                v = v2
            else:
                return None
        if isinstance(v, int):
            return v + off
        return None

    def successors(self, i):
        """[(index or None for stop, kind)] for state i."""
        st = self.states[i]
        tab = self.ptab if st['owner'] == 'BrutalWeapon' else self.ctab
        out = []
        always = False
        act = (st['act'] or '').lower()
        args = st['args']
        if act.startswith('a_jump'):
            if act == 'a_jump':
                targets = args[1:]
                try:
                    always = int(args[0]) >= 256
                except Exception:
                    pass
            else:
                targets = args[-1:] if args else []
            for t in targets:
                t = t.strip()
                if t.startswith('"'):
                    lab = t.strip('"')
                    mm = re.match(r'([^+]+)\+(\d+)$', lab)
                    j = self.resolve(self.ctab, mm.group(1), int(mm.group(2))) if mm else self.resolve(self.ctab, lab)
                    if j is not None:
                        out.append((j, 'jump'))
                elif re.match(r'^-?\d+$', t):
                    out.append((i + int(t), 'jump'))
        if act == 'a_raise':
            j = self.resolve(self.ctab, 'Ready')
            if j is not None:
                out.append((j, 'raise'))
        if act == 'a_weaponready':
            flags = ' '.join(args).upper()
            labs = []
            if 'WRF_NOFIRE' not in flags:
                if 'WRF_NOPRIMARY' not in flags:
                    labs.append('Fire')
                if 'WRF_NOSECONDARY' not in flags:
                    labs.append('AltFire')
            if 'WRF_ALLOWRELOAD' in flags or args[:1] == ['1']:
                labs.append('Reload')
            if 'WRF_ALLOWZOOM' in flags:
                labs.append('Zoom')
            for u in ('1', '2', '3', '4'):
                if 'WRF_ALLOWUSER' + u in flags:
                    labs.append('User' + u)
            if 'WRF_NOSWITCH' not in flags:
                labs.append('Deselect')
            for lab in labs:
                j = self.resolve(self.ctab, lab)
                if j is not None:
                    out.append((j, 'weaponready'))
        if act in ('a_refire', 'a_refire'):
            for lab in ('Hold', 'Fire'):
                j = self.resolve(self.ctab, lab)
                if j is not None:
                    out.append((j, 'refire'))
                    break
        if not always:
            nx = st['next']
            if nx[0] == 'fall':
                if i + 1 < len(self.states) and (i + 1 < self.off) == (i < self.off):
                    out.append((i + 1, 'fall'))
            elif nx[0] == 'goto':
                j = self.resolve(tab, nx[1], nx[2])
                if j is not None:
                    out.append((j, 'goto'))
            elif nx[0] == 'index':
                base = 0 if st['owner'] == 'BrutalWeapon' else self.off
                if nx[1] is not None:
                    out.append((base + nx[1], 'loop'))
        return out, always

    def flash_targets(self, i):
        st = self.states[i]
        if (st['act'] or '').lower() != 'a_gunflash':
            return []
        if st['args'] and st['args'][0].startswith('"'):
            j = self.resolve(self.ctab, st['args'][0].strip('"'))
            return [j] if j is not None else []
        out = []
        for lab in ('AltFlash', 'Flash'):
            j = self.resolve(self.ctab, lab)
            if j is not None:
                out.append(j)
        return out


ROOTS = ('Select', 'Deselect', 'Ready', 'Fire', 'AltFire', 'Reload', 'Zoom',
         'User1', 'User2', 'User3', 'User4', 'Hold', 'AltHold')


def explore(w):
    """Return {layer: {(spr,fr): set(labels-ish)}} and unresolved notes."""
    disp = {'weapon': {}, 'flash': {}}
    seen = set()
    q = deque()
    for r in ROOTS:
        j = w.resolve(w.ctab, r)
        if j is not None:
            q.append(('weapon', j, '?', '?'))
    while q:
        node = q.popleft()
        if node in seen:
            continue
        seen.add(node)
        layer, i, cs, cf = node
        if i is None or i < 0 or i >= len(w.states):
            continue
        st = w.states[i]
        spr = st['spr'] if st['spr'] != '####' else cs
        fr = st['fr'] if st['fr'] != '#' else cf
        succ, always = w.successors(i)
        if st['tics'] != 0 and not always:
            disp[layer].setdefault((spr, fr), set()).add(st['line'][:60])
        for j in w.flash_targets(i):
            q.append(('flash', j, '?', '?'))
        for j, kind in succ:
            q.append((layer, j, spr, fr))
        if len(seen) > 200000:
            break
    return disp


D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bd22src/actors/Weapons')
CLASSES = {'AssaultShotgun': 'AssaultShotgun.dec', 'BIG_FUCKING_GUN': 'BFG.dec', 'BrutalAxe': 'Axe.dec',
           'BrutalPistol': 'Pistol.dec', 'BrutalSMG': 'SubMachinegun.dec', 'Chain_saw': 'Saw.dec',
           'DSweap': 'Dragonslayer.dec', 'FlameCannon': 'FlameCannon.dec', 'Flamethrower2': 'Flamethrower.dec',
           'HellishMissileLauncher': 'HellishMissile.dec', 'GrenadeLauncher': 'GrenadeLaunch.dec', 'MP40': 'Mp40.dec',
           'Minigun': 'Minigun.dec', 'Plasma_Gun': 'Plasma.dec', 'Rocket_Launcher': 'RocketLauncher.dec',
           'RailGun': 'Railgun.dec', 'Revolver': 'Revolver.dec', 'Rifle': 'Rifle.dec', 'SSG': 'SSG.dec',
           'Shot_Gun': 'Shotgun.dec', 'Unmaker': 'Unmaker.dec'}


def load(cls):
    parent = actor_states_block(os.path.join(D, 'DEFAULTWEAPON.dec'), 'BrutalWeapon')
    child = actor_states_block(os.path.join(D, CLASSES[cls]), cls)
    return Weapon(parent, child, cls)


def spawn_pairs(cls):
    w = load(cls)
    j = w.resolve(w.ctab, 'Spawn')
    out = set()
    seen = set()
    while j is not None and j not in seen and 0 <= j < len(w.states):
        seen.add(j)
        st = w.states[j]
        if st['tics'] != 0:
            out.add((st['spr'], st['fr']))
        succ, _ = w.successors(j)
        j = succ[0][0] if succ else None
    return out


if __name__ == '__main__':
    cls = sys.argv[1]
    w = load(cls)
    d = explore(w)
    for layer in ('weapon', 'flash'):
        print('==', layer, len(d[layer]))
        for (s, f), ls in sorted(d[layer].items()):
            print('   %s %s   e.g. %s' % (s, f, sorted(ls)[0]))
