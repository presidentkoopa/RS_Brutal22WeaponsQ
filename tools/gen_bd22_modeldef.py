#!/usr/bin/env python3
"""Generate MODELDEF for BD22's guns: authored placement + BD22's own keying.

THE TWO SOURCES, AND WHY EACH
-----------------------------
PLACEMENT comes from the authored BD21 set (`Modeldef.<Class>.def` in
br_vr/PK3_pbr). Scale, Offset, ZOffset, NoInterpolation and the rest were fitted
by hand against these exact meshes and are correct; none of it depends on which
game drives the sprite. They are copied VERBATIM, with only `Path` rewritten to
where we ship the mesh. Do not re-derive these numbers.

KEYING comes from BD22's own DECORATE. MODELDEF keys a model on
(class, sprite, frame), and the authored FrameIndex lines name BD21's sprites --
AssaultShotgun on A12S, which occurs nowhere in BD22 (it uses USAS and 2SAR).
Every one keys a frame the weapon never enters, so nothing can draw. Those lines
are dropped and rebuilt from BD22.

WHICH SPRITES BELONG TO THE GUN: THE STATE LABEL, NOT A HEADCOUNT
-----------------------------------------------------------------
BD22 drives a punch, a kick, a grenade toss and dual-wield out of the WEAPON's
own state chain, which is why the authored set carries four blocks per weapon
(the gun, FIST, Grenade, Boot). Those frames must not key the gun's mesh, or
four meshes draw at once.

An earlier attempt guessed this by counting how many classes share a sprite, and
it failed in BOTH directions: it threw out RIFR, the rifle's own reload sprite
(5 files use it), and it kept PUNS, HBUS and DURR -- a punch, Hitler's buzzsaw
and the dual rifle -- because few files use those. Sharing is not the question.

The discriminator is the STATE LABEL the frame sits under. A label naming a
kick, taunt, salute, grenade, punch, fist or dual-wield belongs to another mesh,
and its frames are left out.

SPRITES WITH NO ART ARE DROPPED. BD22 names sprites it never ships; keying one
is the fatal "Unknown sprite ... in model definition" that refuses the pk3. A
missing individual FRAME is harmless by contrast -- it simply never draws.

STATIC, FOR NOW. Every pair points at model 0 frame 0, so the gun is present in
every state. The authored per-frame mapping described BD21's animation and means
nothing against BD22's chains; animating is a second pass off the mesh's own
frame list.

    python tools/gen_bd22_modeldef.py            # report
    python tools/gen_bd22_modeldef.py --write    # write MODELDEF.bd.txt
"""

import argparse
import os
import re
import struct
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "MODELDEF.bd.txt")
MODELS = os.path.join(ROOT, "models", "bd")

AUTHORED = r"E:/DOOMWork/VR_WeaponSetRebuild/WeaponSets/br_vr/PK3_pbr"
BD22_DECS = r"D:/SteamLibrary/steamapps/common/DooM VR/BD22 ModelDefs/brutal22test6/brutaldoom22/actors/Weapons"
BD22_PK3 = r"D:/SteamLibrary/steamapps/Common/DooM VR/BD22 ModelDefs/brutal22test6/brutal22test6.pk3"
IWAD = r"D:/SteamLibrary/steamapps/common/DooM VR/___Sourceport/doom2.wad"

# Mesh folder -> BD22 class, where the names simply differ. Each right-hand side
# is the ACTOR name in BD22's DECORATE.
# BD22 class / mesh folder -> the AUTHORED def's name, where all three differ.
# The authored set is named after BD21's own weapons, so this is a third set of
# names and not a duplicate of ALIASES. Verified against the file listing.
AUTHORED_NAME = {
    "brutalpistol":           "Pistol",
    "brutalsmg":              "SMG",
    "plasma_gun":             "Plasma",
    "grenadelauncher":        "M79",
    "shot_gun":               "Shotgun",
    "rocket_launcher":        "RPG",
    "big_fucking_gun":        "BFG",
    "hellishmissilelauncher": "HellishMissile",
    "railgun":                "Railgun",
    "chain_saw":              "Chain_saw",
}

ALIASES = {
    "bfg": "BIG_FUCKING_GUN",
    "rpg": "Rocket_Launcher",
    "m79": "GrenadeLauncher",
    "shotgun": "Shot_Gun",
    "hellishmissile": "HellishMissileLauncher",
}

# A state label driving one of the OTHER meshes. Case-insensitive substring.
SHARED_LABEL = ("kick", "taunt", "salute", "grenade", "punch", "fist",
                "boot", "dual", "melee")

STATE_RE = re.compile(
    r'^\s*(?P<spr>"####"|####|[A-Z0-9_]{4})\s+'
    r'(?P<frames>"[^"]+"|[A-Za-z0-9\[\]\\_]+)\s+'
    r'(?P<tics>-?\d+)', re.I)
LABEL_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*:\s*(?://.*)?$')
ACTOR_RE = re.compile(r'^\s*ACTOR\s+(?P<name>\S+)', re.I)
MODELBLOCK_RE = re.compile(r'^\s*Model\s+([A-Za-z0-9_]+)\s*$', re.I)
FRAMEINDEX_RE = re.compile(r'^\s*FrameIndex\s', re.I)
PATH_RE = re.compile(r'^\s*Path\s+"?([^"\n]*)"?', re.I)
# Model N / Skin N are re-emitted from the mesh we actually ship, so they are
# not carried over from the authored block -- otherwise each lands twice.
MODEL0_RE = re.compile(r'^\s*(?:Model|Skin|SurfaceSkin)\s+\d', re.I)


def frame_letters(tok):
    # '#' is not a frame: in the frame column it means "keep the current
    # frame", the way "####" means "keep the current sprite". Emitting it
    # produces impossible lumps like 2SAR#0.
    return [c for c in tok.strip('"') if c not in ' \t#']


# ------------------------------------------------------------------ placement
def authored_blocks():
    """{key_lower: (classname, [placement lines], mesh_basename)}

    Placement is every line of the authored Model block except Path, the
    Model N lines and the FrameIndex lines -- i.e. Scale, Offset, ZOffset,
    NoInterpolation, and anything else the author put there.
    """
    out = {}
    if not os.path.isdir(AUTHORED):
        return out

    for fn in sorted(os.listdir(AUTHORED)):
        low = fn.lower()
        if not low.startswith("modeldef.") or not low.endswith(".def"):
            continue
        lines = open(os.path.join(AUTHORED, fn), errors="replace").read().splitlines()

        i = 0
        while i < len(lines):
            m = MODELBLOCK_RE.match(lines[i])
            if not m:
                i += 1
                continue
            cls = m.group(1)
            placement, mesh = [], None
            depth, j = 0, i + 1
            while j < len(lines):
                ln = lines[j]
                opened = ln.count("{")
                closed = ln.count("}")
                if opened:
                    depth += opened
                    if ln.strip() == "{":
                        j += 1
                        continue
                if closed:
                    depth -= closed
                    if depth <= 0:
                        break
                s = ln.strip()
                if s and not FRAMEINDEX_RE.match(ln) and not s.startswith("//"):
                    p = PATH_RE.match(ln)
                    if p:
                        mesh = os.path.basename(p.group(1).replace("\\", "/"))
                    elif not MODEL0_RE.match(ln):
                        placement.append(ln.rstrip())
                j += 1

            if placement or mesh:
                out.setdefault(cls.lower(), (cls, placement, mesh))
                if mesh:
                    out.setdefault(mesh.lower(), (cls, placement, mesh))
            i = j + 1
    return out


# ------------------------------------------------------------------ art
def wad_lumps(path):
    names = set()
    try:
        with open(path, "rb") as fh:
            head = fh.read(12)
            if head[:4] not in (b"IWAD", b"PWAD"):
                return names
            count, offset = struct.unpack("<ii", head[4:12])
            fh.seek(offset)
            for _ in range(count):
                e = fh.read(16)
                if len(e) < 16:
                    break
                names.add(e[8:16].rstrip(bytes([0])).decode("latin-1").upper())
    except OSError:
        pass
    return names


def sprites_with_art():
    lumps = set()
    if os.path.exists(BD22_PK3):
        with zipfile.ZipFile(BD22_PK3) as z:
            for n in z.namelist():
                b = os.path.splitext(os.path.basename(n))[0]
                if b:
                    lumps.add(b.upper())
    lumps |= wad_lumps(IWAD)
    d = os.path.join(ROOT, "sprites")
    if os.path.isdir(d):
        for fn in os.listdir(d):
            lumps.add(os.path.splitext(fn)[0].upper())
    return {l[:4] for l in lumps if len(l) >= 5}


# ------------------------------------------------------------------ keying
def gun_pairs(actor):
    """[(sprite, frame)] under this actor's OWN labels; shared ones excluded."""
    if not os.path.isdir(BD22_DECS):
        return [], None, set(), [], {}, {}

    pat = re.compile(r'^\s*ACTOR\s+' + re.escape(actor) + r'\s*(:|\{|$|\s)', re.I)
    for fn in sorted(os.listdir(BD22_DECS)):
        if not fn.lower().endswith(".dec"):
            continue
        lines = open(os.path.join(BD22_DECS, fn), errors="replace").read().splitlines()
        start = next((i for i, ln in enumerate(lines) if pat.match(ln)), None)
        if start is None:
            continue

        pairs, seen, dropped = [], set(), set()
        actions = {}          # (sprite, frame) -> action, from its label
        ready = []
        label, carried = "", None
        for ln in lines[start + 1:]:
            m = ACTOR_RE.match(ln)
            if m and not pat.match(ln):
                break
            m = LABEL_RE.match(ln)
            if m:
                label = m.group(1).lower()
                continue
            m = STATE_RE.match(ln)
            if not m:
                continue
            spr = m.group('spr').strip('"').upper()
            if spr == '####':
                if not carried:
                    continue
                spr = carried
            else:
                carried = spr
            if any(k in label for k in SHARED_LABEL):
                dropped.add(spr)
                continue
            for f in frame_letters(m.group('frames')):
                k = (spr, f.upper())
                if label.startswith("ready"):
                    ready.append(k)
                if k not in seen:
                    seen.add(k)
                    pairs.append(k)
                    actions[k] = action_of_label(label)
        return pairs, fn, dropped, ready, actions
    return [], None, set(), []


# "p_flame" and not "flame": the latter also excluded FlameCannon.md3 and
# Flamethrower2.md3, which ARE the guns.
OTHER_MESH = ("nade", "boot", "fistclosed", "dual", "p_flame")
MODELFILE_RE = re.compile(r'^\s*Model\s+(\d+)\s+"([^"]+)"', re.I)
FI_FULL_RE = re.compile(r'^\s*FrameIndex\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)', re.I)


def authored_frame_map(cls, folder=None):
    """{(sprite, frame): model_frame} from the GUN block of the authored def.

    THE POSE IS THE WHOLE POINT. These meshes are animations -- Rifle.md3 has 32
    frames -- and the fourth column of a FrameIndex line picks which one. The
    authored set is a hand-made mapping of sprite frame to pose, and BD21 and
    BD22 share most sprite names for the same gun, so wherever BD22 shows a
    frame the author also keyed, that pose is copied verbatim.

    ONLY THE GUN'S BLOCK. Each .def holds several Model blocks -- the gun, a
    dual variant, nade.md3, Boot.md3, fistclosed.md3 -- each using `Model 0`
    within itself. Reading them together yields model frame 74 for a 32-frame
    mesh, which is how a gun ends up drawn in a pose that does not exist.
    """
    if not os.path.isdir(AUTHORED):
        return {}, None
    # The authored file is named after the MESH, which is not always the BD22
    # class: Modeldef.BFG.def holds BIG_FUCKING_GUN, Modeldef.RPG.def holds
    # Rocket_Launcher. So try the class name and the mesh folder.
    names = []
    a = AUTHORED_NAME.get(cls.lower()) or AUTHORED_NAME.get((folder or "").lower())
    if a:
        names.append(a.lower())
    names.append(cls.lower())
    if folder:
        names.append(folder.lower())
    target = None
    for want in names:
        for fn in os.listdir(AUTHORED):
            low = fn.lower()
            if low.startswith("modeldef.") and low.endswith(".def"):
                if low[len("modeldef."):-len(".def")] == want:
                    target = os.path.join(AUTHORED, fn)
                    break
        if target:
            break
    if not target:
        return {}, None

    lines = open(target, errors="replace").read().splitlines()
    best = ({}, None)
    i = 0
    while i < len(lines):
        if not MODELBLOCK_RE.match(lines[i]):
            i += 1
            continue
        mesh, pairs = None, {}
        depth, j = 0, i + 1
        while j < len(lines):
            ln = lines[j]
            depth += ln.count("{")
            if ln.count("}") and depth - ln.count("}") <= 0:
                break
            depth -= ln.count("}")
            m = MODELFILE_RE.match(ln)
            if m and mesh is None:
                mesh = os.path.basename(m.group(2).replace("\\", "/"))
            m = FI_FULL_RE.match(ln)
            if m:
                pairs[(m.group(1).upper(), m.group(2).upper())] = int(m.group(4))
            j += 1
        if mesh and not any(k in mesh.lower() for k in OTHER_MESH):
            if len(pairs) > len(best[0]):
                best = (pairs, mesh)
        i = j + 1
    return best


# WHICH ACTION A LABEL OR A SPRITE RUN BELONGS TO.
#
# Name-matching sprite frames only works where BD21 and BD22 happen to use the
# same sprite name. For AssaultShotgun, GrenadeLauncher and Plasma_Gun they do
# not (A12S vs USAS), so nothing matched and every frame fell back to the one
# ready pose.
#
# But the MESH animation is the same object in both cases: a select sweep, an
# idle, a fire kick, a reload. So the i-th frame of BD22's reload maps to the
# i-th frame of the authored reload, and so on per action. The authored side is
# classified by Doom's weapon sprite suffix convention -- S select, G idle,
# F fire, R reload -- and BD22's side by its state label.
ACTION_BY_LABEL = (
    ("select",  ("select", "raise", "firstselect")),
    ("reload",  ("reload", "insert", "unload", "remove", "turbo")),
    ("fire",    ("fire", "recoil", "flash", "letfly", "charge", "cooldown",
                 "shoot", "althold")),
    ("deselect", ("deselect", "lower")),
    ("idle",    ("ready", "fidget", "sprint", "aim", "zoom", "hold", "warmup",
                 "inspect")),
)

def authored_decorate_actions(name):
    """{(sprite, frame): action} from BD21's OWN DECORATE, by state label.

    The authored sprite runs follow no suffix convention -- Plasma's are PLSA,
    PLSN, PLSP, PLSR, PLST, PLS9 -- so they cannot be classified by name. But
    BD21's DECORATE sits in the same folder as its modeldef (Plasma.txt next to
    Modeldef.Plasma.def), with the same kind of state labels BD22 uses. So both
    sides get classified the same way, by the label the frame sits under, and
    the per-action mapping is symmetric instead of guessed.
    """
    path = os.path.join(AUTHORED, name + ".txt")
    if not os.path.exists(path):
        return {}
    out, label, carried = {}, "", None
    for ln in open(path, errors="replace"):
        m = LABEL_RE.match(ln)
        if m:
            label = m.group(1).lower()
            continue
        m = STATE_RE.match(ln)
        if not m:
            continue
        spr = m.group('spr').strip('"').upper()
        if spr == '####':
            if not carried:
                continue
            spr = carried
        else:
            carried = spr
        for f in frame_letters(m.group('frames')):
            out.setdefault((spr, f.upper()), action_of_label(label))
    return out


def action_of_label(label):
    for action, keys in ACTION_BY_LABEL:
        if any(k in label for k in keys):
            return action
    return "other"


def authored_action_frames(fmap, decmap):
    """{action: [model frames, in the order the animation plays]}"""
    runs = {}
    for (spr, fr), mf in fmap.items():
        runs.setdefault(spr, []).append((fr, mf))

    out = {}
    for spr, items in runs.items():
        items.sort()
        for fr, mf in items:
            action = decmap.get((spr, fr), "other")
            out.setdefault(action, []).append(mf)
    for a in out:
        out[a].sort()
    for a in out:
        # Preserve order, drop repeats, so a run keyed twice does not stretch it.
        seen, keep = set(), []
        for mf in out[a]:
            if mf not in seen:
                seen.add(mf)
                keep.append(mf)
        out[a] = keep
    return out


def gun_mesh_folders():
    out = {}
    if not os.path.isdir(MODELS):
        return out
    for d in sorted(os.listdir(MODELS)):
        if d.lower() in ("fist", "grenade", "boot"):
            continue
        full = os.path.join(MODELS, d)
        if not os.path.isdir(full):
            continue
        md3 = next((f for f in sorted(os.listdir(full)) if f.lower().endswith(".md3")), None)
        skin = next((f for f in sorted(os.listdir(full))
                     if f.lower().endswith((".png", ".jpg"))), None)
        if md3:
            out[d] = (md3, skin)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    authored = authored_blocks()
    art = sprites_with_art()
    folders = gun_mesh_folders()

    if not authored:
        print("could not read the authored set at %s" % AUTHORED)
        return 1

    blocks, skipped = [], []
    for folder in sorted(folders):
        md3, skin = folders[folder]
        cls = ALIASES.get(folder.lower(), folder)

        pairs, dec, shared_sprites, ready_pairs, pair_action = gun_pairs(cls)
        if not pairs:
            skipped.append("%s (no BD22 states)" % cls)
            continue

        kept = [(s, f) for (s, f) in pairs if s in art]
        noart = sorted({s for (s, _f) in pairs if s not in art})
        if not kept:
            skipped.append("%s (no sprite it uses has art)" % cls)
            continue

        auth = authored.get(folder.lower()) or authored.get(cls.lower())
        if auth and auth[1]:
            placement, src, fitted = auth[1], "authored %s" % auth[0], True
        else:
            placement = ["   Scale -1.0 1.0 1.0", "   Offset 0.0 0.0 0.0",
                         "   NoInterpolation"]
            src, fitted = "NO AUTHORED BLOCK, flat defaults", False

        b = ["// %s -- placement from the %s; keying from BD22's %s." % (cls, src, dec)]
        b.append("// %d pairs. Shared-mesh labels excluded: kick, punch, grenade, dual."
                 % len(kept))
        if shared_sprites:
            b.append("// Sprites those labels used: %s"
                     % ", ".join(sorted(shared_sprites)[:12]))
        if noart:
            b.append("// Dropped -- BD22 names these and ships no art, and keying one")
            b.append("// is fatal: %s" % ", ".join(noart))
        b.append("Model %s" % cls)
        b.append("{")
        b.append('   Path "models/bd/%s"' % folder)
        b.append('   Model 0 "%s"' % md3)
        if skin:
            b.append('   Skin 0 "%s"' % skin)
        b += placement

        # THE POSE. The fourth column picks which frame of the mesh to draw, and
        # these meshes are animations -- 32 frames for the rifle. Pinning 0
        # draws the first frame of the raise animation in every state: a gun
        # angled at the floor while you fire it.
        #
        # So it is copied from the authored mapping wherever that keyed this
        # exact sprite frame, and otherwise falls back to the gun's READY pose,
        # found by looking up what BD22's own Ready label shows.
        fmap, fmesh = authored_frame_map(cls, folder)

        ready_frame = None
        for k in ready_pairs:
            if k in fmap:
                ready_frame = fmap[k]
                break
        if ready_frame is None and fmap:
            # Doom's weapon sprite convention: the run ending in G is the idle
            # one (PISG, SHTG, RIFG), F is the muzzle flash, R the reload, S the
            # select. So the authored pose for the G run is the ready pose.
            gruns = sorted((sp, fr) for (sp, fr) in fmap if sp.endswith("G"))
            if gruns:
                ready_frame = fmap[gruns[0]]

        if ready_frame is None and fmap:
            # Nothing in Ready was keyed. A sprite run the author gave exactly
            # one pose is an idle by construction, so take the lowest of those.
            runs = {}
            for (s2, _f2), mf in fmap.items():
                runs.setdefault(s2, []).append(mf)
            singles = [v[0] for v in runs.values() if len(v) == 1]
            ready_frame = min(singles) if singles else 0
        if ready_frame is None:
            ready_frame = 0

        # PER-ACTION POSITIONAL MAPPING, for the frames name-matching cannot
        # reach. The mesh animation is the same object in both games -- a select
        # sweep, an idle, a fire kick, a reload -- so BD22's i-th reload frame
        # takes the authored i-th reload pose, and likewise for the others.
        # Clamped to the last pose of that action, because BD22's chains are
        # often longer than BD21's.
        aname = (AUTHORED_NAME.get(cls.lower())
                 or AUTHORED_NAME.get(folder.lower()) or folder)
        act_frames = authored_action_frames(fmap, authored_decorate_actions(aname))
        counters = {}

        def pose_for(k):
            if k in fmap:
                return fmap[k], "name"
            a = pair_action.get(k, "other")
            seq = act_frames.get(a)
            if not seq:
                # The authored side classified nothing into this action -- its
                # DECORATE may not cover every frame its modeldef keys. Walk the
                # unclassified pool rather than freezing: a gun that animates
                # through poses of the same mesh still reads as a gun being
                # handled, and a frozen one does not.
                a = "other"
                seq = act_frames.get("other")
            if not seq:
                return ready_frame, "ready"
            i = counters.get(a, 0)
            counters[a] = i + 1
            return seq[min(i, len(seq) - 1)], "action"

        poses, how = [], {"name": 0, "action": 0, "ready": 0}
        for k in kept:
            mf, src2 = pose_for(k)
            poses.append(mf)
            how[src2] += 1

        b.append("// Pose: %d frames from the authored mapping by name, %d by "
                 "position" % (how["name"], how["action"]))
        b.append("// within their action, %d left at the ready pose (model frame %d)."
                 % (how["ready"], ready_frame))
        if fmesh and fmesh.lower() != md3.lower():
            b.append("// NOTE the authored block's mesh was %s; we ship %s."
                     % (fmesh, md3))
        b.append("")
        for spr, f in kept:
            b.append("   FrameIndex\t%s\t%s\t0\t%d"
                     % (spr, f, fmap.get((spr, f), ready_frame)))
        b.append("}")
        blocks.append((cls, len(kept), fitted, "\n".join(b)))

    print("guns: %d" % len(blocks))
    for cls, n, fitted, _ in blocks:
        print("   %-24s %4d pairs   %s"
              % (cls, n, "authored placement" if fitted else "** FLAT DEFAULTS, NEEDS FITTING **"))
    if skipped:
        print("\nskipped: %s" % "; ".join(skipped))

    if not args.write:
        print("\nreport only -- pass --write")
        return 0

    header = [
        "// ===========================================================================",
        "// RS_QuestHands -- 3D weapons for Brutal Doom v22.",
        "//",
        "// GENERATED by tools/gen_bd22_modeldef.py. Do not hand-edit; regenerate.",
        "//",
        "// PLACEMENT (Scale / Offset / ZOffset / ...) is copied VERBATIM from the",
        "// authored BD21 set, which was fitted by hand against these exact meshes.",
        "// Only Path is rewritten. Do not re-derive those numbers.",
        "//",
        "// KEYING is read from BD22's own DECORATE. The authored FrameIndex lines named",
        "// BD21's sprites (AssaultShotgun on A12S, absent from BD22) and so could never",
        "// draw. Frames under a kick / punch / grenade / dual label are left out: BD22",
        "// drives those from the weapon's own chain and they belong to other meshes.",
        "// ===========================================================================",
        "",
    ]
    open(OUT, "w").write("\n".join(header) + "\n\n".join(b for _c, _n, _f, b in blocks) + "\n")
    print("\nwrote %s  (%d blocks)" % (OUT, len(blocks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
