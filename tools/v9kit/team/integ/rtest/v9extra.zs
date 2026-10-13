// TEST ONLY: the parts of the test driver that need v9's classes
class V9T_RSR abstract play
{
	static bool Idle(PlayerPawn mo)
	{
		let s = RSR_Handler.StateOf(mo);
		int n = mo.PlayerNumber();
		return (!s || s.phase == RSR.IDLE) && !RSB_Handler.Busy(n) && !RSP_Handler.Busy(n);
	}
}

// what RSQ_Hands.ModifyBobLayer3D gives the gun / support hand (called from ui as the
// renderer does), every frame the gun layer is kicked, else every 5 tics (v9t_hl 1)
class V9T_HandsLog : EventHandler
{
	ui int lastTic;

	// ------------------------------------------------------------------ recoil log
	override void RenderOverlay(RenderEvent e)
	{
		if (V9T_Driver.CVInt('v9t_hl', 0) == 0)
			return;
		int now = Level.maptime;
		if (now == lastTic)
			return;
		let mo = players[consoleplayer].mo;
		if (!mo)
			return;
		let h = RSQ_Hands(mo.FindInventory('RSQ_Hands'));
		let w = mo.player.ReadyWeapon;
		let g = mo.player.FindPSprite(PSP_WEAPON);
		if (!h || !w || !g)
			return;
		bool kicked = h.gunTurn != (0, 0, 0) || h.gunMove != (0, 0, 0) || h.nextMove != (0, 0, 0) || g.y != 32 || g.x != 0;
		if (now % 5 && !kicked)
			return;
		lastTic = now;
		Vector3 t0, r0, t1, r1;
		[t0, r0] = h.ModifyBobLayer3D((0, 0, 0), (0, 0, 0), RSQ_Layers.GUNHAND, e.FracTic);
		[t1, r1] = h.ModifyBobLayer3D((0, 0, 0), (0, 0, 0), RSQ_Layers.SUPPORT, e.FracTic);
		let f = mo.player.FindPSprite(RSQ_Layers.FREEHAND);
		let gh = mo.player.FindPSprite(RSQ_Layers.GUNHAND);
		Console.Printf("hl t%d %s %c%s gun@(%.1f,%.1f) turn(%.2f %.2f %.2f) move(%.2f %.2f %.2f) next(%.2f %.2f %.2f) | gun T(%.2f %.2f %.2f) R(%.2f %.2f %.2f) | sup T(%.2f %.2f %.2f) R(%.2f %.2f %.2f) | free y %.0f gunhand y %.0f",
			now, w.GetClassName(), 65 + g.Frame, kicked ? " K" : "", g.x, g.y,
			h.gunTurn.x, h.gunTurn.y, h.gunTurn.z, h.gunMove.x, h.gunMove.y, h.gunMove.z, h.nextMove.x, h.nextMove.y, h.nextMove.z,
			t0.x, t0.y, t0.z, r0.x, r0.y, r0.z, t1.x, t1.y, t1.z, r1.x, r1.y, r1.z,
			f ? f.y : -1, gh ? gh.y : -1);
	}
}
