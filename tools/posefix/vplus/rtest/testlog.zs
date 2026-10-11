// TEST ONLY: logs the Vanilla VR Plus guns' ammo, gate and layers every 7 tics
class RSQ_TestLog : EventHandler
{
	static String SprName(int spr)
	{
		static const Name names[] = { 'RIFL', 'RIFK', 'REVL', 'REVO', 'SHTG', 'SHT2', 'RQGS', 'RQSP', 'RQHN', 'TNT1', 'CHGG', 'SAWG', 'MISG', 'PLSG', 'BFGG', 'PUNG' };
		for (int i = 0; i < names.Size(); i++)
			if (Actor.GetSpriteIndex(names[i]) == spr)
				return names[i];
		return String.Format("#%d", spr);
	}

	override void WorldTick()
	{
		let mo = players[0].mo;
		if (!mo || Level.maptime % 7)
			return;
		let w = mo.player.ReadyWeapon;
		let psp = mo.player.FindPSprite(PSP_WEAPON);
		String st = "-";
		if (psp && psp.CurState)
			st = String.Format("%s%c", SprName(psp.CurState.sprite), 65 + psp.CurState.Frame);
		let s = RSQ_Handler.StateOf(PlayerPawn(mo));
		Console.Printf("t%d %s %s | rifle %d rev %d/%d shot %d ssg %d+%d | clip %d shell %d | gate %s carry %d shells %d hold %d",
			Level.maptime, w ? w.GetClassName() : 'none', st,
			mo.CountInv('VR_RifleLoaded'), mo.CountInv('VR_RevLoaded'), mo.CountInv('VR_RevLoaded2'),
			mo.CountInv('VR_ShotLoaded'), mo.CountInv('VR_SSGLoaded'), mo.CountInv('VR_SSGAlt'),
			mo.CountInv('Clip'), mo.CountInv('VR_Shell'),
			s ? RSQ_State.KindName(s.kind) : "?", s ? s.carry : -1, s ? s.shells : -1, s ? s.holding : -1);
		String lay = "";
		static const int ids[] = { 2100, 2101, 2200 };
		for (int k = 0; k < 3; k++)
		{
			let q = mo.player.FindPSprite(ids[k]);
			lay = lay .. String.Format(" %d:%s", ids[k], !q ? "-" : String.Format("%s%c", SprName(q.Sprite), 65 + q.Frame));
		}
		Console.Printf("   layers%s offhand %s pending %s owns hands %d", lay, mo.player.OffhandWeapon ? mo.player.OffhandWeapon.GetClassName() : 'none', mo.player.PendingWeapon ? mo.player.PendingWeapon.GetClassName() : 'nochange', mo.CountInv('RSQ_Hands'));
		let bb = RSQ_Ballistics.Get(); if (bb) Console.Printf("   ballistics: debris %d tracers %d", bb.liveDebris, bb.liveTracers);
		Console.Printf("   handler %d shown %d invr %d live %d hp %d", EventHandler.Find('RSQ_Handler') != null, RSQ_Hands.Shown(PlayerPawn(mo)), RSVR_VRHand.InVR(PlayerPawn(mo)), mo.player.playerstate == PST_LIVE, mo.health);
	}
}
