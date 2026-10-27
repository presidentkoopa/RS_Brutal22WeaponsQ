// RS VR scopes: a sight that can be put on any gun that has one in its mesh.
//
// Two modes per gun (MENUDEF.rsq -> rsq_scope_<gun>):
//   DOT   a collimated red dot over the view down the bore at 1x (1.99x r6: see-through).
//   REAL  the view down the bore at 3x, rendered into the scope's own glass surface.
// Both cost one extra scene render, and only while an eye is at the eyepiece (scope_real.zs).
//
// THE DOT IS COLLIMATED, and that is the whole point of it. A reticle painted on the glass
// has full parallax: move your head and the dot slides off what the gun is pointing at, which
// is backwards -- a real reflex sight shows the dot in the same place whatever your eye does.
// So the dot is not painted on the glass. Each rendered frame it is placed at the point D on
// the lens plane where the eye-to-dot ray runs parallel to the bore:
//
//     D = E + A * ((P - E) dot A)          E eye, A bore axis, P a point on the lens plane
//
// The dot therefore slides across the glass as the head moves and the sight picture stays
// true. It is two dot products and a scale, once per frame, in the hook the renderer already
// calls -- ModifyBobLayer3D, which is ui scope and per FRAME, not per tic. That matters: a
// dot placed from a tic-rate sample would visibly lag the head.
//
// Per gun this needs four measured numbers and nothing else (RSQ_ScopeTable), so a scope is a
// component and not a per-weapon special case. The railgun's mesh already carries its glass as
// its own surface ("ScopeGlass", 18 verts); the Ruger's ocular disc is carved out of the scope
// surface by the kit so it has one too.
//
// Everything here is inert until a gun is in the table, and out of VR nothing runs at all.

class RSQ_ScopeLayers abstract
{
	// 2112, NOT 2102: RSR.WELLMAG is 2102 (rsr/vreload.zs:24) -- the magazine at the well --
	// and RSR_Guns has RailGun at 6 and Sniper at 8, so both scoped guns already use that id
	// for their VR reload. One psprite id holds one caller; sharing it would have killed the
	// reload on exactly the two guns getting scopes. Taken in the pack: 2100-2111, 2120-2123,
	// 2130-2131, 2200-2203, 2210, 2300-2301. Free: 2112-2119, 2124-2129.
	const RETICLE = 2112;		// RSQ_GunSide, main controller: the collimated reticle
}

class RSQ_ScopeTable abstract
{
	// Measured at each gun's READY frame through the model chain (rgeo.py), centimetres in
	// the weapon controller's frame: F forward, L left, U up.
	//   lens    the centre of the glass
	//   axis    down the bore, unit
	//   radius  the glass, so the dot can be clipped to it instead of floating off the tube
	//   mag     magnification for REAL mode; the DOT never magnifies
	clearscope static int Index(Weapon w)
	{
		if (!w)
			return 0;
		Name n = w.GetClassName();
		if (n == 'RailGun')	return 1;
		if (n == 'Sniper')	return 2;
		return 0;
	}

	clearscope static Vector3 Lens(int i)
	{
		static const double f[] = { 0, 2.756, -0.300 };
		static const double l[] = { 0, 0.416, 0.250 };
		static const double u[] = { 0, 16.469, 9.240 };
				// r9 port: Lens 1 moved with the gun to the FBX hand (was -1.7100 -0.0900 11.8100)
		return i > 0 && i < f.Size() ? (f[i], l[i], u[i]) : (0, 0, 0);
	}

	clearscope static Vector3 Axis(int i)
	{
		static const double f[] = { 0, 0.9940, 1.0000 };
		static const double l[] = { 0, 0.0787, -0.0040 };
		static const double u[] = { 0, 0.0764, 0.0038 };
				// r9 port: Axis 1 moved with the gun to the FBX hand (was 0.9998 0.0149 0.0152)
		return i > 0 && i < f.Size() ? (f[i], l[i], u[i]) : (1, 0, 0);
	}

	clearscope static double Radius(int i)
	{
		static const double v[] = { 0, 1.78, 1.35 };
		return i > 0 && i < v.Size() ? v[i] : 0;
	}

	clearscope static double Mag(int i)
	{
		static const double v[] = { 0, 3.0, 3.0 };	// 1.99x r6: 3x (owner); see scope_real.zs FovFor
		return i > 0 && i < v.Size() ? v[i] : 1.0;
	}

	// the cvar that chooses this gun's mode: 0 dot, 1 real
	clearscope static Name ModeCVar(int i)
	{
		static const Name v[] = { 'none', 'rsq_scope_railgun', 'rsq_scope_sniper' };
		return i > 0 && i < v.Size() ? v[i] : 'none';
	}
}

class RSQ_Scope abstract
{
	const DOT_LIFT = 0.25;	// cm the dot sits in front of the glass, toward the eye
	// The hand's own axes, built from the Euler angles the renderer wrote this frame.
	// CLEARSCOPE, deliberately: nothing here calls a native: AttackAngle / AttackPitch /
	// AttackRoll are plain readable fields and the rest is trig. So the renderer hook (ui, per
	// frame) and the layer-state chooser (play, per tic) share ONE implementation instead of
	// the play side needing a second copy to decide whether to show the reticle at all. AttackDir() cannot be called from ui (it is a play method on Actor), but the
	// ANGLES are plain fields and ui may read play data -- so the basis is rebuilt here with
	// trig instead. AttackAngle is the world yaw MINUS 90 (p_map.cpp adds the 90 back
	// everywhere it uses it); AttackPitch is positive up.
	// F11: RETURNS the three axes. An `out Vector3` parameter aborts the VM the first time it is
	// called (qzd17.3 vmexec.h:828-830, "REGT_ADDROF not implemented for vectors").
	clearscope static Vector3, Vector3, Vector3 Basis(PlayerPawn mo)
	{
		Vector3 fwd, right, up;
		double yaw = mo.AttackAngle + 90.0;
		// 1.99x r6: NOT negated. On QZD 17.3 AttackPitch is positive UP (the hand pitched 20
		// up logs AttackPitch 20 and AttackDir z +0.342). With the old minus, and r0 below
		// pointing left, the basis matched the engine's at no pose at all. This basis now matches the play side's AttackDir axes to four
		// decimals at three logged poses (yaw/pitch/roll mixed; HANDOFF r6-scope).
		double pit = mo.AttackPitch;
		double rol = mo.AttackRoll;
		double cy = cos(yaw), sy = sin(yaw), cp = cos(pit), sp = sin(pit);
		fwd = (cp * cy, cp * sy, sp);
		// 1.99x r6: this was (-sy, cy, 0), which is LEFT, so right and up both came out
		// negated and every eye landed on the mirror image of the lens: DotAt never had a
		// sight picture and the dot never drew (rig log, HANDOFF r6-scope).
		Vector3 r0 = (sy, -cy, 0);
		// roll the right/up pair about the forward axis
		double cr = cos(rol), sr = sin(rol);
		Vector3 u0 = (r0 cross fwd);	// up at zero roll
		right = r0 * cr - u0 * sr;		// positive AttackRoll tips the right side down
		up = (right cross fwd);
		return fwd, right, up;
	}

	// THE EYE, IN THE WORLD, the way the renderer places it. 1.99x r6: this was the pawn's XY at
	// p.viewz, and that is not where either eye is, which is why neither mode ever worked in a
	// headset (shown on the rig, HANDOFF r6-scope):
	//   HEIGHT  with vr_crouch_use_button on (the QZD default, hw_vrmodes.cpp:122) viewz stays at
	//           the pawn's ViewHeight and the headset's real height is added afterwards, in
	//           OpenXRDeviceEyePose::GetViewShift (hw_openxrdevice.cpp:219):
	//               + (hmdPosition.y + vr_height_adjust) * vu / ps - ViewHeight
	//           The hand is placed from the controller's absolute height (AttackPos.Z,
	//           hw_openxrdevice.cpp:595, weaponoffset = controller - hmd, VrInputDefault.cpp:148),
	//           so with the old eye the gate was off by the player's height minus the pawn's:
	//           16 cm on the rig. QZD hands script the head as Actor.HmdPosition (actor.zs:277,
	//           written each frame at hw_vrmodes.cpp:445).
	//   SIDE    the two eyes are vr_ipd/2 either side of that centre (GetViewShift, eye 0 = left
	//           = -right). 3.2 cm, against a 1.35 cm lens: the centre point can NEVER be behind
	//           the glass while an eye is, so both gates were shut for good.
	// side: -1 left eye, +1 right eye, 0 the centre between them.
	clearscope static Vector3 EyeWorld(PlayerPawn mo, int side)
	{
		let p = mo.player;
		if (!p)
			return mo.pos;
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		double vu = CVarF('vr_vunits_per_meter', 34);
		if (vu <= 0)
			vu = 34;
		Vector3 eye = (mo.pos.x, mo.pos.y, p.viewz);
		let cb = CVar.FindCVar('vr_crouch_use_button');
		if (!cb || cb.GetBool())
			eye.z += (mo.HmdPosition.y + CVarF('vr_height_adjust', 0)) * vu / ps - mo.ViewHeight;
		if (side != 0)
		{
			double half = CVarF('vr_ipd', 0.064) * 0.5 * vu * side;
			eye += (sin(mo.angle), -cos(mo.angle), 0) * half;	// the view's right
		}
		return eye;
	}

	clearscope static double CVarF(Name n, double def)
	{
		let cv = CVar.FindCVar(n);
		return cv ? cv.GetFloat() : def;
	}

	// Where an eye is, in the hand's own frame, in centimetres.
	clearscope static Vector3 EyeInHandFrame(PlayerPawn mo, int side = 0)
	{
		let p = mo.player;
		if (!p)
			return (0, 0, 0);
		Vector3 eye = EyeWorld(mo, side);
		Vector3 d = eye - mo.AttackPos;
		double ps = mo.Level.pixelstretch;
		if (ps <= 0)
			ps = 1.2;
		d.z *= ps;				// undo the vertical squash the hand transform applies
		double vu = 34.0;
		let cv = CVar.FindCVar('vr_vunits_per_meter');
		if (cv && cv.GetFloat() > 0)
			vu = cv.GetFloat();
		Vector3 f, r, u;
		[f, r, u] = Basis(mo);
		// map units -> cm in the hand frame
		return ((d dot f) * 100.0 / vu, -(d dot r) * 100.0 / vu, (d dot u) * 100.0 / vu);
	}

	// The collimated dot's position on the lens plane, in the hand frame, cm.
	// D = E + A * ((P - E) dot A), then clipped to the glass so it never leaves the tube.
	clearscope static Vector3, bool DotAt(PlayerPawn mo, int i)
	{
		Vector3 P = RSQ_ScopeTable.Lens(i);
		Vector3 A = RSQ_ScopeTable.Axis(i);
		double al = A.Length();
		if (al <= 0)
			return P, false;
		A = A / al;
		// The sighting eye is whichever eye is nearer the bore line; the dot is collimated for
		// that one (the other is behind the tube or looking past it).
		Vector3 E = EyeInHandFrame(mo, -1);
		Vector3 Er = EyeInHandFrame(mo, 1);
		Vector3 tl = P - E, tr = P - Er;
		if ((tr - A * (tr dot A)).Length() < (tl - A * (tl dot A)).Length())
			E = Er;
		Vector3 D = E + A * ((P - E) dot A);
		// off the glass: the eye is not behind the sight, so show nothing rather than a dot
		// stuck to the rim
		Vector3 off = D - P;
		double rr = RSQ_ScopeTable.Radius(i);
		double side = (off - A * (off dot A)).Length();
		if (rr > 0 && side > rr)
			return D, false;
		// behind the glass (looking at the objective end) is not a sight picture either
		if (((P - E) dot A) <= 0)
			return D, false;
		// 1.99x r6: lifted off the glass toward the eye. On the lens plane itself the quad is
		// coplanar with the glass surface and loses the depth test to it: the rig drew the
		// glass and no dot at all with D exactly on the plane.
		return D - A * DOT_LIFT, true;
	}

	// Play-callable: is there a sight picture at all this frame? The layer chooser uses this to
	// pick the Hidden state, instead of flinging the quad off-screen to make it disappear.
	clearscope static bool DotOk(PlayerPawn mo, int i)
	{
		if (!mo || !mo.player || i <= 0)
			return false;
		Vector3 d;
		bool ok;
		[d, ok] = DotAt(mo, i);
		return ok;
	}
}
