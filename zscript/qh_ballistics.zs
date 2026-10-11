// ============================================================================
// RS_QuestHands -- enhanced ballistics
//
// THE SHAPE THE OWNER ASKED FOR: "enhanced ballistics: on / off", and OFF means
// BD standard -- its own ballistics, its own projectiles, untouched.
//
// So this is strictly ADDITIVE. It does not `replaces` anything, does not own a
// single one of BD22's actors, and does not alter a shot. It listens for shots
// that have already happened and adds to what they left behind. With the cvar
// off the handler returns on its first line and the mod underneath behaves
// exactly as it shipped. That is the only way an on/off switch can honestly
// claim "off = stock".
//
// HOW IT HEARS ABOUT A SHOT WITHOUT OWNING IT
//   WorldHitscanFired (events.zs:171) fires for every hitscan any mod makes.
//   Its WorldEvent carries AttackPos, AttackAngle, AttackPitch, AttackDistance,
//   AttackOffsetForward/Side, AttackZ and even AttackPuffType -- the origin, the
//   line, the range, and what the mod was about to spawn. That is enough to
//   reconstruct the shot without having been part of it.
//
// WHAT IT KNOWS ABOUT WHAT IT HIT
//   The event does not say what was struck, so we re-trace the same line and
//   read FLineTraceData.HitTexture, then ask QH_Surfaces what that texture is
//   made of. On our fork that answer is an engine native; here it is script.
//   See qh_surfaces.zs.
//
// WHAT WAS LOST IN THE PORT, AND WHY THIS IS STILL WORTH DOING
//   Fork-only, with no equivalent on stock QZD: GPU particles (PARTICLEDEFS
//   feeds hw_gpuparticlebuffer), VOLUMEDEFS and DAMAGEDEFS (both have dedicated
//   C++ parsers), and the engine's segment lights. What survives is real meshes
//   instead of sprites, surface-correct impacts, and ordinary dynamic lights --
//   which is already past what BD22 does with a sprite puff.
// ============================================================================

class QH_Ballistics : EventHandler
{
	QH_Surfaces surf;

	// Live QH_Tracer count. Lives here because ZScript has no mutable statics,
	// and it keeps the cap O(1) instead of a scan over every thinker.
	int liveTracers;

	override void OnRegister()
	{
		surf = new("QH_Surfaces");
		surf.Load();
	}

	static bool Enabled()
	{
		let cv = CVar.FindCVar('qh_enhanced');
		return cv ? cv.GetInt() != 0 : true;
	}

	// ------------------------------------------------------------------------
	// Projectiles. Every actor spawn passes through here (p_mobj.cpp:5151), so
	// this sees BD22's own tracers without owning any of them.
	// ------------------------------------------------------------------------
	override void WorldThingSpawned(WorldEvent e)
	{
		if (!Enabled()) return;

		let a = e.Thing;
		if (!a || !a.bMISSILE) return;

		// Hard cap. Past it a projectile simply gets no trail: one missing trail
		// on the twentieth simultaneous plasma bolt is invisible, a frame rate
		// collapse is not.
		int cap = QH_CV.PI('qh_trail_max', 24);
		if (cap <= 0) return;
		if (liveTracers >= cap) return;

		QH_Tracer.Attach(a);
	}

	override void WorldHitscanFired(WorldEvent e)
	{
		// OFF means BD standard. First line, no exceptions.
		if (!Enabled()) return;

		let shooter = e.Thing;
		if (!shooter || !surf) return;

		// Re-trace the shot that just happened. Same origin, same line, same
		// range, so the impact we find is the one the mod found.
		FLineTraceData d;
		bool ok = shooter.LineTrace(
			e.AttackAngle, e.AttackDistance, e.AttackPitch, 0,
			e.AttackZ, e.AttackOffsetForward, e.AttackOffsetSide, d);

		if (!ok) return;
		if (d.HitType == FLineTraceData.TRACE_HitNone) return;
		if (d.HitType == FLineTraceData.TRACE_HasHitSky) return;
		if (d.HitType == FLineTraceData.TRACE_HitActor) return;	// flesh is the mod's

		// Floors and ceilings answer their flat rules, walls their wall rules --
		// the same split the engine keys on.
		bool isFlat = (d.HitType == FLineTraceData.TRACE_HitFloor
		            || d.HitType == FLineTraceData.TRACE_HitCeiling);

		Name mat = surf.Of(d.HitTexture, isFlat);
		if (mat == 'None') return;		// nothing claims this texture; leave it alone

		Spall(d, mat);
	}

	// ------------------------------------------------------------------------
	// Throw chips off the surface, along its normal, away from the round.
	// ------------------------------------------------------------------------
	// RNG AND NETPLAY: these are playsim random() calls, and that is safe here
	// only because BOTH gates above -- qh_enhanced and qh_debris_scale -- are
	// SERVER cvars. Every machine therefore reaches this function on the same
	// shots and consumes the same draws in the same order.
	//
	// If either were a user cvar, a player who turned debris off would stop
	// consuming draws the others still consumed, and the RNG streams would walk
	// apart. That is the whole reason those two are not user cvars, and it is
	// why a future effect toggle must be server too.
	//
	// The named stream [qhb] keeps those draws out of every other mod's
	// sequence, so adding or removing this pack cannot shift anyone else's.
	// Not private: QH_Tracer calls it for projectile impacts, so a rocket into
	// concrete throws the same chips a bullet does.
	void Spall(FLineTraceData d, Name mat)
	{
		int base = QH_Debris.BaseFrameFor(mat);
		if (base < 0) return;			// a surface with no debris of its own

		int count = QH_Debris.CountFor(mat);
		let cv = CVar.FindCVar('qh_debris_scale');
		double mult = cv ? cv.GetFloat() : 1.0;
		count = int(count * mult);
		if (count <= 0) return;

		// Away from the incoming round. HitDir is the direction of travel, so
		// the surface throws back along its negation.
		//
		// NOT NAMED `out`: that is ZScript's parameter qualifier, and using it
		// as a local REFUSED THE ENTIRE PK3 at load ("Unexpected 'out'"). It
		// had been here since this file was written and was never seen, because
		// nothing in this lane had ever been compiled.
		vector3 away = -d.HitDir;

		for (int i = 0; i < count; i++)
		{
			let a = QH_Debris(Actor.Spawn("QH_Debris",
				d.HitLocation + away * 2.0, ALLOW_REPLACE));
			if (!a) continue;

			a.frame = base + random[qhb](0, 3);

			// A cone around the surface normal, with speed spread so a burst
			// does not read as one rigid spray.
			double sp = frandom[qhb](1.5, 5.0);
			a.Vel = (away * sp)
			      + (frandom[qhb](-1.2, 1.2), frandom[qhb](-1.2, 1.2), frandom[qhb](0.4, 2.0));
		}
	}
}


// ----------------------------------------------------------------------------
// One debris actor, twelve meshes. The material picks a block of four frames
// and the spawn picks one of them, so a burst is not four copies of one chip.
//
//   A-D concrete    E-H brick    I-L dirt
//
// Surfaces with no debris of their own (glass, liquid, lava, screens) return -1
// and are skipped rather than throwing concrete, which is the kind of detail
// that makes an effect read as wrong without anyone being able to say why.
// ----------------------------------------------------------------------------

class QH_Debris : Actor
{
	static int BaseFrameFor(Name mat)
	{
		switch (mat)
		{
			case 'concrete':	return 0;	// A
			case 'marble':		return 0;
			case 'tile':		return 0;
			case 'metal':		return 0;	// sparks would be better; chips for now
			case 'tech':		return 0;
			case 'brick':		return 4;	// E
			case 'wood':		return 4;	// splinters are closer to chunks than chips
			case 'dirt':		return 8;	// I
			case 'slime':		return 8;
		}
		return -1;
	}

	static int CountFor(Name mat)
	{
		switch (mat)
		{
			case 'dirt':	return 6;
			case 'slime':	return 4;
			case 'brick':	return 5;
			case 'concrete':return 5;
			case 'marble':	return 4;
			case 'tile':	return 4;
			case 'wood':	return 4;
			case 'metal':	return 3;
			case 'tech':	return 3;
		}
		return 0;
	}

	Default
	{
		Radius 1;
		Height 1;
		Gravity 0.7;
		BounceType "Doom";
		BounceFactor 0.3;
		WallBounceFactor 0.3;
		+MISSILE
		+NOBLOCKMAP
		+NOTELEPORT
		+CLIENTSIDEONLY
		+DONTSPLASH
		+THRUACTORS
		RenderStyle "Normal";
	}

	States
	{
	Spawn:
		// The first state establishes the SPRITE; the spawner then overwrites
		// `frame` to pick its mesh. Every state after it is "####" "#" -- same
		// sprite, same frame -- because a literal frame letter here would reset
		// that choice the moment the state advanced, and every chip in the map
		// would silently become chip1.
		QDBR A 350;
		"####" "#" 1 A_FadeOut(0.08);
		wait;
	}
}
