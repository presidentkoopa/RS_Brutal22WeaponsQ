// roster.zs (1.97) -- guns added to the BD22 roster with an option to stand in for a BD22 gun
// (c2q/bd22_mg.py). Off (default): both exist. On: every spawn of the BD22 gun is the added gun
// (map pickups, spawners, drops). Server cvars: the playsim must agree.
// 2026-10-27 (owner r3 item 20, "I don't need two revolvers and one shotvolver"): BD21's slug
// revolver (Revolver2) and its "Shotvolver Swap for Revolver" option are gone. The two revolvers are
// the Revolver (BrutalRevolver, the Moonlight) and the Shotvolver (BD22's own Revolver).
class RSQ_Roster : EventHandler
{
	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		let mg = CVar.FindCVar('rsq_mg_replaces_mg42');
		if (mg && mg.GetInt() != 0 && e.Replacee.GetClassName() == 'MG42')
			e.Replacement = 'Machinegun';
	}
}
