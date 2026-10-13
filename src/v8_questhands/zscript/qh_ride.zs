// ============================================================================
// RS_QuestHands -- step 3: the support hand rides the magazine
//
// THE PROBLEM
//   The magazine is a surface of the gun's own mesh, moved by vertex animation.
//   Stock QZD gives script no way to ask where it is: no bone control of any
//   kind, and one rigid transform per layer. So its position is measured ONCE,
//   offline, per frame, and replayed here.
//
//   Measured with tools/md3_part_track.py against
//   FILTER/DOOM/models/weapons/hud/guns/m16.md3 -- 41 frames, 4 surfaces.
//   The magazine is 'weapon.005' (73 verts), identified by being the only
//   surface that travels: Y from -8.2 seated to -21.6 out and back. Not by its
//   name, which is 'weapon.005'.
//
// WHAT THE NUMBERS SHOWED THAT READING THE DECORATE DID NOT
//   RIFK A-I is model frames 26-34, and the obvious reading is that the insert
//   runs 26->34. It does not. At frame 27 the magazine's X jumps 27.25 -> 30.32
//   and Y drops to -29.9: that is a CUT. Frames 24-26 are the OLD magazine
//   falling away; frame 27 is the NEW one appearing down at the hand. From 27 it
//   climbs monotonically to seated at 34.
//
//   So the hand rides 27 -> 34 (RIFK B through RIFK I), eight frames at 2 tics
//   = 16 tics, about 0.46 s. Riding from 26 would snap the hand across the cut.
//
// HOW IT STAYS IN STEP WITH THE GUN
//   The engine's own blend is models.cpp:379:
//     inter = (curState->Tics - curTics + ticFraction) / curState->Tics
//   and its ticFraction is zeroed whenever a blocking menu is open, the console
//   is down, or the level is frozen (models.cpp:373-378) -- while the hook's
//   ticfrac is not. Per the plan's step 3 decision we reconstruct inter WITHOUT
//   the tic fraction and step at 35 Hz, which matches what the engine draws when
//   it freezes. A hand that steps is better than a hand that detaches.
// ============================================================================

// A CLASS AND NOT A STRUCT: ZScript's dynamic array cannot hold a struct, so
// `Array<QH_RideKey>` refuses to compile and takes QH_RideTrack down with it.
// See the same note on QH_Stop in qh_reload.zs.
class QH_RideKey
{
	int frame;			// model frame
	vector3 pos;		// magazine centroid, MODEL UNITS, hook axis order
}


class QH_RideTrack
{
	Name weaponClass;
	double modelScale;		// MODELDEF Scale. VR_Rifle is 1.35 uniform.
	int firstFrame;			// first ridable frame
	int lastFrame;			// last ridable frame
	Array<QH_RideKey> keys;

	static QH_RideTrack Make(Name cls, double scale, int first, int last)
	{
		let t = new("QH_RideTrack");
		t.weaponClass = cls;
		t.modelScale = scale;
		t.firstFrame = first;
		t.lastFrame = last;
		return t;
	}

	void Key(int frame, double x, double y, double z)
	{
		let k = new("QH_RideKey");
		k.frame = frame;
		k.pos = (x, y, z);
		keys.Push(k);
	}

	bool Covers(int frame) const
	{
		return frame >= firstFrame && frame <= lastFrame;
	}

	// Exact measured position for one frame, already scaled into the hook's
	// translation space. Returns false if that frame was never measured.
	bool, vector3 At(int frame) const
	{
		for (int i = 0; i < keys.Size(); i++)
			if (keys[i].frame == frame)
				return true, keys[i].pos * modelScale;
		return false, (0, 0, 0);
	}

	// Position between two frames. `inter` is the engine's blend fraction,
	// reconstructed without the tic fraction.
	bool, vector3 Between(int frame, double inter) const
	{
		bool okA, okB;
		vector3 a, b;
		[okA, a] = At(frame);
		if (!okA) return false, (0, 0, 0);

		[okB, b] = At(frame + 1);
		if (!okB) return true, a;		// last measured frame: sit on it

		if (inter < 0.0) inter = 0.0;
		if (inter > 1.0) inter = 1.0;

		return true, a + (b - a) * inter;
	}
}


// ----------------------------------------------------------------------------
// The ride service. Lives in play scope and is ticked from QH_Hands' Ready
// loop; the hook reads its result. ui may read play data, so the sprite and
// frame resolution all happens here once per tic instead of twice per eye per
// rendered frame.
// ----------------------------------------------------------------------------

class QH_RideService
{
	Array<QH_RideTrack> tracks;

	// Published for the hook.
	bool riding;			// is the support hand on the magazine right now
	vector3 ridePos;		// where, in the hook's translation space

	// Sprite index of the run the ride frames live in, resolved once.
	int rideSprite;
	Name rideOwner;
	int rideSpriteBase;		// model frame of that run's frame 0

	// ------------------------------------------------------------------------
	// VR_Rifle. Every row measured, none guessed.
	//
	//   python tools/md3_part_track.py m16.md3 --surface weapon.005 --frames 24-40
	//
	// Model units, hook axis order (X right, Y up, Z back). Scale 1.35 is
	// applied at read time, not baked in, so the table stays comparable to the
	// tool's output.
	// ------------------------------------------------------------------------

	void Init()
	{
		riding = false;
		ridePos = (0, 0, 0);
		rideSprite = -1;
		rideOwner = 'None';
		rideSpriteBase = 0;

		// RIFK A-O is model frames 26-40. The ride is 27-34: frame 26 is the
		// old magazine, frame 27 is the new one appearing at the hand.
		let r = QH_RideTrack.Make('VR_Rifle', 1.35, 27, 34);
		r.Key(26, 27.250, -21.047, 0.000);	// RIFK A -- old mag, NOT ridden
		r.Key(27, 30.320, -29.919, 0.000);	// RIFK B -- new mag at the hand
		r.Key(28, 30.461, -28.796, 0.000);	// RIFK C
		r.Key(29, 30.796, -25.864, 0.000);	// RIFK D
		r.Key(30, 31.187, -21.770, 0.000);	// RIFK E
		r.Key(31, 31.526, -17.179, 0.000);	// RIFK F
		r.Key(32, 31.747, -12.759, 0.000);	// RIFK G
		r.Key(33, 31.827,  -9.186, 0.000);	// RIFK H
		r.Key(34, 31.770,  -7.395, 0.000);	// RIFK I -- seated
		tracks.Push(r);
	}

	QH_RideTrack TrackFor(Actor weap) const
	{
		if (!weap) return null;
		Name cn = weap.GetClassName();
		for (int i = 0; i < tracks.Size(); i++)
			if (tracks[i].weaponClass == cn)
				return tracks[i];
		return null;
	}

	// The ride frames sit in the second sprite run of the reload chain (RIFK for
	// the rifle). Resolve that sprite index once per weapon by walking the chain
	// until the sprite changes, rather than hardcoding an index we cannot name.
	play void ResolveRideSprite(Actor weap, QH_ReloadCard card)
	{
		if (rideOwner == card.weaponClass) return;

		rideOwner = card.weaponClass;
		rideSprite = -1;
		rideSpriteBase = 0;

		State st = weap.FindStateByString("" .. card.reloadLabel, false);
		int first = -1;
		int guard = 0;

		while (st && guard < 256)
		{
			if (st.Tics > 0)
			{
				if (first < 0)
				{
					first = st.sprite;
				}
				else if (st.sprite != first)
				{
					rideSprite = st.sprite;
					// That run's frame 0 is the model frame after the first
					// run ends. For the rifle: RIFL is 0-25, so RIFK A is 26.
					rideSpriteBase = 26;
					return;
				}
			}
			st = st.NextState;
			guard++;
		}
	}

	play void Tick(PlayerInfo p, QH_ReloadCard card)
	{
		riding = false;

		if (!p || !p.mo || !card) return;

		let weap = p.ReadyWeapon;
		let track = TrackFor(weap);
		if (!track) return;

		let psp = p.FindPSprite(PSP_WEAPON);
		if (!psp || !psp.CurState) return;

		ResolveRideSprite(weap, card);
		if (rideSprite < 0) return;
		if (psp.CurState.sprite != rideSprite) return;

		int modelFrame = rideSpriteBase + psp.CurState.Frame;
		if (!track.Covers(modelFrame)) return;

		// The engine's blend fraction, without the tic fraction. See the header.
		double stateTics = psp.CurState.Tics;
		double inter = 0.0;
		if (stateTics > 0.0)
		{
			inter = (stateTics - psp.Tics) / stateTics;
			if (inter < 0.0) inter = 0.0;
			if (inter > 1.0) inter = 1.0;
		}

		bool ok;
		vector3 pos;
		[ok, pos] = track.Between(modelFrame, inter);
		if (!ok) return;

		// NOTE: qh_ride_* is NOT added here. Where in the hand the magazine sits
		// is per-player placement, so it is a user cvar and is applied in the ui
		// hook. Reading it in play would drag a per-player value into the
		// simulation for no benefit -- this service publishes the magazine's
		// own position and nothing else.
		ridePos = pos;
		riding = true;
	}
}
