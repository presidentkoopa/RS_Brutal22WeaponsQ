"""Shared parts of the v9 pack builders (build_bd22_v9.py, build_vplus_v9.py).

Reads, never writes: tool/, team/reload_release/ (or the --reload dir), team/melee_hands/,
team/hands.zs, team/gunmoves_*.zs, the v8 packs. Writes only the output pk3 (via a .tmp,
then an atomic rename) and a scratch folder team/out_v9/_work/<set>/.

The real VR reload release (DIR = team/reload_release by default) is first copied to
team/out_v9/_work/release/<set>/ (retried until two hashes of the tree agree, so a publish
landing mid-build cannot mix versions); everything below reads that snapshot:
  src/rsr_weapons.json, rsr_files.json   the release's own manifests (what build_proto.py
                                  ships per set); their paths point into team/reload/src and
                                  are mapped to the snapshot's src/
  weapon files (manifest)         BD22: replace our GATES=[] copy (checked: only lines inserted);
                                  V+: replace our FIX_SWITCH copy (checked the same way)
  other files (manifest)          the clear skin per gun model folder, split meshes
  src/zscript/rsr/*.zs            shipped; vreload.zs reads rsr_reload instead of rsq_reload
  src/zscript/rsvr/vrhand.zs      shipped
  src/MODELDEF.rsr.<bd|vp> + MODELDEF.rsr.hands -> MODELDEF.rsr;  src/CVARINFO.rsr
  tools/hands_hook.py             run on team/hands.zs
  tools/build_proto.py            read for the menu's VR-reload help lines (not run: it builds
                                  from out/quick.pk3 and writes into team/reload/src)
  tools/gen_rsr.py, rsr_patch.py  run into the snapshot's regen/ as a cross-check that src/
                                  is what the tools make today (a difference is a warning)
"""
import difflib, os, re, struct, subprocess, sys, zipfile

sys.dont_write_bytecode = True

TEAM = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(TEAM)
V9SRC = os.path.join(TEAM, 'v9src')
OUTDIR = os.path.join(TEAM, 'out_v9')
RELOAD_DEFAULT = os.path.join(TEAM, 'reload_merged') if os.path.isdir(os.path.join(TEAM, 'reload_merged')) \
    else os.path.join(TEAM, 'reload_release')     # the merged reloads (RSR + break-open + pump) when there
NEW_DATE = (2026, 10, 11, 12, 0, 0)

# v8's immersive reload carried ammo in the off hand (hands.zs AmmoB..AmmoG, ammo_hand.md3 frames
# 0-5 with these meshes and skins). Nothing can show them in v9: they are left out.
OLD_CARRY_FILES = ['models/rsq/' + f for f in (
    'mag_pistol.md3', 'shot_shell.md3', 'shot_shell2.md3', 'mag_chaingun.md3', 'pod_rocket.md3', 'mag_plasma.md3',
    'berettam9.jpg', 'shells.png', 'chaingun.png', 'rocketlauncher.png', 'plasmarifle.png')]
OLD_CARRY_LETTERS = 'BCDEFG'

# names the owner will read in the menu
GUN_NAMES = {'Rifle': 'assault rifle', 'VR_Rifle': 'M16'}

CHANGED = []      # gun lines a reload hook changed one for one (same state count)


def log(*a):
    print(*a)
    sys.stdout.flush()


# ------------------------------------------------------------------------------ md3

def md3_frames(data):
    return struct.unpack_from('<i', data, 76)[0]


def md3_frame_verts(data, k):
    """the vertex bytes of frame k, all surfaces"""
    nsurf, ofs = struct.unpack_from('<i', data, 84)[0], struct.unpack_from('<i', data, 100)[0]
    out = b''
    for _ in range(nsurf):
        nf, nshader, nvert, ntri, otri, osh, ost, oxyz, oend = struct.unpack_from('<9i', data, ofs + 72)
        n = nvert * 8
        out += data[ofs + oxyz + k * n: ofs + oxyz + (k + 1) * n]
        ofs += oend
    return out


# ------------------------------------------------------------------------------ text helpers

def replace_once(t, old, new, what):
    if t.count(old) != 1:
        raise SystemExit('%s: anchor found %d times: %r' % (what, t.count(old), old[:90]))
    return t.replace(old, new)


def modeldef_blocks(text):
    """[(start, end, body)] of every top-level 'Model X { ... }' block"""
    out = []
    for m in re.finditer(r'(?m)^Model\s+\w+\s*\r?\n?\{', text):
        depth, i = 0, m.end() - 1
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out.append((m.start(), i + 1, text[m.start():i + 1]))
    return out


def strip_old_carry_blocks(md):
    """MODELDEF.rsq without the RSQ_Hands blocks of v8's carried ammo (RQHN B..G)"""
    cut = []
    for a, b, body in modeldef_blocks(md):
        letters = set(re.findall(r'FrameIndex\s+RQHN\s+(\w)\s', body))
        if letters and letters <= set(OLD_CARRY_LETTERS):
            cut.append((a, b))
        elif letters & set(OLD_CARRY_LETTERS):
            raise SystemExit('MODELDEF.rsq: a block mixes carried-ammo frames with others')
    if len(cut) != len(OLD_CARRY_LETTERS):
        raise SystemExit('MODELDEF.rsq: expected %d carried-ammo blocks, found %d' % (len(OLD_CARRY_LETTERS), len(cut)))
    for a, b in reversed(cut):
        while b < len(md) and md[b] in '\r\n':
            b += 1
        md = md[:a] + md[b:]
    md = md.replace('// the free hand (off controller): open, a fist, or holding ammo',
                    '// the free hand (off controller): open, or a fist')
    for f in OLD_CARRY_FILES:
        if os.path.basename(f) in md:
            raise SystemExit('MODELDEF.rsq still names %s' % f)
    return md


# ------------------------------------------------------------------------------ the reload release

def _tree_hash(d):
    import hashlib
    h = hashlib.sha1()
    for root, dirs, files in os.walk(d):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            st = os.stat(p)
            h.update(('%s %d %d\n' % (os.path.relpath(p, d), st.st_size, st.st_mtime_ns)).encode())
    return h.hexdigest()


def snapshot_release(rdir, kind):
    """copy the parts of the release the build uses; returns the snapshot dir and its hash"""
    import shutil
    dst = os.path.join(OUTDIR, '_work', 'release', kind)
    parts = ['src', 'tools', 'rtest/vrhand_rsr.zs', 'rtest/rsb_testdriver.zs', 'rtest/pump_test.zs', 'DESIGN.md', 'PROGRESS.md']
    for attempt in range(10):
        h0 = _tree_hash(rdir)
        shutil.rmtree(dst, ignore_errors=True)
        os.makedirs(dst)
        try:
            for p in parts:
                s = os.path.join(rdir, p)
                if os.path.isdir(s):
                    shutil.copytree(s, os.path.join(dst, p), ignore=shutil.ignore_patterns('__pycache__'))
                elif os.path.isfile(s):
                    os.makedirs(os.path.dirname(os.path.join(dst, p)), exist_ok=True)
                    shutil.copy2(s, os.path.join(dst, p))
        except (FileNotFoundError, shutil.Error):
            import time
            time.sleep(3)
            continue
        if _tree_hash(rdir) == h0:
            return dst, h0
        import time
        time.sleep(3)
    raise SystemExit('the reload release kept changing while it was copied: try again')


def _manifest(src, name, kind, live_src, rel_src=None):
    """{pk3 path: snapshot file} from the release's manifest (None if it has none)"""
    import json
    p = os.path.join(src, name)
    if not os.path.isfile(p):
        return None
    m = json.load(open(p)).get(kind, {})
    out = {}
    for k, v in m.items():
        v = os.path.normpath(v)
        for base in [b for b in (live_src, rel_src, src) if b]:
            if v.startswith(base + os.sep):
                f = os.path.join(src, os.path.relpath(v, base))
                break
        else:
            raise SystemExit('%s: %s -> %s is not under the reload src' % (name, k, v))
        if not os.path.isfile(f):
            raise SystemExit('%s: %s -> %s is not in the release' % (name, k, f))
        out[k] = f
    return out


def menu_help(snap):
    """the VR-reload help lines the release's own menu shows (tools/build_proto.py)"""
    bp = os.path.join(snap, 'tools', 'build_proto.py')
    t = open(bp).read()
    a = t.find('RSRReload "Reloading"')
    if a < 0:
        raise SystemExit('build_proto.py: its Reloading item is not there any more; update the menu help by hand')
    seg = t[a:]
    seg = seg[:seg.find('old2')] if 'old2' in seg else seg[:3000]
    lines = re.findall(r"'\\tStaticText \"([^\"]+)\", 1\\n'", seg)
    if len(lines) < 3:
        raise SystemExit('build_proto.py: could not read its VR-reload help lines')
    pb = os.path.join(snap, 'tools', 'pump_build.py')
    if os.path.isfile(pb):
        pl = re.findall(r"'\\tStaticText \"([^\"]+)\", 1\\n'", open(pb).read())
        if pl:
            lines += [' '] + pl
    if os.path.isfile(os.path.join(snap, 'src', 'zscript', 'rsr', 'rsr_break.zs')):
        lines += [' ', 'Break-open guns and revolvers, VR: reload opens',
                  'the gun. Take a shell or round (off trigger, or',
                  'grip away from the gun), put it in a chamber from',
                  'behind and push it home. Flick the gun shut, or',
                  'push it shut with the off hand.']
    return lines


def read_release(rdir, kind):
    """the release's files for one set: {pk3 path: bytes}, the weapon files, the gun classes.
    Handles the merged layout too: several reloads in src/zscript/rsr (vreload.zs, rsr_break.zs,
    rsr_pump.zs, ...), the per-set gun table rsr_guns.<set>.zs, MODELDEF.<group>.<set> +
    MODELDEF.<group>.hands groups, several CVARINFO.*, and hands hooks tools/hands_hook.py then
    tools/*_hands_hook.py."""
    rdir = os.path.abspath(rdir)
    snap, thash = snapshot_release(rdir, kind)
    src = os.path.join(snap, 'src')
    live_src = os.path.join(TEAM, 'reload', 'src')
    other = 'vp' if kind == 'bd' else 'bd'
    for n in ['zscript/rsr/vreload.zs', 'zscript/rsvr/vrhand.zs', 'CVARINFO.rsr', 'MODELDEF.rsr.hands',
              'MODELDEF.rsr.' + kind, 'rsr_clear.png']:
        if not os.path.isfile(os.path.join(src, n)):
            raise SystemExit('reload release %s: missing src/%s' % (rdir, n))
    hook = os.path.join(snap, 'tools', 'hands_hook.py')
    if not os.path.isfile(hook):
        raise SystemExit('reload release %s: missing tools/hands_hook.py' % rdir)
    hooks = [hook] + sorted(os.path.join(snap, 'tools', f) for f in os.listdir(os.path.join(snap, 'tools'))
                            if f.endswith('_hands_hook.py'))
    rd = lambda n: open(os.path.join(src, n), 'rb').read()
    files, notes = {}, []
    status = ''
    pg = os.path.join(snap, 'PROGRESS.md')
    if os.path.isfile(pg):
        m = re.search(r'^## Status[^\n]*', open(pg).read(), re.M)
        status = m.group(0)[3:] if m else ''

    # zscript/rsr/*.zs (vreload.zs first); of the per-set gun tables only this set's
    zdir = os.path.join(src, 'zscript', 'rsr')
    rsr_zs = sorted(f for f in os.listdir(zdir) if f.endswith('.zs') and f != 'rsr_guns.%s.zs' % other)
    if not any(f in rsr_zs for f in ('rsr_guns.zs', 'rsr_guns.%s.zs' % kind)):
        raise SystemExit('reload release %s: no zscript/rsr/rsr_guns.%s.zs (or rsr_guns.zs)' % (rdir, kind))
    rsr_zs.sort(key=lambda f: (f != 'vreload.zs', f))
    for f in rsr_zs:
        t = rd('zscript/rsr/' + f).decode('utf-8')
        if f == 'vreload.zs':
            t = fix_vreload(t, notes)
        elif "'rsq_reload'" in t:
            t = t.replace("'rsq_reload'", "'rsr_reload'")
            notes.append('%s: rsq_reload -> rsr_reload' % f)
        files['zscript/rsr/' + f] = t.encode('utf-8')
    files['zscript/rsvr/vrhand.zs'] = rd('zscript/rsvr/vrhand.zs')
    for f in sorted(os.listdir(src)):
        if f.startswith('CVARINFO.'):
            t = fix_cvarinfo_rsr(rd(f).decode('utf-8'), notes) if f == 'CVARINFO.rsr' else \
                rd(f).decode('utf-8').replace('rsq_reload', 'rsr_reload')
            files[f] = t.encode('utf-8')
    # MODELDEF groups: MODELDEF.<g>.<set> (+ MODELDEF.<g>.hands) -> MODELDEF.<g>
    md_all = ''
    for f in sorted(os.listdir(src)):
        m = re.match(r'MODELDEF\.(\w+)\.' + kind + '$', f)
        if m:
            g = m.group(1)
            md = rd(f).decode('utf-8').rstrip('\n') + '\n'
            if os.path.isfile(os.path.join(src, 'MODELDEF.%s.hands' % g)):
                md += '\n' + rd('MODELDEF.%s.hands' % g).decode('utf-8')
            files['MODELDEF.' + g] = md.encode('utf-8')
            md_all += md + '\n'

    # the release's manifests (or, for an older release without them, the same by rule)
    wm = _manifest(src, 'rsr_weapons.json', kind, live_src, os.path.join(rdir, 'src'))
    fm = _manifest(src, 'rsr_files.json', kind, live_src, os.path.join(rdir, 'src'))
    if wm is None:
        wdir = os.path.join(src, 'actors', 'Weapons') if kind == 'bd' else os.path.join(src, 'Decorate')
        pre = 'actors/Weapons/' if kind == 'bd' else 'Decorate/'
        wm = {pre + f: os.path.join(wdir, f) for f in sorted(os.listdir(wdir))} if os.path.isdir(wdir) else {}
        notes.append('no rsr_weapons.json: weapon files taken from src/ by folder')
    if fm is None:
        fm = {}
        notes.append('no rsr_files.json')
    weapons = {}
    for k, v in wm.items():
        d = open(v, 'rb').read().decode('latin-1')
        d2 = re.sub(r'(?m)^(//[^\r\n]*?); "rsq gate": optional immersive reload pauses', r'\1', d)
        if d2 != d:
            notes.append('%s: the old "rsq gate" wording taken out of its header comment' % k)
        weapons[k] = d2.encode('latin-1')
    for k, v in fm.items():
        files[k] = open(v, 'rb').read()
        if len(files[k]) > 100000:
            notes.append('LARGE: the release ships %s, %d bytes' % (k, len(files[k])))
    # every block skinned with the clear png has it in its folder
    have = {k.lower() for k in fm}
    for a, b, body in modeldef_blocks(md_all):
        if 'rsr_clear.png' in body:
            pth = re.search(r'Path\s+"([^"]+)"', body).group(1).strip('/').lower()
            if pth + '/rsr_clear.png' not in have:
                raise SystemExit('a MODELDEF block uses rsr_clear.png in %s, the release ships none there' % pth)
    unlisted = []
    mdir = os.path.join(src, 'models')
    if os.path.isdir(mdir):
        for root, _, fs in os.walk(mdir):
            for f in fs:
                p = os.path.join(root, f)
                if p not in fm.values():
                    unlisted.append('%s (%d bytes)' % (os.path.relpath(p, src), os.path.getsize(p)))
    if unlisted:
        notes.append('not shipped (in src/ but not in rsr_files.json): ' + ', '.join(unlisted))

    # the guns of this set: named in a gun table and drawn by one of this set's MODELDEF groups
    names = []
    for f in rsr_zs:
        for g in re.findall(r"if \(n == '(\w+)'\)\s*return \d+;", files['zscript/rsr/' + f].decode()):
            if g not in names:
                names.append(g)
    guns = [g for g in names if re.search(r'(?m)^Model\s+%s\s*$' % g, md_all)]
    if not guns:
        raise SystemExit('reload release: no gun of this set')
    handlers = []
    for f in rsr_zs:
        for h in re.findall(r'(?m)^class\s+(\w+)\s*:\s*EventHandler\b', files['zscript/rsr/' + f].decode()):
            if 'test' not in h.lower():
                handlers.append(h)
    return dict(files=files, guns=guns, weapons=weapons, hook=hook, hooks=hooks, notes=notes, rsr_zs=rsr_zs,
                snap=snap, hash=thash, status=status, help=menu_help(snap), handlers=handlers)


def regen_check(rel):
    """run the release's gen_rsr.py and rsr_patch.py into the snapshot and compare with src/"""
    snap = rel['snap']
    out = os.path.join(snap, 'regen')
    import shutil
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    msgs = []
    # the guns this release ships (both sets): gen_rsr.py --only them, as build_proto.py --only does
    zd = os.path.join(snap, 'src', 'zscript', 'rsr')
    gz = ''.join(open(os.path.join(zd, f)).read() for f in os.listdir(zd) if f.startswith('rsr_guns'))
    only = ','.join(re.findall(r"if \(n == '(\w+)'\)\s*return \d+;", gz))
    for tool in ('gen_rsr.py', 'rsr_patch.py', 'gen_rsb.py', 'rsb_patch.py', 'gen_pump.py', 'rsr_pump_patch.py'):
        p = os.path.join(snap, 'tools', tool)
        if not os.path.isfile(p):
            continue
        extra = ['--only', only] if tool == 'gen_rsr.py' and '--only' in open(p).read() else []
        r = subprocess.run([sys.executable, '-I', '-B', p, out] + extra, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if r.returncode:
            msgs.append('%s failed: %s' % (tool, r.stderr.decode()[-300:].strip()))
    src = os.path.join(snap, 'src')
    same, diff = 0, []
    for root, _, fs in os.walk(out):
        for f in fs:
            if f.endswith('.json') or f == 'shotty.txt':     # shotty.txt: merged from two patchers
                continue
            g = os.path.join(root, f)
            rel_p = os.path.relpath(g, out)
            s = os.path.join(src, rel_p)
            if not os.path.isfile(s):
                continue
            if open(g, 'rb').read() == open(s, 'rb').read():
                same += 1
            else:
                diff.append(rel_p)
    if diff:
        msgs.append('WARNING: regenerated today, these differ from the release\'s src/ (src/ is shipped): ' + ', '.join(diff))
    msgs.append('gen_rsr.py --only %s + rsr_patch.py rerun into the snapshot: %d generated files identical to src/, %d differ'
                % (only, same, len(diff)))
    return msgs


def fix_vreload(t, notes):
    if "'rsq_reload'" in t:
        n = t.count('rsq_reload')
        t = t.replace('rsq_reload', 'rsr_reload')
        notes.append('vreload.zs: rsq_reload -> rsr_reload (%d places)' % n)
    elif "'rsr_reload'" not in t:
        raise SystemExit("vreload.zs: neither 'rsq_reload' nor 'rsr_reload' found: how is the reload switched on?")
    # an options-menu class that overrides anything (the old one switched vr_two_handed_weapons) goes;
    # an empty one (a plain option) can stay: the v9 menu does not use it
    m = re.search(r'\nclass\s+OptionMenuItem\w+\s*:\s*\w+\s*\{', t)
    if m and re.search(r'\boverride\b', t[m.end():t.find('\n}', m.end())]):
        a = m.start() + 1
        lines_before = t[:a].split('\n')
        k = len(lines_before) - 1
        while k > 0 and lines_before[k - 1].startswith('//'):
            k -= 1
        a2 = len('\n'.join(lines_before[:k])) + (1 if k else 0)
        b = t.find('\n}', m.end()) + 2
        t = t[:a2].rstrip('\n') + '\n' + t[b:].lstrip('\n')
        notes.append('vreload.zs: options-menu class with overrides left out')
    old_hint = ('Console.Printf("\\cfReal reload: engine two-hand steadying took the grip. Turn it off in RS VR '
                'Reload options (it aims the gun at the hand).");')
    if old_hint in t:
        t = t.replace(old_hint, 'Console.Printf("\\cfReal reload: the engine\'s two-hand steadying took the grip '
                                '(it aims the gun at your off hand). The off-hand trigger grabs too.");')
        notes.append('vreload.zs: steadying hint reworded')
    elif 'Turn it off' in t:
        raise SystemExit('vreload.zs: a hint tells the player to turn something off; check its wording by hand')
    for bad in ('.SetBool(', '.SetInt(', '.SetFloat(', '.SetString(', 'rsq_reload'):
        if bad in t:
            raise SystemExit('vreload.zs: %r still there after the workarounds' % bad)
    return t


def fix_cvarinfo_rsr(t, notes):
    out = []
    for ln in t.split('\n'):
        if re.match(r'\s*\w+\s+\w+\s+rsr_saved_steady\b', ln):
            notes.append('CVARINFO.rsr: rsr_saved_steady left out')
            continue
        if 'rsq_reload' in ln:
            ln = ln.replace('rsq_reload 1 turns it on', 'rsr_reload 1 (CVARINFO.rsq) turns it on')
            notes.append('CVARINFO.rsr: comment names rsr_reload')
        out.append(ln)
    t = '\n'.join(out)
    if 'rsq_reload' in t:
        raise SystemExit('CVARINFO.rsr still names rsq_reload')
    return t


def frames_of(line):
    """number of states a DECORATE state line makes (0 for labels / flow / blanks)"""
    s = line.split('//')[0].strip()
    if not s or s.endswith(':') or s.split()[0].lower() in ('goto', 'stop', 'loop', 'wait', 'fail', '{', '}'):
        return 0
    toks = re.findall(r'"[^"]*"|\S+', s)
    return len(toks[1].strip('"')) if len(toks) >= 2 else 0


def check_inserts_only(base_lines, new_lines, what):
    """new_lines must be base_lines with lines inserted; a changed line is allowed only one for one
    with the same number of states (a hook that changes a jump target), so every relative jump
    of the set's own states still lands where it did"""
    sm = difflib.SequenceMatcher(None, base_lines, new_lines, autojunk=False)
    added = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        if op == 'replace' and i2 - i1 == j2 - j1 and all(
                frames_of(a) == frames_of(b) for a, b in zip(base_lines[i1:i2], new_lines[j1:j2])):
            CHANGED.append('%s: %r -> %r' % (what, base_lines[i1].strip()[:70], new_lines[j1].strip()[:70]))
            continue
        if op == 'replace' and j2 - j1 > i2 - i1 and all(
                frames_of(a) == frames_of(b) for a, b in zip(base_lines[i1:i2], new_lines[j1:j1 + i2 - i1])):
            CHANGED.append('%s: %r -> %r (+%d lines)' % (what, base_lines[i1].strip()[:70], new_lines[j1].strip()[:70], j2 - j1 - (i2 - i1)))
            added += j2 - j1 - (i2 - i1)
            continue
        if op != 'insert':
            raise SystemExit('%s: the reload release changes the gun\'s own lines (%s %d-%d: %r)' % (
                what, op, i1 + 1, i2, base_lines[i1:i2][:2]))
        for x in new_lines[j1:j2]:
            if re.search(r'RSQ_|rsq gate', x) and not x.lstrip().startswith('//'):
                raise SystemExit('%s: the release\'s weapon file has an old gate line: %r' % (what, x))
        added += j2 - j1
    return added


# ------------------------------------------------------------------------------ hands.zs

def build_hands(hands_path, hook_py, work):
    """team/hands.zs + the reload's six hooks + GunH + the free hand's y + no carried-ammo states"""
    os.makedirs(work, exist_ok=True)
    hooked = os.path.join(work, 'hands_hooked.zs')
    hooks = hook_py if isinstance(hook_py, list) else [hook_py]
    cur = hands_path
    for h in hooks:
        subprocess.check_call([sys.executable, '-I', '-B', h, cur, hooked], stdout=subprocess.DEVNULL)
        cur = hooked
    t = open(hooked).read()
    steps = ['reload hooks: ' + ', '.join(os.path.basename(h) for h in hooks)]
    # GunH: hand.md3 letter H (BD22 v9: axe and chainsaw; V+: the BFG)
    if 'GunH:' not in t:
        t = replace_once(t, '\tGunG: RQGS G -1; Stop;\n',
                         '\tGunG: RQGS G -1; Stop;\n\tGunH: RQGS H -1; Stop;\t// BD22 v9: axe, chainsaw. V+: BFG\n', 'GunH')
        steps.append('GunH state added')
    # every hand layer at y = WEAPONTOP: a fresh layer has y 0, which the renderer turns into an
    # 8 degree pitch (hw_weapon.cpp:108, (my - WEAPONTOP) / -4). 2100/2101 already took their own
    # turn back out in ModifyBobLayer3D; with y = WEAPONTOP that term is 0, so they draw the same.
    t = replace_once(t,
                     '\t\tif (psp)\n\t\t{\n\t\t\tpsp.bAddWeapon = false;\n\t\t\tpsp.bAddBob = true;\n\t\t}\n',
                     '\t\tif (psp)\n\t\t{\n\t\t\tpsp.bAddWeapon = false;\n\t\t\tpsp.bAddBob = true;\n'
                     '\t\t\t// a fresh layer has y 0, which tilts a HUD model 8 degrees (hw_weapon.cpp:\n'
                     '\t\t\t// pitch (y - WEAPONTOP) / -4): every hand layer, the free hand too, sits at WEAPONTOP\n'
                     '\t\t\tpsp.y = WEAPONTOP;\n\t\t\tpsp.oldy = WEAPONTOP;\n\t\t}\n', 'SetLayer y')
    steps.append('SetLayer: y = WEAPONTOP for 2100 / 2101 / 2200')
    # v8's carried ammo (RSQ_State.carry is always 0 now)
    n0 = len(t)
    for L in OLD_CARRY_LETTERS:
        pat = re.compile(r'\tAmmo%s: RQHN %s -1; Stop;[^\n]*\n' % (L, L))
        if len(pat.findall(t)) != 1:
            raise SystemExit('hands.zs: state Ammo%s not found once' % L)
        t = pat.sub('', t)
    steps.append('states AmmoB..AmmoG (v8 carried ammo) left out')
    t = t.replace("(Real reload's menu does)", '(vr_two_handed_weapons off)')
    t = t.replace('// the free hand (MODELDEF.rsq): open, or holding ammo', '// the free hand (MODELDEF.rsq): open, or a fist')
    return t, steps


# ------------------------------------------------------------------------------ text files

def menudef(kind, guns, help_lines):
    t = open(os.path.join(V9SRC, 'MENUDEF.%s.rsq' % ('bd22' if kind == 'bd' else 'vplus'))).read()
    names = [GUN_NAMES.get(g, g) for g in guns]
    t = t.replace('{RSR_GUNS}', ', '.join(names) if names else 'none')
    if t.count('\t{RSR_HELP}\n') != 1:
        raise SystemExit('MENUDEF template: no {RSR_HELP} line')
    return t.replace('\t{RSR_HELP}\n', ''.join('\tStaticText " "\n' if l == ' ' else '\tStaticText "%s", 1\n' % l for l in help_lines))


def cvarinfo_rsq(cvarinfo_rsr_text):
    t = open(os.path.join(V9SRC, 'CVARINFO.rsq')).read()
    if re.search(r'\brsr_reload\b', re.sub(r'//[^\n]*', '', cvarinfo_rsr_text)):
        # the reload release defines it itself now: do not define it twice
        t = '\n'.join(l for l in t.split('\n') if not re.match(r'\s*\w+\s+\w+\s+rsr_reload\b', l))
    return t


# ------------------------------------------------------------------------------ pk3 writing

def write_pk3(base, out, repl, remove, md3_method):
    """base's entries in base's order (same method and date unless replaced), minus remove, with
    repl's contents; entries not in base appended in sorted order. Written to out.tmp, renamed."""
    zb = zipfile.ZipFile(base)
    ib = {i.filename: i for i in zb.infolist()}
    for r in remove:
        if r not in ib:
            raise SystemExit('remove: %s is not in %s' % (r, base))
    order = [n for n in ib if n not in remove] + sorted(n for n in repl if n not in ib)
    tmp = out + '.tmp'
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with zipfile.ZipFile(tmp, 'w') as z:
        for n in order:
            if n in ib:
                zi = zipfile.ZipInfo(n, date_time=ib[n].date_time)
                zi.external_attr = ib[n].external_attr
                zi.compress_type = ib[n].compress_type
            else:
                zi = zipfile.ZipInfo(n, date_time=NEW_DATE)
                zi.external_attr = 0o644 << 16
                zi.compress_type = md3_method if n.lower().endswith('.md3') else zipfile.ZIP_DEFLATED
            if n in repl and n.lower().endswith('.md3'):
                zi.compress_type = md3_method
            data = repl[n] if n in repl else zb.read(n)
            if zi.compress_type == zipfile.ZIP_DEFLATED:
                z.writestr(zi, data, compresslevel=9)
            else:
                z.writestr(zi, data)
    zc = zipfile.ZipFile(tmp)
    if zc.testzip() is not None:
        raise SystemExit('bad CRC in output')
    for n in order:
        if zc.read(n) != (repl[n] if n in repl else zb.read(n)):
            raise SystemExit('%s: content mismatch after writing' % n)
    zc.close()
    return tmp          # the caller checks it, then publish() renames it over out


def publish(tmp, out):
    os.replace(tmp, out)


def size_report(base, out):
    za, zb = zipfile.ZipFile(base), zipfile.ZipFile(out)
    ia = {i.filename: i for i in za.infolist()}
    ib = {i.filename: i for i in zb.infolist()}
    rows = []
    for n in sorted(set(ia) | set(ib)):
        if n in ia and n in ib and za.read(n) == zb.read(n):
            continue
        rows.append((n, ia[n].compress_size if n in ia else None, ib[n].compress_size if n in ib else None))
    log('\nentries changed vs v8 (compressed bytes):')
    for n, a, b in rows:
        log('  %-44s %9s -> %9s' % (n, a if a is not None else '-', b if b is not None else '-'))
    s8, s9 = os.path.getsize(base), os.path.getsize(out)
    log('entries: v8 %d, v9 %d' % (len(ia), len(ib)))
    log('SIZE: v8 %d bytes, v9 %d bytes (%+d bytes, %+.2f%%)' % (s8, s9, s9 - s8, 100.0 * (s9 - s8) / s8))
    return s8, s9


# ------------------------------------------------------------------------------ checks

def zs_const_tables(text, what):
    """this VM indexes a function's constant table wrongly when a static const array starts past
    entry 255 of its kind (codegen.cpp FxArrayElement::Emit: ADD_RK onto the index register in
    place). Returns [(function, array, kind, start, size)] and raises on a bad one."""
    kinds = {'int': 'i', 'bool': 'i', 'name': 'i', 'double': 'f', 'float': 'f', 'string': 's', 'sound': 'i'}
    res = []
    # function bodies: brace depth 2 inside a class (approximate but enough for these files)
    clean = re.sub(r'//[^\n]*', '', text)
    depth, func, fstart = 0, None, 0
    count = {}
    i = 0
    tok = re.compile(r'"(?:\\.|[^"\\])*"|[{}]|static\s+const\s+(\w+)\s+(\w+)\s*\[\s*\]\s*=\s*\{')
    while True:
        m = tok.search(clean, i)
        if not m:
            break
        s = m.group(0)
        if s == '{':
            depth += 1
            if depth == 2:
                head = clean[max(0, m.start() - 300):m.start()]
                fm = re.findall(r'(\w+)\s*\([^()]*\)\s*(?:const\s*)?$', head.rstrip())
                func = fm[-1] if fm else '?'
                count = {}
        elif s == '}':
            depth -= 1
        elif s.startswith('"'):
            pass
        else:
            typ, name = m.group(1).lower(), m.group(2)
            # the elements: up to the matching '}'
            j, d, n, cur = m.end(), 1, 0, ''
            while d:
                c = clean[j]
                if c == '"':
                    k = j + 1
                    while clean[k] != '"':
                        k += 2 if clean[k] == '\\' else 1
                    cur += 'x'
                    j = k + 1
                    continue
                if c == '{':
                    d += 1
                elif c == '}':
                    d -= 1
                    if d == 0:
                        break
                elif c == ',' and d == 1:
                    n += 1
                    cur = ''
                    j += 1
                    continue
                if not c.isspace():
                    cur += c
                j += 1
            n += 1 if cur.strip() else 0
            k = kinds.get(typ, typ)
            start = count.get(k, 0)
            count[k] = start + n
            res.append((func, name, k, start, n))
            if start > 255:
                raise SystemExit('%s: %s() array %s starts at constant %d of its kind (> 255): the VM bug' % (what, func, name, start))
            i = j + 1
            continue
        i = m.end()
    return res


def check_hand_letters(z, kind):
    """handtable letters <-> hands.zs states <-> MODELDEF.rsq FrameIndex <-> md3 frame counts"""
    ht = z.read('zscript/rsq/handtable.zs').decode()
    hz = z.read('zscript/rsq/hands.zs').decode()
    md = z.read('MODELDEF.rsq').decode()
    mdr = '\n'.join(z.read(n).decode() for n in z.namelist() if n.startswith('MODELDEF.') and n not in ('MODELDEF.rsq', 'MODELDEF.bd.txt'))

    def strs(name):
        b = ht[ht.index('String %s(' % name):]
        return [x.strip().strip('"') for x in re.search(r'v\[\] = \{ (.*?) \};', b).group(1).split(',')]
    idx = dict(re.findall(r"if \(w is '(\w+)'\)\s*return (\d+);", ht))
    one, two, sup = strs('GunOne'), strs('GunTwo'), strs('Support')
    n = len(idx)
    if not (len(one) == len(two) == len(sup) == n + 1):
        raise SystemExit('handtable: %d guns but GunOne %d GunTwo %d Support %d entries' % (n, len(one), len(two), len(sup)))
    gun_letters = {x for x in one[1:] + two[1:] if x}
    sup_letters = {x for x in sup[1:] if x}
    states_g = set(re.findall(r'\tGun(\w): RQGS (\w) ', hz))
    states_s = set(re.findall(r'\tSup(\w): RQSP (\w) ', hz))
    if any(a != b for a, b in states_g | states_s):
        raise SystemExit('hands.zs: a Gun/Sup state shows another letter than its name')
    sg, ss = {a for a, _ in states_g}, {a for a, _ in states_s}
    blocks = modeldef_blocks(md)

    def frames_of(sprite):
        res = {}
        for a, b, body in blocks:
            mm = re.search(r'Model 0 "([^"]+)"', body)
            for L, sub, fi in re.findall(r'FrameIndex\s+%s\s+(\w)\s+(\d+)\s+(\d+)' % sprite, body):
                res[L] = (mm.group(1), int(fi))
        return res
    fg, fs = frames_of('RQGS'), frames_of('RQSP')
    probs = []
    for L in sorted(gun_letters):
        if L not in sg:
            probs.append('gun letter %s: no Gun%s state in hands.zs (never drawn)' % (L, L))
        if L not in fg:
            probs.append('gun letter %s: no FrameIndex RQGS %s in MODELDEF.rsq' % (L, L))
    for L in sorted(sup_letters):
        if L not in ss:
            probs.append('support letter %s: no Sup%s state in hands.zs' % (L, L))
        if L not in fs:
            probs.append('support letter %s: no FrameIndex RQSP %s' % (L, L))
    unused = []
    for L in sorted(sg):
        if L not in fg:
            (probs if L in gun_letters else unused).append('Gun%s' % L)
    for L in sorted(ss):
        if L not in fs:
            (probs if L in sup_letters else unused).append('Sup%s' % L)
    for L, (mesh, fi) in list(fg.items()) + list(fs.items()):
        nf = md3_frames(z.read('models/rsq/' + mesh))
        if fi >= nf:
            probs.append('FrameIndex %s -> %s frame %d, but it has %d frames' % (L, mesh, fi, nf))
    # the free hand's letters
    shown = set(re.findall(r'\w+: (RQ\w\w) (\w) -1', hz))
    have = set(re.findall(r'FrameIndex\s+(RQ\w\w)\s+(\w)\s', md + mdr))
    for spr, L in sorted(x for x in shown - have if x[0] not in ('RQGS', 'RQSP')):
        probs.append('hands.zs shows %s %s, no FrameIndex for it' % (spr, L))
    for a, b, body in modeldef_blocks(md + '\n' + mdr):
        for fn in re.findall(r'Model \d+ "([^"]+)"', body):
            pm = re.search(r'Path "([^"]+)"', body)
            if pm and pm.group(1).lower().startswith('models/rsq'):
                if pm.group(1).strip('/') + '/' + fn not in z.namelist():
                    probs.append('MODELDEF names %s/%s, not in the pack' % (pm.group(1), fn))
    if probs:
        raise SystemExit('hand letters:\n  ' + '\n  '.join(probs))
    per_gun = []
    for cls, i in sorted(idx.items(), key=lambda x: int(x[1])):
        i = int(i)
        per_gun.append('%2d %-24s gun %s/%s %s  support %s' % (i, cls, one[i], two[i],
                       '(hand.md3 %d/%d)' % (fg[one[i]][1], fg[two[i]][1]) if one[i] else '', sup[i] or '-'))
    if unused:
        per_gun.append('(hands.zs states %s: no model and no gun uses them; never shown)' % ', '.join(unused))
    return per_gun, sorted(gun_letters), sorted(sup_letters)


def check_pack(path, kind, guns):
    """static checks on a built pack; returns lines for the log"""
    z = zipfile.ZipFile(path)
    names = z.namelist()
    texts = {}
    for n in names:
        low = n.lower()
        if low.endswith(('.zs', '.dec', '.txt')) or os.path.basename(low).split('.')[0] in (
                'zscript', 'mapinfo', 'menudef', 'cvarinfo', 'modeldef', 'surfaces', 'decorate'):
            if low.startswith('models/') and not low.endswith('.txt'):
                continue
            texts[n] = z.read(n).decode('latin-1')
    out = []
    bad = []
    # 1. the old reload is gone
    for n in ('zscript/rsq/reload.zs', 'zscript/rsq/guns.zs'):
        if n in names:
            bad.append('%s is in the pack' % n)
    for f in OLD_CARRY_FILES:
        if f in names:
            bad.append('%s (v8 carried ammo) is in the pack' % f)
    old_words = ['rsq_reload', 'rsq_shells', 'rsq_debug', 'RSQ_Gate', 'RSQ_Pass', 'rsq gate', 'RSQ_Guns', 'RSQ_ReloadMode',
                 'Immersive', 'immersive', 'Marker(']
    for n, t in texts.items():
        body = re.sub(r'//[^\n]*', '', t) if n.lower().endswith(('.dec', '.txt')) else t   # a weapon file's comments may say "no old gates"
        for w in old_words:
            if w in body:
                bad.append('%s contains %r' % (n, w))
    # 2. nothing changes vr_two_handed_weapons
    for n, t in texts.items():
        code = re.sub(r'//[^\n]*', '', t)
        if 'vr_two_handed_weapons' in code:
            if n.upper().startswith('MENUDEF') or n.upper().startswith('CVARINFO'):
                bad.append('%s names vr_two_handed_weapons' % n)
            for ln in code.split('\n'):
                if 'vr_two_handed_weapons' in ln and not re.search(r'CVar\.(Find|Get)CVar\(\'vr_two_handed_weapons\'', ln):
                    bad.append('%s: %s' % (n, ln.strip()))
        for w in ('SetCVar', 'A_SetCVar'):
            if w in t and not n.upper().startswith('MENUDEF'):
                bad.append('%s contains %r' % (n, w))
        for m in re.finditer(r'class\s+OptionMenuItem\w+\s*:\s*\w+\s*\{', t):
            if re.search(r'\boverride\b', t[m.end():t.find('\n}', m.end())]):
                bad.append('%s: an options-menu class overrides something' % n)
        if n.endswith('.zs') and re.search(r'\.(SetBool|SetInt|SetFloat|SetString|ResetToDefault)\s*\(', t):
            bad.append('%s sets a cvar' % n)
    # 3. menu: one RS menu with the four items
    md = texts['MENUDEF.rsq']
    nmenu = len(re.findall(r'^OptionMenu "', md, re.M))
    if nmenu != 1:
        bad.append('MENUDEF.rsq: %d option menus' % nmenu)
    for item in ('"rsq_hands"', '"rsr_reload"', '"rsq_ballistics"', '"rsr_debug"'):
        if item not in md:
            bad.append('MENUDEF.rsq: no %s item' % item)
    cv = ''.join(t for n, t in texts.items() if n.upper().startswith('CVARINFO'))
    m = re.search(r'user\s+int\s+rsr_reload\s*=\s*(\d+)', cv)
    if not m or m.group(1) != '1':
        bad.append('CVARINFO: rsr_reload is not a user int defaulting to 1 (VR)')
    if len(re.findall(r'^\s*\w+\s+\w+\s+rsr_reload\b', cv, re.M)) != 1:
        bad.append('CVARINFO: rsr_reload defined %d times' % len(re.findall(r'^\s*\w+\s+\w+\s+rsr_reload\b', cv, re.M)))
    # 4. ZSCRIPT includes every script exactly once; MAPINFO handlers
    zsname = 'ZSCRIPT.rsvr' if kind == 'bd' else 'ZSCRIPT.rsq'
    inc = re.findall(r'#include "([^"]+)"', texts[zsname])
    scripts = sorted(n for n in names if n.endswith('.zs'))
    if sorted(inc) != scripts:
        bad.append('%s includes %s, pack has %s' % (zsname, sorted(inc), scripts))
    mi = texts['MAPINFO.rsvr' if kind == 'bd' else 'MAPINFO.rsq']
    want = (['"RSVR_MeleeHandler"'] if kind == 'bd' else []) + ['"RSQ_Handler"', '"RSQ_Ballistics"', '"RSR_Handler"']
    for h in want:
        if h not in mi:
            bad.append('MAPINFO: no %s' % h)
    # 5. hands
    hz = texts['zscript/rsq/hands.zs']
    if 'GunH:' not in hz:
        bad.append('hands.zs: no GunH')
    if 'psp.y = WEAPONTOP;' not in hz:
        bad.append('hands.zs: hand layers not at WEAPONTOP')
    if 'RSR_Handler.FreeHand' not in hz or 'RSR_Handler.Place' not in hz or 'RsrHold:' not in hz:
        bad.append('hands.zs: the reload hooks are missing')
    if '#include "zscript/rsq/gunmoves.zs"' not in texts[zsname] or \
            texts[zsname].index('handtable.zs') > texts[zsname].index('gunmoves.zs'):
        bad.append('%s: gunmoves.zs not included after handtable.zs' % zsname)
    if bad:
        raise SystemExit('CHECK FAILED %s:\n  ' % path + '\n  '.join(bad))
    per_gun, gl, sl = check_hand_letters(z, kind)
    out.append('hand table (index class: gun one/two-hand letter, support letter):')
    out += ['  ' + x for x in per_gun]
    out.append('gun letters used %s, support letters used %s: every one has a hands.zs state, a FrameIndex and an md3 frame' % (''.join(gl), ''.join(sl)))
    # 6. VM constant tables
    worst = []
    for n in scripts:
        for func, arr, k, start, size in zs_const_tables(texts[n], n):
            worst.append((start + size, n, func, arr, k, start, size))
    worst.sort(reverse=True)
    out.append('VM constant tables: every static const array starts at or below entry 255 of its kind; largest:')
    for end, n, func, arr, k, start, size in worst[:4]:
        out.append('  %s %s() %s[%d] kind %s starts at %d' % (n, func, arr, size, k, start))
    out.append('old reload: no reload.zs / guns.zs / carried-ammo files, no %s' % ', '.join(old_words[:8]))
    out.append('menu: one RS menu (rsq_hands, rsr_reload default 1 = VR, rsq_ballistics, rsr_debug); '
               'nothing names or sets vr_two_handed_weapons except read-only FindCVar')
    out.append('VR reload guns: %s' % ', '.join(guns))
    return out
