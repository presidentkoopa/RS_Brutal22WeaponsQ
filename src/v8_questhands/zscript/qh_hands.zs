// ============================================================================
// RS_QuestHands -- the hands weapon, the gun-side helper, and the per-frame hook
//
// Step 1 of the build order in _reports/QUEST_RELOAD_DIAGNOSIS_2026-10-02.md.
//
// WHAT STEP 1 PROVES
//   1. A ModifyBobLayer3D override on OUR off-hand weapon is called for layers
//      owned by OUR helper item   -- hw_weapon.cpp:332 and :941-951
//   2. The axis and unit convention (X right, Y up, Z back toward the player;
//      1 unit = 1 cm times the MODELDEF scale)
//   3. Four model layers drawing together on Quest
//   4. Which controller each one lands on   -- models.cpp:221
//
// THE OWNERSHIP RULE, WHICH IS LOAD-BEARING
//   models.cpp:221:  int hand = psp->GetCaller() == player->OffhandWeapon ? 1 : 0;
//   A layer reaches the OFF controller only if its caller IS the off-hand
//   weapon. Everything else goes to the MAIN controller. So:
//     free hand + carried magazine -> owned by QH_Hands   -> off controller
//     gun hand + support hand      -> owned by QH_GunSide -> main controller
//   That is also exactly why steadying hides the first two and not the last two
//   (hw_weapon.cpp:917), which is correct behaviour under the owner's rule that
//   reloading takes two hands.
//
// LAYER IDs
//   player.zs:555-566 destroys a layer whose ID is PSP_WEAPON (1) or
//   PSP_OFFHANDWEAPON (1000000) with the wrong caller, and hw_weapon.cpp:915
//   only walks layers with ID < PSP_TARGETCENTER (0x7ffffffd). Ours sit well
//   inside that window and avoid both reserved values.
// ============================================================================

class QH_Layers abstract
{
	const GUNHAND  = 2100;	// helper-owned -> main controller
	const SUPPORT  = 2101;	// helper-owned -> main controller
	const FREEHAND = 2200;	// hands-owned  -> off controller
	const CARRY    = 2201;	// hands-owned  -> off controller
}


// ============================================================================
// QH_GunSide -- the gun-side helper.
//
// A plain Inventory, deliberately NOT a Weapon. player.zs:555-566 keeps a layer
// alive when its caller is a non-Weapon Inventory the player still owns, so
// these two layers survive every weapon switch without touching any mod's
// weapon class. That is the trick the whole plan rests on.
// ============================================================================

class QH_GunSide : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.KEEPDEPLETED
		+INVENTORY.QUIET
	}

	// Sprite and frame here must match the MODELDEF blocks keyed to QH_GunSide.
	States
	{
	GunHand:
		QHGS A -1;
		stop;
	Support:
		QHGS B -1;
		stop;
	}
}


// ============================================================================
// QH_Hands -- the off-hand weapon. Carries the hook.
//
// Occupies the off-hand slot via +WEAPON.OFFHANDWEAPON
// (flagdef OffhandWeapon: WeaponFlags, 20).
//
// MUST NOT be +WEAPON.TWOHANDED -- player.zs:1977-1994 makes that flag delete
// the weapon in the other slot, in both directions.
//
// MUST NEVER FIRE. The off hand only ever supports; it must not take or gate
// the trigger. Hence WRF_NOFIRE throughout and an empty Fire state.
//
// ITS READY LOOP MUST STAY 1 TIC. WF_TWOHANDSTABILIZED is cleared and
// re-evaluated in DPSprite::SetState (p_pspr.cpp:591-607); only a PSP_WEAPON or
// PSP_OFFHANDWEAPON state change clears it, while ANY layer's state change
// re-sets it. It is sticky-on. A 1-tic Ready loop on this weapon's own
// PSP_OFFHANDWEAPON layer is what keeps the bit an honest per-tic mirror, which
// the steadying guard depends on. Do not lengthen it.
// ============================================================================

class QH_Hands : Weapon
{
	Default
	{
		+WEAPON.OFFHANDWEAPON
		+WEAPON.NOALERT
		+WEAPON.CHEATNOTWEAPON
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.KEEPDEPLETED
		+INVENTORY.QUIET
		Weapon.SelectionOrder 32000;	// never preferred by auto-switch
		Weapon.Kickback 0;
		Weapon.UpSound "";
		Weapon.ReadySound "";
		Tag "Hands";
	}

	// The step 2 reload service. transient because it is pure runtime state and
	// rebuilds itself on demand -- it must not go into a savegame.
	transient QH_ReloadService qhReload;

	// ------------------------------------------------------------------------
	// Steadying
	//
	// While steadying is on, stock disables the off-hand slot four ways:
	//   hw_weapon.cpp:917     every off-hand-weapon-owned layer is not drawn
	//   weapons.zs:415-418    WF_OFFHANDREADY is never granted
	//   p_pspr.cpp:847-850    P_CheckWeaponButtons returns early for the off hand
	//   gl_openvr.cpp:1742    the main hand's aim becomes the hand-to-hand line
	//
	// And it is LATCHED ON THE BUTTON, NOT THE DISTANCE: gl_openvr.cpp:1717-1728
	// is edge-triggered on the off-hand grip and tests the 0.50 m gap only at the
	// instant of the press. After that the flag holds until the grip is released,
	// however far apart the hands travel. So a player can grip at the gun and
	// then reach to their hip, still steadying.
	// ------------------------------------------------------------------------

	clearscope static bool IsSteadying(PlayerInfo p)
	{
		return p && (p.WeaponState & WF_TWOHANDSTABILIZED);
	}

	// Stale-latch detection.
	//
	// gl_openvr.cpp:1704 gates the whole steadying block on
	// menuactive == MENU_Off, so opening a menu while gripping and releasing the
	// grip inside it leaves the flag stuck on with no button held. If we are told
	// we are steadying but the hands are further apart than anyone could steady
	// at, believe the hands.
	play static bool IsStaleLatch(PlayerInfo p)
	{
		if (!p || !p.mo)         return false;
		if (!IsSteadying(p))     return false;

		double d = QH_Metric.DistMetres(
			p.mo.AttackPos, p.mo.OffhandPos,
			QH_Metric.StretchOf(p.mo.Level),
			QH_CV.Play_UnitsPerMetre());

		return d > QH_CV.PF('qh_stale_latch_m', 0.60);
	}

	// THE RELOAD GUARD, from the owner's rule: reloading takes two hands, so it
	// cannot happen while steadying. Ask before starting a reload, and ask again
	// each tic during one -- on a false answer the reload HOLDS, it does not
	// abort. The pause structure already does the holding; the hand check simply
	// never passes.
	play static bool ReloadAllowed(PlayerInfo p)
	{
		if (!p)              return false;
		if (!IsSteadying(p)) return true;
		return IsStaleLatch(p);
	}

	// ------------------------------------------------------------------------
	// Layer upkeep. Idempotent; called every tic from Ready.
	// ------------------------------------------------------------------------

	action void A_QH_EnsureLayers()
	{
		let p = player;
		if (!p) return;

		// Ours, owned by this weapon -> off controller.
		if (!p.FindPSprite(QH_Layers.FREEHAND))
			p.SetPsprite(QH_Layers.FREEHAND, invoker.FindState("FreeHand"), false, invoker);

		if (!p.FindPSprite(QH_Layers.CARRY))
			p.SetPsprite(QH_Layers.CARRY, invoker.FindState("Carry"), false, invoker);

		// The gun-side pair, owned by the helper -> main controller.
		let gs = QH_GunSide(FindInventory("QH_GunSide"));
		if (!gs)
		{
			A_GiveInventory("QH_GunSide", 1);
			gs = QH_GunSide(FindInventory("QH_GunSide"));
			if (!gs) return;
		}

		if (!p.FindPSprite(QH_Layers.GUNHAND))
			p.SetPsprite(QH_Layers.GUNHAND, gs.FindState("GunHand"), false, gs);

		if (!p.FindPSprite(QH_Layers.SUPPORT))
			p.SetPsprite(QH_Layers.SUPPORT, gs.FindState("Support"), false, gs);
	}

	// Drives step 2. This weapon's Ready loop is already 1 tic (it has to be,
	// for WF_TWOHANDSTABILIZED), so it is the natural per-tic driver and saves
	// standing up a second ticker. The hold it applies decays every tic and is
	// re-written from here for as long as a stop is held.
	action void A_QH_Reload()
	{
		let p = player;
		if (!p) return;

		if (!invoker.qhReload)
		{
			invoker.qhReload = new("QH_ReloadService");
			invoker.qhReload.Init();
		}

		invoker.qhReload.Tick(p);
	}

	// ------------------------------------------------------------------------
	// THE HOOK.
	//
	// weapons.zs:46 -- virtual ui Vector3, Vector3 ModifyBobLayer3D(...)
	// It is `ui`: it may read play data but must not write any; it only returns
	// numbers (weapons.zs:44-48).
	//
	// The renderer calls it once per model layer, per eye, per rendered frame
	// (hw_weapon.cpp:951-965), for every layer whose caller is not the ready
	// weapon -- which is all four of ours.
	//
	// Translation (0,0,0) already sits AT the controller the layer rides, because
	// models.cpp:220-228 applies that controller's transform before the
	// translation goes in. So we return our own offset outright rather than
	// adding to the incoming bob.
	//
	// Never touch ModifyBobPivotLayer3D. It is broken in this build: weapons.zs:48
	// declares 3 slots with self, hw_weapon.cpp:973-974 passes 6.
	//
	// Cvar reads here are one hash lookup each. If that ever shows up on Quest,
	// cache them in a ui StaticEventHandler -- do not move them to play scope.
	// ------------------------------------------------------------------------

	// NO `ui` ON THE OVERRIDE. The scope comes from the base declaration and
	// restating it is "Attempt to change scope for virtual function" -- a
	// load-time refusal, not a warning. The body is still ui scope, inherited,
	// so the cvar reads described above are unaffected.
	override vector3, vector3 ModifyBobLayer3D(vector3 Translation, vector3 Rotation, int layer, double ticfrac)
	{
		switch (layer)
		{
			case QH_Layers.FREEHAND:
			{
				// Already rides the off controller. Park it there.
				vector3 t = (QH_CV.UF('qh_free_x', 0.0),
				             QH_CV.UF('qh_free_y', 0.0),
				             QH_CV.UF('qh_free_z', 0.0));
				vector3 r = (QH_CV.UF('qh_free_yaw',   0.0),
				             QH_CV.UF('qh_free_pitch', 0.0),
				             QH_CV.UF('qh_free_roll',  0.0));
				return t, r;
			}

			case QH_Layers.CARRY:
			{
				// Sits in the free hand, so the same place plus a small offset.
				vector3 t = (QH_CV.UF('qh_free_x', 0.0) + QH_CV.UF('qh_carry_x', 0.0),
				             QH_CV.UF('qh_free_y', 0.0) + QH_CV.UF('qh_carry_y', 0.0),
				             QH_CV.UF('qh_free_z', 0.0) + QH_CV.UF('qh_carry_z', 0.0));
				vector3 r = (QH_CV.UF('qh_free_yaw',   0.0),
				             QH_CV.UF('qh_free_pitch', 0.0),
				             QH_CV.UF('qh_free_roll',  0.0));
				return t, r;
			}

			case QH_Layers.GUNHAND:
			{
				// Rides the main controller. Offset to the gun's grip.
				vector3 t = (QH_CV.UF('qh_gun_x', 0.0),
				             QH_CV.UF('qh_gun_y', 0.0),
				             QH_CV.UF('qh_gun_z', 0.0));
				vector3 r = (QH_CV.UF('qh_gun_yaw',   0.0),
				             QH_CV.UF('qh_gun_pitch', 0.0),
				             QH_CV.UF('qh_gun_roll',  0.0));
				return t, r;
			}

			case QH_Layers.SUPPORT:
			{
				vector3 r = (QH_CV.UF('qh_sup_yaw',   0.0),
				             QH_CV.UF('qh_sup_pitch', 0.0),
				             QH_CV.UF('qh_sup_roll',  0.0));

				// STEP 3. While the magazine is going in, the support hand is on
				// it, at a position measured offline from the gun's own mesh.
				// Reading a play field from ui scope, which is allowed; the
				// resolution all happened once in play this tic.
				if (qhReload && qhReload.ride && qhReload.ride.riding)
				{
					// The ride track is simulation-side; where in the HAND the
					// magazine sits is this player's own placement, so it is
					// added here in ui and never in play.
					vector3 rp = qhReload.ride.ridePos;
					rp.x += QH_CV.UF('qh_ride_x', 0.0);
					rp.y += QH_CV.UF('qh_ride_y', 0.0);
					rp.z += QH_CV.UF('qh_ride_z', 0.0);
					return rp, r;
				}

				// Otherwise parked at the gun's support point.
				vector3 t = (QH_CV.UF('qh_sup_x', 0.0),
				             QH_CV.UF('qh_sup_y', 0.0),
				             QH_CV.UF('qh_sup_z', 0.0));
				return t, r;
			}
		}

		// Not ours -- hand back exactly what came in.
		return Translation, Rotation;
	}

	States
	{
	Ready:
		// 1 TIC, LOOPING, ON PURPOSE. See the class comment.
		QHND A 1
		{
			A_QH_EnsureLayers();
			A_QH_Reload();
			A_WeaponReady(WRF_NOFIRE | WRF_NOSWITCH | WRF_NOBOB);
		}
		loop;
	Deselect:
		QHND A 1 A_Lower();
		loop;
	Select:
		QHND A 1 A_Raise();
		loop;
	Fire:
		// Empty on purpose. The off hand never fires.
		QHND A 1 A_WeaponReady(WRF_NOFIRE | WRF_NOSWITCH | WRF_NOBOB);
		goto Ready;

	// ---- the pieces this weapon owns -> off controller ----
	//
	// STEP 4. The engine blends a layer between its current frame and the frame
	// of its NEXT STATE, over that state's Tics (models.cpp:367-405). The target
	// ALWAYS comes from the state chain -- writing psp.Frame changes what is
	// drawn now but not what it blends toward (models.cpp:404). So a transition
	// is a PAIR of states: the pose being left, then the pose being entered.
	//
	// A resting pose ends in `stop`, which leaves NextState null, so
	// models.cpp:370 skips the blend and the hand sits still. That is also what
	// makes -1 safe here: with no next state there is nothing to over-blend
	// toward. A -1 on a state that DOES have a successor would drive inter above
	// 1 with nothing clamping it.
	FreeHand:			// resting, open relaxed
		QHND B -1;
		stop;
	FreeHandClosed:		// resting, closed round the magazine
		QHND D -1;
		stop;
	FreeHandClose:		// open -> closed, over 6 tics
		QHND B 6;
		QHND D -1;
		stop;
	FreeHandOpen:		// closed -> open, over 6 tics
		QHND D 6;
		QHND B -1;
		stop;

	// The carried magazine is hidden by parking the layer on TNT1: it has no
	// model, so hw_weapon.cpp:925 skips the layer outright. Cleaner than alpha
	// 0, which would make it a translucent draw, and translucent HUD layers do
	// not depth-sort (hw_models.cpp:94-96).
	Carry:				// hidden
		TNT1 A -1;
		stop;
	// One state per carried part. Which one a gun uses is on its reload card,
	// so adding a gun with a different magazine is a card field, not new code.
	CarryHand:			// ammo_hand mesh -- the fallback when a gun has no part
		QHND C -1;
		stop;
	CarryRifleMag:		// rifle_mag.md3
		QHND E -1;
		stop;
	CarryShell:			// shell.md3
		QHND F -1;
		stop;
	}
}
