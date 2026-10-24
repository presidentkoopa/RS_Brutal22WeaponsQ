// Options that are weapon FLAGS rather than behaviour, held from a cvar each tic.
//
// +WEAPON.NOAUTOFIRE is a DECORATE flag: it is baked into the actor and there is no way to
// turn it off from a menu. But bNoAutoFire is a plain field, so a handler can hold it at
// whatever the player chose -- which is how rsq/fists.zs already keeps bNoHandSwitch on the
// fists weapon. Nothing here is VR-only; a semi-auto rifle is semi-auto on the desktop too.
class RSQ_Ruger : EventHandler
{
	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			class<Inventory> c = 'Sniper';
			let w = c ? Weapon(mo.FindInventory(c)) : null;
			if (!w)
				continue;
			// default ON: the Mini-14 Ranch is a semi-automatic rifle
			w.bNoAutoFire = RSQ.PlayerInt(mo, 'rsq_ruger_semi', 1) != 0;
		}
	}
}
