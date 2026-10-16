// RS VR grenade (2026-10-16). BD22's own hand grenade, worked by hand in VR:
//   1. the off hand takes the RING (off trigger, or grip) and pulls it away: the pin is out
//      (BD's own "Grenade/Pin"). Bring the hand back to the top and grab again: pin back in.
//   2. the main TRIGGER is your squeeze on the spoon. Let go of it while swinging: thrown,
//      at the speed and direction of the swing. Let go while still: the spoon flies off
//      (ping) and the fuse is lit in your hand -- cooking. Squeeze and let go again to throw.
//   3. cook too long (BD's fuse, 48 tics) and it goes off in the hand.
// BD22's own HandGrenade projectile, its fuse token, its explosion and sounds.
// Out of VR, or rsg_vr 0, BD22's own canned throw is untouched.
class RSG_Handler : EventHandler
{
	RSG_State st[MAXPLAYERS];

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
				continue;
			let mo = players[n].mo;
			if (!st[n])
				st[n] = new('RSG_State');
			st[n].Tick(mo);
		}
	}
}

class RSG_State play
{
	const FUSE = 48;				// BD22: GrenadeTime 3, 16 tics a count
	const RING_GRAB = 12.0;			// cm round the ring the off hand can take it
	const PULL = 8.0;				// cm past that: the pin is out
	const HIST = 6;
	const RING_F = -3.04;		// the ring: nade.md3 in Ermac's hand (MODELDEF.rsq RQNP), gun hand cm (F, L, U)
	const RING_L = 5.45;
	const RING_U = 4.18;

	RSR_State geo;
	bool armed;			// pin out
	bool ringHeld;
	bool ringKept;		// the pulled ring is still in the off hand (until its grab lets go)
	bool spoonOff;		// cooking
	int cookTic;
	bool trigPrev, grabPrev;
	int gripPrevPresses;
	double hx[HIST], hy[HIST], hz[HIST], px[HIST], py[HIST], pz[HIST];
	int head, count;

	static class<Actor> Cls(Name n) { class<Actor> c = n; return c; }

	static bool Wanted(PlayerPawn mo)
	{
		let w = mo.player.ReadyWeapon;
		if (!w || w.GetClassName() != 'HandGrenades' || !RSVR_VRHand.InVR(mo))
			return false;
		if (RSR.PlayerInt(mo.player, 'rsg_vr', 1) == 0)
			return false;
		class<Inventory> am = (class<Inventory>)(Cls('GrenadeAmmo'));
		return am && mo.CountInv(am) > 0;
	}

	void Reset(PlayerPawn mo)
	{
		armed = ringHeld = ringKept = spoonOff = false;
		mo.SetInventory('RSG_PinOut', 0);
		mo.SetInventory('RSG_Spoon', 0);
	}

	void Buzz(PlayerPawn mo) { RSVR_Hand.Buzz(mo); }

	// the off hand shows the ring pinched in its fingers while it holds it (hands.zs RsgRing)
	void Tick(PlayerPawn mo)
	{
		// 1.12 (owner: "throwing all grenades makes both hands disappear forever"): BD22 keeps the
		// empty grenade out (its no-ammo jump never fires) and shows nothing. In VR, the last
		// grenade gone switches to the fists (an empty hand is a fist).
		let p = mo.player;
		let w = p ? p.ReadyWeapon : null;
		class<Inventory> am = (class<Inventory>)(Cls('GrenadeAmmo'));
		if (w && w.GetClassName() == 'HandGrenades' && am && mo.CountInv(am) <= 0 && !armed
			&& p.PendingWeapon == WP_NOCHANGE && RSVR_VRHand.InVR(mo))
			mo.A_SelectWeapon('Melee_Attacks');	// out of grenades: the hand becomes a fist
		Step(mo);
		mo.SetInventory('RSG_RingHand', RSG_VR_On(mo) && (ringHeld || ringKept) ? 1 : 0);
	}

	static bool RSG_VR_On(PlayerPawn mo) { return mo.CountInv('RSG_VR') > 0; }

	void Step(PlayerPawn mo)
	{
		bool want = Wanted(mo);
		mo.SetInventory('RSG_VR', want ? 1 : 0);
		if (!want)
		{
			if (armed && spoonOff)
				Boom(mo);			// switched or left VR with the fuse lit: it still goes off
			if (armed)
				Reset(mo);
			count = 0;
			return;
		}
		if (!geo)
			geo = new('RSR_State');
		geo.Frames(mo);

		// the hand's path, for the throw
		head = (head + 1) % HIST;
		Vector3 hp = RSVR_VRHand.HandPos(mo);
		hx[head] = hp.x; hy[head] = hp.y; hz[head] = hp.z;
		px[head] = mo.pos.x; py[head] = mo.pos.y; pz[head] = mo.pos.z;
		count = min(count + 1, HIST);

		// the off hand's grab: its trigger, or the grip
		let rs = RSR_Handler.StateOf(mo);
		int mask = RSR.PlayerInt(mo.player, 'rsr_grab_buttons', BT_OFFHANDATTACK);
		bool grab = (mo.player.cmd.buttons & mask) != 0 || rs && rs.netGrip;
		bool grabPress = grab && !grabPrev;
		grabPrev = grab;
		if (!grab)
			ringKept = false;
		bool trig = (mo.player.cmd.buttons & BT_ATTACK) != 0;
		bool trigUp = !trig && trigPrev;
		trigPrev = trig;

		double cap = RING_GRAB * RSR.Float('rsr_assist', 1.0);
		double d = (geo.offLocal - (RING_F, RING_L, RING_U)).Length();
		int now = mo.Level.maptime;

		if (!armed)
		{
			if (grabPress && d < cap)
			{
				ringHeld = true;
				Buzz(mo);
			}
			if (ringHeld && !grab)
				ringHeld = false;
			if (ringHeld && d > cap + PULL)
			{
				armed = true;
				ringHeld = false;
				ringKept = true;
				mo.SetInventory('RSG_PinOut', 1);
				mo.A_StartSound("Grenade/Pin", CHAN_WEAPON, CHANF_OVERLAP);
				Buzz(mo);
			}
			return;
		}

		if (!spoonOff)
		{
			if (grabPress && d < cap * 0.6)
			{
				Reset(mo);			// the pin back in
				mo.A_StartSound("Grenade/Pin", CHAN_WEAPON, CHANF_OVERLAP);
				Buzz(mo);
				return;
			}
			if (trigUp)
			{
				if (!Throw(mo, 0, true))
				{
					spoonOff = true;		// let go while still: the spoon flies, it is cooking
					cookTic = now;
					mo.SetInventory('RSG_Spoon', 1);
					mo.A_StartSound("weapons/shell", CHAN_AUTO, CHANF_OVERLAP);
					Buzz(mo);
				}
			}
			return;
		}

		int cooked = now - cookTic;
		if (cooked >= FUSE)
		{
			Boom(mo);
			return;
		}
		if (trigUp)
			Throw(mo, cooked, false);
	}

	// the fastest step of the hand over the last tics, less the player's own movement
	Vector3 Swing(out double best)
	{
		best = 0;
		Vector3 vel = (0, 0, 0);
		for (int i = 0; i < count - 1; i++)
		{
			int a = (head - i + HIST) % HIST, b = (head - i - 1 + HIST) % HIST;
			Vector3 v = (hx[a] - hx[b], hy[a] - hy[b], hz[a] - hz[b]);
			Vector3 m = (px[a] - px[b], py[a] - py[b], pz[a] - pz[b]);
			double rel = (v - m).Length();
			if (rel > best)
			{
				best = rel;
				vel = v - m;
			}
		}
		return vel;
	}

	bool Throw(PlayerPawn mo, int cooked, bool needSwing)
	{
		double best;
		Vector3 vel = Swing(best);
		double vu = geo.vu > 0 ? geo.vu : 34;
		if (needSwing && best < RSVR_Hand.THROW_MIN * vu / 35.0)
			return false;
		class<Actor> gc = Cls('HandGrenade');
		if (!gc)
			return false;
		Vector3 dir = best > 0.01 ? vel.Unit() : geo.F;
		double spd = clamp(best * 2.2, 3, 32);
		let g = Actor.Spawn(gc, RSVR_VRHand.HandPos(mo), ALLOW_REPLACE);
		if (!g)
			return false;
		g.target = mo;
		g.angle = VectorAngle(dir.x, dir.y);
		g.pitch = -asin(clamp(dir.z, -1, 1));
		g.vel = dir * spd + mo.vel;
		class<Inventory> gt = (class<Inventory>)(Cls('GrenadeTime'));
		if (gt && cooked >= 16)
			g.GiveInventory(gt, cooked / 16);	// the fuse already burned in the hand
		mo.A_StartSound("Grenade/Toss", CHAN_WEAPON, CHANF_OVERLAP);
		if (!spoonOff)
			mo.A_StartSound("weapons/shell", CHAN_AUTO, CHANF_OVERLAP);
		Spent(mo);
		return true;
	}

	void Boom(PlayerPawn mo)
	{
		class<Actor> ec = Cls('FragGrenadeExplosion');
		if (ec)
		{
			let e = Actor.Spawn(ec, RSVR_VRHand.HandPos(mo));
			if (e)
				e.target = mo;
		}
		Spent(mo);
	}

	void Spent(PlayerPawn mo)
	{
		class<Inventory> am = (class<Inventory>)(Cls('GrenadeAmmo'));
		if (am)
			mo.TakeInventory(am, 1);
		Reset(mo);
		mo.GiveInventory('RSG_Thrown', 1);
		Buzz(mo);
	}
}

class RSG_VR : RSVR_Token {}
class RSG_PinOut : RSVR_Token {}
class RSG_Spoon : RSVR_Token {}
class RSG_Thrown : RSVR_Token {}
class RSG_RingHand : RSVR_Token {}
