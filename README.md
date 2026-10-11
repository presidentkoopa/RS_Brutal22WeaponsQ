# RS_QuestHands

Hands and physical reload for **stock QuestZDoom 17.x**. No engine changes.

Target engine: `qzd17.3` = `9afc750917bf54870f2d16b7ba0d00f2b77e6fb5` (GZDoom 4.14.3 base).

- Plan and build order: `E:/DOOMWork/_reports/QUEST_RELOAD_DIAGNOSIS_2026-10-02.md`
- Source audits: `E:/DOOMWork/_reports/qzd17_stock_audit_2026-10-02/`

## Status

**BOTH QUEST PACKS ARE DONE AND SHIPPED (2026-10-10).** Only a headset test is
outstanding; nothing below is waiting on code.

| pack | file | built |
|---|---|---|
| BD22 hands, reload and ballistics | `E:\DOOMWork\BD22_Models_v8.pk3` | 2026-10-10 18:44 |
| Vanilla VR Plus add-on | `E:\DOOMWork\VanillaVRPlus_VR.pk3` | 2026-10-10 19:45 |

Posed hands on every gun. Reload stock or immersive, ballistics stock or ours,
both switchable in the options menu. The Vanilla VR Plus pack also carries a fix
for a crash in that set: with default weapon switching, switching away from the
M16 or the revolvers overflows the stack. **Never load the two packs together.**

Load orders: `brutal22test6.pk3` then the BD22 pack; or Doom/Doom 2, then the
owner's `1.0b_Weapons_VanillaVRPlus_v1.2` set, then the Vanilla VR Plus pack.

Sources for both are under `tools/posefix/` — start with its `README.md` and
`hands/HAND_FITTING.md`; the Vanilla VR Plus half is in `tools/posefix/vplus/`.

**The rest of this file is the ORIGINAL STAGED PROVING PLAN, written 2026-10-03,
and it is kept for its engine citations, not as a statement of what is left.**
Every claim below cites the engine file and line it rests on, and that is still
worth having. The step numbering is historical: step 1 proved the four claims,
and the reload that step 2 described shipped in both packs above.

This pack is separate from `RS_VR_Reload` on purpose: that one is built on
`level.HandPos`, `SetModelJoint` and `SetModelFlag`, which are UZDXREMA engine
additions and do not exist in stock QZD. It cannot run on this target.
