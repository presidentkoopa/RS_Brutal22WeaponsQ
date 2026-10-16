// RS VR fists (2026-10-16, owner): one fist per hand, and they never change hands.
//   main hand   BD22's fists weapon (Melee_Attacks). Ermac's fist is drawn on it (hands.zs).
//   off hand    our off-hand weapon (RSQ_Hands, "Hands"): a fist whenever it is free. It is
//               also what does the immersive reloads, so the main gun keeps reloading by hand.
// A real punch with either controller lands BD22's own punch (MeleeStrikeNormal, or the
// berserk one), from the hand, the way the punch went. Only a fast, mostly forward blow counts,
// once per blow; the hand has to slow down before it can punch again.
// Neither fist can be moved to the other hand (WEAPON.NOHANDSWITCH).
// rsq_punch 0 turns the real punches off. Out of VR nothing here does anything.
class RSQ_Fists : EventHandler
{
	RSQ_FistHand mainH[MAXPLAYERS];
	RSQ_FistHand offH[MAXPLAYERS];

	static Class<Actor> Cls(Name n) { class<Actor> c = n; return c; }

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			let p = mo.player;

			// the fists weapon stays in the main hand
			class<Inventory> mc = (class<Inventory>)(Cls('Melee_Attacks'));
			let fw = mc ? Weapon(mo.FindInventory(mc)) : null;
			if (fw)
				fw.bNoHandSwitch = true;

			if (!mainH[n])
				mainH[n] = new('RSQ_FistHand');
			if (!offH[n])
				offH[n] = new('RSQ_FistHand');
			bool vr = RSVR_VRHand.InVR(mo) && p.playerstate == PST_LIVE && mo.health > 0
				&& RSQ.PlayerInt(mo, 'rsq_punch', 0) != 0;
			bool mainFist = vr && p.ReadyWeapon && fw && p.ReadyWeapon == fw;
			bool offFist = vr && p.OffhandWeapon is 'RSQ_Hands' && RSQ_Hands.OffFist(mo);
			mainH[n].Tick(mo, RSVR_VRHand.HandPos(mo), mainFist);
			offH[n].Tick(mo, RSVR_VRHand.OffPos(mo), offFist);
		}
	}
}

// 1.5 (owner: "constantly firing when I walk around"). 1.4 measured the hand in the world and took
// the body's movement out, which a turn (the hand swings round the player) and the controller's
// position landing a tic apart from the body's both defeat: walking and turning read as blows.
// Now the hand is measured IN THE BODY'S OWN FRAME (from the pawn, turned by the pawn's angle),
// so walking, strafing and turning move nothing. A blow must then be all of:
//   fast         over PUNCH m/s in the body frame;
//   forward      mostly along the body's forward axis;
//   a real jab   the hand has travelled JAB_LEN forward within the last few tics;
//   out in front the hand ends at least FRONT ahead of the body.
// After a blow the hand must come back (RECOCK towards the body) or go still before the next.
class RSQ_FistHand play
{
	const PUNCH = 2.5;		// m/s
	const CALM = 0.35;		// of PUNCH: this slow counts as still
	const FORWARD = 0.7;	// share of the blow along the body's forward axis
	const JAB_LEN = 0.15;	// m forward within the window: a jab, not a twitch
	const FRONT = 0.25;		// m ahead of the body when the blow lands
	const RECOCK = 0.08;	// m back towards the body re-arms the fist
	const HIST = 6;			// tics of history (about 0.17 s)
	const REACH = 16.0;		// map units per tic the strike travels (it lives 2 tics)

	double fx[HIST], fy[HIST], fz[HIST];	// the hand in the body frame: forward, left, up
	int head, count;
	bool ready;
	double peak;			// forward reach at the last blow

	void Tick(PlayerPawn mo, Vector3 hand, bool on)
	{
		if (!on)
		{
			count = 0;
			ready = false;
			return;
		}
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		double vu = cv ? cv.GetFloat() : 34;
		if (vu <= 0)
			vu = 34;

		Vector3 d = hand - mo.pos;
		double c = cos(mo.angle), s = sin(mo.angle);
		double lf = d.x * c + d.y * s;
		double ll = -d.x * s + d.y * c;
		double lu = d.z;

		int prev = head;
		head = (head + 1) % HIST;
		fx[head] = lf; fy[head] = ll; fz[head] = lu;
		if (count < HIST)
		{
			count++;
			if (count < 2)
				return;
		}

		Vector3 v = (lf - fx[prev], ll - fy[prev], lu - fz[prev]);	// map units per tic, body frame
		double speed = v.Length();
		double thr = PUNCH * vu / 35.;

		if (!ready)
		{
			// re-arm: the hand has come back towards the body, or gone still
			if (speed < thr * CALM || lf < peak - RECOCK * vu)
				ready = true;
			return;
		}
		if (speed < thr || v.x / speed < FORWARD || lf < FRONT * vu)
			return;
		double back = lf;
		for (int i = 0; i < count; i++)
			back = min(back, fx[i]);
		if (lf - back < JAB_LEN * vu)
			return;

		ready = false;
		peak = lf;
		Vector3 dir = (v.x * c - v.y * s, v.x * s + v.y * c, v.z) / speed;	// back to the world

		Name sn = mo.CountInv('PowerStrength') > 0 ? 'MeleeStrike1Berserked' : 'MeleeStrikeNormal';
		class<Actor> sc = RSQ_Fists.Cls(sn);
		if (!sc)
			return;
		let a = Actor.Spawn(sc, hand, ALLOW_REPLACE);
		if (!a)
			return;
		a.target = mo;
		a.angle = VectorAngle(dir.x, dir.y);
		a.pitch = -asin(clamp(dir.z, -1, 1));
		a.vel = dir * REACH;
		mo.A_StartSound("Melee/Swing", CHAN_AUTO, CHANF_OVERLAP);
	}
}
