# Concern: why a VR world weapon is still hard to make

For the co-designer. Written 2026-10-12 at the owner's request. Everything stated as fact
below was read off the tree today; where I am inferring, it says so.

---

## 1. The owner's position, in his words

> "We busted our ass getting guns to live in the hand. Tons of engine work. So now, any
> loaded weaponset with models will be in the hand. Good. But the fine positioning of hands
> on gun is still a nut we have not cracked."

> "We have never successfully imported a weaponset after the og tools were lost during
> vanilla, V+ and modern."

> "Our Quest BD22 set is good -- amazing, with posed hands. And the models we use are the
> same as the BD22 set."

> "I just get so mad thinking about how hard it is getting VR worldweapons and I feel like I
> am missing something simple."

**He is not wrong that something simple is being missed.** Section 4 is what I found.

**AND THE CARD SYSTEM ITSELF IS ON THE TABLE.** His words, added after the rest of this was
written:

> "I am willing to bin the entire card system regardless of the myriad of existing work.
> Completely new approaches to this are acceptable as well. If this card method is flawed
> this way or that, then we are allowed to get creative in establishing a new way."

> "What matters most is that creating worldweapons needs to be mod friendly and easy for
> [modders] to understand... eventually. It needs to work, and then [be] refined for normals
> to be able to contribute."

Read that before section 2, because it changes what the rest of this document is for. Every
constraint below -- three files, fitted hand keys, a lost importer -- is a description of
what exists, **not a boundary on what may be proposed.** Sunk work is explicitly not an
argument here. If the right answer is a different representation entirely, that is in scope.

The acceptance order he gave is worth keeping in that order:

1. **It works.** A set can be brought in and played, by us, at all.
2. **Then it is refined until a modder can do it** without this conversation, this tree's
   history, or either of us.

So a proposal that is elegant but cannot yet import a set is worse than an ugly one that
can. And a proposal that works but can only ever be driven by someone who already knows
where the bodies are buried has only finished half the job.

---

## 2. What the card system actually is

He described it as two things. It is three, and the third is where the confusion starts.

| file | what it answers | example keys |
|---|---|---|
| `WMCARD.<set>` | **the MODEL card.** Where things ARE on the mesh and how they move. Measured off the geometry. | `part`, `grip`, `handseat`, `handaxis`, `store`, `cycle`, `dof`, `out axis` |
| `WMSHEET.<set>` | **the WEAPON card.** What the gun IS as a game object. | `slot`, `ammo`, `capacity`, `firetics`, `fullauto`, `selectionorder`, `name` |
| `RSBDEFS.txt` | **ballistics and effects.** | muzzle, casing, tracer, impact profiles |

His own summary was right about the first two -- "the reload card is a measurement of the
model, the weapon card is the data" -- and his one guess was wrong: **ballistics does not
live in the weapon card.** It is a third file with its own grammar. Worth knowing, because
"the card" means different things to different people in this tree and that alone has cost
conversations.

WMSHEET's own header states the split cleanly: *"What each gun IS. How its parts MOVE is
WMCARD, measured off br_vr's meshes."*

So a complete VR world weapon needs **three authored artefacts plus the mesh**, and they are
maintained by different tools with different provenance. That is the first structural answer
to "why is this hard": there is no single thing to make. There are three, and nothing checks
that they agree with each other.

---

## 3. Where the hand actually comes from, and why it is the weak one

Of the three, the model card is the only one carrying hand placement, through three keys:

- `grip` -- which part the hand holds
- `handseat` -- where the palm sits on that part
- `handaxis` -- which way the hand is rolled (index-to-pinky line)

**`grip` is cheap** -- it names a part. **`handseat` and `handaxis` are the expensive ones**,
because they are a measured 3D point and a measured direction per gun, and no tool in the
tree derives them from the mesh automatically. They are fitted.

That is the nut he says is uncracked, and he is right that it is the hand keys specifically.
Everything else about a world weapon has a generator or a measurement script behind it.

---

## 4. THE THING THAT IS BEING MISSED

**The BD22 meshes are the same on Quest and on REMA. The Quest pack has a fitted hand
placement for all 25 guns. The REMA card for the same meshes has 9.**

Counted today:

| | REMA `WMCARD.bd22` | Quest `BD22_Models_v9.pk3` |
|---|---|---|
| guns with a `grip` | **25** | 25 |
| guns with a palm placement | **9** (`handseat`) | **25** (`GunHook` + `GunRot`) |
| guns with a hand roll | **1** (`handaxis`) | **25** (`GunRot`) |
| support hand placement | none in the card | **25** (`SupportHook`/`SupportRot`/`SupportPoint`) |
| finger poses | `grip_*` / `hold_*` curls | 8 cut mesh frames, letters A-H |

The Quest side's `handtable.zs` carries a hook and a rotation per gun, per hand, as flat
arrays -- I read them. The REMA side has sixteen guns with no seat at all and twenty-four
with no axis.

**So the measurement the owner thinks is missing has largely been done, on the same
geometry, by the lane next door.** What separates the two is not fitting work. It is:

1. **a frame and unit conversion.** Quest numbers are centimetres in a controller frame
   (forward / left / up). REMA `handseat` is model space in map units on the named part.
   The hand-unit ratio for this tree is already known and written down (2.941, correction
   x0.34), and the engine divides `vr_vunits_per_meter` out on the hand path.
2. **a per-part reseat.** Quest hooks the hand to the WHOLE GUN; REMA seats it on a NAMED
   PART. A hook on the gun has to become an offset from that part's origin.
3. **a validation render per gun**, which both lanes already have tooling for.

That is a conversion with a check, not a fitting campaign. **I have not done it and I am not
claiming it will drop in clean** -- the per-part reseat is real work and the two frames have
to be proved equal on one gun before anyone trusts the other twenty-four. But the distance
between "9 of 25" and "25 of 25" is almost certainly a transform, and the owner's instinct
that something simple is being missed looks correct.

**The question for you:** is there a reason this has not been done that I cannot see from
the tree? If it is simply that the two lanes never compared their data, that is the cheapest
win available in this whole area.

---

## 5. The second structural problem: the lost tools

> "We have never successfully imported a weaponset after the og tools were lost during
> vanilla, V+ and modern."

Vanilla, V+ and Modern were made with tooling that no longer exists. Everything since has
been made by hand or by one-off scripts, and the standing rule is now **never regenerate the
working sets** -- because nothing can reproduce them.

This has a consequence worth stating plainly: **the three good sets are unreproducible
artefacts, not outputs of a pipeline.** Any new set is therefore not "run the importer", it
is "redo by hand what was once automated, without the thing that automated it." That is the
second structural answer to why this is hard, and no amount of care in the hand-fitting step
fixes it.

The BD22 Quest work is the counter-example and the proof it is tractable: a complete set,
25 guns, with posed hands, built recently with tools that still exist. The question is
whether that pipeline can be pointed at REMA rather than only at Quest.

---

## 6. Concerns with `VR_HAND_FITTING_SKILL.md`

He asked for these to be included. The document is a Claude Code skill -- it loads
automatically when a session is asked to fit hands. It is better than most: every one of the
eleven paths in it resolves, the pose frame table is hard data, and the "mandatory checks"
section names two real failures the owner caught rather than generic QA. Four problems:

1. **The hard step is one clause.** Step 2 ends "bend/choose the index finger so its pad
   sits ON the trigger". That is the entire job `HANDOFF_trigger_finger.md` devotes a plan
   to -- find the index vertices, find the joint pivots, author two frames per pose.

2. **It omits what will actually stall the work.** Pose letters are SHARED across guns: in
   BD22's `handtable.zs`, letter F is used by 26 guns, B by 11, E by 9 -- eight letters
   cover the set. "Two frames per pose" cannot land a fingertip on 26 different triggers
   unless those guns share a trigger-to-grip offset. The skill does not mention sharing, and
   has no answer for splitting a letter (which collides with the builder refusing changed v8
   rows).

3. **Not one numeric acceptance threshold.** Every check is "look at the sheet". For a
   fitting job that is partly defensible -- it IS a visual judgement -- but it means two
   sessions can disagree and neither is wrong, and nothing can be regression-tested. Compare
   the body work, which is gated at 1e-4.

4. **"Prefer patching the shipped pack over rebuilding" enshrines a workaround.** The reason
   given is that rebuilds drop later patches -- which is exactly why the minigun fix must be
   re-applied by hand after every rebuild. The skill teaches the dodge rather than naming
   the defect, and the defect is that the pack and the kit have drifted apart.

It also covers **two engines with opposite constraints** -- Quest (rigid MD3, no bones, no
engine changes permitted) and REMA (boned hands, card keys, engine changes encouraged) --
and interleaves them line by line, so a reader doing one filters the other out of every step.

**And one line in it is the most useful sentence in this whole area**, which is why it is odd
that nothing follows from it:

> "BD22 meshes are the same on Quest and REMA: reuse measured numbers across both."

The skill already knows section 4. Nobody has acted on it.

---

## 7. What I would want decided

Not for me to choose, and I am not starting any of it:

- Is the Quest-to-REMA hand data conversion worth proving on **one gun**? That is the
  cheapest possible test of section 4 and it either works or it fails visibly.
- Should the three card files get **one check that they agree with each other**? Nothing
  currently notices if WMCARD declares a part that WMSHEET's capacity contradicts.
- Is rebuilding an importer for whole weapon sets a real goal, or has it been
  correctly abandoned in favour of per-set hand work?
- **Does the three-file card system survive at all?** He has put it on the table. The
  questions worth asking of any replacement, including the current one:
  - Can a modder with a weapon mod and no knowledge of this tree get it into VR hands? Today
    the honest answer is no -- it takes three authored files, a fitted palm point and roll
    per gun, and a pose frame chosen from a mesh in a quarantined folder.
  - **What is the smallest honest input?** A mesh plus a handful of named points is the
    floor; everything else in the current cards is either derivable from geometry or is
    game-stat data that already has a home.
  - **Which numbers must a human author, and which can be measured?** The grip, the trigger
    and the magazine well are findable in a mesh. The palm seat and hand roll currently are
    not -- that is the real asymmetry, and a new design earns its keep mostly by shrinking
    that list rather than by being tidier.
  - **What does it do when it is given a gun it cannot fit?** Today a wrong seat is silent
    and shows up in a headset. A system normals can use has to refuse out loud instead.
