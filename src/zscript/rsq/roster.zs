// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
// 2026-10-27 (owner r3 item 20, "I don't need two revolvers and one shotvolver"): BD21's slug
// revolver (Revolver2) and its "Shotvolver Swap for Revolver" option are gone. The two revolvers are
// the Revolver (BrutalRevolver, the Moonlight) and the Shotvolver (BD22's own Revolver).
//
// 2026-10-27, the Moonlight (BrutalRevolver.dec):
//   * MAP SPAWNS (owner 19:40), menu "Moonlight Revolver", server cvar rsq_moonlight:
//     0 Off; 1 "50% Replaces Shotvolver"; 2 "Replaces Shotvolver". BD22 puts the Shotvolver in the
//     world only as RevolverSpawner (WeaponSpawners.dec: ShotgunSpawnerReplacer's revolver branch,
//     NewGunsSpawner's SpawnRevolver). Each RevolverSpawner spawn is replaced by the Moonlight's own
//     pickup (BrutalRevolver: the gun and its 6 rounds, as RevolverSpawner gives the Shotvolver and
//     6 shells) half the time (1) or every time (2). The Revolver CLASS is never replaced (the give
//     weapons cheat skips a replaced weapon, r4), so a Shotvolver thrown down by a player stays one.
//   * CAP (owner 19:06, "Our Moonlight is 36 total rounds. If we have 2, it goes up to 72"):
//     36 with one Moonlight; 72 while the player holds two -- the off-hand copy RSQ_Off_BrutalRevolver,
//     which dual.zs gives when a second one is picked up (BD22's rule for dual; BrutalRevolver is
//     +ALWAYSPICKUP, so the second is taken even with the reserve full). The cap is set on the player's
//     RevolverRounds every tic, so nothing else moves it: the backpack does NOT raise it (owner 19:40).
//   * ROUNDS ON MAPS (only while rsq_moonlight is not Off, owner 19:40): a bullet pickup placed by the
//     map -- any Clip2 (BD22's replacement of Doom's Clip, ednum 2007, and its subclasses: ClipBox2 for
//     the box, 2048, and EasyClip2, which is what the rig measured on MAP01 at skill 3) that is on the
//     map at tic 0, not dropped (a monster's drop, the player's start ammo) and not owned -- gets one
//     RevolverRounds beside it, 1 time in 4. The rounds share the spot, they replace nothing.
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

	int moonClips, moonSpawned;	// this map: map-placed Clip2 seen, RevolverRounds put beside them
	int revSpawns;			// this map: RevolverSpawner spawns kept as the Shotvolver

	static int MoonMode()
	{
		let cv = CVar.FindCVar('rsq_moonlight');
		return cv ? cv.GetInt() : 0;
	}

	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		Name n = e.Replacee.GetClassName();
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && n == 'MG42')
			e.Replacement = 'Machinegun';
		if (n == 'RevolverSpawner')
		{
			int mode = MoonMode();
			if (mode >= 2 || (mode == 1 && Random[RSQMoonGun](0, 1) == 0))
				e.Replacement = 'BrutalRevolver';
		}
	}

	static bool Debug(PlayerPawn mo)
	{
		let cv = CVar.GetCVar('rsr_debug', mo.player);
		return cv && cv.GetInt() != 0;
	}

	void Counts()
	{
		// what is in the world now, unowned: the Shotvolver's pickup and the Moonlight's
		int sv = 0, ml = 0, rr = 0;
		let it = ThinkerIterator.Create('Inventory');
		Inventory a;
		while (a = Inventory(it.Next()))
		{
			if (a.Owner)
				continue;
			Name n = a.GetClassName();
			if (n == 'RevolverSpawner' || n == 'Revolver')
				sv++;
			else if (n == 'BrutalRevolver')
				ml++;
			else if (n == 'RevolverRounds')
				rr++;
		}
		Console.Printf("RSQ moon: map %s, rsq_moonlight %d: in the world Shotvolver %d, Moonlight %d, RevolverRounds %d; "
			.. "RevolverSpawner spawns kept as the Shotvolver this map %d; map bullet pickups %d, RevolverRounds put beside %d",
			Level.MapName, MoonMode(), sv, ml, rr, revSpawns, moonClips, moonSpawned);
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

	override void WorldThingSpawned(WorldEvent e)
	{
		let a = e.Thing;
		if (!a)
			return;
		Name n = a.GetClassName();
		if (n == 'RevolverSpawner')
			revSpawns++;
		// the map's own Clip2 gets the Moonlight's rounds beside it, 1 in MOON_SPAWN_IN, while the option is on
		if (Level.maptime > 0 || !(a is 'Clip2') || a.bDropped || Inventory(a).Owner)
			return;
		moonClips++;
		if (MoonMode() == 0)
			return;
		if (Random[RSQMoonSpawn](1, MOON_SPAWN_IN) != 1)
			return;
		double ang = Random[RSQMoonSpawn](0, 359);
		Vector2 at = a.Vec2Angle(MOON_SPAWN_OFS, ang);
		let r = Actor.Spawn('RevolverRounds', (at, a.pos.z));
		if (!r)
			return;
		if (!r.TestMobjLocation() || abs(r.floorz - a.floorz) > 24)
			r.SetOrigin(a.pos, false);		// no room: on the Clip2's own spot
		r.SetZ(r.floorz);
		r.bAmbush = a.bAmbush;
		moonSpawned++;
	}
}
