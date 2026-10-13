---
name: "vr-hand-fitting"
description: "Fit VR hands onto a weapon set (Quest packs or REMA RS_VR_Weapons/RS_VR_Avatar): grip, trigger finger, support hand, reload seats, with render checks. One session, no subagents."
---

# VR hand fitting

This is the proven method from 2026-10-10..12 (BD22 + Vanilla VR Plus Quest packs, REMA reload seats).
Use it for any weapon set: Quest (stock QZD 17.3, rigid Ermac meshes) or REMA (boned avatar hands, card keys).

## Budget rules (non-negotiable)
- One session per weapon set. NO subagents unless the owner approves a count first.
- Before starting, say what you will do and the rough size. Check in after each group of ~5 guns.
- Never launch the game on the owner's PC without asking. Never commit without explicit paths.
- Prefer patching the current shipped pack in place over rebuilding (rebuilds can drop later patches).
- Deliver to E:\DOOMWork, send the file, say what changed in 2-4 lines.

## Where things are
- Ermac's posed hands (the pose source): E:\DOOMWork\_old\doom-force-unleashed_devbuild\models\hand\ (hand.md3 gun hand, hand2.md3 off hand, ammo_hand.md3). Force Unleashed is the one owner-authorized exception to the `_old/` rule; nothing else under `_old/`.
  - Vertex animation only, no bones. Ermac's grip frames have the INDEX FINGER STRAIGHT along the receiver, NOT on the trigger. There are no trigger-pulled frames (all 211 checked).
  - Pose frames by set (gun hand / support): pistol 19/4, shotgun 30/15, ssg 47/33, chaingun 84/70, rocket 95/80, plasma 106/91 (91 = vertical-grip fist), bfg 113/98; one-hand pistol 6.
- Quest fitting tools: E:\DOOMWork\RS_QuestHands\tools\posefix\hands\ (HAND_FITTING.md, align.py, handfit.py, minigun_fit.py rot_hook/frame) and RS_QuestHands\v9kit.zip (melee/, hands/, gunview.py, hudrender.py, team builders). Units: cm, F forward / L left / U up.
- REMA tools: E:\DOOMWork\tools\avatar_grip\ (parts.py, seat.py, seatsheet.py, seatemit.py, avhand.py; README "Reload hands"); UZDXREMA tools/avatar/mkgrippose.py (Ermac frame -> per-finger curl -> handcurl.txt grip_* / hold_* poses); cards WMCARD.* keys grip, handseat, handaxis.
- Latest status: E:\DOOMWork\HANDOFF_trigger_finger.md, HANDOFF_2026-10-11_reload_hands.md.

## Method
1. **Measure each gun first** (gunview side/bottom/top views of the ready frame, 5 cm grid): grip, TRIGGER face point, support part (forend / pump / vertical grip / side handle / tube underside) and its axis, magazine well or port, handle/slide grab point and pull direction. BD22 meshes are the same on Quest and REMA: reuse measured numbers across both.
2. **Gun hand**: fit Ermac's held grip patch (points within 3 cm of his hand) onto this gun's grip by trimmed ICP, translation only, inside a box around the grip. Then bend/choose the index finger so its pad sits ON the trigger.
3. **Support hand by hold type**:
   - wrap: forend/pump; if the part is >6 cm thick search only its underside; centre left-right.
   - vgrip: vertical foregrip -> fist 91, its curl slot (F 25, L -1.5, U -5.2 in Ermac frame) on the grip centre.
   - handlebar (minigun/chaingun side handle): fist 91 turned so the BAR RUNS THROUGH THE FIST: index->pinky along the bar outward, knuckles forward/up, forearm back. Use rot_hook(c, t, frame(bar_axis,(1,0,0.3)) @ frame((0,0,-1),(1,0,0)).T). NEVER a flat palm laid over the bar.
   - under: palm under a tube (rocket). same: pistol support cups the gun hand.
4. **Output**:
   - Quest: hook/rot rows in zscript/rsq/handtable.zs (GunHook/GunRot/SupportHook/SupportRot/SupportPoint) + cut hand meshes (~8 KB per frame).
   - REMA: card lines `grip`, `handseat` (palm point at the part's cross-section centre), `handaxis` (index->pinky line, model space) and finger poses via mkgrippose (grip_*, hold_*).
5. **Reload seats** (REMA): one handseat per moving part (slide, charging handle, bolt, pump, barrels, cylinder) from the part's mesh; subject decides frame (slide = over the top, forend = wrap under).

## Mandatory checks before shipping (look at every sheet)
- Side + bottom + player-eye render per gun (handfit.sheet / seatsheet).
- Is the INDEX FINGER on the trigger? (It was not on every gun in v9 - caught by the owner.)
- Does every bar/handle run THROUGH the fist? (Minigun was a flat hand - caught by the owner.)
- Cross-section (xsec) where a grip is in doubt: the part must sit inside the hand's curl.
- Support hand not inside the barrel / not floating above the forend.
- Pack loads with no script errors (headless or the owner's build, with permission).

## Engine facts that bit us (Quest / QZD 17.3)
- RenderHUDModel adds pitch (y-WEAPONTOP)/-4 per layer: set new layers' y to WEAPONTOP or they tilt 8 deg.
- BD22/V+ recoil lives in md3 frames, not psprite offsets: hands follow via a per-frame gunmoves table.
- Engine steadying: off grip pressed within 50 cm sets weaponStabilised; gun aims at off hand and off-hand layers hide. Never change vr_two_handed_weapons from a mod.
- ZScript cannot name DECORATE classes at compile time: look them up by Name at run time.
- give all skips weapons with CHEATNOTWEAPON and weapons that are `replaces`-d; a CheckReplacement setting Replacement=null with IsFinal=true removes the replacement.
- VM: >255 constants of one type in one function breaks constant tables: one table per type.