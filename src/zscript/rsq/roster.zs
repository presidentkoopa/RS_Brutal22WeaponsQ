// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
// 2026-10-27 (owner r3 item 20, "I don't need two revolvers and one shotvolver"): BD21's slug
// revolver (Revolver2) and its "Shotvolver Swap for Revolver" option are gone. The two revolvers are
// the Revolver (BrutalRevolver, the Moonlight) and the Shotvolver (BD22's own Revolver).
//
// 2026-10-27, the Revolver's own rounds (RevolverRounds, BrutalRevolver.dec):
//   * CAP (owner 19:06, "Our Moonlight is 36 total rounds. If we have 2, it goes up to 72"):
//     36 with one Revolver; 72 once a SECOND Revolver has been picked up. The second one is seen
//     the way dual.zs sees a second gun (BD22's rule for dual): a BrutalRevolver world pickup
//     destroyed within reach of a player who already owned one (it is +ALWAYSPICKUP, so it is
//     taken even with the reserve full). That player gets RSQ_MoonPair, kept until death like any
//     inventory. The cap is set on the player's RevolverRounds every tic, so nothing else
//     (a backpack, BackpackMaxAmount) moves it; the backpack rule is the owner's open call.
//   * MAP SPAWNS: a bullet pickup placed by the map -- any Clip2 (BD22's replacement of Doom's Clip,
//     ednum 2007, and its subclasses: ClipBox2 for the box, 2048, and EasyClip2, which is what the rig
//     measured on MAP01 at skill 3) that is on the map at tic 0, not dropped (a monster's drop, the
//     player's start ammo) and not owned -- gets one RevolverRounds beside it, 1 time in 4. The rounds
//     share the spot, they replace nothing.
class RSQ_MoonPair : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE;
		+INVENTORY.UNTOSSABLE;
		+INVENTORY.QUIET;
	}
}

class RSQ_Roster : EventHandler
{
	const MOON_CAP_ONE = 36;	// owner 2026-10-27 19:06
	const MOON_CAP_TWO = 72;	// ...with two Revolvers
	const MOON_SPAWN_IN = 4;	// one RevolverRounds beside 1 in this many map-placed Clip2 (clips and bullet boxes)
	const MOON_SPAWN_OFS = 14.0;	// map units from the Clip2 (BD22's SMG spawner puts its Clip1 10, 10 off)

	bool hadMoon[MAXPLAYERS];	// owned a BrutalRevolver last tic
	int moonClips, moonSpawned;	// this map: map-placed Clip2 seen, RevolverRounds put beside them (debug line at tic 1)

	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && e.Replacee.GetClassName() == 'MG42')
			e.Replacement = 'Machinegun';
	}

	static bool Debug(PlayerPawn mo)
	{
		let cv = CVar.GetCVar('rsr_debug', mo.player);
		return cv && cv.GetInt() != 0;
	}

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			if (Level.maptime == 1 && Debug(mo))
				Console.Printf("RSQ moon: map %s: %d map-placed bullet pickups (Clip2 family), RevolverRounds put beside %d", Level.MapName, moonClips, moonSpawned);
			hadMoon[n] = mo.FindInventory('BrutalRevolver') != null;
			let am = mo.FindInventory('RevolverRounds');
			if (!am)
				continue;
			int cap = mo.CountInv('RSQ_MoonPair') > 0 ? MOON_CAP_TWO : MOON_CAP_ONE;
			if (am.MaxAmount != cap)
			{
				if (Debug(mo))
					Console.Printf("RSQ moon t%d: RevolverRounds cap %d -> %d (%s Revolver%s), holding %d", Level.maptime,
						am.MaxAmount, cap, cap == MOON_CAP_TWO ? "two" : "one", cap == MOON_CAP_TWO ? "s" : "", am.Amount);
				am.MaxAmount = cap;
				if (am.Amount > cap)
					am.Amount = cap;
			}
		}
	}

	// a Revolver world pickup taken by a player who already had one: the second Revolver
	override void WorldThingDestroyed(WorldEvent e)
	{
		let a = e.Thing;
		if (!a || a.GetClassName() != 'BrutalRevolver' || Inventory(a).Owner)
			return;
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo || !hadMoon[n])
				continue;
			let mo = players[n].mo;
			if (mo.Distance3D(a) > mo.radius + a.radius + 16 || mo.CountInv('RSQ_MoonPair') > 0)
				continue;
			mo.GiveInventory('RSQ_MoonPair', 1);
			if (Debug(mo))
				Console.Printf("RSQ moon t%d: second Revolver picked up", Level.maptime);
			break;
		}
	}

	// the map's own Clip2 gets the Revolver's rounds beside it, 1 in MOON_SPAWN_IN
	override void WorldThingSpawned(WorldEvent e)
	{
		let a = e.Thing;
		if (!a || Level.maptime > 0 || !(a is 'Clip2') || a.bDropped || Inventory(a).Owner)
			return;
		moonClips++;
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
