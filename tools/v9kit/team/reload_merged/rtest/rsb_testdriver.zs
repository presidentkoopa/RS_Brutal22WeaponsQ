// RSR-BREAK, TEST ONLY: scripts the off hand and the gun hand through a break-open / revolver real
// VR reload (zscript/rsr/rsr_break.zs) on the desktop harness (rtest/vrhand_rsr.zs fakes the VR
// hands). The grip goes through the same path as a real key: an rsr_grip network event.
//
// rsbtest_script:
//   1 full: every empty chamber loaded (or the speedloader), then a flick shuts it
//   2 partial: rsbtest_chambers rounds (default 1), then a flick
//   3 sweeps: aiming sweeps and snap turns while it is open (it must stay open), then the off
//     hand pushes it shut
//   4 fumble: the first round let go of half way in (it drops), then a full load, then a flick
//   5 proximity: the hand goes through every chamber and onto the hinged part without a grab,
//     the gun hand turns slowly the closing way: nothing may happen; then a flick
//   6 trigger: no grip; the scenario holds +oh_attack (the off trigger) for the grab; then a flick
//   7 steady: the grip pressed 30 cm from the gun hand (the engine's steadying zone) must not
//     grab; then at the pouch (58 cm) it does; a full load; a flick
//   8 wrong way: a fast turn the OPENING way (must not close), a slow return, then a flick
class RSB_TestDriver : EventHandler
{
	Vector3 off;			// the off hand, gun frame cm
	Vector3 offR0, offR1, offR2;	// the off hand's turn (rows, in the gun hand's axes)
	Vector3 gunTurn;		// the gun hand: yaw left, pitch up, roll right (deg)
	bool grip, sentGrip;
	int at;
	int lastPhase, lastHand;
	int step;				// a step inside the script
	int stepTic;
	int holdUntil;
	String holdName;
	int loads;				// rounds this script has pushed home
	int fumbled;
	int target;				// the chamber the hand is going for
	int sweepTic;
	int closedAt;
	double pushAng0;
	int flickStep;			// 0 not yet, 1 holding, 2 turning

	const REST_F = -5.0;		// the off hand at rest, low and to the left (clear of the gun in the views)
	const REST_L = 14.0;
	const REST_U = -22.0;

	clearscope bool Active()
	{
		let cv = CVar.FindCVar('rsbtest_script');
		return cv && cv.GetInt() > 0;
	}

	override void WorldLoaded(WorldEvent e)
	{
		off = (REST_F, REST_L, REST_U);
		offR0 = (1, 0, 0);
		offR1 = (0, 1, 0);
		offR2 = (0, 0, 1);
	}

	// d turned in the gun hand's own axes: roll about F (L -> U), pitch about -L (F -> U), yaw about U (F -> L)
	clearscope static Vector3 TurnLocal(Vector3 v, Vector3 t)
	{
		double y = t.x, p = t.y, r = t.z;
		v = (v.x, v.y * cos(r) - v.z * sin(r), v.y * sin(r) + v.z * cos(r));
		v = (v.x * cos(p) - v.z * sin(p), v.y, v.x * sin(p) + v.z * cos(p));
		v = (v.x * cos(y) - v.y * sin(y), v.x * sin(y) + v.y * cos(y), v.z);
		return v;
	}

	bool Hold(int now, String name, int tics)
	{
		if (holdName == name)
			return now < holdUntil;
		holdName = name;
		holdUntil = now + tics;
		Console.Printf("HOLD %s t%d..t%d", name, now, holdUntil);
		return true;
	}

	bool MoveTo(Vector3 t, double stp)
	{
		Vector3 dv = t - off;
		double l = dv.Length();
		if (l <= stp)
		{
			off = t;
			at++;
			return true;
		}
		off += dv * (stp / l);
		at = 0;
		return false;
	}

	// turn the off hand so the round in it points along v (gun frame)
	void AimRound(int i, Vector3 v)
	{
		Vector3 u = RSB_Guns.HandTip(i) - RSB_Guns.HandBase(i);
		u = u.Unit();
		Vector3 w = u cross v;
		double s = w.Length();
		double ang = atan2(s, u dot v);
		if (s < 1e-6)
		{
			offR0 = (1, 0, 0);
			offR1 = (0, 1, 0);
			offR2 = (0, 0, 1);
			return;
		}
		Vector3 r0, r1, r2;
		[r0, r1, r2] = RSB.RotRows(w / s, ang);
		offR0 = r0;
		offR1 = r1;
		offR2 = r2;
	}

	Vector3 OffTurn(Vector3 p)
	{
		return (offR0 dot p, offR1 dot p, offR2 dot p);
	}

	// the off hand where the round's tip is at p (gun frame)
	Vector3 HandForTip(int i, Vector3 p)
	{
		return p - OffTurn(RSB_Guns.HandTip(i));
	}

	void TurnToward(Vector3 want, double degPerTic)
	{
		Vector3 d = want - gunTurn;
		double l = d.Length();
		if (l <= degPerTic)
			gunTurn = want;
		else
			gunTurn += d * (degPerTic / l);
	}

	// the flick: a quick turn the closing way about the hinge (pitch up / roll right), then back
	Vector3 ClosingTurn(int i, double deg)
	{
		Vector3 a = RSB_Guns.Axis(i);
		if (abs(a.y) > 0.5)
			return (0, a.y > 0 ? deg : -deg, 0);		// about -L: muzzle up
		return (0, 0, a.x < 0 ? deg : -deg);			// about +F: roll right
	}

	override void WorldTick()
	{
		let mo = players[0].mo;
		if (!mo)
			return;
		let cv = CVar.FindCVar('rsbtest_script');
		int script = cv ? cv.GetInt() : 0;
		let s = RSB_Handler.StateOf(mo);
		int now = Level.maptime;
		if (s && script > 0)
		{
			Script(mo, s, now, script);
			s.tR0 = offR0;
			s.tR1 = offR1;
			s.tR2 = offR2;
		}
		if (grip != sentGrip)
		{
			EventHandler.SendNetworkEvent("rsr_grip", grip ? 1 : 0, 443);
			sentGrip = grip;
		}
		if (s && (s.phase != lastPhase || s.hand != lastHand))
		{
			Log(mo, s, now, "change");
			lastPhase = s.phase;
			lastHand = s.hand;
		}
		else if (now % 35 == 0)
			Log(mo, s, now, "tick");
	}

	void Script(PlayerPawn mo, RSB_State s, int now, int script)
	{
		int i = s.gun;
		Vector3 rest = (REST_F, REST_L, REST_U);
		Vector3 pouch = (-15, 25, -50);
		if (s.phase == RSB.IDLE || s.phase == RSB.DONE)
		{
			grip = false;
			MoveTo(rest, 3);
			TurnToward((0, 0, 0), 4);
			if (s.phase == RSB.DONE)
				closedAt = now;
			step = 0;
			flickStep = 0;
			holdName = "";
			return;
		}
		if (s.phase == RSB.OPENING || s.phase == RSB.CLOSING)
			return;
		// OPEN
		if (step == 0)
		{
			if (Hold(now, "OPEN", 25))
				return;
			step = 1;
			target = -1;
		}
		loads = s.loadedNow;
		int want = script == 2 ? max(1, CVar.FindCVar('rsbtest_chambers').GetInt()) : 99;
		bool loadMore = s.AnyEmpty() && loads < want && script != 3 && script != 5 && script != 8;
		if (script == 3 && step < 50)
		{
			Sweeps(mo, s, now);
			return;
		}
		if (script == 5 && step < 50)
		{
			Proximity(mo, s, now);
			return;
		}
		if (script == 8 && step < 50)
		{
			WrongWay(mo, s, now);
			return;
		}
		if (script == 7 && step < 3)
		{
			// the grip 30 cm from the gun hand: the engine's steadying zone, not a grab
			Vector3 near = (-5, 20, -22);
			if (step == 1)
			{
				grip = false;
				if (MoveTo(near, 3) && at > 3)
				{
					grip = true;
					step = 2;
					stepTic = now;
				}
				return;
			}
			if (now - stepTic < 20)
				return;
			grip = false;
			step = 3;
			Console.Printf("STEADYTEST hand at %.0f cm: hand %s", off.Length(), RSB.HandName(s.hand));
			return;
		}
		if (script == 3 || script == 5 || script == 8)
		{
			if (script == 3)
			{
				Push(mo, s, now);
				return;
			}
			Flick(mo, s, now);		// the sub-test is done: now a real flick
			return;
		}
		if (loadMore || s.hand != RSB.FREE)
		{
			Load(mo, s, now, script);
			return;
		}
		Flick(mo, s, now);
	}

	// one round: to the pouch, grab, beside the gun (a look), behind the chamber, along the bore, home
	void Load(PlayerPawn mo, RSB_State s, int now, int script)
	{
		int i = s.gun;
		Vector3 pouch = (-15, 25, -50);
		bool trig = script == 6;
		switch (s.hand)
		{
		case RSB.FREE:
		case RSB.EMPTYLOADER:
			grip = false;
			if (fumbled == 1)
			{
				fumbled = 2;
				Console.Printf("FUMBLE hand free at t%d, dropped rounds %d", now, CountRounds());
			}
			offR0 = (1, 0, 0);
			offR1 = (0, 1, 0);
			offR2 = (0, 0, 1);
			if (MoveTo(pouch, 3) && at > 3 && !trig)
				grip = true;
			target = -1;
			return;

		case RSB.CARRY:
		{
			grip = !trig;
			if (target < 0)
			{
				for (int k = 0; k < s.nch; k++)
				{
					if (s.ch[k] == RSB.EMPTY)
					{
						target = k;
						break;
					}
				}
				step = 10;
			}
			if (target < 0)
				return;
			Vector3 b = s.BoreAt(target, s.theta);
			Vector3 tip = s.TipAt(target, s.theta);
			double dep = s.Depth(target);
			Vector3 behind = tip - b * (dep + 4);
			if (step == 10)
			{
				// up beside the gun, the round on view
				if (!MoveTo(HandForTip(i, behind + (0, 14, 4)), 3))
					return;
				if (Hold(now, "ROUND_IN_HAND" .. loads, 25))
					return;
				step = 11;
			}
			AimRound(i, b);
			if (step == 11)
			{
				if (MoveTo(HandForTip(i, behind), 2) && at > 2)
					step = 12;
				return;
			}
			MoveTo(HandForTip(i, tip - b * (dep - 1.0)), 1.0);		// in through the mouth, along the bore
			return;
		}

		case RSB.INSERT:
		{
			grip = !trig;
			int k = s.insCh;
			Vector3 b = s.BoreAt(k, s.theta);
			Vector3 tip = s.TipAt(k, s.theta);
			double dep = s.Depth(k);
			if (step < 20)
			{
				if (!MoveTo(HandForTip(i, tip - b * (dep * 0.5)), 1.0))
					return;
				if (Hold(now, "HALF_IN" .. loads, 20))
					return;
				step = 20;
				if (script == 4 && !fumbled)
				{
					fumbled = 1;
					grip = false;		// let go half way: it must drop
					Console.Printf("FUMBLE let go at t%d", now);
					return;
				}
			}
			if (fumbled == 1)
			{
				grip = false;		// still let go: the hand waits for it to drop
				return;
			}
			if (MoveTo(HandForTip(i, tip + b * 0.8), 1.0))
				step = 21;
			return;
		}
		}
	}

	void Flick(PlayerPawn mo, RSB_State s, int now)
	{
		int i = s.gun;
		grip = false;
		MoveTo((REST_F, REST_L, REST_U), 3);
		if (flickStep < 2)
		{
			flickStep = 1;
			if (Hold(now, "BEFORE_FLICK", 20))
				return;
			flickStep = 2;
			stepTic = now;
			Console.Printf("FLICK start t%d", now);
		}
		// 21 deg a tic (735 deg/s) the closing way for 4 tics
		int t = now - stepTic;
		if (t < 4)
			gunTurn = ClosingTurn(i, 21 * (t + 1));
		else
			TurnToward((0, 0, 0), 3);
	}

	// aiming: sweeps about every axis, both ways, at up to 250 deg/s, and snap turns; then it waits
	void Sweeps(PlayerPawn mo, RSB_State s, int now)
	{
		grip = false;
		if (step < 40)
		{
			step = 40;
			sweepTic = now;
			Console.Printf("SWEEPS start t%d", now);
		}
		int t = now - sweepTic;
		// one full, smooth period per axis (no jumps between them), 35 tics each:
		// yaw +-40 (peak 251 deg/s), pitch +-35 (220 deg/s), roll +-40 (251 deg/s); then a fast aim
		// snap the closing way (25 deg in 3 tics, 292 deg/s) and slowly back; snap turns at 50 / 90 / 120
		double ph = (t % 35) * 360.0 / 35;
		if (t < 35)
			gunTurn = (40 * sin(ph), 0, 0);
		else if (t < 70)
			gunTurn = (0, 35 * sin(ph), 0);
		else if (t < 105)
			gunTurn = (0, 0, 40 * sin(ph));
		else if (t < 140)
		{
			int u = t - 105;
			double d = u < 3 ? 8.33 * (u + 1) : max(0, 25.0 - 1.0 * (u - 2));
			gunTurn = ClosingTurn(s.gun, d);
		}
		else
			gunTurn = (0, 0, 0);
		if (t == 50 || t == 90 || t == 120)
		{
			mo.A_SetAngle(mo.angle + 45);
			Console.Printf("SNAPTURN t%d", now);
		}
		if (t >= 160)
		{
			step = 50;
			Console.Printf("SWEEPS done t%d: phase %s", now, RSB.PhaseName(s.phase));
		}
	}

	// the off hand meets the hinged part from its open side and pushes it through its arc
	void Push(PlayerPawn mo, RSB_State s, int now)
	{
		int i = s.gun;
		grip = false;
		gunTurn = (0, 0, 0);
		offR0 = (1, 0, 0);
		offR1 = (0, 1, 0);
		offR2 = (0, 0, 1);
		Vector3 a = RSB_Guns.Axis(i);
		Vector3 h = RSB_Guns.Hinge(i);
		Vector3 r0 = RSB_Guns.PushRef(i);
		double rho = (RSB_Guns.PushR0(i) + RSB_Guns.PushR1(i)) * 0.6;
		double edge = RSB_Guns.PushEdge(i, rho);
		if (edge < -900)
			edge = 10;
		double z = (RSB_Guns.PushZ0(i) + RSB_Guns.PushZ1(i)) * 0.5;
		if (step < 60)
		{
			step = 60;
			stepTic = now;
			Console.Printf("PUSH start t%d", now);
		}
		// the palm (RSR.PalmGrab in the off frame) goes just outside the part's open-side face,
		// then sweeps through the arc the way it closes, 3 deg a tic, to past shut
		double ang;
		if (step == 60)
		{
			ang = s.theta + edge + atan(2.0 / rho);
			Vector3 p = h + a * z + RSB.Turn(r0, a, ang) * rho;
			if (MoveTo(p - RSR.PalmGrab(), 3) && at > 5)
			{
				step = 61;
				stepTic = now;
				pushAng0 = ang;
				Console.Printf("PUSH on the part at t%d (%.0f deg open)", now, s.theta);
			}
			return;
		}
		ang = pushAng0 - 3.0 * (now - stepTic);
		ang = max(ang, edge - 8);
		Vector3 p = h + a * z + RSB.Turn(r0, a, ang) * rho;
		off = p - RSR.PalmGrab();
	}

	// through every chamber and onto the hinged part, no grab; the gun hand turns the closing way slowly
	void Proximity(PlayerPawn mo, RSB_State s, int now)
	{
		int i = s.gun;
		grip = false;
		if (step < 40)
		{
			step = 40;
			stepTic = now;
			target = 0;
		}
		int t = now - stepTic;
		gunTurn = ClosingTurn(i, min(40, t * 0.5));		// 17 deg/s
		int k = target;
		if (k < s.nch)
		{
			Vector3 b = s.BoreAt(k, s.theta);
			Vector3 tip = s.TipAt(k, s.theta);
			AimRound(i, b);
			if (step == 40 && MoveTo(HandForTip(i, tip - b * (s.Depth(k) + 3)), 3) && at > 3)
				step = 41;
			else if (step == 41 && MoveTo(HandForTip(i, tip + b), 1) && at > 5)
			{
				step = 40;
				target++;
			}
			return;
		}
		if (step < 45)
		{
			step = 45;
			stepTic = now;
		}
		// over the hinged part's open side
		Vector3 a = RSB_Guns.Axis(i);
		double rho = (RSB_Guns.PushR0(i) + RSB_Guns.PushR1(i)) * 0.6;
		double edge = RSB_Guns.PushEdge(i, rho);
		Vector3 p = RSB_Guns.Hinge(i) + a * (RSB_Guns.PushZ0(i) + RSB_Guns.PushZ1(i)) * 0.5 + RSB.Turn(RSB_Guns.PushRef(i), a, s.theta + edge - 20) * rho;
		MoveTo(p - RSR.PalmGrab(), 2);
		if (now - stepTic > 60)
		{
			step = 50;
			gunTurn = (0, 0, 0);
			Console.Printf("PROXIMITY done t%d: phase %s chambers live %d", now, RSB.PhaseName(s.phase), s.LiveCount());
		}
	}

	// a fast turn the OPENING way: it must stay open
	void WrongWay(PlayerPawn mo, RSB_State s, int now)
	{
		int i = s.gun;
		grip = false;
		if (step < 40)
		{
			step = 40;
			stepTic = now;
			Console.Printf("WRONGWAY start t%d", now);
		}
		int t = now - stepTic;
		if (t < 4)
			gunTurn = ClosingTurn(i, -21 * (t + 1));
		else
			TurnToward((0, 0, 0), 3);
		if (t > 40)
		{
			step = 50;
			Console.Printf("WRONGWAY done t%d: phase %s", now, RSB.PhaseName(s.phase));
		}
	}

	int CountRounds()
	{
		int n = 0;
		let it = ThinkerIterator.Create('RSB_Round');
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (!(a is 'RSB_Casing'))
				n++;
		}
		return n;
	}

	static int Cnt(Actor mo, String n)
	{
		class<Inventory> c = n;
		return c ? mo.CountInv(c) : -1;
	}

	static String Layer(PlayerInfo p, int id)
	{
		let q = p.FindPSprite(id);
		if (!q)
			return "-";
		String nm = "?";
		static const Name n[] = { 'TNT1', 'RBSG', 'RBSP', 'RBGG', 'RBGP', 'RBRG', 'RBRP', 'RBTG', 'RBTP', 'RBVG', 'RBVP', 'RBWG', 'RBWP', 'RQHN',
			'SHT2', 'SHTZ', 'REVO', 'REVL', 'GRLN', 'RQGS', 'RQSP' };
		for (int k = 0; k < n.Size(); k++)
		{
			if (q.Sprite == Actor.GetSpriteIndex(n[k]))
				nm = n[k];
		}
		return String.Format("%s/%c", nm, 65 + q.Frame);
	}

	void Log(PlayerPawn mo, RSB_State s, int now, String why)
	{
		let p = mo.player;
		let w = p.ReadyWeapon;
		let wp = p.FindPSprite(PSP_WEAPON);
		String st = "-";
		if (wp && w)
		{
			if (wp.CurState == w.FindState("RSB_Wait"))
				st = "RSB_Wait";
			else if (wp.CurState == w.FindState("Ready"))
				st = "Ready";
			else
			{
				st = String.Format("%+d", wp.CurState.DistanceTo(w.FindState("Ready")));
				static const String labs[] = { "Select", "RaiseReloading", "ResumeNormalRaise", "RaiseNoAmmo", "Reload", "Inspect", "Deselect", "Fire", "RSB_Stock" };
				for (int k = 0; k < labs.Size(); k++)
				{
					let ls = w.FindStateByString(labs[k]);
					if (ls)
						st = st .. String.Format(" %s%+d", labs[k], wp.CurState.DistanceTo(ls));
				}
				st = st .. String.Format(" tics %d", wp.Tics);
			}
		}
		String chs = "";
		if (s)
		{
			for (int k = 0; k < s.nch; k++)
				chs = chs .. (s.ch[k] == RSB.LIVE ? "L" : s.ch[k] == RSB.SPENT ? "S" : ".");
		}
		int rounds = 0, casings = 0;
		let it = ThinkerIterator.Create('RSB_Round');
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a is 'RSB_Casing')
				casings++;
			else
				rounds++;
		}
		Console.Printf("t%d %s [%s] %s state %s gun %s | phase %s hand %s theta %.1f s %.1f ch [%s] | off %.1f %.1f %.1f grip %d turn %.0f %.0f %.0f",
			now, why, holdName, w ? w.GetClassName() : 'none', st, Layer(p, PSP_WEAPON), s ? RSB.PhaseName(s.phase) : "?", s ? RSB.HandName(s.hand) : "?",
			s ? s.theta : 0, s ? s.s : 0, chs, off.x, off.y, off.z, grip, gunTurn.x, gunTurn.y, gunTurn.z);
		Console.Printf("   ammo SSGAmmo %d SSGAlt %d SSGLoaded %d AmmoShell %d | GLAmmo %d GLLoaded %d AmmoRocket %d | RevolverAmmo %d | VR_SSGAlt %d VR_SSGLoaded %d VR_Shell %d | VR_RevLoaded %d VR_RevLoaded2 %d Clip %d held %d %d | dropped %d thrown %d",
			Cnt(mo, "SSGAmmo"), Cnt(mo, "SSGAlt"), Cnt(mo, "SSGLoaded"), Cnt(mo, "AmmoShell"), Cnt(mo, "GLAmmo"), Cnt(mo, "GLLoaded"), Cnt(mo, "AmmoRocket"),
			Cnt(mo, "RevolverAmmo"), Cnt(mo, "VR_SSGAlt"), Cnt(mo, "VR_SSGLoaded"), Cnt(mo, "VR_Shell"), Cnt(mo, "VR_RevLoaded"), Cnt(mo, "VR_RevLoaded2"), Cnt(mo, "Clip"),
			Cnt(mo, "RSB_Held_VR_Revolver"), Cnt(mo, "RSB_Held_VR_Revolver2"), rounds, casings);
		Console.Printf("   layers 2105 %s 2106 %s 2107 %s 2108 %s 2109 %s 2110 %s | 2200 %s 2202 %s | 2100 %s",
			Layer(p, 2105), Layer(p, 2106), Layer(p, 2107), Layer(p, 2108), Layer(p, 2109), Layer(p, 2110), Layer(p, 2200), Layer(p, 2202), Layer(p, 2100));
	}
}
