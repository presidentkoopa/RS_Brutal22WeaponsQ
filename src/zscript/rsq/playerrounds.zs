// playerrounds.zs (BD 2.0, owner 2026-10-27 11:21): "Player Ballistics: Hitscan / Bullet".
//
// HITSCAN (0, the default) is BD22 as it ships: nothing here runs.
// BULLET  (1) the player's hitscans fly as real rounds. Ported from the owner's RS_Ballistics,
//         zscript/rsb/enemyfire.zs (presidentkoopa/rs_ballistics), which does this for MONSTERS:
//         WorldHitscanPreFired cancels the hitscan and a round flies along the shot's own aim at
//         sv_rsb_enemy_round_speed (80 map units a tic, its default) instead. Same here, for you.
//
// WHAT IS KEPT EXACTLY (the shotgun stays a shotgun):
//   * PELLETS AND SPREAD. A_FireBullets calls LineAttack once per pellet with that pellet's
//     spread already rolled into its angle and pitch, so every LineAttack is one event and one
//     round. Four pellets are four rounds, each on the line the hitscan pellet would have taken.
//   * WHERE IT POINTS. In VR the engine does not trace along the event's angle: it maps it
//     through the weapon controller (p_map.cpp P_LineAttack, AttackDir). The round takes that
//     same AttackDir (OffhandDir for an off-hand gun), so it flies the hitscan's line.
//   * DAMAGE, DAMAGE TYPE, PUFF, BLOOD, DECALS, KILL CREDIT. A round does NOT deal damage as a
//     missile. When its flight reaches something, it fires the ORIGINAL hitscan -- the event's
//     own damage, damage type and puff class -- from where it is, for the rest of the original
//     range. That last stretch is the engine's own P_LineAttack, so BD22's puff picks the damage
//     type (Shotgun, Minigun, Saw...), BLOODLESSIMPACT, MTHRUSPECIES and the decal all apply as
//     they always did. LAF_TARGETISSOURCE makes the player the damage source: the kill is yours.
//     A_FireBullets has already rolled the damage before the event (FBF_NORANDOM on every BD22
//     gun), so not one random call is added or removed.
//   * WHERE IT STARTS. The drawn muzzle, RSQ_Muzzle.Where (muzzle.zs), with its wall guard; off
//     the table, or with the guard saying no, where the engine would have started the hitscan.
//
// WHAT IS LEFT A HITSCAN, on purpose:
//   * a hitscan shorter than MISSILERANGE (2048): melee, and the SSG's 300-unit point-blank
//     blast (SSG.dec: A_FireBullets(0, 0, 1, 40, "shotpuff", FBF_NORANDOM, 300)) -- the same
//     rule enemyfire.zs uses;
//   * rails (the Ruger's 30-damage "Heavy penetration" rail, the Railgun): they are not hitscan
//     events, and a rail pierces, which a round does not;
//   * anything a non-player fires, and the round's own last-stretch hitscan.
//
// THE ROUND ITSELF never collides as a missile (+NOINTERACTION): each tic it traces its own
// next step with LineTrace -- traced as the SHOOTER, because the drawn muzzle can sit inside the
// player's own box and the engine's hitscan never hits its shooter either (rig, 2026-10-27: a
// pistol held out to the right shot its owner until this) -- and moves there if the step is clear.
// It draws RS_Ballistics' btracer.obj at the calibre bullet.zs already picks per gun.
//
// ORDER. It must see the shot AFTER RSQ_Recoil and RSQ_FlashHandler (they watch the same event
// and would never see a cancelled one) and after RSQ_Muzzle (whose re-fire from the muzzle,
// LAF_ABSPOSITION, is the event taken here). SetOrder puts this handler last.
//
// NETPLAY. sv_rsq_player_ballistics is a server cvar (it decides where shots go). The round is
// playsim: spawned from the event, moved by traces, no random numbers.

class RSQ_PlayerRound : Actor
{
	Default
	{
		+NOINTERACTION;
		+NOBLOCKMAP;
		+NOGRAVITY;
		+DONTSPLASH;
		+NOTELEPORT;
		Radius 1;
		Height 1;
		RenderStyle "Normal";
	}

	// the hitscan it carries
	double shotAngle, shotPitch;	// world direction (already through AttackDir)
	double rangeLeft;				// of the original AttackDistance
	int dmg;
	Name dmgType;
	class<Actor> puffType;
	int laf;						// the original line-attack flags, minus position/hand bits
	Vector3 dir;
	double flySpeed;
	int life;

	const MAX_LIFE = 350;			// 10 s: 8192 units at 80 a tic is 103 tics

	void Setup(Actor shooter, Vector3 at, double ang, double pit, double dist, int damage, Name dtype,
		class<Actor> puff, int flags, double spd, int look)
	{
		target = shooter;
		Species = shooter.GetSpecies();	// MTHRUSPECIES puffs compare with the CALLER's species: the round fires the last stretch
		shotAngle = ang;
		shotPitch = pit;
		angle = ang;
		pitch = pit;
		double cp = cos(pit);
		dir = (cp * cos(ang), cp * sin(ang), -sin(pit));
		rangeLeft = dist;
		dmg = damage;
		dmgType = dtype;
		puffType = puff;
		laf = flags & ~(LAF_ABSPOSITION | LAF_ABSOFFSET | LAF_ISOFFHAND | LAF_OVERRIDEZ | LAF_TARGETISSOURCE);
		flySpeed = spd;
		frame = look;
	}

	override void Tick()
	{
		if (isFrozen())
			return;
		if (life++ > MAX_LIFE || rangeLeft <= 0)
		{
			Destroy();
			return;
		}
		double step = min(flySpeed, rangeLeft);
		// Traced AS THE SHOOTER, as the engine's own hitscan is (P_LineAttack never hits t1): the
		// muzzle can sit inside the player's own box, and a round must not shoot its owner.
		// TRF_ABSPOSITION without TRF_USEWEAPON: a plain line from here, no VR remapping.
		let src = target;
		FLineTraceData t;
		if (src)
			src.LineTrace(shotAngle, step, shotPitch, TRF_ABSPOSITION, pos.z, pos.x, pos.y, t);
		else
			LineTrace(shotAngle, step, shotPitch, TRF_ABSPOSITION, pos.z, pos.x, pos.y, t);
		if (t.HitType != TRACE_HitNone)
		{
			Arrive(t.Distance);
			return;
		}
		rangeLeft -= step;
		SetOrigin(pos + dir * step, true);
	}

	// Something is within this tic's step, `dist` ahead: deliver the hitscan from just short of
	// it, for the rest of the original range. Starting 2 units short keeps the shooter's own box
	// behind the start, and from there the engine does everything a BD22 hitscan does.
	void Arrive(double dist)
	{
		let src = target;
		if (src && puffType)
		{
			double back = max(0.0, dist - 2.0);
			SetOrigin(pos + dir * back, false);
			rangeLeft -= back;
			RSQ_PlayerRounds.SetDelivering(true);
			LineAttack(shotAngle, max(rangeLeft, 4.0), shotPitch, dmg, dmgType, puffType,
				laf | LAF_ABSPOSITION | LAF_TARGETISSOURCE, null, pos.z, pos.x, pos.y);
			RSQ_PlayerRounds.SetDelivering(false);
		}
		Destroy();
	}

	States
	{
	Spawn:
		RSBM A -1;		// the frame is the calibre (Setup); RSBM draws nothing without its model
		Stop;
	}
}

class RSQ_PlayerRounds : EventHandler
{
	const SPEED = 80.0;	// map units a tic: RS_Ballistics' sv_rsb_enemy_round_speed default (CVARINFO.txt)

	bool delivering;

	override void OnRegister()
	{
		SetOrder(1000);	// after recoil, the flash and the muzzle (see ORDER above)
	}

	static void SetDelivering(bool on)
	{
		let h = RSQ_PlayerRounds(EventHandler.Find('RSQ_PlayerRounds'));
		if (h)
			h.delivering = on;
	}

	static bool On()
	{
		let cv = CVar.FindCVar('sv_rsq_player_ballistics');
		return cv && cv.GetInt() == 1;
	}

	override bool WorldHitscanPreFired(WorldEvent e)
	{
		if (delivering || !On())
			return false;
		let mo = PlayerPawn(e.Thing);
		if (!mo || !mo.player || e.AttackDistance < MISSILERANGE || !e.AttackPuffType)
			return false;
		bool off = (e.AttackLineFlags & LAF_ISOFFHAND) != 0;

		// THE START: muzzle.zs's re-fire hands it to us as absolute coordinates; otherwise the
		// muzzle is worked out here the same way, so the order of the handlers cannot change it.
		Vector3 at;
		if (e.AttackLineFlags & LAF_ABSPOSITION)
			at = (e.AttackOffsetForward, e.AttackOffsetSide, e.AttackZ);
		else
		{
			bool ok = false;
			if (!off)
				[at, ok] = RSQ_Muzzle.Where(mo);
			if (!ok)
			{
				if (mo.OverrideAttackPosDir)
					at = off ? mo.OffhandPos : mo.AttackPos;
				else
				{
					double sz = mo.Height * 0.5 - mo.Floorclip + mo.player.mo.AttackZOffset * mo.player.crouchFactor + e.AttackZ;
					at = mo.pos + (0, 0, sz);
				}
			}
		}

		// THE LINE: the engine's own mapping of the event's angles through the controller
		double ang = e.AttackAngle, pit = e.AttackPitch;
		if (mo.OverrideAttackPosDir)
		{
			Vector3 ap = off ? mo.OffhandDir(mo, e.AttackAngle, e.AttackPitch) : mo.AttackDir(mo, e.AttackAngle, e.AttackPitch);
			ang = ap.x;
			pit = ap.y;
		}

		Weapon w = off ? mo.player.OffhandWeapon : mo.player.ReadyWeapon;
		int look = w ? RSQ_Bullet.FrameOf(w.GetClassName()) : -1;
		if (look < 0)
			look = 2;	// RSBMC, the intermediate streak, for a gun bullet.zs has no calibre for

		let r = RSQ_PlayerRound(Actor.Spawn('RSQ_PlayerRound', at, ALLOW_REPLACE));
		if (!r)
			return false;
		r.Setup(mo, at, ang, pit, e.AttackDistance, e.Damage, e.DamageType, e.AttackPuffType,
			e.AttackLineFlags, SPEED, look);
		return true;	// the hitscan is not run now: the round carries it
	}
}
