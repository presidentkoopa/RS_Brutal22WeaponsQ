// RS VR hands for BD22 on QuestZDoom 17.x. rsq_hands 0 hides them.
//
// The hands and their poses are Ermac's (Force Unleashed / Rusted Legacy, MIT):
// a gun hand posed on each gun's grip, a support hand posed on its front, and
// an off hand that is open, or holds the right magazine / shell / cell while
// reloading. rsq_hands_gen.py fitted his poses onto BD22's guns
// (handtable.zs).
//
//   gun hand      always on the gun (none for melee, grenades, two-gun
//                 weapons, and the flame cannon your arm goes into)
//   off hand      free on the off controller; bring it to the front of the gun
//                 and it takes hold there (the support hand), the way Ermac's
//                 two-hand models swap in; take it away and it lets go. It
//                 never holds on while a reload needs it.
//
// How they reach the controllers (no engine changes): models.cpp puts a layer
// on the OFF controller only when its caller is the off-hand weapon, so the
// free hand belongs to RSQ_Hands (an off-hand weapon that never fires) and the
// gun and support hands to RSQ_GunSide (a plain item: main controller).
// hw_weapon.cpp asks the off-hand weapon's ModifyBobLayer3D where to put every
// layer that is not the ready weapon's; that places them per gun.

class RSQ_Layers abstract
{
	const GUNHAND = 2100;	// RSQ_GunSide, main controller
	const SUPPORT = 2101;	// RSQ_GunSide, main controller
	const FREEHAND = 2200;	// RSQ_Hands, off controller
}

class RSQ_GunSide : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.QUIET
	}

	States
	{
	GunA: RQGS A -1; Stop;
	GunB: RQGS B -1; Stop;
	GunC: RQGS C -1; Stop;
	GunD: RQGS D -1; Stop;
	GunE: RQGS E -1; Stop;
	GunF: RQGS F -1; Stop;
	GunG: RQGS G -1; Stop;
	SupA: RQSP A -1; Stop;
	SupB: RQSP B -1; Stop;
	SupC: RQSP C -1; Stop;
	SupD: RQSP D -1; Stop;
	SupE: RQSP E -1; Stop;
	SupF: RQSP F -1; Stop;
	Hidden: TNT1 A -1; Stop;
	}
}

class RSQ_Hands : Weapon
{
	const SNAP_IN = 0.15;	// the off hand takes hold within this of the front (m)
	const SNAP_OUT = 0.22;	// ...and lets go past this

	Default
	{
		+WEAPON.OFFHANDWEAPON
		+WEAPON.NOHANDSWITCH
		+WEAPON.NO_AUTO_SWITCH
		+WEAPON.NOAUTOSWITCHTO
		+WEAPON.NOALERT
		+WEAPON.CHEATNOTWEAPON
		+WEAPON.NODEATHINPUT
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.QUIET
		Weapon.SelectionOrder 32000;
		Weapon.Kickback 0;
		Weapon.UpSound "";
		Weapon.ReadySound "";
		Weapon.UseRange 48;
		Tag "Hands";
	}

	static bool Shown(PlayerPawn mo)
	{
		return mo && RSQ.PlayerInt(mo, 'rsq_hands', 1) != 0 && RSVR_VRHand.InVR(mo);
	}

	// every tic, from RSQ_Handler.WorldTick: hand the player the off-hand
	// weapon when hands are on and they are playing in VR
	static void Upkeep(PlayerPawn mo)
	{
		let p = mo.player;
		if (!p || p.playerstate != PST_LIVE || mo.health <= 0 || !Shown(mo))
			return;
		let h = Weapon(mo.FindInventory('RSQ_Hands'));
		if (!h)
		{
			mo.GiveInventory('RSQ_Hands', 1);
			h = Weapon(mo.FindInventory('RSQ_Hands'));
		}
		if (h && !p.OffhandWeapon && p.PendingWeapon == WP_NOCHANGE)
			p.PendingWeapon = h;
	}

	action void A_RSQ_Layers()
	{
		let p = player;
		let mo = PlayerPawn(self);
		if (!p || !mo)
			return;
		bool on = Shown(mo);
		let s = RSQ_Handler.StateOf(mo);
		int carry = s ? s.carry : 0;
		int i = on ? RSQ_HandTable.Index(p.ReadyWeapon) : 0;

		// the off hand holds the front of the gun when it is there, unless a
		// reload needs it
		bool hold = false;
		if (i > 0 && s && s.kind == 0 && carry == 0)
		{
			double d = (RSQ.OffLocal(mo) - RSQ_HandTable.SupportPoint(i)).Length();
			hold = d < (s.holding ? SNAP_OUT : SNAP_IN);
		}
		if (s)
			s.holding = hold;

		static const String ammo[] = { "FreeHand", "AmmoB", "AmmoC", "AmmoD", "AmmoE", "AmmoF", "AmmoG", "AmmoH" };
		invoker.SetLayer(p, RSQ_Layers.FREEHAND, invoker,
			!on || hold ? "Hidden" : ammo[clamp(carry, 0, 7)]);

		let gs = RSQ_GunSide(FindInventory('RSQ_GunSide'));
		if (!gs)
		{
			A_GiveInventory('RSQ_GunSide', 1);
			gs = RSQ_GunSide(FindInventory('RSQ_GunSide'));
		}
		if (!gs)
			return;
		String g = hold ? RSQ_HandTable.GunTwo(i) : RSQ_HandTable.GunOne(i);
		invoker.SetLayer(p, RSQ_Layers.GUNHAND, gs, i > 0 && g != "" ? "Gun" .. g : "Hidden");
		String sp = RSQ_HandTable.Support(i);
		invoker.SetLayer(p, RSQ_Layers.SUPPORT, gs, hold && sp != "" ? "Sup" .. sp : "Hidden");
	}

	// put a layer on a state only when it changes, so a pose is not
	// restarted every tic
	void SetLayer(PlayerInfo p, int id, Actor caller, String label)
	{
		State want = caller.FindStateByString(label);
		let psp = p.FindPSprite(id);
		if (psp && psp.Caller == caller && psp.CurState == want)
			return;
		p.SetPsprite(id, want, false, caller);
		psp = p.FindPSprite(id);
		if (psp)
		{
			psp.bAddWeapon = false;
			psp.bAddBob = true;
		}
	}

	// Where the gun-side hands sit for the gun in hand (ui scope, inherited).
	// The incoming translation is the weapon bob every layer gets; the hook is
	// added to it. The free hand keeps Ermac's own placement on its controller.
	override Vector3, Vector3 ModifyBobLayer3D(Vector3 translation, Vector3 rotation, int layer, double ticfrac)
	{
		if (layer != RSQ_Layers.GUNHAND && layer != RSQ_Layers.SUPPORT)
			return translation, rotation;
		let o = Owner ? Owner.player : null;
		int i = o ? RSQ_HandTable.Index(o.ReadyWeapon) : 0;
		if (i <= 0)
			return translation, rotation;
		if (layer == RSQ_Layers.GUNHAND)
			return translation + RSQ_HandTable.GunHook(i), rotation;
		return translation + RSQ_HandTable.SupportHook(i), rotation + RSQ_HandTable.SupportRot(i);
	}

	States
	{
	Ready:
		TNT1 A 1
		{
			A_RSQ_Layers();
			A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
		}
		Loop;
	Deselect:
		TNT1 A 1 A_Lower(64);
		Loop;
	Select:
		TNT1 A 1 A_Raise(64);
		Loop;
	Fire:
		TNT1 A 1;
		Goto Ready;

	// the free hand (MODELDEF.rsq): open, or holding ammo
	FreeHand: RQHN A -1; Stop;
	AmmoB: RQHN B -1; Stop;		// pistol magazine
	AmmoC: RQHN C -1; Stop;		// a shell
	AmmoD: RQHN D -1; Stop;		// two shells
	AmmoE: RQHN E -1; Stop;		// rifle magazine
	AmmoF: RQHN F -1; Stop;		// rocket / grenade
	AmmoG: RQHN G -1; Stop;		// cell
	AmmoH: RQHN H -1; Stop;		// a closed hand
	Hidden: TNT1 A -1; Stop;
	}
}
