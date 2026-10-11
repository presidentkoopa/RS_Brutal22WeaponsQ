// TEST ONLY: stands in for zscript/rsvr/vrhand.zs. The gun hand 16 units in
// front of the player at chest height; the off hand is a "player" that does
// each reload step (rsqtest_mode 1) or keeps still beside the gun (mode 0).
class RSVR_VRHand play
{
	static bool InVR(PlayerPawn mo) { return mo && mo.player; }

	static Vector3 HandPos(PlayerPawn mo)
	{
		return mo.pos + (cos(mo.angle) * 16, sin(mo.angle) * 16, 40);
	}

	static Vector3 OffPos(PlayerPawn mo)
	{
		let cv = CVar.FindCVar('rsqtest_mode');
		int mode = cv ? cv.GetInt() : 0;
		Vector3 p = (0.02, 0.10, -0.06);			// resting beside the gun
		if (mode == 2)
			p = RSQ_HandTable.SupportPoint(RSQ_HandTable.Index(mo.player.ReadyWeapon));
		let s = RSQ_Handler.StateOf(mo);
		if (mode == 1 && s && s.kind)
		{
			Vector3 away = (-0.10, 0.45, -0.35);
			int t = mo.Level.maptime - s.waitStart;
			switch (s.kind)
			{
			case RSQ.FETCH:	p = t > 6 ? away : p; break;
			case RSQ.INSERT: p = !s.carry ? away : (t > 4 ? RSQ_Guns.Well(s.gun) : away); break;
			case RSQ.RACK:	p = RSQ_Guns.Handle(s.gun) - (s.armed ? (0.02 * min(t, 6), 0, 0) : (0, 0, 0)); break;
			case RSQ.SHELL:	p = s.shells > 0 ? RSQ_Guns.Well(s.gun) : away; break;
			}
		}
		return RSQ.WorldPoint(mo, p);
	}

	static Vector3 HandDir(PlayerPawn mo, double yaw, double pitch, double ps)
	{
		double a = mo.angle + yaw;
		return (cos(pitch) * cos(a), cos(pitch) * sin(a), sin(pitch));
	}
}

class RSQ_TestLog : EventHandler
{
	override void WorldTick()
	{
		let mo = players[0].mo;
		if (!mo || Level.maptime % 35)
			return;
		let w = mo.player.ReadyWeapon;
		let psp = mo.player.FindPSprite(PSP_WEAPON);
		Console.Printf("t%d %s state %s | Rifle %d Clip %d | Shotgun %d Shells %d | Pistol %d | hands %s off %s",
			Level.maptime, w ? w.GetClassName() : 'none', psp && psp.CurState ? psp.CurState.DistanceTo(w ? w.FindState("Ready") : null) .. "" : "-",
			mo.CountInv('RifleAmmo'), mo.CountInv('Clip1'), mo.CountInv('ShotgunAmmo'), mo.CountInv('AmmoShell'),
			mo.CountInv('BDPistolAmmo'),
			mo.FindInventory('RSQ_Hands') ? "yes" : "no", mo.player.OffhandWeapon ? mo.player.OffhandWeapon.GetClassName() : 'none');
		let s = RSQ_Handler.StateOf(PlayerPawn(mo));
		String lay = "";
		for (int id = 2100; id <= 2200; id += 1)
		{
			if (id == 2102) id = 2200;
			let q = mo.player.FindPSprite(id);
			lay = lay .. String.Format(" %d:%s", id, !q ? "-" : q.Sprite == Actor.GetSpriteIndex('TNT1') ? "hidden" : String.Format("spr%d/%c", int(q.Sprite), 65 + q.Frame));
		}
		Console.Printf("   holding %d layers%s", s ? s.holding : -1, lay);
		let b = RSQ_Ballistics.Get();
		if (b)
			Console.Printf("   ballistics: debris %d tracers %d", b.liveDebris, b.liveTracers);
	}
}
