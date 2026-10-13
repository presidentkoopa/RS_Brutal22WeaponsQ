// RS VR melee for Brutal Doom v22 on QuestZDoom 17.3 (stock engine).
//
// Axe (BrutalAxe) and Dragonslayer (DSweap): swing the controller and the blade
// hits whatever it passes through. The hit is BD22's own attack actor (AxeAttack,
// AxeAttackNoDecal, DSAttack, DSAttack2) started at the point and height where
// the blade met the body, so BD22's gore rules decide the result: its blood
// actors mark a head or leg hit from the impact height, and the Saw / Cut deaths
// take heads, legs, arms or cut the body in half from there.
//
// Axe alt-fire: hold it, swing, let go -> BD22's thrown axe (ThrowedAxe, or
// ThrowedAxeStrong with berserk) leaves the hand with the hand's speed.
//
// The trigger keeps BD22's own chop. Outside VR nothing here does anything and
// the axe's alt-fire is BD22's sideways swing.

class RSVR_MeleeHandler : EventHandler
{
	RSVR_Hand hands[MAXPLAYERS];

	// rsvr_axe_keys: the weapon hand's grip arrives as a KEY, not a usercmd button, so its codes
	// become a synchronised event the same way rsr_grip_keys does in vreload.zs. Every machine
	// sees the same down and up, so readying a throw is never a local-only decision.
	bool keyDown[MAXPLAYERS];
	ui Array<int> axeKeys;
	ui String axeKeysFrom;
	ui bool keyIsDown;

	static bool KeyHeld(PlayerPawn mo)
	{
		let h = RSVR_MeleeHandler(EventHandler.Find('RSVR_MeleeHandler'));
		if (!h || !mo || !mo.player)
			return false;
		int n = mo.PlayerNumber();
		return n >= 0 && n < MAXPLAYERS && h.keyDown[n];
	}

	override void NetworkProcess(ConsoleEvent e)
	{
		if (e.Name != "rsvr_axe_grip")
			return;
		int n = e.Player;
		if (n >= 0 && n < MAXPLAYERS && playeringame[n])
			keyDown[n] = e.Args[0] != 0;
	}

	override bool InputProcess(InputEvent e)
	{
		if (e.Type != InputEvent.Type_KeyDown && e.Type != InputEvent.Type_KeyUp)
			return false;
		let me = players[consoleplayer];
		let cv = CVar.GetCVar('rsvr_axe_keys', me);
		String keys = cv ? cv.GetString() : "";
		if (keys != axeKeysFrom)
		{
			axeKeysFrom = keys;
			axeKeys.Clear();
			Array<String> w;
			keys.Split(w, " ", TOK_SKIPEMPTY);
			for (int j = 0; j < w.Size(); j++)
				axeKeys.Push(w[j].ToInt());
		}
		if (axeKeys.Size() == 0 || axeKeys.Find(e.KeyScan) == axeKeys.Size())
			return false;
		bool down = e.Type == InputEvent.Type_KeyDown;
		if (down == keyIsDown)
			return false;			// key repeat: only the edges are worth a net event
		keyIsDown = down;
		EventHandler.SendNetworkEvent("rsvr_axe_grip", down ? 1 : 0, e.KeyScan);
		return false;				// never eaten: the grip keeps whatever else it does
	}

	override void WorldTick()
	{
		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo)
				continue;
			if (!hands[i])
				hands[i] = new('RSVR_Hand');
			let mo = players[i].mo;
			hands[i].Tick(mo);
			// RSVR_AxeHold lets the axe's Ready state enter its hold loop from the grip. The
			// hold used to be reachable only from alt-fire, so no other button could ever ready
			// a throw however the cvars were set (owner, 2026-10-13: throwing should be hold and
			// release the grip). Only in VR: out of VR the axe keeps BD22's own sideways swing.
			bool want = RSVR_VRHand.InVR(mo) && RSVR_Hand.HoldDown(mo)
				&& mo.player.ReadyWeapon && RSVR_Hand.KindOf(mo) == RSVR_Hand.AXE;
			mo.SetInventory('RSVR_AxeHold', want ? 1 : 0);
		}
	}

	static RSVR_Hand HandOf(PlayerPawn mo)
	{
		let h = RSVR_MeleeHandler(EventHandler.Find('RSVR_MeleeHandler'));
		if (!h || !mo || !mo.player)
			return null;
		int n = mo.PlayerNumber();
		if (n < 0 || n >= MAXPLAYERS)
			return null;
		if (!h.hands[n])
			h.hands[n] = new('RSVR_Hand');
		return h.hands[n];
	}
}

class RSVR_Hand play
{
	const HIST = 6;
	const AXE = 1;
	const SWORD = 2;

	// swing speed (m/s at the blade's outer point, relative to the player's own
	// movement) that counts as a blow, and the slowest release that throws
	const AXE_SWING = 3.0;
	const SWORD_SWING = 3.5;
	const THROW_MIN = 2.5;
	const RISE = 0.55;			// of the blade's speed that may be upward before it is a backswing

	// rsvr_melee_swing scales how hard you have to swing; rsvr_melee_rise is how much of the
	// motion may point UP before it counts as raising the axe rather than striking with it.
	// Both are user cvars (CVARINFO.rsvr), read per player so a netgame cannot disagree.
	clearscope static double Cv(PlayerPawn mo, Name n, double def)
	{
		let cv = mo && mo.player ? CVar.GetCVar(n, mo.player) : CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	clearscope static int CvI(PlayerPawn mo, Name n, int def)
	{
		let cv = mo && mo.player ? CVar.GetCVar(n, mo.player) : CVar.FindCVar(n);
		return cv ? cv.GetInt() : def;
	}

	// Is the throw's hold input down? QuestZDoom has no usercmd bit for the WEAPON hand's grip,
	// so this takes either a button mask (rsvr_axe_hold, default BT_ALTATTACK, how it has always
	// worked) or raw key codes (rsvr_axe_keys), read the way vreload.zs reads rsr_grip_keys.
	static bool HoldDown(PlayerPawn mo)
	{
		if (!mo || !mo.player)
			return false;
		int mask = CvI(mo, 'rsvr_axe_hold', BT_ALTATTACK);
		if (mask != 0 && (mo.player.cmd.buttons & mask) != 0)
			return true;
		return RSVR_MeleeHandler.KeyHeld(mo);
	}

	// recent samples: blade outer point and player position, newest at [head]
	double tx[HIST];
	double ty[HIST];
	double tz[HIST];
	double px[HIST];
	double py[HIST];
	double pz[HIST];
	int count;
	int head;

	int kind;
	bool havePrev;
	Vector3 prevIn;
	Vector3 prevOut;
	Vector3 prevPos;
	double lastAngle;
	int settle;
	int swingTics;
	int calmTics;
	int whooshWait;
	int scrapeWait;
	bool inWall;
	Array<Actor> struck;

	// this tic's hand frame and view settings
	transient Vector3 fH;
	transient Vector3 fF;
	transient Vector3 fR;
	transient Vector3 fU;
	transient double vu;
	transient double ws;
	transient double ox;
	transient double oy;
	transient double oz;
	transient double ps;

	transient bool spritesSet;
	transient SpriteID sAXEG;
	transient SpriteID s1XEG;
	transient SpriteID s2XEG;
	transient SpriteID s3XEG;
	transient SpriteID s4XEG;
	transient SpriteID s5XEG;
	transient SpriteID sDSLA;

	//------------------------------------------------------------------
	// the blade, in the held model's own units (BrutalAxe.md3 frame 5 = AXEG A,
	// DSweap.md3 frame 0 = DSLA A; posefix/melee measurements)
	static Vector3 BladeIn(int k)
	{
		if (k == AXE)
			return (44, 0, 26);		// top of the axe head
		return (38, 0, 16);			// Dragonslayer: guard
	}

	static Vector3 BladeOut(int k)
	{
		if (k == AXE)
			return (55, 0, 16);		// the axe's cutting edge
		return (90, 0, 159);		// Dragonslayer: point
	}

	static Vector3 AxeHead()
	{
		return (50, 0, 20);
	}

	//------------------------------------------------------------------
	void InitSprites()
	{
		sAXEG = Actor.GetSpriteIndex('AXEG');
		s1XEG = Actor.GetSpriteIndex('1XEG');
		s2XEG = Actor.GetSpriteIndex('2XEG');
		s3XEG = Actor.GetSpriteIndex('3XEG');
		s4XEG = Actor.GetSpriteIndex('4XEG');
		s5XEG = Actor.GetSpriteIndex('5XEG');
		sDSLA = Actor.GetSpriteIndex('DSLA');
		spritesSet = true;
	}

	static int KindOf(PlayerPawn mo)
	{
		let p = mo.player;
		if (!p || !p.ReadyWeapon || p.PendingWeapon != WP_NOCHANGE || mo.health <= 0)
			return 0;
		Name n = p.ReadyWeapon.GetClassName();
		if (n == 'BrutalAxe')
			return AXE;
		if (n == 'DSweap')
			return SWORD;
		return 0;
	}

	// the weapon is in its held pose (AXEG A or a blood-colour copy, DSLA A):
	// the blade is where the model shows it
	bool ReadyPose(PlayerPawn mo, int k)
	{
		if (!spritesSet)
			InitSprites();
		let psp = mo.player.FindPSprite(PSP_WEAPON);
		if (!psp || psp.Frame != 0)
			return false;
		SpriteID s = psp.Sprite;
		if (k == SWORD)
			return s == sDSLA;
		return s == sAXEG || s == s1XEG || s == s2XEG || s == s3XEG || s == s4XEG || s == s5XEG;
	}

	static double CVarF(Name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	bool Frame(PlayerPawn mo)
	{
		if (!RSVR_VRHand.InVR(mo))
			return false;
		ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		fH = RSVR_VRHand.HandPos(mo);
		fF = RSVR_VRHand.HandDir(mo, 0, 0, ps);
		fR = -RSVR_VRHand.HandDir(mo, 90, 0, ps);
		fU = RSVR_VRHand.HandDir(mo, 0, 90, ps);
		vu = CVarF('vr_vunits_per_meter', 34);
		ws = CVarF('vr_weaponScale', 1.02);
		ox = CVarF('vr_3dweaponOffsetX', 0);
		oy = CVarF('vr_3dweaponOffsetY', 0);
		oz = CVarF('vr_3dweaponOffsetZ', 0);
		return true;
	}

	// a point of the held model -> world. Same chain as RenderHUDModel: hand,
	// scale .01, translate (0, 5, 30), model Scale -1 1 1 with ZOffset -5,
	// the jDoom 90 degree turn, vr_weaponScale; local x right, y up, -z forward.
	Vector3 Place(Vector3 m)
	{
		double f = 0.01 * (ws * m.x - 30 - oz);
		double r = 0.01 * (-ws * m.y + ox);
		double u = 0.01 * (ws * m.z + oy);
		Vector3 w = fF * f + fR * r + fU * u;
		w.z /= ps;
		return fH + w * vu;
	}

	void Push(Vector3 tip, Vector3 pos)
	{
		head = (head + 1) % HIST;
		tx[head] = tip.x;
		ty[head] = tip.y;
		tz[head] = tip.z;
		px[head] = pos.x;
		py[head] = pos.y;
		pz[head] = pos.z;
		if (count < HIST)
			count++;
	}

	void Reset()
	{
		count = 0;
		havePrev = false;
		swingTics = 0;
		calmTics = 0;
		inWall = false;
		struck.Clear();
	}

	//------------------------------------------------------------------
	void Tick(PlayerPawn mo)
	{
		if (whooshWait > 0)
			whooshWait--;
		if (scrapeWait > 0)
			scrapeWait--;

		int k = KindOf(mo);
		if (k != kind)
		{
			Reset();
			kind = k;
		}
		if (k == 0 || !ReadyPose(mo, k) || !Frame(mo))
		{
			Reset();
			return;
		}

		// a snap turn or a teleport moves the hand without a swing
		if (havePrev && (abs(Actor.deltaangle(lastAngle, mo.angle)) > 12 || (mo.pos - prevPos).Length() > 64))
			settle = 2;
		lastAngle = mo.angle;
		if (settle > 0)
		{
			settle--;
			Reset();
		}

		Vector3 bin = Place(BladeIn(k));
		Vector3 bout = Place(BladeOut(k));
		Push(bout, mo.pos);
		if (!havePrev)
		{
			prevIn = bin;
			prevOut = bout;
			prevPos = mo.pos;
			havePrev = true;
			return;
		}

		double thr = (k == AXE ? AXE_SWING : SWORD_SWING) * vu / 35.
			* max(0.2, Cv(mo, 'rsvr_melee_swing', 1.0));
		Vector3 vel = (bout - prevOut) - (mo.pos - prevPos);
		double speed = vel.Length();
		double power = speed / thr;

		// THE BACKSWING IS NOT A STRIKE. The test used to be speed alone, so raising the axe to
		// strike was itself a hit -- it landed before the player had swung, and read as the axe
		// being wildly oversensitive (owner, 2026-10-13). Motion that is mostly upward is the
		// player winding up, so it does not cut, and it falls through to the calm branch below
		// so the downswing that follows is a fresh swing with a cleared strike list.
		double rise = speed > 0 ? vel.z / speed : 0;
		bool backswing = rise > max(0.05, Cv(mo, 'rsvr_melee_rise', RISE));

		if (power >= 1 && !backswing)
		{
			calmTics = 0;
			swingTics++;
			if (swingTics == 1 && whooshWait == 0)
			{
				if (k == AXE)
					mo.A_StartSound("Axe/Swing", CHAN_WEAPON, CHANF_OVERLAP);
				else
					mo.A_StartSound("Melee/SwingStrong", CHAN_WEAPON, CHANF_OVERLAP);
				whooshWait = 12;
			}
			Sweep(mo, k, prevIn, prevOut, bin, bout, power);
		}
		else if (++calmTics > 2)
		{
			swingTics = 0;
			struck.Clear();
		}
		WallCheck(mo, bout, power);

		prevIn = bin;
		prevOut = bout;
		prevPos = mo.pos;
	}

	//------------------------------------------------------------------
	// the blade's path this tic (a0-b0 -> a1-b1) against every body near it;
	// each body is hit once per swing, at the first point the blade reaches it
	void Sweep(PlayerPawn mo, int k, Vector3 a0, Vector3 b0, Vector3 a1, Vector3 b1, double power)
	{
		double pad = (k == AXE) ? 3 : 5;
		Vector3 c = (a0 + b0 + a1 + b1) / 4;
		double r = max(max((a0 - c).Length(), (b0 - c).Length()), max((a1 - c).Length(), (b1 - c).Length())) + pad;
		double travel = max((b1 - b0).Length(), (a1 - a0).Length());
		int steps = clamp(int(travel / 4) + 1, 1, 16);
		int segs = (k == AXE) ? 2 : 8;

		Array<Actor> victims;
		Array<double> hx;
		Array<double> hy;
		Array<double> hz;
		Array<double> dx;
		Array<double> dy;
		Array<double> dz;
		let it = BlockThingsIterator.CreateFromPos(c.x, c.y, c.z - r, 2 * r, r, false);
		while (it.Next())
		{
			Actor t = it.thing;
			if (!t || t == mo || t.player || !t.bSHOOTABLE || t.bFRIENDLY || t.bDORMANT || t.health <= 0)
				continue;
			if (struck.Find(t) != struck.Size() || victims.Find(t) != victims.Size())
				continue;
			bool hit = false;
			Vector3 at = (0, 0, 0);
			Vector3 dir = (0, 0, 0);
			for (int i = 1; i <= steps && !hit; i++)
			{
				double f = double(i) / steps;
				for (int j = segs; j >= 0 && !hit; j--)
				{
					double s = double(j) / segs;
					Vector3 p0 = a0 + (b0 - a0) * s;
					Vector3 p1 = a1 + (b1 - a1) * s;
					Vector3 q = p0 + (p1 - p0) * f;
					if (Touches(t, q, pad))
					{
						hit = true;
						at = q;
						dir = p1 - p0;
					}
				}
			}
			if (!hit || !Clear(mo, fH, at))
				continue;
			victims.Push(t);
			hx.Push(at.x);
			hy.Push(at.y);
			hz.Push(at.z);
			dx.Push(dir.x);
			dy.Push(dir.y);
			dz.Push(dir.z);
		}

		// strike after the search: the hits spawn gore and kill things
		for (int i = 0; i < victims.Size(); i++)
		{
			Actor t = victims[i];
			if (!t || t.health <= 0)
				continue;
			struck.Push(t);
			Strike(mo, k, t, (hx[i], hy[i], hz[i]), (dx[i], dy[i], dz[i]), power);
		}
	}

	static bool Touches(Actor t, Vector3 q, double pad)
	{
		if (q.z < t.pos.z - pad || q.z > t.pos.z + t.height + pad)
			return false;
		double ddx = q.x - t.pos.x;
		double ddy = q.y - t.pos.y;
		double rr = t.radius + pad;
		return ddx * ddx + ddy * ddy <= rr * rr;
	}

	// nothing solid between the hand and that point
	static bool Clear(Actor mo, Vector3 from, Vector3 to)
	{
		Vector3 d = to - from;
		double len = d.Length();
		if (len < 1)
			return true;
		FLineTraceData tr;
		mo.LineTrace(VectorAngle(d.x, d.y), len, -asin(clamp(d.z / len, -1, 1)),
			TRF_ABSPOSITION | TRF_THRUACTORS, from.z, from.x, from.y, tr);
		return tr.HitType == TRACE_HitNone || tr.HitType == TRACE_HitActor;
	}

	void Strike(PlayerPawn mo, int k, Actor t, Vector3 at, Vector3 dir, double power)
	{
		// start BD22's attack just inside the body, at the height the blade met it
		double rx = at.x - t.pos.x;
		double ry = at.y - t.pos.y;
		double rl = sqrt(rx * rx + ry * ry);
		double lim = max(t.radius - 2, 1);
		if (rl > lim)
		{
			rx *= lim / rl;
			ry *= lim / rl;
		}
		Vector3 p = (t.pos.x + rx, t.pos.y + ry, clamp(at.z, t.pos.z + 1, t.pos.z + max(t.height - 1, 1)));
		double dl = dir.Length();
		if (dl > 0)
			dir = dir / dl;
		else
			dir = (cos(mo.angle), sin(mo.angle), 0);

		if (k == AXE)
		{
			Launch(mo, 'AxeAttack', p, dir);
			if (power >= 1.6)
				Launch(mo, 'AxeAttackNoDecal', p, dir);
			if (power >= 2.4)
				Launch(mo, 'AxeAttack', p, dir);
		}
		else
		{
			Launch(mo, 'DSAttack', p, dir);
			Launch(mo, 'DSAttack2', p, dir);
		}
		Buzz(mo);
	}

	// BD22's attack actor, fired by the player from that point
	static void Launch(PlayerPawn mo, Name cname, Vector3 p, Vector3 dir)
	{
		class<Actor> cls = cname;
		if (!cls)
			return;
		let a = Actor.Spawn(cls, p, ALLOW_REPLACE);
		if (!a)
			return;
		a.target = mo;
		a.angle = VectorAngle(dir.x, dir.y);
		a.pitch = -asin(clamp(dir.z, -1, 1));
		a.vel = dir * a.speed;
		a.CheckMissileSpawn(0);
	}

	// controller rumble: the engine buzzes the weapon hand when the player
	// fires a projectile (p_mobj.cpp P_SpawnPlayerMissile)
	static void Buzz(PlayerPawn mo)
	{
		mo.SpawnPlayerMissile('RSVR_Buzz', mo.angle, noautoaim: true);
	}

	// the blade going into a wall, floor or ceiling at speed: BD22's axe impact
	// (sparks and clang, or the floor's splash / dirt)
	void WallCheck(PlayerPawn mo, Vector3 bout, double power)
	{
		Vector3 d = bout - fH;
		double len = d.Length();
		bool blocked = false;
		Vector3 hitAt = (0, 0, 0);
		if (len > 1)
		{
			FLineTraceData tr;
			mo.LineTrace(VectorAngle(d.x, d.y), len, -asin(clamp(d.z / len, -1, 1)),
				TRF_ABSPOSITION | TRF_THRUACTORS, fH.z, fH.x, fH.y, tr);
			if (tr.HitType == TRACE_HitWall || tr.HitType == TRACE_HitFloor || tr.HitType == TRACE_HitCeiling)
			{
				blocked = true;
				hitAt = tr.HitLocation;
			}
		}
		if (blocked && !inWall && power >= 1 && scrapeWait == 0)
		{
			Vector3 dir = d / len;
			Launch(mo, 'AxeAttack', hitAt - dir * 6, dir);
			Buzz(mo);
			scrapeWait = 8;
		}
		inWall = blocked;
	}

	//------------------------------------------------------------------
	// axe alt-fire, called every tic of the hold by RSVR_AxeGrip
	static void Grip(PlayerPawn mo)
	{
		bool vr = RSVR_VRHand.InVR(mo);
		mo.SetInventory('RSVR_NotVR', vr ? 0 : 1);
		mo.SetInventory('RSVR_AxeThrown', 0);
		if (!vr)
			return;
		bool held = HoldDown(mo);
		mo.SetInventory('RSVR_AxeHolding', held ? 1 : 0);
		if (held)
			return;
		let h = RSVR_MeleeHandler.HandOf(mo);
		if (h && h.Throw(mo))
			mo.SetInventory('RSVR_AxeThrown', 1);
	}

	bool Throw(PlayerPawn mo)
	{
		if (KindOf(mo) != AXE || !Frame(mo))
			return false;

		// fastest step of the axe's edge over the last few tics: people slow
		// down as they let go
		Vector3 t1 = Place(BladeOut(AXE));
		Vector3 p1 = mo.pos;
		double best = 0;
		Vector3 vel = (0, 0, 0);
		int n = min(count, 4);
		for (int i = 0; i < n; i++)
		{
			int j = (head - i + HIST) % HIST;
			Vector3 t0 = (tx[j], ty[j], tz[j]);
			Vector3 p0 = (px[j], py[j], pz[j]);
			Vector3 v = t1 - t0;
			double rel = (v - (p1 - p0)).Length();
			if (rel > best)
			{
				best = rel;
				vel = v;
			}
			t1 = t0;
			p1 = p0;
		}
		if (best < THROW_MIN * vu / 35. || vel.Length() <= 0)
			return false;

		double spd = clamp(vel.Length() * 3, 14, 42);
		Vector3 dir = vel.Unit();
		Vector3 from = Place(AxeHead());
		if (!Clear(mo, fH, from))
			from = fH;
		dir = AimAssist(mo, from, dir, spd);

		Name cname = mo.CountInv('PowerStrength') > 0 ? 'ThrowedAxeStrong' : 'ThrowedAxe';
		class<Actor> cls = cname;
		if (!cls)
			return false;
		let axe = Actor.Spawn(cls, from, ALLOW_REPLACE);
		if (!axe)
			return false;
		axe.target = mo;
		axe.angle = VectorAngle(dir.x, dir.y);
		axe.pitch = -asin(clamp(dir.z, -1, 1));
		axe.vel = dir * spd;
		mo.A_StartSound("Axe/Throw", CHAN_WEAPON, CHANF_OVERLAP);
		Buzz(mo);
		axe.CheckMissileSpawn(mo.radius);
		Reset();
		return true;
	}

	// a throw within 8 degrees of a visible monster goes to it, arced for the drop
	static Vector3 AimAssist(PlayerPawn mo, Vector3 from, Vector3 dir, double spd)
	{
		Actor best = null;
		double bestCos = cos(8);
		let it = ThinkerIterator.Create('Actor');
		Actor t;
		while (t = Actor(it.Next()))
		{
			if (!t.bISMONSTER || !t.bSHOOTABLE || t.bFRIENDLY || t.bDORMANT || t.health <= 0)
				continue;
			Vector3 to = t.pos + (0, 0, t.height * 0.5) - from;
			double dist = to.Length();
			if (dist < 1 || dist > 1536)
				continue;
			double c = (to dot dir) / dist;
			if (c <= bestCos || !mo.CheckSight(t))
				continue;
			bestCos = c;
			best = t;
		}
		if (!best)
			return dir;
		Vector3 to = best.pos + (0, 0, best.height * 0.5) - from;
		double tics = to.Length() / spd;
		to.z += 0.5 * mo.GetGravity() * tics * tics;
		return to.Unit();
	}
}

// the axe's alt-fire state gives this every tic it holds; it never stays in
// the inventory, it only runs RSVR_Hand.Grip for the player
class RSVR_AxeGrip : Inventory
{
	override bool TryPickup(in out Actor toucher)
	{
		let mo = PlayerPawn(toucher);
		if (mo)
			RSVR_Hand.Grip(mo);
		return false;
	}
}

class RSVR_Token : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
	}
}

class RSVR_AxeHolding : RSVR_Token {}
class RSVR_AxeHold : RSVR_Token {}		// the hold input is down: Ready enters the hold loop
class RSVR_AxeThrown : RSVR_Token {}
class RSVR_NotVR : RSVR_Token {}

// a projectile the engine counts as a shot: spawning it buzzes the weapon hand
class RSVR_Buzz : Actor
{
	Default
	{
		Projectile;
		+NOCLIP
		Radius 1;
		Height 1;
		Speed 1;
		DamageType "RSVRHaptic";
		RenderStyle "None";
	}
	States
	{
	Spawn:
		TNT1 A 1;
		Stop;
	}
}
