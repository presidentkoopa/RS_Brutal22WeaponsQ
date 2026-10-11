// RS VR shared helpers (posefix): used by rsvr/melee.zs and rsq/*.zs

// an inventory flag: one of, never dropped
class RSVR_Token : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
	}
}

// a projectile the engine counts as a shot: spawning it buzzes the weapon hand
class RSVR_Buzz : Actor
{
	Default
	{
		Projectile;
		+NOCLIP
		Radius 1;
		Height 1;
		Speed 1;
		DamageType "RSVRHaptic";
		RenderStyle "None";
	}
	States
	{
	Spawn:
		TNT1 A 1;
		Stop;
	}
}
