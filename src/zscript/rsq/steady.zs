// RS VR steadied aim: the off hand on the forend drives the barrel.
//
// THE PROBLEM. At 6x a 2 mm tremor in your hand is a 12 mm wander in the sight picture, and a
// VR rifle has nothing to brace against -- no sling, no bipod, no cheek weld. Holding a scoped
// rifle steady in mid air is not a skill the game can ask for.
//
// WHAT THIS IS NOT. It does not slow your arm down. It cannot: the controller is where it is,
// and AttackPos / AttackAngle are written by the renderer and are read-only to us.
//
// WHAT IT IS. Put your off hand under the handguard, as you would with a real rifle, and the
// BORE is taken from the line between your two hands instead of from the gun hand's wrist --
// a long baseline instead of a short one, which is exactly why a real support hand steadies a
// rifle. Then a DEADZONE is applied to what is left: movement under the threshold is damped
// hard, movement over it passes at 1:1. That is deliberately not a low-pass filter -- a filter
// buys steadiness with lag, so swinging to a new target arrives late and reads as a broken
// gun. A deadzone is dead still when you hold and instant when you mean it.
//
// WHERE IT SHOWS. The gun model cannot move: hw_weapon.cpp:946 takes ModifyBobLayer3D from
// each layer's own caller, and a host-mod gun is a DECORATE actor that cannot override a
// ZScript virtual. So the rifle keeps shaking with your hand -- honestly, because your hand IS
// shaking -- while the SIGHT is steady. That is a gimbal-stabilised optic, which is a real
// thing, rather than pretending your arm got better.
//
// Engaged by holding the gun's secondary fire AND having the off hand near the forend. Both:
// the button alone would be an accuracy button, and the posture alone would fire by accident.

class RSQ_SteadyTable abstract
{
	// Where the support hand belongs, per gun: the underside of the handguard, measured from
	// the mesh (F 20..34, lower 45% of those vertices) in the weapon controller's frame.
	clearscope static Vector3 Forend(int i)
	{
		static const double f[] = { 0, 0.00, 27.14 };
		static const double l[] = { 0, 0.00,  0.38 };
		static const double u[] = { 0, 0.00,  3.04 };
		return i > 0 && i < f.Size() ? (f[i], l[i], u[i]) : (0, 0, 0);
	}

	// How close the off hand has to be to count as supporting it. Generous: failing to engage
	// while the player IS holding the rifle properly is far worse than engaging a little early.
	clearscope static double Reach(int i)
	{
		static const double v[] = { 0, 0.0, 14.0 };
		return i > 0 && i < v.Size() ? v[i] : 0;
	}
}

class RSQ_Steady : EventHandler
{
	// the filtered bore, per player, in the weapon controller's frame
	private Vector3 aim[MAXPLAYERS];
	private bool have[MAXPLAYERS];
	private bool on[MAXPLAYERS];

	const DEAD = 0.9;			// degrees: wander under this is damped to almost nothing
	const SOFT = 0.12;			// what fraction of it still gets through, so it never feels locked
	const SNAP = 6.0;			// degrees: past this it is a deliberate move and passes at 1:1

	clearscope static RSQ_Steady Get()
	{
		return RSQ_Steady(EventHandler.Find('RSQ_Steady'));
	}

	// Is this player's sight steadied right now? The scope layer and the dot ask this so the
	// three can never disagree about where the gun is pointing.
	clearscope static bool Active(PlayerPawn mo)
	{
		let h = Get();
		if (!h || !mo || !mo.player)
			return false;
		int n = mo.PlayerNumber();
		return n >= 0 && n < MAXPLAYERS && h.on[n];
	}

	// The steadied bore, or the raw one when it is not engaged.
	clearscope static Vector3 Bore(PlayerPawn mo, Vector3 raw)
	{
		let h = Get();
		if (!h || !mo || !mo.player)
			return raw;
		int n = mo.PlayerNumber();
		if (n < 0 || n >= MAXPLAYERS || !h.on[n] || !h.have[n])
			return raw;
		return h.aim[n];
	}

	// the two-hand baseline: from the gun hand to the off hand, which is the line a braced
	// rifle actually points along
	private static Vector3 Braced(PlayerPawn mo, int si)
	{
		// in the GUN'S OWN frame, the same space RSQ_ScopeTable.Axis is measured in, so the
		// steadied bore can be dropped straight into the dot's maths
		Vector3 d = RSQ_Scope.OffInHandFrame(mo);
		double l = d.Length();
		if (l < 8.0)			// hands together: no baseline worth having
			return (0, 0, 0);
		return d / l;
	}

	override void WorldTick()
	{
		for (int n = 0; n < MAXPLAYERS; n++)
		{
			if (!playeringame[n] || !players[n].mo)
			{
				have[n] = false;
				on[n] = false;
				continue;
			}
			let mo = players[n].mo;
			let p = mo.player;
			int si = RSQ_ScopeTable.Index(p.ReadyWeapon);
			bool vr = RSVR_VRHand.InVR(mo);
			// the gun offers it, the player asked for it, and the off hand is where it belongs
			bool want = vr && si > 0 && RSQ_SteadyTable.Reach(si) > 0
				&& (p.cmd.buttons & BT_ALTATTACK) != 0
				&& OffHandOnForend(mo, si);
			if (!want)
			{
				on[n] = false;
				have[n] = false;
				continue;
			}

			Vector3 raw = Braced(mo, si);
			if (raw == (0, 0, 0))
			{
				on[n] = false;
				have[n] = false;
				continue;
			}
			on[n] = true;
			if (!have[n])
			{
				aim[n] = raw;
				have[n] = true;
				continue;
			}

			// THE DEADZONE. How far has the bore moved since last tic?
			double c = clamp(aim[n] dot raw, -1.0, 1.0);
			double deg = acos(c);
			double k;
			if (deg <= DEAD)
				k = SOFT;							// tremor: almost none of it gets through
			else if (deg >= SNAP)
				k = 1.0;							// a real swing: all of it, with no lag
			else
				k = SOFT + (1.0 - SOFT) * (deg - DEAD) / (SNAP - DEAD);
			Vector3 v = aim[n] + (raw - aim[n]) * k;
			double vl = v.Length();
			// a real if: a ternary does not short-circuit in the JIT, so the division runs
			// even on the branch that is not taken
			if (vl > 0)
				aim[n] = v / vl;
			else
				aim[n] = raw;
		}
	}

	// the off hand within Reach of the gun's forend point, in the gun's own frame
	private static bool OffHandOnForend(PlayerPawn mo, int si)
	{
		Vector3 fe = RSQ_SteadyTable.Forend(si);
		Vector3 off = RSQ_Scope.OffInHandFrame(mo);
		return (off - fe).Length() <= RSQ_SteadyTable.Reach(si);
	}
}
