// The sniper rifle is out of this pack: anything that would spawn it spawns BD22's rifle,
// and a player who is given it (spawner pickups, give all) gets the rifle instead.
// Class names are looked up at run time: BD22's classes are DECORATE, unseen when this compiles.
class RSQ_NoSniper : EventHandler
{
	class<Actor> Find(Name n) { return FindS(n); }
	static class<Actor> FindS(Name n) { class<Actor> c = n; return c; }

	override void CheckReplacement(ReplaceEvent e)
	{
		if (!e.Replacee) return;
		Name n = e.Replacee.GetClassName();
		if (n == 'Sniper')            e.Replacement = Find('Rifle');
		else if (n == 'PuristSniper') e.Replacement = Find('PuristRifle');
		else if (n == 'SniperAmmo')   e.Replacement = Find('Clip2');
		// BD22 swaps these four for pickup spawners, and give all skips any replaced weapon.
		// Keep them as themselves so give all / idkfa include them (maps place the spawners directly).
		else if (n == 'MG42' || n == 'Devastator' || n == 'NukeLauncher' || n == 'IncendiaryLauncher')
		{ e.Replacement = null; e.IsFinal = true; }	// null + final = no replacement (events.cpp)
	}

	override void WorldTick()
	{
		class<Inventory> sn = (class<Inventory>)(Find('Sniper'));
		class<Inventory> ps = (class<Inventory>)(Find('PuristSniper'));
		class<Inventory> rf = (class<Inventory>)(Find('Rifle'));
		class<Inventory> am = (class<Inventory>)(Find('Clip2'));
		if (!sn || !rf) return;
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo) continue;
			let mo = players[i].mo;
			bool had = mo.CountInv(sn) > 0 || (ps && mo.CountInv(ps) > 0);
			if (!had) continue;
			mo.TakeInventory(sn, 999);
			if (ps) mo.TakeInventory(ps, 999);
			if (mo.CountInv(rf) == 0)
			{
				mo.GiveInventory(rf, 1);
				if (am) mo.GiveInventory(am, 30);
			}
		}
	}
}

