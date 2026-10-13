"""Build RS_VanillaVRPlus_VR.pk3: VR hands, stock / immersive reloading and optional
ballistics for the Vanilla VR Plus weapon set (1.0b_Weapons_VanillaVRPlus_v1.2) on
stock QuestZDoom 17.x. Load it after the set.

    python build_vplus.py <set folder> <out.pk3>

Uses the same RS VR scripts as RS_BD22_Models (tool/vrmelee/zscript/rsq, rsvr/vrhand.zs,
rsvr/common.zs); only the gates (vplus_patch.py) and the hand table (vfits.json ->
rsq_hands_gen.py) are this set's own.
"""
import os, sys, shutil, zipfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(HERE)
V = os.path.join(TOOL, 'vrmelee')
sys.path.insert(0, HERE); sys.path.insert(0, TOOL)
import vplus_patch, rsq_hands_gen

ZSCRIPT = '''version "4.10"

// RS VR hands, reloading and ballistics for Vanilla VR Plus (QuestZDoom 17.x).
// The same scripts as RS_BD22_Models; options in RSQ_Options (MENUDEF.rsq).
#include "zscript/rsvr/vrhand.zs"
#include "zscript/rsvr/common.zs"
#include "zscript/rsq/reload.zs"
#include "zscript/rsq/guns.zs"
#include "zscript/rsq/handtable.zs"
#include "zscript/rsq/hands.zs"
#include "zscript/rsq/ballistics.zs"
'''
MAPINFO = '''// RS VR reload, hands and ballistics: zscript/rsq
gameinfo
{
	AddEventHandlers = "RSQ_Handler", "RSQ_Ballistics"
}
'''
MENUDEF = '''// RS VR reload / hands / ballistics (zscript/rsq)
AddOptionMenu "OptionsMenu"
{
	Submenu "RS VR Reload, Hands, Ballistics", "RSQ_Options"
}

AddOptionMenu "EDW_Settings"
{
	StaticText " "
	Submenu "RS VR Reload, Hands, Ballistics", "RSQ_Options"
}

OptionValue "RSQ_ReloadMode"
{
	0, "Stock"
	1, "Immersive (VR)"
}

OptionValue "RSQ_Ballistics"
{
	0, "Stock"
	1, "Enhanced"
}

OptionMenu "RSQ_Options"
{
	Title "RS VR RELOAD, HANDS, BALLISTICS"
	Option "Reloading", "rsq_reload", "RSQ_ReloadMode"
	Slider "Shells per hand trip", "rsq_shells", 1, 8, 1, 0
	StaticText " "
	StaticText "Immersive: when the gun stops in its reload,", 1
	StaticText "take your off hand away for ammo, then bring it", 1
	StaticText "to the glowing marker. A green marker is the", 1
	StaticText "magazine well, cylinder or loading port, a yellow", 1
	StaticText "one the charging handle or pump: take it and pull", 1
	StaticText "it back. The pump shotgun pumps by hand after", 1
	StaticText "every shot. Press reload to do a step for you.", 1
	StaticText " "
	StaticText "VR hands: bring your off hand to the front of", 1
	StaticText "the gun and it takes hold.", 1
	StaticText " "
	Option "VR hands", "rsq_hands", "OnOff"
	Option "Ballistics", "rsq_ballistics", "RSQ_Ballistics"
	StaticText " "
	Option "Reload debug readout", "rsq_debug", "OnOff"
}
'''
README = '''RS_VanillaVRPlus_VR -- VR hands, reloading and ballistics for Vanilla VR Plus
(1.0b_Weapons_VanillaVRPlus_v1.2) on stock QuestZDoom 17.x. No engine changes.

Load after the weapon set. Options: Options > RS VR Reload, Hands, Ballistics
(also at the bottom of the set's 3D Weapon Settings).

  Reloading   Stock (default): the set's own reloads, unchanged.
              Immersive (VR): the reload stops at each step until your off hand
              does it -- away for ammo, back to the green marker (magazine well,
              cylinder, loading port), or take the yellow marker (charging
              handle, pump) and pull it back. Press reload to do a step for you.
              M16: magazine out, in, charging handle. Revolvers: rounds into
              the open cylinder. Pump shotgun: a shell per pass, and the pump
              after every shot. Super shotgun: shells into the open breech.
  VR hands    Ermac's posed hands on every gun; bring your off hand to the front
              of the gun and it takes hold.
  Ballistics  Enhanced: impacts throw dust, sparks and chips by surface.

Files: Decorate/rifle.txt, revolver.txt and shotty.txt are the set's own files with
the reload pauses added; they replace the set's copies while this pack is loaded.
Do not load together with RS_BD22_Models (they share these scripts).

Hands and poses: Ermac, Rusted Legacy / Force Unleashed (MIT,
models/rsq/LICENSE_RustedLegacy_MIT.txt).
'''

def build(setdir, out):
    B = os.path.join(os.path.dirname(os.path.abspath(out)) if False else HERE, '_build')
    if os.path.isdir(B):
        shutil.rmtree(B)
    os.makedirs(os.path.join(B, 'zscript', 'rsq'))
    os.makedirs(os.path.join(B, 'zscript', 'rsvr'))
    vplus_patch.main(os.path.join(setdir, 'FILTER', 'DOOM', 'Decorate'), os.path.join(B, 'Decorate'))
    shutil.copy(os.path.join(V, 'MODELDEF.rsq'), os.path.join(B, 'MODELDEF.rsq'))     # debris tail
    rsq_hands_gen.main(os.path.join(HERE, 'vfits.json'), B)
    for f in ('zscript/rsvr/vrhand.zs', 'zscript/rsvr/common.zs', 'zscript/rsq/reload.zs', 'zscript/rsq/guns.zs',
              'zscript/rsq/hands.zs', 'zscript/rsq/ballistics.zs', 'CVARINFO.rsq', 'SURFACES.rsq',
              'models/rsq/hand.png', 'models/rsq/LICENSE_RustedLegacy_MIT.txt'):
        os.makedirs(os.path.dirname(os.path.join(B, f)), exist_ok=True)
        shutil.copy(os.path.join(V, f), os.path.join(B, f))
    shutil.copytree(os.path.join(V, 'models', 'rsq', 'debris'), os.path.join(B, 'models', 'rsq', 'debris'))
    for name, text in (('ZSCRIPT.rsq', ZSCRIPT), ('MAPINFO.rsq', MAPINFO), ('MENUDEF.rsq', MENUDEF),
                       ('README_RS_VanillaVRPlus_VR.txt', README)):
        open(os.path.join(B, name), 'w', newline='\n').write(text)
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(B):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, B).replace(os.sep, '/'))
    print(out, os.path.getsize(out))

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
