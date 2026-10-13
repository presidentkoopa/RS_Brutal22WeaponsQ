// RS VR hands for BD22 and Vanilla VR Plus on QuestZDoom 17.x. rsq_hands 0 hides them.
//
// The hands and their poses are Ermac's (Force Unleashed / Rusted Legacy, MIT):
// a gun hand posed on each gun's grip, a support hand posed on its front, and
// an off hand that is open, or holds the right magazine / shell / cell while
// reloading. rsq_hands_gen.py fitted his poses onto each set's guns
// (handtable.zs, one per set).
//
//   gun hand      always on the gun (none for melee, grenades, two-gun
//                 weapons, and the flame cannon your arm goes into)
//   off hand      free on the off controller. When the engine steadies the gun
//                 with both hands (the off hand brought to the gun and grip
//                 pressed: vr_two_handed_weapons), it takes hold of the front
//                 of the gun (the support hand), the way Ermac's two-hand
//                 models swap in, and lets go when the engine does. It never
//                 holds on while a reload needs it.
//
// The gun and support hands stay on the gun when it moves under them: when its
// layer is offset (raised, lowered, kicked by Offset) and when its model frames
// kick (BD22's and Vanilla VR Plus's recoil is in the meshes: gunmoves.zs, one
// per set, made by rsq_gunmoves_gen.py).
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
	// How the ready weapon's model frame has moved the gun (RSQ_GunMoves), for
	// ModifyBobLayer3D: looked up in play by A_RSQ_Layers when the gun layer
	// changes frame, read by the renderer.
	State gunState;				// the gun layer's state, sprite and frame they are for
	int gunSprite, gunFrame;
	Vector3 gunTurn, gunMove;	// that frame
	Vector3 nextTurn, nextMove;	// the next state's frame, which the engine blends toward

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
		if (!p || p.playerstate != PST_LIVE || mo.health <= 0 || !Shown(mo) && !RSR_Handler.WantsHands(mo))
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
		// a real reload (rsr/vreload.zs) has the off hand: it says what the free hand shows
		String rsr = RSR_Handler.FreeHand(mo);
		int i = on ? RSQ_HandTable.Index(p.ReadyWeapon) : 0;

		// The off hand holds the front of the gun exactly while the engine
		// steadies the gun with both hands (WF_TWOHANDSTABILIZED: the player
		// brought the off hand to the gun and pressed grip), unless a reload
		// needs it. Going by the engine's own grab keeps the hands and the
		// steadying together: a distance snap of our own fought it, and lost
		// the minigun's handlebar grip.
		bool hold = i > 0 && (p.WeaponState & WF_TWOHANDSTABILIZED) != 0 && s && s.kind == 0 && carry == 0;
		if (s)
			s.holding = hold;
		invoker.FollowGun(p, i);

		static const String ammo[] = { "FreeHand", "AmmoB", "AmmoC", "AmmoD", "AmmoE", "AmmoF", "AmmoG", "AmmoH" };
		invoker.SetLayer(p, RSQ_Layers.FREEHAND, invoker,
			!on || hold ? "Hidden" : rsr != "" ? rsr : ammo[clamp(carry, 0, 7)]);

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

	// Look up how the gun's model frame moves it when the gun layer shows
	// another frame. The gun layer has ticked by now (layers tick in ID order,
	// the off-hand weapon's last), so this is the frame drawn this tic.
	void FollowGun(PlayerInfo p, int i)
	{
		let g = i > 0 ? p.FindPSprite(PSP_WEAPON) : null;
		if (!g || !g.CurState)
		{
			gunState = null;
			gunTurn = gunMove = nextTurn = nextMove = (0, 0, 0);
			return;
		}
		int spr = g.Sprite;
		if (g.CurState == gunState && spr == gunSprite && g.Frame == gunFrame)
			return;
		gunState = g.CurState;
		gunSprite = spr;
		gunFrame = g.Frame;
		Vector3 t, m;
		[t, m] = RSQ_GunMoves.Frame(i, spr, g.Frame);
		gunTurn = nextTurn = t;
		gunMove = nextMove = m;
		// The engine blends a model toward the next state's frame, unless that
		// state keeps the layer's sprite ("####": sprite index 1 or 2), which it
		// cannot look up.
		let n = gunState.NextState;
		if (RSQ_GunMoves.Blends(i) && n && n != gunState && n.sprite > 2)
		{
			[t, m] = RSQ_GunMoves.Frame(i, n.sprite, n.Frame);
			nextTurn = t;
			nextMove = m;
		}
	}

	// a layer's offset as the renderer draws it this frame (hw_weapon.cpp BobWeapon3D)
	ui static Vector2 LayerOffset(PSprite s, double ticfrac)
	{
		if (s.firstTic)
			return (s.x, s.y);
		return (s.oldx + (s.x - s.oldx) * ticfrac, s.oldy + (s.y - s.oldy) * ticfrac);
	}

	// Where the gun-side hands sit for the gun in hand (ui scope, inherited).
	// The incoming translation is the weapon bob every layer gets; the hook is
	// added to it. The free hand keeps Ermac's own placement on its controller.
	override Vector3, Vector3 ModifyBobLayer3D(Vector3 translation, Vector3 rotation, int layer, double ticfrac)
	{
		// the real reload's layers (rsr/vreload.zs)
		if (layer >= RSR.LAYER_FIRST && layer <= RSR.LAYER_LAST || layer == RSR.HANDMAG || layer == RSQ_Layers.FREEHAND)
		{
			Vector3 t, r;
			[t, r] = RSR_Handler.Place(Owner, translation, rotation, layer, ticfrac);
			if (layer != RSQ_Layers.FREEHAND)
				return t, r;
			translation = t;
			rotation = r;
		}
		if (layer != RSQ_Layers.GUNHAND && layer != RSQ_Layers.SUPPORT)
			return translation, rotation;
		let o = Owner ? Owner.player : null;
		int i = o ? RSQ_HandTable.Index(o.ReadyWeapon) : 0;
		if (i <= 0)
			return translation, rotation;
		bool gunHand = layer == RSQ_Layers.GUNHAND;
		Vector3 hook = gunHand ? RSQ_HandTable.GunHook(i) : RSQ_HandTable.SupportHook(i);
		Vector3 hookTurn = gunHand ? RSQ_HandTable.GunRot(i) : RSQ_HandTable.SupportRot(i);

		// The renderer turns every HUD model by its own layer's offset: yaw x / 4,
		// pitch (y - WEAPONTOP) / -4 (hw_weapon.cpp, RenderHUDModel's call). The gun
		// layer is at y = 32 when ready and moves when it is raised, lowered or
		// kicked by Offset; ours stay at 0, which on its own tipped the hands 8
		// degrees up off the gun (the support hand into the shotguns' barrels). So
		// the hands take the gun layer's turn instead of their own, about the point
		// the gun model turns on. A gun model mirrored against the hands turns the
		// other way sideways.
		PSprite gp, hp;
		for (let s = o.psprites; s; s = s.Next)
		{
			if (s.ID == PSP_WEAPON)
				gp = s;
			else if (s.ID == layer)
				hp = s;
		}
		Vector2 g = gp ? LayerOffset(gp, ticfrac) : (0, WEAPONTOP);
		Vector2 h = hp ? LayerOffset(hp, ticfrac) : (0, 0);
		Vector3 gunTurnNow = (g.x / 4, (g.y - WEAPONTOP) / -4, 0);
		if (RSQ_GunMoves.Mirrored(i))
			gunTurnNow.x = -gunTurnNow.x;

		// The gun's model frame (the recoil is in the meshes), blended toward the
		// next state's frame the way the engine blends the model
		// (models.cpp CalcModelFrame).
		Vector3 frameTurn = gunTurn;
		Vector3 frameMove = gunMove;
		if (gp && gunState && gp.CurState == gunState && gunState.Tics > 0 && gp.Tics <= gunState.Tics)
		{
			double inter = (gunState.Tics - gp.Tics + ticfrac) / gunState.Tics;
			frameTurn += (nextTurn - gunTurn) * inter;
			frameMove += (nextMove - gunMove) * inter;
		}

		Vector3 t, r;
		[t, r] = RSQ_Turn.Place(hook, hookTurn, gunTurnNow, frameTurn, frameMove, RSQ_GunMoves.Pivot(i));
		// the renderer still adds this layer's own turn on top: take it back out
		return translation + t, rotation + r - (h.x / 4, (h.y - WEAPONTOP) / -4, 0);
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
	RsrHold: RQHN I -1; Stop;	// real reload: Ermac's hold, round the gun's own magazine (rsr)
	Hidden: TNT1 A -1; Stop;
	}
}

// Turns the way ModifyBobLayer3D gives them: models.cpp RenderHUDModel turns
// yaw about y, then pitch about x, then roll about z (degrees), in the hand
// models' frame before the MODELDEF scale (x left, y up, z back). A turn is
// kept as the three rows of its matrix.
class RSQ_Turn abstract
{
	clearscope static Vector3, Vector3, Vector3 Rows(Vector3 a)
	{
		double cx = cos(a.x), sx = sin(a.x);
		double cy = cos(a.y), sy = sin(a.y);
		double cz = cos(a.z), sz = sin(a.z);
		return (cx * cz + sx * sy * sz, -cx * sz + sx * sy * cz, sx * cy),
			(cy * sz, cy * cz, -sy),
			(-sx * cz + cx * sy * sz, sx * sz + cx * sy * cz, cx * cy);
	}

	clearscope static Vector3 Angles(Vector3 r0, Vector3 r1, Vector3 r2)
	{
		return (atan2(r0.z, r2.z), asin(clamp(-r1.z, -1., 1.)), atan2(r1.x, r1.y));
	}

	// the rows of a * b
	clearscope static Vector3, Vector3, Vector3 Mul(Vector3 a0, Vector3 a1, Vector3 a2, Vector3 b0, Vector3 b1, Vector3 b2)
	{
		Vector3 c0 = (b0.x, b1.x, b2.x);
		Vector3 c1 = (b0.y, b1.y, b2.y);
		Vector3 c2 = (b0.z, b1.z, b2.z);
		return (a0 dot c0, a0 dot c1, a0 dot c2), (a1 dot c0, a1 dot c1, a1 dot c2), (a2 dot c0, a2 dot c1, a2 dot c2);
	}

	// v turned back (by the transpose)
	clearscope static Vector3 Back(Vector3 r0, Vector3 r1, Vector3 r2, Vector3 v)
	{
		return r0 * v.x + r1 * v.y + r2 * v.z;
	}

	// Where a gun-side hand goes, and how it turns, so that it stays where it
	// holds the gun. hook / hookTurn: its place on the gun at rest (the hand
	// table). gunTurn: the gun layer's turn, about pivot (the gun model's turning
	// point from the hands'). frameTurn / frameMove: how the gun's model frame
	// has moved it off its ready frame. rsq_gunmoves_gen.py checks this against
	// RenderHUDModel's chain.
	clearscope static Vector3, Vector3 Place(Vector3 hook, Vector3 hookTurn, Vector3 gunTurn, Vector3 frameTurn, Vector3 frameMove, Vector3 pivot)
	{
		Vector3 q0, q1, q2, k0, k1, k2, h0, h1, h2, a0, a1, a2, e0, e1, e2;
		[q0, q1, q2] = Rows(gunTurn);
		[k0, k1, k2] = Rows(frameTurn);
		[h0, h1, h2] = Rows(hookTurn);
		[a0, a1, a2] = Mul(q0, q1, q2, k0, k1, k2);
		[e0, e1, e2] = Mul(a0, a1, a2, h0, h1, h2);
		Vector3 v = frameMove + Back(k0, k1, k2, Back(q0, q1, q2, pivot) - pivot);
		return hook + Back(h0, h1, h2, v), Angles(e0, e1, e2);
	}
}
