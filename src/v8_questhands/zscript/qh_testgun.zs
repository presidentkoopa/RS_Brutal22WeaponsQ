// ============================================================================
// RS_QuestHands -- step 1's test gun, and the thing that hands the kit out
//
// WHY A TEST GUN AND NOT THE VANILLA RIFLE.
//
// Step 1's four claims are about the hook, the axes, several layers at once, and
// which controller each lands on. None of them need a particular gun. A weapon
// we ship proves all four with no dependency on another pack, which also means
// step 1 can be tried the moment this loads.
//
// Vanilla VR Plus enters at step 2, where the reload stops go into its own
// states. It lives at
//   D:\SteamLibrary\steamapps\Common\DooM VR\__CurrentRotationDONOTDELETE\1.0b_Weapons_VanillaVRPlus_v1.2\
// inside the owner's live play rotation, so it is READ-ONLY.
//
// The test gun deliberately has NO model. PSP_WEAPON then finds no model frame
// and hw_weapon.cpp:925 skips that layer -- harmless, and it keeps the view to
// the four hand layers we are actually judging.
// ============================================================================

class QH_TestGun : Weapon
{
	Default
	{
		+WEAPON.NOALERT
		+WEAPON.CHEATNOTWEAPON
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.KEEPDEPLETED
		+INVENTORY.QUIET
		Weapon.SelectionOrder 31000;
		Weapon.Kickback 0;
		Weapon.UpSound "";
		Weapon.ReadySound "";
		Tag "Hands Test Gun";
	}

	States
	{
	Ready:
		QTST A 1 A_WeaponReady(WRF_NOFIRE);
		loop;
	Deselect:
		QTST A 1 A_Lower();
		loop;
	Select:
		QTST A 1 A_Raise();
		loop;
	Fire:
		QTST A 1 A_WeaponReady(WRF_NOFIRE);
		goto Ready;
	}
}


// ============================================================================
// QH_Boot -- gives the kit on spawn.
//
// The hands weapon has to be IN the off-hand slot for any of this to work, and
// for two separate reasons:
//
//   1. models.cpp:221 sends a layer to the off controller only if its caller is
//      player->OffhandWeapon.
//   2. hw_weapon.cpp:941 looks the hook up on w.weapon->GetCaller(), and
//      GetWeaponPosition3D (hw_weapon.cpp:332) sets w.weapon to the
//      PSP_OFFHANDWEAPON psprite for any layer not owned by the ready weapon.
//      If that psprite does not exist, w.weapon is null and THE HOOK IS NEVER
//      CALLED AT ALL -- not for our layers, not for anyone's.
//
// So: no hands weapon in the off slot, no step 1. +WEAPON.OFFHANDWEAPON plus
// BringUpWeapon's branch at player.zs:1977-1994 is what seats it.
// ============================================================================

class QH_Boot : EventHandler
{
	override void PlayerSpawned(PlayerEvent e)
	{
		let p = players[e.PlayerNumber].mo;
		if (!p) return;

		if (!p.FindInventory("QH_GunSide")) p.A_GiveInventory("QH_GunSide", 1);
		if (!p.FindInventory("QH_Hands"))   p.A_GiveInventory("QH_Hands",   1);
		if (!p.FindInventory("QH_TestGun")) p.A_GiveInventory("QH_TestGun", 1);
	}

	override void NetworkProcess(ConsoleEvent e)
	{
		// THE RELOAD RELEASE. Sent by the owning client when its hands make the
		// gesture; received here identically on every machine, which is what
		// makes the stop release a synced decision rather than a local one.
		// See the NETPLAY note in qh_reload.zs.
		if (e.Name == "qh_rel")
		{
			if (e.Player < 0 || e.Player >= MAXPLAYERS) return;
			let pmo = players[e.Player].mo;
			if (!pmo) return;

			let hands = QH_Hands(pmo.FindInventory("QH_Hands"));
			if (hands && hands.qhReload)
				hands.qhReload.NetRelease(e.Args[0]);
			return;
		}

		if (e.Name != "qh_report") return;

		let p = players[e.Player].mo;
		if (!p || !p.player) return;
		let pi = p.player;

		Console.Printf("--- RS_QuestHands step 1 ---");
		// A ternary cannot mix Name and String -- "Incompatible types for ?:".
		// GetClassName returns a Name, so stringify it before the branch.
		String rwName = "none";
		if (pi.ReadyWeapon) rwName = "" .. pi.ReadyWeapon.GetClassName();
		String ohName = "none  <-- hook will NOT fire";
		if (pi.OffhandWeapon) ohName = "" .. pi.OffhandWeapon.GetClassName();

		Console.Printf("ReadyWeapon   : %s", rwName);
		Console.Printf("OffhandWeapon : %s", ohName);

		for (int i = 0; i < 4; i++)
		{
			int id = (i == 0) ? QH_Layers.GUNHAND
			       : (i == 1) ? QH_Layers.SUPPORT
			       : (i == 2) ? QH_Layers.FREEHAND
			                  : QH_Layers.CARRY;

			let psp = pi.FindPSprite(id);
			Console.Printf("layer %d : %s  caller=%s  bAddBob=%d",
				id,
				psp ? "present" : "MISSING",
				(psp && psp.Caller) ? ("" .. psp.Caller.GetClassName()) : "-",
				psp ? (psp.bAddBob ? 1 : 0) : 0);
		}

		double d = QH_Metric.DistMetres(
			p.AttackPos, p.OffhandPos,
			QH_Metric.StretchOf(p.Level),
			QH_CV.Play_UnitsPerMetre());

		Console.Printf("hand separation : %.3f m (metric-corrected)", d);

		// ------------------------------------------------------------------
		// THE GRAB READOUT, and it is the tuning instrument: there is no
		// visible marker yet, so these numbers are how a grab point gets
		// placed. Hold the gun, put your off hand exactly where the magazine
		// well LOOKS like it is, run qh_report, and move qh_well_x/y/z until
		// `off hand` reads near zero. Widen qh_well_r only as far as needed.
		// ------------------------------------------------------------------
		// Spelled out rather than a ternary: a ternary whose arms are an object
		// and `null` is one of this language's quieter traps.
		let qhi = QH_Hands(p.FindInventory("QH_Hands"));
		QH_ReloadService svc = null;
		if (qhi) svc = qhi.qhReload;

		if (!svc)
		{
			Console.Printf("grab            : no reload service on this player");
		}
		else
		{
			let card = svc.CardFor(pi.ReadyWeapon);
			if (!card)
			{
				Console.Printf("grab            : %s is not carded -- no reload, no grab",
					rwName);
			}
			else
			{
				double stretch = QH_Metric.StretchOf(p.Level);
				double upm     = QH_CV.Play_UnitsPerMetre();

				vector3 wl = svc.WellOf(card);
				double  wr = svc.WellROf(card);
				vector3 hl = svc.HandleOf(card);
				double  hr = svc.HandleROf(card);

				double dw = QH_Grab.OffhandDistTo(p, wl, stretch, upm);
				double dh = QH_Grab.OffhandDistTo(p, hl, stretch, upm);
				double body = QH_CV.PF('qh_grab_body_m', 0.30);

				Console.Printf("grab mode       : %s   (%s)",
					QH_CV.PI('qh_grab', 1) != 0 ? "REAL GRAB" : "hand separation",
					card.wellR > 0.0 ? "baked in the card" : "global default cvars");

				Console.Printf("well   (%.3f,%.3f,%.3f) r %.3f -> off hand %.3f m  %s",
					wl.x, wl.y, wl.z, wr, dw, dw <= wr ? "INSIDE" : "outside");

				Console.Printf("handle (%.3f,%.3f,%.3f) r %.3f -> off hand %.3f m  %s",
					hl.x, hl.y, hl.z, hr, dh, dh <= hr ? "INSIDE" : "outside");

				Console.Printf("left the gun    : %.3f m of %.3f  %s",
					d, body, d > body ? "YES" : "no");

				// The hand frame itself. If these angles are wrong then every
				// point is wrong, and nudging x/y/z will never fix it.
				Console.Printf("gun hand pose   : yaw %.1f  pitch %.1f  roll %.1f",
					p.AttackAngle, p.AttackPitch, p.AttackRoll);
			}
		}

		Console.Printf("steadying       : %d   stale latch: %d   reload allowed: %d",
			QH_Hands.IsSteadying(pi) ? 1 : 0,
			QH_Hands.IsStaleLatch(pi) ? 1 : 0,
			QH_Hands.ReloadAllowed(pi) ? 1 : 0);
	}
}
