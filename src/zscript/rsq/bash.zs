// bash.zs: the MELEE HIT FLASH (RSQ_BashFX). It began with the 1.97 kick-key gun bash; the bash itself is gone
// (2.0.2, owner r3 item 39: "I asked for a pistol whip"), the flash stays on every melee hit (melee.zs).
//
// 2.0.2 (owner r3 item 36: "way, way too large"): a small spark at the contact point. MEASURED on the art
// (the brightest-channel x alpha > 40 bounding box over every frame, tools/optmelee/fxsize.py): RSS3 206 px,
// RSU1 60, RSU4 15, RSU5 103, RSH0 79. At 1.97's scales (art drawn at the 96 px standard) that is 79, 96, 96,
// 88 and 79 MAP UNITS across -- 2.3 to 2.8 m at 34 units a metre. Each is now scaled to SPARK map units
// (13, about 38 cm: one sixth of what it was), centred where the blow landed.

// the impact: the effect the owner picked, at the point the blow landed (melee.zs WorldThingDamaged);
// this picks which of the five to draw, and tints it.
class RSQ_BashFX : Actor
{
	Default { +NOINTERACTION; +NOBLOCKMAP; +DONTSPLASH; RenderStyle "Add"; Alpha 1.0; }

	override void PostBeginPlay()
	{
		Super.PostBeginPlay();
		// 2.0.3d (owner 21:53, "add option for melee hit flash on off"): Off draws nothing
		if (RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_flash', 1) == 0)
		{
			Destroy();
			return;
		}
		int n = RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_fx', 0);
		static const Name FXC[] = { 'RSQ_FX_RSS3', 'RSQ_FX_RSU1', 'RSQ_FX_RSU4', 'RSQ_FX_RSU5', 'RSQ_FX_RSH0' };
		if (n < 0 || n >= 5)
			n = 0;
		let a = Spawn(FXC[n], pos, ALLOW_REPLACE);
		if (a)
		{
			a.target = target;
			int t = RSQ.PlayerInt(PlayerPawn(target), 'rsq_bash_tint', 0);
			// r6 (owner item 17): the colour is assignable on every effect, not only RSH0 -- the
			// tints are a luminance ramp (TRNSLATE.rsq), so they recolour any of the five
			// r6b: a translation does nothing on these truecolor PNGs on QZD's renderer (rig frames:
			// tints 1-4 drew as the art). AddShaded draws the art's brightness in one colour, which
			// is the tint. Colours as TRNSLATE.rsq's RSQ_BashTint1-4 ramps' top ends.
			static const int TC[] = { 0, 0x50AAFF, 0x5AFF78, 0xFFBE46, 0xFFFFFF };
			if (t > 0 && t < 5)
			{
				a.A_SetRenderStyle(1.0, STYLE_AddShaded);
				a.SetShade(TC[t]);
			}
		}
		Destroy();
	}
}

class RSQ_FXBase : Actor
{
	const SPARK = 13;	// map units across, the visible art (see the head of this file)
	Default { +NOINTERACTION; +NOBLOCKMAP; +DONTSPLASH;
		+FORCEXYBILLBOARD; RenderStyle "Add"; Alpha 1.0; }
}
class RSQ_FX_RSS3 : RSQ_FXBase
{
	Default { Scale 0.0631; }	// 206 px visible -> RSQ_FXBase.SPARK (13) map units (1.97: 0.384)
	States
	{
	Spawn:
		RSS3 ABCDEFG 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSU1 : RSQ_FXBase
{
	Default { Scale 0.2167; }	// 60 px visible -> RSQ_FXBase.SPARK (13) map units (1.97: 1.600)
	States
	{
	Spawn:
		RSU1 ABCD 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSU4 : RSQ_FXBase
{
	Default { Scale 0.8667; }	// 15 px visible -> RSQ_FXBase.SPARK (13) map units (1.97: 6.400)
	States
	{
	Spawn:
		RSU4 ABCD 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSU5 : RSQ_FXBase
{
	Default { Scale 0.1262; }	// 103 px visible -> RSQ_FXBase.SPARK (13) map units (1.97: 0.857)
	States
	{
	Spawn:
		RSU5 ABCDEFGHIJ 2 Bright;
		Stop;
	}
}
class RSQ_FX_RSH0 : RSQ_FXBase
{
	Default { Scale 0.1646; }	// 79 px visible -> RSQ_FXBase.SPARK (13) map units (1.97: 1.000)
	States
	{
	Spawn:
		RSH0 ABCDEFGHIJKLMNOPQRS 2 Bright;
		Stop;
	}
}
