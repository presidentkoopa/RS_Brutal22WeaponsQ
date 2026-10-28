// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
// 2026-10-27 (owner r3 item 20, "I don't need two revolvers and one shotvolver"): BD21's slug
// revolver (Revolver2) and its "Shotvolver Swap for Revolver" option are gone. The two revolvers are
// the Revolver (BrutalRevolver, the Moonlight) and the Shotvolver (BD22's own Revolver).
//
// 2026-10-27, the Moonlight (BrutalRevolver.dec):
//   * Round 4 (owner 20:45: "Shotvolver and our Slug secondary shot are back. No slugvolver replaces shotvolver. New
//     option to have revolver replace brutal pistol, option to start with two."): the Shotvolver is never replaced.
//   * "Moonlight Replaces Pistol" (server rsq_moonlight_pistol, default Off): the Moonlight takes BD22's Brutal Pistol's
//     place everywhere. Map pistols and the pistol zombie's drop both arrive as BD22's PistolSpawner
//     (WeaponSpawners.dec PistolSpawnerReplacer; Dropables.dec DropedPistol's Death A_SpawnItem("PistolSpawner")), so
//     PistolSpawner is replaced by BrutalRevolver (the gun and its 6 rounds). A Brutal Pistol the player still gets
//     (the class start item, give, idkfa) is taken the tic it arrives and the Moonlight given instead (selected if the
//     pistol was in hand); the pistol's off-hand copy goes with it. Slot: the Moonlight is in slot 2, the pistol's.
//   * "Start With Two Moonlights" (server rsq_moonlight_two, default Off; needs the option above): when that swap
//     happens in the map's first second (a new game, a pistol start), the off-hand Moonlight comes too, both cylinders
//     full, and the Dual key is pressed once for the player, so both hands hold one.
//   * CAP (owner 19:06, "Our Moonlight is 36 total rounds. If we have 2, it goes up to 72"):
//     36 with one Moonlight; 72 while the player holds two -- the off-hand copy RSQ_Off_BrutalRevolver,
//     which dual.zs gives when a second one is picked up (BD22's rule for dual; BrutalRevolver is
//     +ALWAYSPICKUP, so the second is taken even with the reserve full) or the start above gives. The cap is
//     set on the player's RevolverRounds every tic, so nothing else moves it: the backpack does NOT raise it.
//   * ROUNDS ON MAPS (only while "Moonlight Replaces Pistol" is On): a bullet pickup placed by the
//     map -- any Clip2 (BD22's replacement of Doom's Clip, ednum 2007, and its subclasses: ClipBox2 for
//     the box, 2048, and EasyClip2, which is what the rig measured on MAP01 at skill 3) that is on the
//     map at tic 0, not dropped and not owned -- gets one RevolverRounds beside it, 1 time in 4.
//   * `netevent rsq_moon_count` (or rsr_debug at tic 1) prints the counts: test and debug only.
class RSQ_SemiLockOff : Inventory
{
	// the off hand's RSQ_SemiLock (semiauto.zs): the off-hand Moonlight fires once per pull of the
	// off trigger (BT_OFFHANDATTACK); the lock goes when that trigger is let go
	Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET }
	override void DoEffect()
	{
		Super.DoEffect();
		if (Owner && Owner.player && !(Owner.player.cmd.buttons & BT_OFFHANDATTACK))
			Owner.TakeInventory("RSQ_SemiLockOff", 1);
	}
}

class RSQ_Roster : EventHandler
{
	const MOON_CAP_ONE = 36;	// owner 2026-10-27 19:06
	const MOON_CAP_TWO = 72;	// ...with two Moonlights
	const MOON_SPAWN_IN = 4;	// one RevolverRounds beside 1 in this many map-placed Clip2 (clips and bullet boxes)
	const MOON_SPAWN_OFS = 14.0;	// map units from the Clip2 (BD22's SMG spawner puts its Clip1 10, 10 off)

	const MINI_SPAWN_IN = 4;	// 2.0: one Minigun ammo box beside every map-placed bullet box and 1 in this many map-placed clips
	int miniSpawned;		// this map: Minigun ammo boxes put beside the map's Clip2
	int moonClips, moonSpawned;	// this map: map-placed Clip2 seen, RevolverRounds put beside them
	int pistolSwaps;		// this map: Brutal Pistols the player got that became the Moonlight
	bool wantDual[MAXPLAYERS];	// start with two: press the Dual key once the Moonlight is in hand

	static bool ServerBool(Name n)
	{
		let cv = CVar.FindCVar(n);
		return cv && cv.GetBool();
	}
	static bool MoonPistol() { return ServerBool('rsq_moonlight_pistol'); }
	static bool MoonTwo() { return ServerBool('rsq_moonlight_two'); }

	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		Name n = e.Replacee.GetClassName();
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && n == 'MG42')
			e.Replacement = 'Machinegun';
		if (n == 'PistolSpawner' && MoonPistol())
			e.Replacement = 'BrutalRevolver';	// map pistols and the pistol zombie's drop
	}

	static bool Debug(PlayerPawn mo)
	{
		let cv = CVar.GetCVar('rsr_debug', mo.player);
		return cv && cv.GetInt() != 0;
	}

	void Counts()
	{
		// what is in the world now, unowned: the pistol's pickup, the Shotvolver's and the Moonlight's
		int ps = 0, sv = 0, ml = 0, rr = 0;
		let it = ThinkerIterator.Create('Inventory');
		Inventory a;
		while (a = Inventory(it.Next()))
		{
			if (a.Owner)
				continue;
			Name n = a.GetClassName();
			if (n == 'PistolSpawner' || n == 'BrutalPistol')
				ps++;
			else if (n == 'RevolverSpawner' || n == 'Revolver')
				sv++;
			else if (n == 'BrutalRevolver')
				ml++;
			else if (n == 'RevolverRounds')
				rr++;
		}
		Console.Printf("RSQ moon: map %s, moonlight_pistol %d two %d: in the world Pistol %d, Shotvolver %d, Moonlight %d, "
			.. "RevolverRounds %d; pistols swapped for the Moonlight this map %d; map bullet pickups %d, RevolverRounds put beside %d, Minigun ammo boxes put beside %d",
			Level.MapName, MoonPistol(), MoonTwo(), ps, sv, ml, rr, pistolSwaps, moonClips, moonSpawned, miniSpawned);
	}

	override void NetworkProcess(ConsoleEvent e)
	{
		if (e.Name == "rsq_moon_count")
			Counts();
	}

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			if (Level.maptime == 1 && Debug(mo))
				Counts();
			if (MoonPistol() && mo.FindInventory('BrutalPistol'))	// exact class: not the off-hand copy, not the purist pistol
				SwapPistol(mo, n);
			if (wantDual[n])
			{
				let p = mo.player;
				if (p.ReadyWeapon && p.ReadyWeapon.GetClassName() == 'BrutalRevolver' && p.PendingWeapon == WP_NOCHANGE
					&& (p.WeaponState & WF_WEAPONREADY))
				{
					wantDual[n] = false;
					if (!RSQ_Dual.IsCopy(p.OffhandWeapon))
						mo.GiveInventory('StartDualWield', 1);	// dual.zs: the Dual key
				}
				else if (Level.maptime > 350)
					wantDual[n] = false;
			}
			let am = mo.FindInventory('RevolverRounds');
			if (!am)
				continue;
			bool two = mo.FindInventory('RSQ_Off_BrutalRevolver') != null;
			int cap = two ? MOON_CAP_TWO : MOON_CAP_ONE;
			if (am.MaxAmount != cap)
			{
				if (Debug(mo))
					Console.Printf("RSQ moon t%d: RevolverRounds cap %d -> %d (%s Moonlight%s), holding %d", Level.maptime,
						am.MaxAmount, cap, two ? "two" : "one", two ? "s" : "", am.Amount);
				am.MaxAmount = cap;
				if (am.Amount > cap)
					am.Amount = cap;
			}
		}
	}

	void SwapPistol(PlayerPawn mo, int n)
	{
		let p = mo.player;
		bool held = p.ReadyWeapon && p.ReadyWeapon.GetClassName() == 'BrutalPistol';
		mo.TakeInventory('BrutalPistol', 1);
		mo.TakeInventory('RSQ_Off_BrutalPistol', 1);
		bool had = mo.FindInventory('BrutalRevolver') != null;
		mo.GiveInventory('BrutalRevolver', 1);
		pistolSwaps++;
		bool start = Level.maptime < 35;
		if (start)
		{
			mo.SetInventory('BrutalRevolverCylinder', 6);	// a pistol start has the pistol loaded
			mo.SetInventory('RevolverRounds', 18);			// owner 2026-10-27 20:5x: a full cylinder + 18 spare (two: both full + 18)
		}
		if (start && MoonTwo())
		{
			mo.GiveInventory('RSQ_Off_BrutalRevolver', 1);
			mo.SetInventory('BrutalRevolverCylinderOff', 6);
			wantDual[n] = true;
		}
		if (held || start)
			mo.A_SelectWeapon('BrutalRevolver');
		if (Debug(mo))
			Console.Printf("RSQ moon t%d: Brutal Pistol -> Moonlight%s%s; cylinder %d, spare RevolverRounds %d", Level.maptime,
				had ? " (already had one)" : "", start && MoonTwo() ? ", start with two" : "",
				mo.CountInv('BrutalRevolverCylinder'), mo.CountInv('RevolverRounds'));
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		let a = e.Thing;
		if (!a)
			return;
		Name n = a.GetClassName();
		// the map's own Clip2 gets the Moonlight's rounds beside it, 1 in MOON_SPAWN_IN, while the option is on
		if (Level.maptime > 0 || !(a is 'Clip2') || a.bDropped || Inventory(a).Owner)
			return;
		moonClips++;
		// 2.0 (owner 2026-10-28): the Minigun's own pool (RSQ_MinigunAmmo, Minigun.dec). Its box goes beside the map's own
		// bullet pickups: EVERY bullet box (ClipBox2) and 1 in MINI_SPAWN_IN clips (Clip2 / EasyClip2). Always on.
		if (a is 'ClipBox2' || Random[RSQMiniSpawn](1, MINI_SPAWN_IN) == 1)
		{
			if (Beside(a, 'RSQ_MinigunAmmo', Random[RSQMiniSpawn](0, 359)))
				miniSpawned++;
		}
		if (!MoonPistol())
			return;
		if (Random[RSQMoonSpawn](1, MOON_SPAWN_IN) != 1)
			return;
		if (Beside(a, 'RevolverRounds', Random[RSQMoonSpawn](0, 359)))
			moonSpawned++;
	}
	// one pickup MOON_SPAWN_OFS map units from the map's Clip2, on the floor (on the Clip2's own spot if there is no room)
	static bool Beside(Actor a, class<Actor> cls, double ang)
	{
		Vector2 at = a.Vec2Angle(MOON_SPAWN_OFS, ang);
		let r = Actor.Spawn(cls, (at, a.pos.z));
		if (!r)
			return false;
		if (!r.TestMobjLocation() || abs(r.floorz - a.floorz) > 24)
			r.SetOrigin(a.pos, false);		// no room: on the Clip2's own spot
		r.SetZ(r.floorz);
		r.bAmbush = a.bAmbush;
		return true;
	}
}
