// RS immersive reload on QuestZDoom 17.x (no engine changes), for BD22 and for
// Vanilla VR Plus.
//
// The set's own reload animations run as they always did. At a few points in
// each one (tool/weapon_patch.py GATES for BD22, tool/vplus/vplus_patch.py for
// Vanilla VR Plus) the gun asks RSQ_Gate whether the player's hand has done
// that step:
//   FETCH   the off hand goes away from the gun (to the belt for a magazine)
//   INSERT  the off hand comes back to the magazine well / breech
//   RACK    the off hand takes the slide / bolt / pump and pulls it back
//   SHELL   one shell into the tube or cylinder per pass; the hand goes away
//           for more after rsq_shells of them
// Pressing reload again during a pause does that step for you.
// With rsq_reload 0 (the default), or when not playing in VR, every gate
// answers yes at once and costs no time: the set's stock reloading.
//
// Positions are the gun hand's frame in metres: x forward along the gun,
// y to the left, z up, measured from the weapon controller (rsq/guns.zs).

class RSQ abstract play
{
	const FETCH = 1;
	const INSERT = 2;
	const RACK = 3;
	const SHELL = 4;

	// what the off hand is holding (rsq/hands.zs AmmoB..AmmoH): 0 nothing
	const AMMO_PISTOL = 1;
	const AMMO_SHELL = 2;
	const AMMO_SHELLS = 3;
	const AMMO_RIFLE = 4;
	const AMMO_ROCKET = 5;
	const AMMO_CELL = 6;
	const AMMO_FIST = 7;

	const AWAY = 0.28;		// the hand has gone for ammo
	const NEAR = 0.13;		// the hand is at the marker (magazine well / port)
	const GRAB = 0.12;		// the hand is on the slide / bolt / pump
	const LETGO = 0.25;		// ...and has let go of it
	const PULL = 0.06;		// how far back a rack has to go
	const SESSION_GAP = 50;	// tics with no pause before a reload counts as over

	static int PlayerInt(PlayerPawn mo, Name n, int def)
	{
		let cv = CVar.GetCVar(n, mo.player);
		return cv ? cv.GetInt() : def;
	}

	static double Float(Name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	static bool Immersive(PlayerPawn mo)
	{
		return mo && mo.player && PlayerInt(mo, 'rsq_reload', 0) != 0 && RSVR_VRHand.InVR(mo);
	}

	// the off hand in the gun hand's frame, metres (forward, left, up)
	static Vector3 OffLocal(PlayerPawn mo)
	{
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		double vu = Float('vr_vunits_per_meter', 34);
		if (vu <= 0)
			vu = 34;
		Vector3 f = RSVR_VRHand.HandDir(mo, 0, 0, ps);
		Vector3 l = RSVR_VRHand.HandDir(mo, 90, 0, ps);
		Vector3 u = RSVR_VRHand.HandDir(mo, 0, 90, ps);
		Vector3 d = RSVR_VRHand.OffPos(mo) - RSVR_VRHand.HandPos(mo);
		d.z *= ps;
		d /= vu;
		return (d dot f, d dot l, d dot u);
	}

	// a point in the gun hand's frame (metres: forward, left, up) -> world
	static Vector3 WorldPoint(PlayerPawn mo, Vector3 p)
	{
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		double vu = Float('vr_vunits_per_meter', 34);
		if (vu <= 0)
			vu = 34;
		Vector3 w = RSVR_VRHand.HandDir(mo, 0, 0, ps) * p.x + RSVR_VRHand.HandDir(mo, 90, 0, ps) * p.y
			+ RSVR_VRHand.HandDir(mo, 0, 90, ps) * p.z;
		w.z /= ps;
		return RSVR_VRHand.HandPos(mo) + w * vu;
	}

	// where to put the hand: a small glowing point, like Ermac's markers
	static void Marker(PlayerPawn mo, Vector3 p, Color c)
	{
		FSpawnParticleParams m;
		m.color1 = c;
		m.style = STYLE_Add;
		m.flags = SPF_FULLBRIGHT;
		m.lifetime = 2;
		m.size = 3.0;
		m.sizestep = 0;
		m.startalpha = 0.9;
		m.fadestep = 0;
		m.pos = WorldPoint(mo, p);
		mo.Level.SpawnParticle(m);
	}

	// a short buzz in the off hand: the engine buzzes the hand a projectile
	// leaves from (p_mobj.cpp P_SpawnPlayerMissile, ALF_ISOFFHAND)
	static void Buzz(PlayerPawn mo)
	{
		mo.SpawnPlayerMissile('RSVR_Buzz', mo.angle, noautoaim: true, aimflags: ALF_ISOFFHAND);
	}
}

// one player's reload
class RSQ_State play
{
	int lastGate;		// maptime a gate last asked
	int kind;			// the step being waited on (0: none)
	int gun;
	int waitStart;
	int carry;
	int shells;			// shells / rounds still in the hand
	bool armed;			// RACK: on the handle
	double armX;		// RACK: furthest forward while on it
	bool prevDown;
	int pressTic;		// when reload was last pressed
	int usedPress;
	int eatUntil;		// BD22's Reloading token is taken until then
	bool eating;
	bool holding;		// the off hand is holding the front of the gun (rsq/hands.zs)

	void NewSession()
	{
		kind = 0;
		carry = 0;
		shells = 0;
		armed = false;
	}

	// every tic, from RSQ_Handler.WorldTick
	void Tick(PlayerPawn mo, int now)
	{
		bool down = mo.player && (mo.player.cmd.buttons & BT_RELOAD);
		if (down && !prevDown)
			pressTic = now;
		prevDown = down;

		// a press used to skip a step must not also make BD22 start another
		// reload (or its inspect animation) once this one ends: BD22's ACS
		// turns the reload button into its "Reloading" token. Looked up by
		// name, so the same script runs on sets without it.
		if (eating)
		{
			if (now <= eatUntil || down)
			{
				String tn = "Reloading";
				class<Inventory> tok = tn;
				if (tok)
					mo.TakeInventory(tok, 999);
			}
			else
				eating = false;
		}

		if (kind && now - lastGate > 1)
			kind = 0;							// passed, or the gun went elsewhere
		if (now - lastGate > RSQ.SESSION_GAP)
			NewSession();						// put the ammo back
	}

	bool Skip(int now)
	{
		if (pressTic < waitStart || pressTic == usedPress)
			return false;
		usedPress = pressTic;
		eating = true;
		eatUntil = now + 20;
		return true;
	}

	// is the step done?
	bool Step(PlayerPawn mo)
	{
		Vector3 off = RSQ.OffLocal(mo);
		double dWell = (off - RSQ_Guns.Well(gun)).Length();
		switch (kind)
		{
		case RSQ.FETCH:
			if (dWell > RSQ.AWAY)
			{
				carry = RSQ_Guns.Carry(gun);
				RSQ.Buzz(mo);
				return true;
			}
			return false;

		case RSQ.INSERT:
			if (carry == 0)
			{
				// reached without a FETCH (after unloading): the hand still
				// has to go and get the ammo
				if (dWell > RSQ.AWAY)
				{
					carry = RSQ_Guns.Carry(gun);
					RSQ.Buzz(mo);
				}
				return false;
			}
			if (dWell < RSQ.NEAR)
			{
				carry = 0;
				RSQ.Buzz(mo);
				return true;
			}
			return false;

		case RSQ.RACK:
		{
			double dh = (off - RSQ_Guns.Handle(gun)).Length();
			if (!armed)
			{
				if (dh < RSQ.GRAB)
				{
					armed = true;
					armX = off.x;
					RSQ.Buzz(mo);
				}
				return false;
			}
			if (dh > RSQ.LETGO)
			{
				armed = false;
				return false;
			}
			armX = max(armX, off.x);
			if (armX - off.x >= RSQ.PULL)
			{
				armed = false;
				RSQ.Buzz(mo);
				return true;
			}
			return false;
		}

		case RSQ.SHELL:
			if (shells <= 0)
			{
				carry = 0;
				if (dWell > RSQ.AWAY)
				{
					shells = clamp(RSQ.PlayerInt(mo, 'rsq_shells', 2), 1, 8);
					carry = RSQ_Guns.Carry(gun);
					RSQ.Buzz(mo);
				}
				return false;
			}
			if (dWell < RSQ.NEAR)
			{
				shells--;
				if (shells <= 0)
					carry = 0;
				RSQ.Buzz(mo);
				return true;
			}
			return false;
		}
		return true;
	}

	static String KindName(int k)
	{
		static const String names[] = { "", "FETCH", "INSERT", "RACK", "SHELL" };
		return k >= 0 && k < 5 ? names[k] : "?";
	}

	void Debug(PlayerPawn mo, int now)
	{
		if (RSQ.PlayerInt(mo, 'rsq_debug', 0) == 0 || (now - waitStart) % 7 != 0)
			return;
		Vector3 off = RSQ.OffLocal(mo);
		Console.Printf("rsq %s gun %d: off hand %.2f %.2f %.2f  well %.2f (away %.2f near %.2f)  handle %.2f%s  carry %d shells %d",
			KindName(kind), gun, off.x, off.y, off.z,
			(off - RSQ_Guns.Well(gun)).Length(), RSQ.AWAY, RSQ.NEAR,
			(off - RSQ_Guns.Handle(gun)).Length(), armed ? " (held)" : "", carry, shells);
	}
}

// what the gun gives itself at a pause; it never stays in the inventory
class RSQ_Gate : Inventory
{
	override bool TryPickup(in out Actor toucher)
	{
		let mo = PlayerPawn(toucher);
		if (mo)
			RSQ_Handler.Gate(mo, Amount);
		return false;
	}
}

class RSQ_Pass : RSVR_Token {}

class RSQ_Handler : EventHandler
{
	RSQ_State st[MAXPLAYERS];

	static RSQ_State StateOf(PlayerPawn mo)
	{
		let h = RSQ_Handler(EventHandler.Find('RSQ_Handler'));
		if (!h || !mo || !mo.player)
			return null;
		int n = mo.PlayerNumber();
		if (n < 0 || n >= MAXPLAYERS)
			return null;
		if (!h.st[n])
			h.st[n] = new('RSQ_State');
		return h.st[n];
	}

	static void Gate(PlayerPawn mo, int code)
	{
		let s = StateOf(mo);
		if (!s || !RSQ.Immersive(mo))
		{
			mo.GiveInventory('RSQ_Pass', 1);		// stock: go straight on
			return;
		}
		int now = mo.Level.maptime;
		int kind = code / 100;
		int gun = code % 100;
		if (now - s.lastGate > RSQ.SESSION_GAP)
			s.NewSession();
		if (s.kind != kind || s.gun != gun || now - s.lastGate > 1)
		{
			s.waitStart = now;
			s.armed = false;
		}
		s.lastGate = now;
		s.kind = kind;
		s.gun = gun;

		bool pass = s.Step(mo);
		if (!pass && s.Skip(now))
		{
			pass = true;
			if (kind == RSQ.FETCH)
				s.carry = RSQ_Guns.Carry(gun);
			else if (kind == RSQ.INSERT)
				s.carry = 0;
			else if (kind == RSQ.SHELL && s.shells > 0)
				s.shells--;
		}
		if (pass)
		{
			mo.GiveInventory('RSQ_Pass', 1);
			s.kind = 0;
			if (RSQ.PlayerInt(mo, 'rsq_debug', 0))
				Console.Printf("rsq %s gun %d done after %d tics", RSQ_State.KindName(kind), gun, now - s.waitStart);
		}
		else
		{
			s.Debug(mo, now);
			if (kind == RSQ.INSERT && s.carry || kind == RSQ.SHELL && s.shells > 0)
				RSQ.Marker(mo, RSQ_Guns.Well(gun), Color(120, 255, 140));
			else if (kind == RSQ.RACK && !s.armed)
				RSQ.Marker(mo, RSQ_Guns.Handle(gun), Color(255, 210, 90));
		}
	}

	override void WorldTick()
	{
		int now = Level.maptime;
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo)
				continue;
			let mo = players[i].mo;
			if (!st[i])
				st[i] = new('RSQ_State');
			st[i].Tick(mo, now);
			RSQ_Hands.Upkeep(mo);
		}
	}
}
