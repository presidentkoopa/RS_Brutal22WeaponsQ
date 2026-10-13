// ============================================================================
// RS_QuestHands -- metric distance helper
//
// WHY THIS EXISTS, AND WHY NOTHING MAY MEASURE HAND DISTANCE WITHOUT IT.
//
// Actor.AttackPos and Actor.OffhandPos are written by the engine at
// hw_openxrdevice.cpp:593-609 (stock qzd17.3). X and Y are metres times
// vr_vunits_per_meter. Z is metres times vr_vunits_per_meter AND THEN DIVIDED
// BY pixelstretch:
//
//   AttackPos.X = X() - weaponoffset[0] * vr_vunits_per_meter
//   AttackPos.Y = Y() - weaponoffset[2] * vr_vunits_per_meter
//   AttackPos.Z = CenterEyePos.Z
//               + ((hmdPosition[1] + weaponoffset[1] + vr_height_adjust)
//                  * vr_vunits_per_meter) / pixelstretch
//               - getDoomPlayerHeightWithoutCrouch(player)
//
// The body terms cancel in (OffhandPos - AttackPos), so that difference IS a
// clean controller-to-controller offset. But it is not metric: at the defaults
// (vr_vunits_per_meter 34, pixelstretch 1.2) it carries 34 units/m horizontally
// and 28.33 units/m vertically. A raw .Length() on it under-reads VERTICAL hand
// separation by 17%, which silently loosens every gesture threshold in the
// reload by about a fifth, varying with how the hands are arranged.
//
// So: never call .Length() on a difference of two hand positions. Call
// DistMetres(). Every threshold in this mod is written in real metres.
//
// The hook's own translation space is a DIFFERENT space and is isotropic -- the
// scale(1, 1/pixelstretch, 1) at hw_openxrdevice.cpp:448,464 is pre-compensation
// for the projection's vertical stretch. Do not "correct" anything handed back
// from ModifyBobLayer3D.
// ============================================================================

class QH_Metric abstract
{
	// Engine defaults, used only when a lookup fails.
	const DEF_UNITS_PER_METRE = 34.0;	// hw_vrmodes.cpp:94
	const DEF_PIXELSTRETCH    = 1.2;	// g_mapinfo.cpp:314

	// ------------------------------------------------------------------------
	// Pure maths. Touches no globals, so it is callable from ui and from play.
	// Callers pass the two scalars from whichever scope they are in; that is
	// deliberate, because reaching for `level` or a CVar from the wrong scope is
	// a compile error in some contexts and a desync risk in others.
	// ------------------------------------------------------------------------

	// A map-space difference vector, expressed in metres.
	clearscope static vector3 ToMetres(vector3 mapvec, double stretch, double unitsPerMetre)
	{
		if (stretch <= 0.0)       stretch = DEF_PIXELSTRETCH;
		if (unitsPerMetre <= 0.0) unitsPerMetre = DEF_UNITS_PER_METRE;

		return (  mapvec.x / unitsPerMetre,
		          mapvec.y / unitsPerMetre,
		         (mapvec.z * stretch) / unitsPerMetre );
	}

	// Distance between two map-space positions, in metres.
	clearscope static double DistMetres(vector3 a, vector3 b, double stretch, double unitsPerMetre)
	{
		return ToMetres(b - a, stretch, unitsPerMetre).Length();
	}

	// The reverse: metres along the three map axes back into map units. For when
	// a measured real-world offset has to be applied to a map position.
	clearscope static vector3 FromMetres(vector3 metres, double stretch, double unitsPerMetre)
	{
		if (stretch <= 0.0)       stretch = DEF_PIXELSTRETCH;
		if (unitsPerMetre <= 0.0) unitsPerMetre = DEF_UNITS_PER_METRE;

		return (  metres.x * unitsPerMetre,
		          metres.y * unitsPerMetre,
		         (metres.z * unitsPerMetre) / stretch );
	}

	// level.pixelstretch -- doombase.zs:366, native readonly float.
	clearscope static double StretchOf(LevelLocals lv)
	{
		double s = lv ? lv.pixelstretch : DEF_PIXELSTRETCH;
		return s > 0.0 ? s : DEF_PIXELSTRETCH;
	}
}


// ----------------------------------------------------------------------------
// Cvar reads, split by scope.
//
// ZScript cannot name a CVARINFO cvar as an identifier; it goes through
// CVar.FindCVar. These wrappers keep that noise in one place and give every
// read a documented fallback, so a missing or malformed cvar degrades to the
// engine default instead of to zero.
//
// vr_vunits_per_meter is a user cvar. Reading a user cvar from playsim is a
// multiplayer desync risk; this pack is local-only by design (see the plan's
// "No multiplayer for now"), and the reload stops must switch off in a netgame
// before that ever changes.
// ----------------------------------------------------------------------------

class QH_CV abstract
{
	ui static double UF(name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	ui static double UI_UnitsPerMetre()
	{
		double u = UF('vr_vunits_per_meter', QH_Metric.DEF_UNITS_PER_METRE);
		return u > 0.0 ? u : QH_Metric.DEF_UNITS_PER_METRE;
	}

	play static int PI(name n, int def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetInt() : def;
	}

	play static double PF(name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	play static double Play_UnitsPerMetre()
	{
		double u = PF('vr_vunits_per_meter', QH_Metric.DEF_UNITS_PER_METRE);
		return u > 0.0 ? u : QH_Metric.DEF_UNITS_PER_METRE;
	}
}
