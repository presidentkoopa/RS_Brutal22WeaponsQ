// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
class RSQ_Roster : EventHandler
{
	// 1.97: the slug revolver (BD21 Revolver2) in place of BD22's Shotvolver, when the option is on
	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && e.Replacee.GetClassName() == 'MG42')
			e.Replacement = 'Machinegun';
		// r4: the swap is made on BD22's RevolverSpawner, NOT on the Revolver class. The engine's
		// give weapons cheat (player_cheat.zs) skips any weapon whose GetReplacement is not
		// itself, so replacing the class took the Revolver out of idkfa / give all whenever this
		// option was on -- and Revolver2 was CHEATNOTWEAPON, so the cheat gave neither gun. And
		// the class replacement never reached a map pickup anyway: RevolverSpawner, the only way
		// BD22 puts a revolver in a map (WeaponSpawners.dec), hands it over with
		// A_GiveInventory, which spawns NO_REPLACE. Not replaced: a Revolver placed directly by
		// its editor number 5874 (no Doom 2 map has one).
		let sv = CVar.FindCVar('rsq_slug_replaces_shotvolver');
		if (sv && sv.GetInt() != 0 && e.Replacee.GetClassName() == 'RevolverSpawner')
			e.Replacement = 'RSQ_ShotvolverSpawner';
	}
}
