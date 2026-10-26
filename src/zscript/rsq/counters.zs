// counters.zs (1.97) -- magazine COUNTERS for guns Brutal Doom never reloads (MG42 belt drum,
// Flamethrower2 canister, Unmaker skull). BD22's firing and ammo are untouched: the counter
// mirrors the reserve going down shot by shot, and when it is empty the gun's Reload runs
// (actors/Weapons/*.dec, "posefix rsr"). The real VR reload (vreload.zs) swaps the part; on
// the seat the counter takes the reserve's count up to its capacity. Idle unless VR reloading
// is on (RSR.WantsHands), so with it off the guns are Brutal Doom's exactly.

class RSQ_Counters : EventHandler
{
	static const Name GUN[] = { 'MG42', 'Flamethrower2', 'IncendiaryLauncher', 'Machinegun', 'Unmaker', 'Devastator', 'NukeLauncher', 'HellishMissileLauncher', 'Minigun' };
	static const Name MAG[] = { 'RSQ_Mag_MG42', 'RSQ_Mag_Flamethrower2', 'RSQ_Mag_IncendiaryLauncher', 'RSQ_Mag_Machinegun', 'RSQ_Mag_Unmaker', 'RSQ_Mag_Devastator', 'RSQ_Mag_NukeLauncher', 'RSQ_Mag_HellishMissileLauncher', 'RSQ_Mag_Minigun' };
	static const Name RES[] = { 'Clip2', 'Gas', 'AmmoM202', 'Clip2', 'SoulAmmo', 'DevastatorAmmo', 'Nuke', 'MiniHellRocketAmmo', 'Clip2' };
	static const int CAP[] = { 100, 200, 6, 100, 60, 50, 1, 6, 100 };
	int lastRes[MAXPLAYERS][9];
	bool inited[MAXPLAYERS][9];

	override void WorldTick()
	{
		for (int pn = 0; pn < MAXPLAYERS; pn++)
		{
			if (!playeringame[pn]) continue;
			PlayerPawn mo = players[pn].mo;
			if (!mo) continue;
			M202Carry(mo);
			let w = players[pn].ReadyWeapon;
			for (int g = 0; g < GUN.Size(); g++)
			{
				class<Inventory> mag = MAG[g]; class<Inventory> res = RES[g];
				class<Inventory> empty = "RSQ_Empty_" .. GUN[g]; class<Inventory> fill = "RSQ_Fill_" .. GUN[g];
				class<Inventory> nomag = "RSQ_NoMag_" .. GUN[g];
				if (!mag || !res || !empty || !fill || !nomag) continue;
				bool held = w && w.GetClassName() == GUN[g];
				int r = mo.CountInv(res);
				if (!held || !RSR_ReloadHandler.WantsHands(mo) || !NonStdOn(mo))
				{
					mo.TakeInventory(empty, 1);
					// 1.99x "Reload Non-Standard Guns" off: no magazine left out of the gun either
					// (a reload switched off half way), and the counter starts again from the
					// reserve when it is switched back on
					if (held && !NonStdOn(mo))
					{
						mo.TakeInventory(nomag, 1);
						inited[pn][g] = false;
					}
					lastRes[pn][g] = r;
					continue;
				}
				if (!inited[pn][g])
				{
					inited[pn][g] = true;
					SetCount(mo, mag, min(CAP[g], r));
					mo.TakeInventory(nomag, 1);
				}
				int d = lastRes[pn][g] - r;
				if (d > 0)
					SetCount(mo, mag, max(0, mo.CountInv(mag) - d));
				if (mo.CountInv(fill) > 0)
				{
					mo.TakeInventory(fill, 1);
					SetCount(mo, mag, min(CAP[g], r));
					mo.TakeInventory(nomag, 1);
				}
				bool e = mo.CountInv(mag) <= 0 && r > 0;
				if (e) mo.GiveInventory(empty, 1); else mo.TakeInventory(empty, 1);
				lastRes[pn][g] = r;
			}
		}
	}

	// 1.99x (owner): "Reload Non-Standard Guns" (rsq_reload_nonstd). Non-standard = the guns in GUN[]:
	// Brutal Doom gives them no reload (parsed from brutal22test6: MG42, MiniGun, IncendiaryLauncher,
	// Unmaker, Devastator, NukeLauncher, HellishMissileLauncher have no Reload state; Flamethrower2's
	// "Reload" is only its dry-ready loop; the BD21 Machinegun's reloads only its grenade). Off: these
	// guns are Brutal Doom's -- no counter, no empty guard, and RSR_Start refuses them (vreload.zs).
	static bool IsNonStd(Weapon w)
	{
		if (!w)
			return false;
		// the same nine as GUN[] (a static function cannot read the handler's static array on 17.3)
		Name n = w.GetClassName();
		return n == 'MG42' || n == 'Flamethrower2' || n == 'IncendiaryLauncher' || n == 'Machinegun' || n == 'Unmaker'
			|| n == 'Devastator' || n == 'NukeLauncher' || n == 'HellishMissileLauncher' || n == 'Minigun';
	}

	// 1.99x (owner, 2026-10-26): "a player can carry 48 incendiary rockets". BD22 declares AmmoM202 with
	// Inventory.MaxAmount 4 and Ammo.BackpackMaxAmount 4 (brutal22test6 actors/Weapons/IncendiaryLauncher.dec),
	// and a pack cannot redefine BD22's actor. But the engine caps a pickup at the OWNED item's MaxAmount
	// (Ammo.HandlePickup), and a backpack only ever raises it (BackpackItem.CreateCopy: MaxAmount <
	// BackpackMaxAmount), so the owned item's field is the whole carry limit. It is set every tic, so it
	// holds after a backpack, a level change and a saved game (MaxAmount is saved; this repairs a save from
	// an older build). Always on, VR reloading or not: it is the carry limit, not the reload.
	// BackpackMaxAmount is LEFT AT BD22's 4 on purpose: BackpackItem.DetachFromOwner drops any ammo whose
	// MaxAmount EQUALS its BackpackMaxAmount back to the default (4) and cuts the rockets to 4, so 48/48
	// would lose 44 rockets whenever a backpack leaves the inventory. With 48/4 a backpack changes nothing,
	// so the carry is 48 with or without one. The cylinder stays 6 (CAP[]).
	const M202_CARRY = 48;
	static void M202Carry(PlayerPawn mo)
	{
		let am = Inventory(mo.FindInventory('AmmoM202'));
		if (am && am.MaxAmount < M202_CARRY)
			am.MaxAmount = M202_CARRY;
	}

	static bool NonStdOn(PlayerPawn mo)
	{
		return RSQ.PlayerInt(mo, 'rsq_reload_nonstd', 1) != 0;
	}

	static void SetCount(PlayerPawn mo, class<Inventory> it, int n)
	{
		int c = mo.CountInv(it);
		if (n > c) mo.GiveInventory(it, n - c);
		else if (n < c) mo.TakeInventory(it, c - n);
	}
}

class RSQ_Mag_MG42 : Inventory { Default { Inventory.MaxAmount 100; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_MG42 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_MG42 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_MG42 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 200; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Flamethrower2 : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_IncendiaryLauncher : Inventory { Default { Inventory.MaxAmount 6; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_IncendiaryLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_IncendiaryLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_IncendiaryLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Machinegun : Inventory { Default { Inventory.MaxAmount 100; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Machinegun : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Machinegun : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Machinegun : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Unmaker : Inventory { Default { Inventory.MaxAmount 60; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Unmaker : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Unmaker : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Unmaker : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Devastator : Inventory { Default { Inventory.MaxAmount 50; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Devastator : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Devastator : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Devastator : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_NukeLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_NukeLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_NukeLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_NukeLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_HellishMissileLauncher : Inventory { Default { Inventory.MaxAmount 6; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_HellishMissileLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_HellishMissileLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_HellishMissileLauncher : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Mag_Minigun : Inventory { Default { Inventory.MaxAmount 100; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_NoMag_Minigun : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Empty_Minigun : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
class RSQ_Fill_Minigun : Inventory { Default { Inventory.MaxAmount 1; +INVENTORY.UNDROPPABLE; +INVENTORY.UNTOSSABLE; +INVENTORY.QUIET } }
