// ============================================================================
// RS_QuestHands -- step 2: the reload, with pauses
//
// THE PLAN SAID TWO MECHANISMS. THERE IS ONLY ONE.
//
// The plan has "Weapons we own (Vanilla VR Plus): the stops are loops written
// into the reload states" and a separate from-outside mechanism for BD22. That
// split does not survive contact: Vanilla VR Plus lives in
//   D:\...\__CurrentRotationDONOTDELETE\1.0b_Weapons_VanillaVRPlus_v1.2\
// which is the owner's live play rotation and is read-only. Its reload states
// are not ours to edit, and overriding its weapon classes would break the
// plan's own premise that no mod's weapon class changes.
//
// So every gun gets the from-outside hold. One mechanism, which is simpler than
// the plan and removes the only place the two could have drifted apart.
//
// HOW THE HOLD WORKS
//   models.cpp:379   inter = (curState->Tics - curTics + ticFraction) / curState->Tics
//   models.cpp:383   if (curState->Tics < curTics) inter = 0.
//   player.zs:3004   if (Tics != -1) { Tics--; if (!Tics) SetState(NextState); }
//
// Writing psp.Tics ABOVE the state's own authored Tics forces inter to 0, so
// the gun sits exactly on its current model frame with no blend creeping
// forward. Tics = -1 would instead make inter exceed 1 with nothing clamping
// it, and the engine would extrapolate past the next frame.
//
// The hold decays -- Tics counts down every tic -- so it is re-written every
// tic from QH_Hands' 1-tic Ready loop for as long as the stop is held.
//
// THE OWNER'S RULE IS THE OUTER GATE
//   Reloading takes two hands, so it cannot happen while steadying. While
//   QH_Hands.ReloadAllowed() is false NO stop releases: the reload holds where
//   it is. It never aborts. See qh_hands.zs.
// ============================================================================


// ----------------------------------------------------------------------------
// A stop, declared the way the gun actually reads rather than by a hand-counted
// state offset.
//
// A reload chain walks through one or more sprite runs. For VR_Rifle that is
// RIFL (frames 0-25, model frames 0-25) then RIFK (frames 0-14, model frames
// 26-40). A stop names which RUN it is in and which FRAME inside that run, and
// is resolved by walking the chain and matching -- so adding or removing a
// 0-tic action state upstream cannot silently move it.
// ----------------------------------------------------------------------------

enum QH_Release
{
	QHR_HAND_AWAY,		// release once the off hand has gone out to fetch
	QHR_HAND_RETURNED,	// release once the off hand is back at the magazine well
	QHR_HAND_PULLBACK,	// release once the off hand pulls back again (the rack)
	QHR_HAND_CYCLE,		// release once the hand has gone out AND come back
}

// Two ways to say WHERE a stop is, because reloads come in two shapes.
//
// QHSM_RUNFRAME -- (sprite run, frame). Reads the way the gun does and survives
//   a 0-tic action state being inserted upstream. Needs the chain to walk
//   cleanly through its sprite runs, which VR_Rifle does (RIFL then RIFK).
//
// QHSM_STEPS -- the Nth tic-bearing state after a named label.
//
//   *** BROKEN IN STOCK QZD, AND IT CANNOT BE REPAIRED AS WRITTEN. ***
//
//   It resolved a step by walking `State.NextState` from the label. But a
//   `Goto` REWRITES the preceding state's NextState -- FStateDefinitions::
//   SetGotoLabel, p_states.cpp:886, `laststate->NextState = <target>` -- and
//   every BD22 reload label opens with a block of 0-TIC guards ending in
//   `Goto Ready`. The guards contribute nothing to the count, so the walk
//   follows the rewritten pointer straight into Ready and resolves EVERY step
//   against the Ready loop.
//
//   At runtime the gun never takes that pointer: it reaches its animation by
//   the guards' RELATIVE jump (`A_JumpIfInventory("AmmoRocket",1,3)` -- three
//   STATE SLOTS forward; a Goto occupies no slot). Script cannot follow that.
//   Stock QZD's ZScript `State` exposes only NextState, sprite, Tics, Frame
//   (doombase.zs:577) -- there is no array arithmetic and no DistanceTo, so
//   execution order is not reachable from script at all.
//
//   Kept only so the nine older cards still parse while they are converted.
//   Do not write a new one. See QHSM_SEQFRAME.
//
// QHSM_SEQFRAME -- a frame, matched as the gun actually plays it, IN SEQUENCE.
//
//   The replacement, and it needs no walking of anything. A card's stops are an
//   ORDERED sequence: stop i only becomes eligible once stop i-1 has released
//   this reload. So a stop is simply "the next time the layer shows frame N",
//   and the thing that made frames ambiguous -- the same frame recurring many
//   times in one chain, like RAIR I ten times or MISR T four times -- stops
//   mattering, because only one stop is ever looking.
//
//   This is strictly more robust than the step count it replaces: it observes
//   the path the gun took rather than predicting it, so a mod's A_Jump, a
//   random duration or a branch we never read cannot shift it.
enum QH_StopMode
{
	QHSM_RUNFRAME,
	QHSM_STEPS,
	QHSM_SEQFRAME,
}

// A CLASS AND NOT A STRUCT, and it is not a style choice: ZScript's dynamic
// array cannot hold a struct. `Array<QH_Stop>` fails with "Base type for
// dynamic array types must be integral, but got Struct<QH_Stop>", and that
// cascades into "Unable to resolve all fields for class QH_ReloadCard" --
// seven errors from one word, refusing the whole pk3. Same for QH_RideKey.
class QH_Stop
{
	int mode;		// QH_StopMode
	int run;		// RUNFRAME: 0 = first sprite run, 1 = next distinct, ...
	int frame;		// RUNFRAME / SEQFRAME: frame index (A = 0, Z = 25, '[' = 26)
	Name label;		// STEPS: the state label to count from
	int step;		// STEPS: how many tic-bearing states past it
	int release;	// QH_Release
}


// ----------------------------------------------------------------------------
// Per-weapon card. One row per gun. VR_Rifle is the first; BD22's guns are more
// rows, not more code.
// ----------------------------------------------------------------------------

class QH_ReloadCard
{
	Name weaponClass;
	Name reloadLabel;
	// Which part the off hand carries for THIS gun -- a state label on QH_Hands.
	Name carryState;
	Array<QH_Stop> stops;

	// STEPS stops resolve to an exact State once, then match by pointer.
	// Parallel to `stops`; null for RUNFRAME stops.
	Array<State> resolved;
	bool didResolve;

	// ------------------------------------------------------------------------
	// GRAB GEOMETRY -- where the hand has to actually BE. See qh_grab.zs.
	//
	// Metres along the gun's own axes: x forward along the bore, y to the gun's
	// right, z up. Radii in metres. A zero radius means "this gun has no such
	// part", and the stop then falls back to the old hand-separation gesture
	// rather than becoming impossible to satisfy -- a gun nobody has tuned yet
	// must stay reloadable.
	//
	// These are SEEDS, not measurements. The drawn gun goes through a transform
	// script cannot read (the block at the top of qh_grab.zs), so they are tuned
	// in the headset against the marker and then baked here.
	// ------------------------------------------------------------------------
	vector3 wellLocal;		// where ammunition goes in
	double wellR;
	vector3 handleLocal;	// what you pull to cycle it
	double handleR;

	void SetGrab(vector3 well, double wellRadius, vector3 handle, double handleRadius)
	{
		wellLocal   = well;
		wellR       = wellRadius;
		handleLocal = handle;
		handleR     = handleRadius;
	}

	// Has anyone given this gun geometry to grab at all?
	bool HasGrab() const { return wellR > 0.0; }

	static QH_ReloadCard Make(Name cls, Name label)
	{
		let c = new("QH_ReloadCard");
		c.weaponClass = cls;
		c.reloadLabel = label;
		c.carryState = 'CarryHand';	// overridden per gun below
		return c;
	}

	void AddStop(int run, int frame, int release)
	{
		let s = new("QH_Stop");
		s.mode = QHSM_RUNFRAME;
		s.run = run;
		s.frame = frame;
		s.label = 'None';
		s.step = 0;
		s.release = release;
		stops.Push(s);
		resolved.Push(null);
	}

	void AddStepStop(Name label, int step, int release)
	{
		let s = new("QH_Stop");
		s.mode = QHSM_STEPS;
		s.run = 0;
		s.frame = 0;
		s.label = label;
		s.step = step;
		s.release = release;
		stops.Push(s);
		resolved.Push(null);
	}

	// A frame, matched in sequence as the gun plays it. See QHSM_SEQFRAME.
	//
	// ORDER IS THE WHOLE MECHANISM: push these in the order the hand does them,
	// because stop i is not even looked at until stop i-1 has released. The
	// frame index is the Doom frame letter (A = 0 ... Z = 25, then [ = 26), the
	// same number `tools/dec_reload_map.py` prints as `FRAME`.
	void AddSeqStop(int frame, int release)
	{
		let s = new("QH_Stop");
		s.mode = QHSM_SEQFRAME;
		s.run = 0;
		s.frame = frame;
		s.label = 'None';
		s.step = 0;
		s.release = release;
		stops.Push(s);
		resolved.Push(null);
	}

	// Is `frame` one of this card's stop frames? Used to tell "the chain has
	// moved on" from "we are sitting on a stop", so the sequence can re-arm for
	// the next reload without needing to know what Ready looks like.
	bool IsStopFrame(int frame) const
	{
		for (int i = 0; i < stops.Size(); i++)
			if (stops[i].mode == QHSM_SEQFRAME && stops[i].frame == frame)
				return true;
		return false;
	}

	// Walk once, counting only states that actually hold for a tic. 0-tic action
	// states are plumbing and must not shift the count.
	play void Resolve(Actor weap)
	{
		if (didResolve || !weap) return;
		didResolve = true;

		for (int i = 0; i < stops.Size(); i++)
		{
			if (stops[i].mode != QHSM_STEPS) continue;

			// FindState takes a compile-time statelabel, so a runtime Name can
			// never reach it -- "Cannot convert Name to StateLabel". The string
			// form is the only runtime lookup.
			State st = weap.FindStateByString("" .. stops[i].label, false);
			int seen = 0;
			int guard = 0;

			while (st && guard < 512)
			{
				if (st.Tics > 0)
				{
					if (seen == stops[i].step) { resolved[i] = st; break; }
					seen++;
				}
				st = st.NextState;
				guard++;
			}
		}
	}
}


// ----------------------------------------------------------------------------
// The service. Driven every tic from QH_Hands' Ready loop.
// ----------------------------------------------------------------------------

class QH_ReloadService
{
	Array<QH_ReloadCard> cards;

	// Step 3. Owned here because the ride needs the same card this service
	// already resolved, and ticking it from one place keeps the two in step.
	QH_RideService ride;

	// Which stop index we are currently holding, -1 for none.
	int heldStop;

	// THE SEQUENCE CURSOR for QHSM_SEQFRAME cards: how many of this card's
	// stops have already released during the reload now running. Only stop
	// `progressed` is eligible, which is what makes a repeated frame harmless.
	//
	// It re-arms by itself: once the last stop has gone, the first tic on a
	// frame that is not any stop's frame means the chain has moved on, and the
	// cursor goes back to 0 ready for the next reload. That deliberately avoids
	// needing to recognise Ready, which differs per gun and per mod.
	int progressed;
	Name seqOwner;	// the class `progressed` is counting for; a swap resets it

	// ------------------------------------------------------------------------
	// NETPLAY
	//
	// Hand positions are per-client VR poses and are NEVER sent over the wire --
	// stock QZD already desyncs when a VR player aims by hand for exactly this
	// reason. So a reload stop must not release on a hand test: machine A would
	// advance the gun and machine B would not.
	//
	// The split:
	//   - Gesture detection is ADVISORY and runs on the owning client only. The
	//     fields below (wentAway, cycleCredits, requested) are local scratch; it
	//     does not matter that they differ between machines because they only
	//     decide whether to ASK.
	//   - The release itself is authorised by a netevent, which every machine
	//     receives identically. That is the only thing that touches psp.Tics,
	//     poses or haptics.
	//
	// consoleplayer appears below for one purpose: "is this my own hand data".
	// The gameplay decision still travels by netevent, so this is not keying
	// gameplay on consoleplayer -- do not "fix" it into the playsim.
	// ------------------------------------------------------------------------

	int requested;		// stop we have already asked the net about, -1 none
	int netReleased;	// stop the net has authorised, -1 none

	// QHR_HAND_CYCLE needs memory: a per-shell reload loops through the SAME
	// stop, so "the hand is near" is not enough -- without this the whole tube
	// fills the instant your hand happens to be close. Set when the hand goes
	// out past the fetch distance.
	bool wentAway;

	// SHELLS PER INSERT. Owner, 2026-10-03: "no matter what set we are playing I
	// want to be able to do 1 to four shells per insert to not wear myself out."
	//
	// A tube-fed gun wants eight fetch-and-return trips to fill, which is a lot
	// of arm for one reload. One trip out earns qh_shells_per_insert credits;
	// each release spends one, and the hand only has to travel again once they
	// run out. At 1 this is strictly one shell per trip, which is the honest
	// default; at 4 a full tube is two trips.
	//
	// Deliberately general: it applies to ANY QHR_HAND_CYCLE stop in any set, so
	// a shell-at-a-time gun we add later gets it without new code.
	int cycleCredits;
	// Sprite indices of the runs in the chain we are currently in.
	Array<int> runSprites;
	Name runOwner;	// the class whose chain runSprites was built from

	// ------------------------------------------------------------------------
	// VR_Rifle, from FILTER/DOOM/Decorate/rifle.txt and FILTER/DOOM/Modeldef.Rifle
	//
	//   ReloadA:
	//     RIFL LMN 2              model 11,12,13   mag release (9mmclip1)
	//     RIFL OPQRSTUVWXYZ 1     model 14-25      magazine travels out
	//     RIFK ABCDEFGHI 2        model 26-34      new magazine goes in (9mmclip2 at I)
	//     RIFK JKL 1              model 35-37      seat (9mmslide at L)
	//     RIFK MNO 2              model 38-40      recover
	//     RIFL A 1                model 0          back to ready
	//
	// 46 tics, about 1.3 s. The block has no NOINTERPOLATION, so it blends --
	// which is what step 3 rides.
	//
	// Stops:
	//   run 0 frame 25  = RIFL Z  -- magazine is clear of the well
	//   run 1 frame 0   = RIFK A  -- about to insert; this is step 3's ride range
	//   run 1 frame 9   = RIFK J  -- about to rack
	// ------------------------------------------------------------------------

	void Init()
	{
		heldStop = -1;
		wentAway = false;
		cycleCredits = 0;
		requested = -1;
		netReleased = -1;
		runOwner = 'None';

		let rifle = QH_ReloadCard.Make('VR_Rifle', 'ReloadA');
		rifle.AddStop(0, 25, QHR_HAND_AWAY);		// RIFL Z
		rifle.AddStop(1,  0, QHR_HAND_RETURNED);	// RIFK A
		rifle.AddStop(1,  9, QHR_HAND_PULLBACK);	// RIFK J
		rifle.carryState = 'CarryRifleMag';
		cards.Push(rifle);

		// VR_Revolver, from FILTER/DOOM/Decorate/revolver.txt.
		//   ReloadA:
		//     REVL QRSTUVWXYZ 2   cylinder out      (9mmclip1)
		//     REVO A 1            loading starts    (9mmclip2)
		//     REVO BCDEFGH 2      rounds going in
		//     REVO IJKL 1         cylinder closes   (9mmslide)
		// Same two-run shape as the rifle -- Modeldef.Revolver maps REVL 0-25
		// then REVO from 26, rev.md3 at scale 1.35.
		let rev = QH_ReloadCard.Make('VR_Revolver', 'ReloadA');
		rev.AddStop(0, 25, QHR_HAND_AWAY);		// REVL Z -- cylinder open
		rev.AddStop(1,  0, QHR_HAND_RETURNED);	// REVO A -- about to load
		rev.AddStop(1,  8, QHR_HAND_PULLBACK);	// REVO I -- about to close
		cards.Push(rev);

		// VR_Revolver2 shares rev.md3 and the same states.
		let rev2 = QH_ReloadCard.Make('VR_Revolver2', 'ReloadA');
		rev2.AddStop(0, 25, QHR_HAND_AWAY);
		rev2.AddStop(1,  0, QHR_HAND_RETURNED);
		rev2.AddStop(1,  8, QHR_HAND_PULLBACK);
		cards.Push(rev2);

		// VR_Shotgun is a DIFFERENT SHAPE: a per-shell loop, not a magazine
		// swap. From FILTER/DOOM/Decorate/shotty.txt:
		//   ReloadLoop:
		//     SHTG A 1 A_WeaponReady(WRF_ALLOWRELOAD)
		//     ... jump to ReloadEnd once 8 are loaded
		//     SHTG RQPONMLKJ 1     one shell in
		//     Goto ReloadLoop
		// One stop, hit once per shell, which is why it needs QHR_HAND_CYCLE
		// rather than QHR_HAND_RETURNED -- the hand has to leave and come back
		// for each shell instead of the stop releasing while it sits there.
		let sht = QH_ReloadCard.Make('VR_Shotgun', 'ReloadLoop');
		sht.AddStop(0, 17, QHR_HAND_CYCLE);		// SHTG R -- shell going in
		sht.carryState = 'CarryShell';
		cards.Push(sht);

		// ------------------------------------------------------------------
		// BD22 Rifle, from brutaldoom22/actors/Weapons/Rifle.dec.
		// Class is plain `Rifle` (ACTOR Rifle : BrutalWeapon).
		//
		// STEP-ADDRESSED, not run-addressed. Its chain is
		//   Reload: ~30 0-tic guards
		//           RIFR ABCDEFGG 1     steps 0-7
		//           RIFR G 0            empty magazine ejected as an ACTOR
		//           RIFR H 3            step 8
		//           RIFR IJKLMNNO 1     steps 9-16
		//           RIFR OONPQR 1       steps 17-22   (Rifle/Reload2 just before)
		//           Goto InsertBullets  <- 0-tic loop that structurally returns
		//                                  to itself, so a walk never gets past it
		//   FinishReloading:
		//           RIFR STUU 1         steps 0-3
		//           RIFR VVVWXYZ 1      steps 4-10
		//           RIFR "[" 1          step 11
		//           RIFR B 1            step 12
		//           2IFR ABCDEFG 1      steps 13-19
		//           2IFR H 3            step 20      (Rifle/Bolt1 just after)
		//
		// The third stop counts from FinishReloading for exactly that reason:
		// nothing can walk there from Reload.
		//
		// NOTE FOR STEP 3: BD22 throws the empty magazine as a spawned actor
		// (A_FireCustomMissile("EmptyClipSpawn")) rather than animating a surface
		// of the gun mesh. There is no magazine surface to ride here, so this gun
		// gets stops without a ride. That is a real difference from VR_Rifle, not
		// an omission.
		let bd22rifle = QH_ReloadCard.Make('Rifle', 'Reload');
		// RIFR H and 2IFR H are BOTH frame 7. The sequence is what separates
		// them: pullback is not looked at until returned's O has released, so
		// it can only match the later one. Order is load-bearing here.
		bd22rifle.AddSeqStop( 7, QHR_HAND_AWAY);		// RIFR H -- Reload step 8
		bd22rifle.AddSeqStop(14, QHR_HAND_RETURNED);	// RIFR O -- Reload step 17
		bd22rifle.AddSeqStop( 7, QHR_HAND_PULLBACK);	// 2IFR H -- FinishReloading step 20
		bd22rifle.carryState = 'CarryRifleMag';
		cards.Push(bd22rifle);

		// ------------------------------------------------------------------
		// BD22 Shot_Gun -- per-shell, like VR_Shotgun. Its InsertingShells label
		// runs one shell and loops:
		//     SHTN UUUVW 1    then Shotgun/Reload, then XYZ[]
		// Step 0 is where a shell begins, so that is the stop, and it is hit once
		// per shell -- which is what makes qh_shells_per_insert apply here.
		// Mapped with tools/dec_reload_map.py.
		let bdShotgun = QH_ReloadCard.Make('Shot_Gun', 'Reload');
		bdShotgun.AddSeqStop(20, QHR_HAND_CYCLE);	// SHTN U -- InsertingShells step 0
		bdShotgun.carryState = 'CarryShell';
		cards.Push(bdShotgun);

		// BD22 Revolver -- also per-shell, cylinder loaded a round at a time.
		//     REVR Z R S 1   then Shotgun/Reload, then TTUVWXY
		let bdRevolver = QH_ReloadCard.Make('Revolver', 'Reload');
		bdRevolver.AddSeqStop(25, QHR_HAND_CYCLE);	// REVR Z -- InsertingShells step 0
		bdRevolver.carryState = 'CarryShell';
		cards.Push(bdRevolver);

		// BD22 BrutalPistol -- magazine swap.
		//     Pistol/Reload1 ... 2ISR A-O (steps 0-18) ... Pistol/Reload2
		// Step 8 is mid-extraction with the magazine clear; step 18 is the last
		// frame before Reload2, so the hand arrives before the new one goes in.
		let bdPistol = QH_ReloadCard.Make('BrutalPistol', 'Reload');
		bdPistol.AddSeqStop( 7, QHR_HAND_AWAY);		// 2ISR H -- Reload step 8
		bdPistol.AddSeqStop(14, QHR_HAND_RETURNED);	// 2ISR O -- Reload step 18
		bdPistol.carryState = 'CarryRifleMag';
		cards.Push(bdPistol);


		// ------------------------------------------------------------------
		// BD22 BrutalSMG -- magazine swap, mapped with tools/dec_reload_map.py.
		//
		//   Reload:          SMG/Reload1 after step 9 (magazine released)
		//                    step 17  EmptyClip2Spawn -- the empty magazine is
		//                             thrown as an ACTOR, not animated on the gun
		//                    steps 18-29  the hand drops away
		//                    -> FinishReload
		//   FinishReload:    SMG/Reload2 just before step 0 (new magazine in)
		//                    steps 6-8  SMGR [ backslash ] -- the bolt
		//
		// Stop 2 sits at the END of Reload rather than the start of FinishReload
		// so that Reload2 fires when the magazine actually goes in, instead of
		// playing to an empty hand while we wait.
		let bdSMG = QH_ReloadCard.Make('BrutalSMG', 'Reload');
		bdSMG.AddSeqStop(15, QHR_HAND_AWAY);		// SMGR P -- step 18, mag ejected
		bdSMG.AddSeqStop(21, QHR_HAND_RETURNED);	// SMGR V -- step 29, before the insert
		bdSMG.AddSeqStop(26, QHR_HAND_PULLBACK);	// SMGR [ -- FinishReload step 6, the bolt
		bdSMG.carryState = 'CarryRifleMag';
		cards.Push(bdSMG);

		// ------------------------------------------------------------------
		// BD22 MP40 -- magazine swap with a bolt at each end. Four sound beats:
		//
		//   Reload:      step 10  MP40/Bolt1       bolt back
		//                step 26  Weapon/Empty     the click
		//                step 36  MP40/Reload1     magazine released
		//                step 41  EmptyClip2Spawn  empty magazine thrown as an actor
		//                step 42  the hand drops away        <- stop 1
		//                step 45  2P4R run begins, new magazine coming up <- stop 2
		//                step 59  MP40/Reload2     magazine seated
		//                -> InsertBullets
		//   FullReload:  steps 4-22  MP4R V..K, the bolt pulled back and returning
		//                after 22    MP40/Bolt2   <- so the stop is step 4, BEFORE
		//                                            the pull, not after it
		//
		// Its chain is the longest of the set at ~280 enumerated states, which is
		// why it was mapped rather than counted by eye.
		let bdMP40 = QH_ReloadCard.Make('MP40', 'Reload');
		bdMP40.AddSeqStop(26, QHR_HAND_AWAY);		// MP4R [ -- Reload step 42
		bdMP40.AddSeqStop( 0, QHR_HAND_RETURNED);	// 2P4R A -- Reload step 45
		bdMP40.AddSeqStop(21, QHR_HAND_PULLBACK);	// MP4R V -- FullReload step 4
		bdMP40.carryState = 'CarryRifleMag';
		cards.Push(bdMP40);

		// ------------------------------------------------------------------
		// BD22 Sniper -- magazine swap. Mapped with tools/dec_reload_map.py.
		//   step 10  Sniper/MagOut            magazine released
		//   step 16  EmptySniperAmmoSpawn     thrown as an actor
		//   step 17  hand drops away                      <- stop 1
		//   step 34  last frame before Sniper/MagIn       <- stop 2
		let bdSniper = QH_ReloadCard.Make('Sniper', 'Reload');
		bdSniper.AddSeqStop(13, QHR_HAND_AWAY);		// X21R N -- Reload step 17
		bdSniper.AddSeqStop(20, QHR_HAND_RETURNED);	// X21R U -- Reload step 34
		bdSniper.carryState = 'CarryRifleMag';
		cards.Push(bdSniper);

		// BD22 AssaultShotgun -- a BOX MAGAZINE swap, not a per-shell tube.
		// Worth stating because the name suggests otherwise and carding it as a
		// shell loop would have been wrong.
		//   step 11  ASG/Reload1
		//   step 18  EmptyASGAmmoSpawn        thrown as an actor
		//   step 19  hand drops away                      <- stop 1
		//   step 34  last frame before ASG/Reload2        <- stop 2
		let bdASG = QH_ReloadCard.Make('AssaultShotgun', 'Reload');
		bdASG.AddSeqStop(15, QHR_HAND_AWAY);		// USAR P -- Reload step 19
		bdASG.AddSeqStop(22, QHR_HAND_RETURNED);	// USAR W -- Reload step 34
		bdASG.carryState = 'CarryRifleMag';
		cards.Push(bdASG);

		// ------------------------------------------------------------------
		// BD22 SSG -- BREAK ACTION, a third shape: both hulls leave at once and
		// two shells go in together, so it is neither a magazine swap nor a
		// per-shell loop.
		//
		// Its real sequence is under Reload2; the Reload label only guards and
		// jumps there, which is why carding 'Reload' would have found nothing.
		//   step 3   SSG/Lever2                   the break
		//   step 6   weapons/sshoto + SSGCaseSpawner -- BOTH hulls thrown as actors
		//   step 7   breech open, hand goes down          <- stop 1
		//   steps 7-19  SHZ2, the hand bringing shells up
		//   step 19  last frame before SHZ3 closes it     <- stop 2
		let bdSSG = QH_ReloadCard.Make('SSG', 'Reload2');
		bdSSG.AddSeqStop(15, QHR_HAND_AWAY);		// SHZ2 P -- Reload2 step 7
		bdSSG.AddSeqStop(25, QHR_HAND_RETURNED);	// SHZ2 Z -- Reload2 step 19
		bdSSG.carryState = 'CarryShell';
		cards.Push(bdSSG);

		// ------------------------------------------------------------------
		// THE CARRY PART FOR THE NEXT FOUR is 'CarryHand', the documented
		// fallback, and that is a finding rather than a shortcut: BD22 throws
		// the spent round as a SPAWNED ACTOR in every one of them
		// (RocketCaseSpawn, PlasmaCaseSpawn, GrenadeCasingSpawner) instead of
		// animating a surface of the gun, and models/ has no rocket, cell or
		// grenade part. There is nothing to put in the hand yet. A real part
		// for these is one new QH_Hands state plus one mesh -- mesh work, not
		// card work -- and the stops below do not change when it arrives.
		// ------------------------------------------------------------------

		// ------------------------------------------------------------------
		// BD22 Rocket_Launcher, from actors/Weapons/RocketLauncher.dec.
		// Opens and loads under Reload; CLOSES under FinishReload, and nothing
		// walks from one to the other, so the third stop counts from there --
		// the same split as the Rifle above, for the same reason.
		//   Reload:
		//     steps 0-6    MISR A-E    the tube swinging open
		//     (0-tic)      A_FireCustomMissile("RocketCaseSpawn") -- case thrown
		//     step 7       MISR F      first tic with the case gone   <- away
		//     steps 8-16   MISR G-N    (N holds 3 tics)
		//     step 17      MISR O      hand back with the rocket      <- returned
		//     steps 18-26  MISR P-T    the push and seat (T four times)
		//     Goto FinishReload
		//   FinishReload:
		//     step 0       MISG A      A_Refire gate, NOT animation
		//     (0-tic)      A_PlaySound("rocket/reload2") -- the audible close
		//     step 1       MISR U      first real close frame         <- pullback
		//     steps 2-10   MISR V-Z, MIR2 A
		let bdRL = QH_ReloadCard.Make('Rocket_Launcher', 'Reload');
		// Frames, in sequence. The Reload/FinishReload split stops mattering
		// here: a frame is matched wherever the gun actually goes, so crossing
		// a label is no longer something the card has to know about.
		bdRL.AddSeqStop( 5, QHR_HAND_AWAY);		// MISR F -- Reload step 7
		bdRL.AddSeqStop(14, QHR_HAND_RETURNED);	// MISR O -- Reload step 17
		bdRL.AddSeqStop(20, QHR_HAND_PULLBACK);	// MISR U -- FinishReload step 1
		bdRL.carryState = 'CarryHand';
		cards.Push(bdRL);

		// ------------------------------------------------------------------
		// BD22 RailGun. All three stops live in Reload: by the time
		// FinishReload runs the cell is already in and it is the return to
		// ready, not part of the load.
		//   (0-tic)      A_PlaySound("Railgun/Reload1") + PlasmaCaseSpawn
		//                -- the spent cell is gone BEFORE step 0
		//   steps 0-8    RAIR A-H    breech opening
		//   steps 9-18   RAIR I      TEN steps on one frame: it sits open <- away
		//   step 19      RAIR J      motion resumes, cell going in    <- returned
		//   steps 20-24  RAIR K-O
		//   (0-tic)      A_PlaySound("Railgun/Reload2")
		//   step 25      RAIR O      the audible close                <- pullback
		//   steps 26-32  RAIR P-S, then the ammo block and Goto FinishReload
		//
		// InsertBullets IS NOT A PER-ROUND LOOP despite the name -- unlike
		// Shot_Gun's InsertingShells it holds no tic-bearing state at all, only
		// the 0-tic A_Giveinventory("RailgunAmmo",1) accounting. There is
		// nothing in it to stop on, so qh_shells_per_insert does not apply.
		let bdRail = QH_ReloadCard.Make('RailGun', 'Reload');
		// RAIR I repeats TEN times and the sequence makes that harmless: the
		// away stop takes the first of them and nothing looks at I again.
		bdRail.AddSeqStop( 8, QHR_HAND_AWAY);		// RAIR I -- step 9, first of ten
		bdRail.AddSeqStop( 9, QHR_HAND_RETURNED);	// RAIR J -- step 19
		bdRail.AddSeqStop(15, QHR_HAND_PULLBACK);	// RAIR P -- step 26, after Reload2
		bdRail.carryState = 'CarryHand';
		cards.Push(bdRail);

		// ------------------------------------------------------------------
		// BD22 Plasma_Gun.
		//
		// AWAY AND RETURNED STRADDLE A SINGLE 10-TIC STATE, so they are
		// ADJACENT IN STEPS and ten tics apart in time. That is deliberate and
		// it is the window that matters -- do not "space them out" by step
		// count, which would move returned past the insert.
		//   (0-tic)      A_PlaySound("Plasma/Reload1") + PlasmaCaseSpawn
		//   steps 0-10   PRSR A,A,Z,B-H   the housing opening
		//   step 11      PRSR I  10 TICS  open and waiting            <- away
		//   step 12      PRSR J           motion resumes, cell in     <- returned
		//   steps 13-18  PRSR K-O
		//   (0-tic)      A_PlaySound("Plasma/Reload2")
		//   step 19      PRSR O           the audible close           <- pullback
		//   steps 20-22  PRSR O, then the ammo block
		//
		// FinishReload and ReloadingSequence share one PRSR P-Z tail, so either
		// would address the same frames; Reload reaches all three stops without
		// crossing a label at all.
		let bdPlasma = QH_ReloadCard.Make('Plasma_Gun', 'Reload');
		bdPlasma.AddSeqStop( 8, QHR_HAND_AWAY);		// PRSR I -- step 11, the 10-tic hold
		bdPlasma.AddSeqStop( 9, QHR_HAND_RETURNED);	// PRSR J -- step 12
		bdPlasma.AddSeqStop(15, QHR_HAND_PULLBACK);	// PRSR P -- step 23, the close
		bdPlasma.carryState = 'CarryHand';
		cards.Push(bdPlasma);

		// ------------------------------------------------------------------
		// BD22 GrenadeLauncher -- break action, one grenade at a time.
		//
		// MUST BE STEP-ADDRESSED. Every state carries its sprite as "####", so
		// there is no run to name: the mapper reports run -1 throughout, and
		// AddStop(run, frame, ...) has nothing to match.
		//   steps 0-4    F-I   raising into the reload
		//   step 5       J     A_PlaySound("GrenadeLauncher/Open")
		//   step 6       K     breech opening
		//   (0-tic)      GrenadeCasingSpawner + SmokeSpawner -- casing thrown
		//   step 7       L     first tic with the casing gone         <- away
		//   steps 8-18   L-U
		//   step 19      U     last frame before A_GiveInventory("GLAmmo") and
		//                      A_PlaySound("GrenadeLauncher/Load"), so the hand
		//                      arrives AS the grenade goes in         <- returned
		//   steps 20-25  U-Y, then TNT1 for 4 tics
		//   step 26      Z     A_PlaySound("GrenadeLauncher/Close")   <- pullback
		//   steps 27-43  [ \ ] then A-L, then Goto Ready
		//
		// The mechanical walk runs on past step 43 into Unload, because a Goto
		// is followed. Those steps are NOT this label's and nothing here
		// addresses them.
		let bdGL = QH_ReloadCard.Make('GrenadeLauncher', 'Reload');
		// The "####" sprite stops being a problem too: a frame is read off the
		// live layer, which has a concrete sprite whatever the .dec wrote.
		bdGL.AddSeqStop(11, QHR_HAND_AWAY);		// L -- step 7, casing thrown
		bdGL.AddSeqStop(20, QHR_HAND_RETURNED);	// U -- step 18, the grenade goes in
		bdGL.AddSeqStop(25, QHR_HAND_PULLBACK);	// Z -- step 26, the Close sound
		bdGL.carryState = 'CarryHand';
		cards.Push(bdGL);

		// ------------------------------------------------------------------
		// NOT CARDED, AND CORRECTLY SO:
		//   MiniGun, MG42 -- neither has a Reload label. They are belt-fed and
		//   never reload, so there is nothing to stop. Checked, not assumed.
		//
		//   Flamethrower2 (Flamethrower.dec:93), FlameCannon (FlameCannon.dec:65)
		//   -- both DO define a Reload label, and it is A READY LOOP: one 1-tic
		//   A_WeaponReady, the standard Kicking/Taunting/Salute/TossGrenade/
		//   IsRunning jump block, then Loop (Flamethrower2) or Goto Ready3
		//   (FlameCannon). BD22 provides the label only so that
		//   A_JumpIfInventory("Reloading",1,"Reload") has somewhere to land. No
		//   magazine, no round, no animation -- nothing to stop. Read in the
		//   .dec, not inferred from the mapper.
		//
		//   The six Dual* variants (DualPistols, DualSMG, DualRifles,
		//   DualPlasmaRifles, DualMP40, DualFlameCannon) -- flatscreen
		//   dual-wield. In VR both hands are already real hands, so they are
		//   out of scope by the owner's call, not left undone.
		// ------------------------------------------------------------------

		ride = new("QH_RideService");
		ride.Init();
	}

	QH_ReloadCard CardFor(Actor weap)
	{
		if (!weap) return null;
		Name cn = weap.GetClassName();
		for (int i = 0; i < cards.Size(); i++)
			if (cards[i].weaponClass == cn)
				return cards[i];
		return null;
	}

	// Walk the reload chain once and record the sprite index of each distinct
	// run, in order. Cheap, and only redone when the weapon class changes.
	void BuildRuns(Actor weap, QH_ReloadCard card)
	{
		if (runOwner == card.weaponClass) return;

		runSprites.Clear();
		runOwner = card.weaponClass;

		State st = weap.FindStateByString("" .. card.reloadLabel, false);
		int guard = 0;
		int last = -1;

		while (st && guard < 256)
		{
			// 0-tic action states carry TNT1 and are not part of a run.
			if (st.Tics > 0 && st.sprite != last)
			{
				// A run we have already seen means the chain has looped back.
				bool seen = false;
				for (int i = 0; i < runSprites.Size(); i++)
					if (runSprites[i] == st.sprite) { seen = true; break; }

				if (seen) break;

				runSprites.Push(st.sprite);
				last = st.sprite;
			}
			st = st.NextState;
			guard++;
		}
	}

	int RunOf(int sprite) const
	{
		for (int i = 0; i < runSprites.Size(); i++)
			if (runSprites[i] == sprite) return i;
		return -1;
	}

	// Which declared stop, if any, the layer is sitting on right now.
	int StopAt(QH_ReloadCard card, PSprite psp) const
	{
		if (!psp || !psp.CurState) return -1;

		// SEQFRAME first, and it looks at exactly ONE stop: the one the cursor
		// is on. Nothing else is eligible, so a frame that recurs later in the
		// chain cannot jump the queue and an earlier stop cannot re-fire.
		if (progressed >= 0 && progressed < card.stops.Size()
		    && card.stops[progressed].mode == QHSM_SEQFRAME)
		{
			if (card.stops[progressed].frame == psp.CurState.Frame)
				return progressed;
			return -1;
		}

		int run = RunOf(psp.CurState.sprite);

		for (int i = 0; i < card.stops.Size(); i++)
		{
			if (card.stops[i].mode == QHSM_SEQFRAME) continue;

			if (card.stops[i].mode == QHSM_STEPS)
			{
				if (card.resolved[i] && psp.CurState == card.resolved[i])
					return i;
				continue;
			}

			if (run < 0) continue;
			if (card.stops[i].run == run && card.stops[i].frame == psp.CurState.Frame)
				return i;
		}

		return -1;
	}

	// ------------------------------------------------------------------------
	// Gestures are by POSITION, never the off-hand grip button -- the engine
	// takes that button for steadying (gl_openvr.cpp:1717), and under the
	// owner's rule steadying and reloading are mutually exclusive anyway.
	//
	// Every threshold is in REAL METRES through QH_Metric, because the raw
	// difference of two hand positions is not metric in Z. See qh_metric.zs.
	// ------------------------------------------------------------------------

	// Is this the machine whose hands these actually are?
	clearscope static bool IsLocal(PlayerInfo p)
	{
		return p && p.mo && consoleplayer >= 0
		       && players[consoleplayer].mo == p.mo;
	}

	// Called from the net handler. The ONLY thing that authorises a release.
	play void NetRelease(int stopIndex)
	{
		netReleased = stopIndex;
	}

	play double HandSeparation(PlayerInfo p) const
	{
		if (!p || !p.mo) return 0.0;
		return QH_Metric.DistMetres(
			p.mo.AttackPos, p.mo.OffhandPos,
			QH_Metric.StretchOf(p.mo.Level),
			QH_CV.Play_UnitsPerMetre());
	}

	// ------------------------------------------------------------------------
	// A REAL GRAB: is the off hand on the part this stop wants?
	//
	// The release kind already says which part and which direction, so a stop
	// needs no extra data:
	//   AWAY      the hand LEAVES the gun entirely -- it has gone to fetch.
	//             Tested against a body sphere about the main hand, not about
	//             the well, because "outside the well" is already true when the
	//             hand never went there and would release the stop instantly.
	//   RETURNED  the hand ARRIVES at the well.
	//   CYCLE     the same, once per shell, still spending a credit.
	//   PULLBACK  the hand ARRIVES at the handle -- a different place, which is
	//             the thing hand separation could never express.
	// ------------------------------------------------------------------------
	// A BAKED CARD WINS, OTHERWISE THE GLOBAL DEFAULT. One shared set of cvars
	// means every carded gun has a real grab the first time it is loaded and
	// can be tuned on the spot, instead of thirteen guns waiting on thirteen
	// bakes. Crude -- a pistol's well is not a rifle's -- and that is what the
	// per-card bake is for.
	play vector3 WellOf(QH_ReloadCard card)
	{
		if (card && card.wellR > 0.0) return card.wellLocal;
		return (QH_CV.PF('qh_well_x',  0.10),
		        QH_CV.PF('qh_well_y',  0.00),
		        QH_CV.PF('qh_well_z', -0.08));
	}

	play double WellROf(QH_ReloadCard card)
	{
		if (card && card.wellR > 0.0) return card.wellR;
		return QH_CV.PF('qh_well_r', 0.12);
	}

	play vector3 HandleOf(QH_ReloadCard card)
	{
		if (card && card.handleR > 0.0) return card.handleLocal;
		return (QH_CV.PF('qh_handle_x', 0.02),
		        QH_CV.PF('qh_handle_y', 0.04),
		        QH_CV.PF('qh_handle_z', 0.02));
	}

	play double HandleROf(QH_ReloadCard card)
	{
		if (card && card.handleR > 0.0) return card.handleR;
		return QH_CV.PF('qh_handle_r', 0.10);
	}

	play bool ReleasedGrab(int release, PlayerInfo p, QH_ReloadCard card)
	{
		let mo = p.mo;
		if (!mo || !card) return false;

		double stretch = QH_Metric.StretchOf(mo.Level);
		double upm     = QH_CV.Play_UnitsPerMetre();

		switch (release)
		{
			case QHR_HAND_AWAY:
			{
				// Distance from the gun itself, so any direction counts as
				// leaving. The gun is at the main hand.
				double d = QH_Metric.DistMetres(mo.AttackPos, mo.OffhandPos, stretch, upm);
				return d > QH_CV.PF('qh_grab_body_m', 0.30);
			}
			case QHR_HAND_RETURNED:
				return QH_Grab.Inside(mo, WellOf(card), WellROf(card), stretch, upm);
			case QHR_HAND_CYCLE:
				return cycleCredits > 0
				    && QH_Grab.Inside(mo, WellOf(card), WellROf(card), stretch, upm);
			case QHR_HAND_PULLBACK:
			{
				// A gun with no tuned handle falls back to the well rather than
				// refusing to finish the reload.
				return QH_Grab.Inside(mo, HandleOf(card), HandleROf(card), stretch, upm);
			}
		}
		return true;
	}

	// The old gesture, kept as the fallback for a gun nobody has tuned and as
	// an escape hatch if a seed turns out to be badly placed: `qh_grab 0`.
	play bool ReleasedBySeparation(int release, PlayerInfo p)
	{
		double d = HandSeparation(p);

		switch (release)
		{
			case QHR_HAND_AWAY:
				return d > QH_CV.PF('qh_fetch_m', 0.35);
			case QHR_HAND_RETURNED:
				return d < QH_CV.PF('qh_insert_m', 0.18);
			case QHR_HAND_PULLBACK:
				return d > QH_CV.PF('qh_rack_m', 0.30);
			case QHR_HAND_CYCLE:
				return cycleCredits > 0 && d < QH_CV.PF('qh_insert_m', 0.18);
		}
		return true;
	}

	play bool Released(int release, PlayerInfo p, QH_ReloadCard card)
	{
		if (QH_CV.PI('qh_grab', 1) != 0 && WellROf(card) > 0.0)
			return ReleasedGrab(release, p, card);

		return ReleasedBySeparation(release, p);
	}

	// ------------------------------------------------------------------------
	// SHOW THE GRAB SPHERES while tuning. Off by default: this is an instrument,
	// not a feature, and nobody wants dots on their gun while playing.
	//
	// Local only. Particles are visual, not playsim state, so drawing them on
	// one machine changes nothing anywhere else -- but the gate keeps this
	// consistent with everything else here that reads a VR pose.
	// ------------------------------------------------------------------------
	play void DrawMarkers(PlayerInfo p, QH_ReloadCard card)
	{
		if (QH_CV.PI('qh_grab_marker', 0) == 0) return;
		if (!IsLocal(p) || !p.mo || !card) return;

		let mo = p.mo;
		double stretch = QH_Metric.StretchOf(mo.Level);
		double upm     = QH_CV.Play_UnitsPerMetre();

		vector3 wl = WellOf(card);
		double  wr = WellROf(card);
		vector3 hl = HandleOf(card);
		double  hr = HandleROf(card);

		QH_GrabMarker.Sphere(mo, wl, wr, stretch, upm,
			QH_Grab.Inside(mo, wl, wr, stretch, upm));
		QH_GrabMarker.Sphere(mo, hl, hr, stretch, upm,
			QH_Grab.Inside(mo, hl, hr, stretch, upm));

		// The off hand itself, so a sphere that has landed somewhere absurd
		// reads as a placement error instead of as "the grab does not work".
		QH_GrabMarker.Blip(mo, mo.OffhandPos, Color(255, 120, 180, 255), 5.0);
	}

	// Keep the cycle latch current. Called every tic, stop or no stop.
	//
	// Going out past the fetch distance tops the credits back up. It is an
	// assignment rather than an increment on purpose: holding the hand out does
	// not bank an unlimited supply.
	play void TrackCycle(PlayerInfo p)
	{
		if (!IsLocal(p)) return;	// advisory; see the NETPLAY note above

		if (HandSeparation(p) > QH_CV.PF('qh_fetch_m', 0.35))
		{
			wentAway = true;

			int want = int(QH_CV.PF('qh_shells_per_insert', 1.0));
			if (want < 1) want = 1;
			if (want > 4) want = 4;
			cycleCredits = want;
		}
	}

	// ------------------------------------------------------------------------
	// Called every tic.
	// ------------------------------------------------------------------------

	play void Tick(PlayerInfo p)
	{
		if (!p || !p.mo) { heldStop = -1; return; }

		let weap = p.ReadyWeapon;
		let card = CardFor(weap);
		if (!card) { heldStop = -1; return; }

		let psp = p.FindPSprite(PSP_WEAPON);
		if (!psp || !psp.CurState) { heldStop = -1; return; }

		// A weapon swap mid-reload leaves the cursor somewhere meaningless.
		if (seqOwner != card.weaponClass)
		{
			seqOwner = card.weaponClass;
			progressed = 0;
		}

		BuildRuns(weap, card);
		card.Resolve(weap);

		// Step 3 runs whether or not we are at a stop: the ride happens AFTER a
		// stop releases, while the insert frames play out.
		if (ride) ride.Tick(p, card);

		TrackCycle(p);
		DrawMarkers(p, card);

		int at = StopAt(card, psp);
		if (at < 0)
		{
			// RE-ARM. The sequence is spent and the layer has moved onto a
			// frame that is nobody's stop, so the reload is over: put the
			// cursor back for the next one.
			if (progressed >= card.stops.Size()
			    && !card.IsStopFrame(psp.CurState.Frame))
			{
				progressed = 0;
			}

			heldStop = -1;
			requested = -1;
			netReleased = -1;
			return;
		}

		heldStop = at;

		// The outer gate: his rule. While steadying, nothing releases and the
		// reload simply waits where it is.
		bool allowed = QH_Hands.ReloadAllowed(p);

		// ADVISORY, LOCAL ONLY. Decide whether to ask; ask once per stop.
		if (allowed && requested != at && IsLocal(p)
		    && Released(card.stops[at].release, p, card))
		{
			requested = at;
			EventHandler.SendNetworkEvent("qh_rel", at);
		}

		// AUTHORITATIVE, EVERY MACHINE. Only a netevent gets past here.
		if (netReleased == at)
		{
			netReleased = -1;
			requested = -1;

			// Let it go. Leave Tics alone and the state advances normally,
			// blending into the next model frame.
			QH_Haptic.Tick(p, card.stops[at].release);
			QH_Pose.OnRelease(p, card.stops[at].release, card.carryState);

			// ADVANCE THE CURSOR. A per-shell QHR_HAND_CYCLE stop stays where
			// it is -- it is meant to be hit once per shell, and the credits
			// below are what govern how often it may go.
			if (card.stops[at].mode == QHSM_SEQFRAME
			    && card.stops[at].release != QHR_HAND_CYCLE)
			{
				progressed = at + 1;
			}

			// Credit bookkeeping is local scratch -- it only gates the next ASK,
			// so it does not matter that a remote machine's copy is untouched.
			if (card.stops[at].release == QHR_HAND_CYCLE)
			{
				if (cycleCredits > 0) cycleCredits--;
				if (cycleCredits <= 0) wentAway = false;
			}
			else
			{
				wentAway = false;
			}
			return;
		}

		// Hold. Above the state's own authored Tics, so models.cpp:383 forces
		// inter to 0 and the gun sits exactly on this frame.
		int want = psp.CurState.Tics + 8;
		if (want < 8) want = 8;
		psp.Tics = want;
	}
}


// ----------------------------------------------------------------------------
// Haptics.
//
// There is no script-callable haptic in stock -- no DEFINE_ACTION_FUNCTION for
// Vibrate or VR_HapticEvent anywhere. The reachable route is a 1-damage
// LineAttack, which buzzes for a fixed 150 ms at 0.8 (p_map.cpp:4764-4775).
//
// The HAND IS OURS TO CHOOSE: p_map.cpp:4766-4768 flips it on LAF_ISOFFHAND,
// and that flag is exposed to ZScript and used by stock content
// (weaponssg.zs:101, weaponpistol.zs:74). The plan had this as one-handed; it
// is not.
//
// LAF_NOINTERACT keeps it from touching the world (attacks.zs:108 uses it the
// same way). The haptic fires before the trace, so NOINTERACT does not mute it.
// ----------------------------------------------------------------------------

class QH_Haptic abstract
{
	play static void Buzz(PlayerInfo p, bool offHand)
	{
		if (!p || !p.mo) return;

		p.mo.LineAttack(
			p.mo.Angle, 1, p.mo.Pitch, 1,
			'Hitscan', "BulletPuff",
			LAF_NOINTERACT | (offHand ? LAF_ISOFFHAND : 0));
	}

	play static void Tick(PlayerInfo p, int release)
	{
		switch (release)
		{
			case QHR_HAND_AWAY:
				Buzz(p, true);		// magazine released into the off hand
				break;
			case QHR_HAND_RETURNED:
				Buzz(p, true);		// magazine seated
				break;
			case QHR_HAND_PULLBACK:
				Buzz(p, false);		// the rack lands in the gun hand
				break;
		}
	}
}


// ----------------------------------------------------------------------------
// Step 4: pose changes, driven off the same stop releases.
//
// The hand closes when it goes out to fetch and opens once the magazine is in
// the gun. Both are PAIRED states on QH_Hands (see its States block) because the
// engine takes its blend target from the state chain and nowhere else.
//
// These fire on the RELEASE of a stop rather than on entering one, so the pose
// change and the gun's own animation start together.
// ----------------------------------------------------------------------------

class QH_Pose abstract
{
	play static void Set(PlayerInfo p, int layer, Name stateLabel)
	{
		if (!p || !p.OffhandWeapon) return;

		let psp = p.FindPSprite(layer);
		if (!psp) return;

		let st = p.OffhandWeapon.FindStateByString("" .. stateLabel, false);
		if (st) psp.SetState(st);
	}

	play static void OnRelease(PlayerInfo p, int release, Name carryState)
	{
		switch (release)
		{
			case QHR_HAND_AWAY:
				// Gone out to fetch: close the hand and put a magazine in it.
				Set(p, QH_Layers.FREEHAND, 'FreeHandClose');
				Set(p, QH_Layers.CARRY,    carryState);
				break;

			case QHR_HAND_RETURNED:
				// Magazine is in the gun now: open the hand, take it away.
				Set(p, QH_Layers.FREEHAND, 'FreeHandOpen');
				Set(p, QH_Layers.CARRY,    'Carry');
				break;
		}
	}
}
