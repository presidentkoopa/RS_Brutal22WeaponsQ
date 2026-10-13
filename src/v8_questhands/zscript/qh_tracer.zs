// ============================================================================
// RS_QuestHands -- projectile trails and projectile impacts
//
// THE OWNER'S CONDITION: trails and impacts together or neither. A trail that
// stops in mid-air with nothing happening at the end reads as broken.
//
// They are not separable here anyway, and that is the point of the design. ONE
// tracker per projectile draws the trail each tic AND holds the projectile's
// last position and velocity. When the projectile vanishes, that record is
// exactly what the impact needs to trace to a surface. You cannot have the
// trail without getting the impact for free.
//
// WHY THIS WORKS ON A MOD WE DO NOT OWN
//   WorldThingSpawned fires from a single call site in the engine
//   (p_mobj.cpp:5151), so it sees every actor any mod spawns -- including
//   BD22's own tracers. We attach to them. Nothing is replaced, no class is
//   touched, and with the cvar off not one line of this runs.
//
//   BD22 fires hitscan AND projectiles from the same guns: A_FireBullets does
//   the damage, A_FireProjectile draws the visible shot. Plasma, the rocket
//   launcher, the BFG and the railgun are pure projectile -- 81 projectile
//   calls in Plasma alone.
//
// "LIGHT BUT PUNCHY" -- THE PERFORMANCE SHAPE
//   Trails are ENGINE PARTICLES (Level.SpawnParticle), not actors. A particle
//   has no thinker, no blockmap entry and no state machine; an actor per trail
//   segment would be hundreds of thinkers a second off a plasma rifle and would
//   not survive Quest.
//
//   Punch comes from contrast and brevity, not volume: a short bright core that
//   fades in a few tics reads harder than a long dim smear and costs a fifth as
//   much. Hence short lifetimes and a low per-tic count rather than a dense
//   ribbon.
//
//   There is a hard cap on live trackers. Past it, new projectiles simply get
//   no trail. A missing trail on the twentieth simultaneous plasma bolt is
//   invisible; a frame rate collapse is not.
// ============================================================================

class QH_Tracer : Thinker
{
	Actor target;
	vector3 lastPos;
	vector3 lastVel;
	int age;
	bool hadTarget;

	// Live tracker count, so the cap is O(1) rather than a scan.
	static int LiveCount(int delta)
	{
		// ZScript has no mutable statics, so the count rides on the handler.
		let h = QH_Ballistics(EventHandler.Find("QH_Ballistics"));
		if (!h) return 0;
		h.liveTracers += delta;
		if (h.liveTracers < 0) h.liveTracers = 0;
		return h.liveTracers;
	}

	static QH_Tracer Attach(Actor missile)
	{
		if (!missile) return null;

		let t = new("QH_Tracer");
		t.target = missile;
		t.lastPos = missile.Pos;
		t.lastVel = missile.Vel;
		t.age = 0;
		t.hadTarget = true;
		LiveCount(1);
		return t;
	}

	override void Tick()
	{
		if (!hadTarget) { Destroy(); return; }

		age++;

		// Runaway guard: a projectile that never resolves must not leave a
		// tracker ticking for the rest of the level.
		if (age > 700)
		{
			hadTarget = false;
			LiveCount(-1);
			Destroy();
			return;
		}

		if (target)
		{
			lastPos = target.Pos;
			lastVel = target.Vel;
			Trail();
			return;
		}

		// The projectile is gone. lastPos/lastVel are its final state, which is
		// what the impact needs -- we do not depend on the destroy event still
		// having valid fields.
		hadTarget = false;
		LiveCount(-1);
		Impact();
		Destroy();
	}

	// ------------------------------------------------------------------------
	// The trail. Particles only.
	// ------------------------------------------------------------------------
	private void Trail()
	{
		if (!target || !target.Level) return;

		int every = QH_CV.PI('qh_trail_every', 1);
		if (every < 1) every = 1;
		if (age % every != 0) return;

		double sz = QH_CV.PF('qh_trail_size', 2.0);
		int life = QH_CV.PI('qh_trail_life', 7);
		if (life < 1) return;			// 0 silences trails without touching impacts

		FSpawnParticleParams p;
		p.color1     = QH_Palette.ForProjectile(target);
		p.style      = STYLE_Add;
		p.lifetime   = life;
		p.size       = sz;
		p.sizestep   = -sz / double(life);	// taper to nothing rather than popping out
		p.pos        = target.Pos;
		// A touch of the projectile's own travel, so the trail reads as thrown
		// off the round rather than painted on the world.
		p.vel        = target.Vel * 0.04;
		p.accel      = (0, 0, 0);
		p.startalpha = 1.0;
		p.fadestep   = -1;				// -1 = fade evenly across the lifetime
		p.startroll  = 0;
		p.rollvel    = 0;
		p.rollacc    = 0;

		target.Level.SpawnParticle(p);
	}

	// ------------------------------------------------------------------------
	// The impact. Trace the last metre of flight to find what was hit, then
	// hand off to the same surface lookup and debris the hitscan path uses --
	// so a rocket into concrete throws the same chips a bullet does.
	// ------------------------------------------------------------------------
	private void Impact()
	{
		let h = QH_Ballistics(EventHandler.Find("QH_Ballistics"));
		if (!h || !h.surf) return;
		if (!QH_Ballistics.Enabled()) return;

		double sp = lastVel.Length();
		if (sp <= 0.0) return;

		// A throwaway actor is needed only because LineTrace is an Actor method.
		// It exists for one call and is gone in the same tic.
		let probe = Actor.Spawn("QH_TraceProbe", lastPos - lastVel, NO_REPLACE);
		if (!probe) return;

		vector3 dir = lastVel / sp;
		double yaw = atan2(dir.y, dir.x);
		double pit = -asin(clamp(dir.z, -1.0, 1.0));

		FLineTraceData d;
		bool ok = probe.LineTrace(yaw, sp * 2.0 + 16.0, pit, 0, 0, 0, 0, d);
		probe.Destroy();

		if (!ok) return;
		if (d.HitType == FLineTraceData.TRACE_HitNone) return;
		if (d.HitType == FLineTraceData.TRACE_HasHitSky) return;
		if (d.HitType == FLineTraceData.TRACE_HitActor) return;	// flesh is the mod's

		bool isFlat = (d.HitType == FLineTraceData.TRACE_HitFloor
		            || d.HitType == FLineTraceData.TRACE_HitCeiling);

		Name mat = h.surf.Of(d.HitTexture, isFlat);
		if (mat == 'None') return;

		h.Spall(d, mat);
	}
}


// A one-tic nothing, spawned only so LineTrace -- an Actor method -- can be
// called from a Thinker that has no actor of its own.
class QH_TraceProbe : Actor
{
	Default
	{
		Radius 1;
		Height 1;
		+NOBLOCKMAP
		+NOGRAVITY
		+NOINTERACTION
		+NOTELEPORT
		+THRUACTORS
		RenderStyle "None";
	}
	States { Spawn: TNT1 A 1; stop; }
}


// ----------------------------------------------------------------------------
// Trail colour.
//
// Keyed off what the projectile already is rather than a per-weapon table, so a
// mod we have never seen still gets a sane trail. Grounded rather than a light
// show: a bullet throws a dull warm spark, plasma reads as its own energy.
// ----------------------------------------------------------------------------

class QH_Palette abstract
{
	static color ForProjectile(Actor a)
	{
		if (!a) return Color(255, 200, 150);

		// Keyed on the class name only. There is no bBRIGHT actor flag -- in
		// Doom, fullbright is a property of a STATE, not of the actor -- so a
		// "does it glow" test is not available to us here.
		String cn = a.GetClassName();
		cn = cn.MakeLower();

		if (cn.IndexOf("plasma") >= 0)  return Color(120, 180, 255);
		if (cn.IndexOf("bfg") >= 0)     return Color(140, 255, 140);
		if (cn.IndexOf("rail") >= 0)    return Color(200, 160, 255);
		if (cn.IndexOf("fire") >= 0)    return Color(255, 150,  60);
		if (cn.IndexOf("flame") >= 0)   return Color(255, 150,  60);

		// Everything else: hot metal, not a firework.
		return Color(255, 190, 130);
	}
}
