// ============================================================================
// RS_QuestHands -- REAL GRABS: is the off hand actually ON the part?
//
// WHAT THIS REPLACES, AND WHY IT WAS WRONG.
//
// The reload stops used to release on HAND SEPARATION -- the distance between
// the two controllers. That reads a rhythm, not a reach: any away-and-back
// motion satisfied it, so a hand drifting sideways dropped a magazine and a
// hand reaching for a real hip pouch was indistinguishable from a shrug. It
// also cannot ever express "grab the pump" or "grab the charging handle",
// because those are two different places and separation is one number.
//
// This is the replacement: a point attached to the gun, a radius around it, and
// the question "is the off hand inside". That is what the fork's RS_VR_Reload
// does with its grab ovals, and the design is deliberately the same so the two
// packs stay recognisable to each other.
//
// ==========================================================================
// THE HARD PART, STATED UP FRONT: WE CANNOT ASK THE RENDERER WHERE THE GUN IS.
// ==========================================================================
//
// RS_VR_Reload gets a part's world position from ModelPointToWorld -- the
// renderer's own matrix, so its ovals sit exactly on the drawn mesh. That
// native DOES NOT EXIST in stock QZD 17.3, and neither does SetModelJoint.
//
// What stock gives us is the PLAYSIM hand pose: AttackPos plus AttackAngle,
// AttackPitch, AttackRoll (actor.zs:282-289), and the same four for the off
// hand. That is the controller, not the drawn model. Between the two sits
// everything RenderHUDModel does (models.cpp): GetWeaponTransform, a 0.01
// scale, translate(0,5,30), the MODELDEF x/y/zoffset, a hardcoded 90 degree
// Y rotation, angleoffset/pitchoffset/rolloffset, vr_3dweaponOffsetX/Y/Z and
// finally vr_weaponScale.
//
// CONSEQUENCE, AND IT IS NOT A BUG TO BE FIXED LATER: a point built here lands
// NEAR the part, not ON it, and the error depends on the player's own
// vr_weaponScale and vr_3dweaponOffset*. So every point is TUNABLE and there is
// a MARKER to tune it against. Measuring the mesh harder does not help; the
// mesh is not where the discrepancy comes from.
//
// Run `qh_baseline` first. Those offsets sit inside the weapon transform, so a
// point tuned without zeroing them is right on one machine and wrong on every
// other one.
//
// ==========================================================================
// NETPLAY
// ==========================================================================
//
// A grab test reads a VR pose, which exists on one machine only. Nothing here
// may decide anything: it is ADVISORY, exactly like the separation gesture it
// replaces, and the release still travels by the `qh_rel` netevent so every
// machine applies the same thing. See the NETPLAY block in qh_reload.zs.
// ============================================================================

// Which part of the gun a stop wants the hand on. Not an enum of gun anatomy --
// three places a hand goes, named for what the hand does there, so a gun whose
// "magazine well" is a cylinder gate or a shell port still uses QH_PART_WELL.
enum QH_PartSlot
{
	QH_PART_WELL   = 0,	// where ammunition goes in: magazine well, gate, breech
	QH_PART_HANDLE = 1,	// what you pull to cycle it: charging handle, bolt, pump
	QH_PART_BODY   = 2,	// the gun itself, for "is your hand anywhere near it"
	QH_PART_COUNT  = 3,
}

class QH_Grab abstract
{
	// ------------------------------------------------------------------------
	// THE MAIN HAND'S FRAME, in metric space.
	//
	// Built in METRES and not map units on purpose. The angles the engine writes
	// are the controller's real orientation, so they describe a real-world
	// rotation; map space has a stretched Z (see qh_metric.zs), and rotating in
	// it would shear the result. Offsets are therefore composed metrically and
	// converted once, at the end, by PartPoint.
	//
	// CONVENTION, AND IT IS AN ASSUMPTION UNTIL SEEN IN A HEADSET: Doom's pitch
	// is positive looking DOWN, and yaw increases anticlockwise seen from above.
	// If a tuned point moves the wrong way vertically, the pitch sign here is
	// the first thing to try -- not the card's numbers.
	// ------------------------------------------------------------------------
	// MULTI-RETURN AND NOT `out vector3`. Three out-vectors compile and then die
	// in the JIT -- "Unexpected JIT error: Unknown REGT value passed to
	// EmitPARAM" on every function that passes them. ZScript's own natives
	// return tuples for exactly this (ModifyBobLayer3D returns vector3,
	// vector3), so do that. Read back with [a, b, c] = GunFrame(mo).
	clearscope static vector3, vector3, vector3 HandBasis(double yaw, double pitch, double roll)
	{
		double cy = cos(yaw),   sy = sin(yaw);
		double cp = cos(pitch), sp = sin(pitch);

		vector3 fwd = (cp * cy, cp * sy, -sp);

		// Right before roll: horizontal, 90 degrees clockwise of the yaw.
		vector3 r0 = (sy, -cy, 0);
		vector3 u0 = fwd cross r0;

		// Roll turns right and up about the forward axis and leaves fwd alone.
		double cr = cos(roll), sr = sin(roll);
		vector3 right = r0 *  cr + u0 * sr;
		vector3 up    = r0 * -sr + u0 * cr;

		return fwd, right, up;
	}

	// The main hand's frame for this player's drawn gun.
	clearscope static vector3, vector3, vector3 GunFrame(Actor mo)
	{
		// NOT `return (1,0,0), (0,-1,0), (0,0,1);` -- a vector literal and the
		// multi-return comma list are the same syntax, so the parser reads that
		// as ONE value: "Incorrect number of return values. Got 1, expected 3".
		// Name them first.
		if (!mo)
		{
			vector3 f = (1,  0, 0);
			vector3 r = (0, -1, 0);
			vector3 u = (0,  0, 1);
			return f, r, u;
		}

		// Nor can a 3-tuple be FORWARDED: `return HandBasis(...)` is also "Got
		// 1, but expected 3". Capture it, then return the three names.
		vector3 f, r, u;
		[f, r, u] = HandBasis(mo.AttackAngle, mo.AttackPitch, mo.AttackRoll);
		return f, r, u;
	}

	// ------------------------------------------------------------------------
	// WHERE A PART IS, in map units, ready to compare against OffhandPos.
	//
	// `local` is in METRES along the gun's own axes: x forward along the bore,
	// y to the gun's right, z up. A magazine well on a rifle is a few
	// centimetres forward of the grip and a little down, so it is roughly
	// (0.10, 0, -0.06).
	// ------------------------------------------------------------------------
	clearscope static vector3 PartPoint(Actor mo, vector3 local, double stretch, double upm)
	{
		if (!mo) return (0, 0, 0);

		vector3 fwd, right, up;
		[fwd, right, up] = GunFrame(mo);

		vector3 offMetres = fwd * local.x + right * local.y + up * local.z;
		return mo.AttackPos + QH_Metric.FromMetres(offMetres, stretch, upm);
	}

	// How far the off hand is from that part, in real metres.
	clearscope static double OffhandDistTo(Actor mo, vector3 local, double stretch, double upm)
	{
		if (!mo) return 1e9;
		vector3 p = PartPoint(mo, local, stretch, upm);
		return QH_Metric.DistMetres(p, mo.OffhandPos, stretch, upm);
	}

	// Is the off hand inside the part's sphere?
	clearscope static bool Inside(Actor mo, vector3 local, double radiusM,
	                              double stretch, double upm)
	{
		if (radiusM <= 0.0) return false;
		return OffhandDistTo(mo, local, stretch, upm) <= radiusM;
	}
}


// ============================================================================
// THE MARKER -- you cannot tune a sphere you cannot see.
//
// Drawn with particles and NOTHING ELSE, deliberately: Level.SpawnParticle
// takes an absolute world position (doombase.zs:560), so this needs no actor,
// no sprite lump, no MODELDEF and no new asset in the pack. That matters on
// Quest, where every lump is weight, and it means the marker can never be the
// reason a load fails.
//
// WHAT YOU SEE: a bright dot at the part's centre and a ring of dots at its
// radius, drawn in the GUN'S OWN right/up plane so the ring shows you how the
// sphere is oriented, not just how big it is. The colour is the answer to the
// only question that matters -- GREEN means your off hand is inside it right
// now, RED means it is not.
//
// Lifetime 2 tics rather than 1: at 35 Hz a one-tic particle strobes.
// ============================================================================

class QH_GrabMarker abstract
{
	const RING = 12;

	// One sphere.
	play static void Sphere(Actor mo, vector3 local, double radiusM,
	                        double stretch, double upm, bool inside)
	{
		if (!mo || !mo.Level || radiusM <= 0.0) return;

		vector3 fwd, right, up;
		[fwd, right, up] = QH_Grab.GunFrame(mo);

		vector3 centre = QH_Grab.PartPoint(mo, local, stretch, upm);

		Color c = inside ? Color(255,  80, 255,  80) : Color(255, 255,  70,  70);

		FSpawnParticleParams p;
		p.color1     = c;
		p.style      = STYLE_Add;
		p.lifetime   = 2;
		p.size       = inside ? 7.0 : 5.0;
		p.startalpha = 1.0;
		p.fadestep   = -1;
		p.pos        = centre;
		mo.Level.SpawnParticle(p);

		// The ring, in the gun's own right/up plane.
		p.size = 3.0;
		for (int i = 0; i < RING; i++)
		{
			double a = i * (360.0 / RING);
			vector3 edge = (right * cos(a) + up * sin(a)) * radiusM;
			p.pos = centre + QH_Metric.FromMetres(edge, stretch, upm);
			mo.Level.SpawnParticle(p);
		}
	}

	// A plain dot, for the off hand itself -- so a point that is nowhere near
	// the gun is obvious as a placement error rather than a mystery.
	//
	// NOT CALLED `Dot`: `dot` is ZScript's vector dot-product operator, and a
	// method of that name does not fail at the call site -- it fails while
	// parsing the DECLARATION, with "Unexpected 'dot', expecting identifier",
	// which refuses the whole pk3.
	play static void Blip(Actor mo, vector3 worldPos, Color c, double size)
	{
		if (!mo || !mo.Level) return;

		FSpawnParticleParams p;
		p.color1     = c;
		p.style      = STYLE_Add;
		p.lifetime   = 2;
		p.size       = size;
		p.startalpha = 1.0;
		p.fadestep   = -1;
		p.pos        = worldPos;
		mo.Level.SpawnParticle(p);
	}
}
