// Where each gun takes its ammo and where its slide / bolt / pump is, rough by
// design: the radii in rsq/reload.zs (RSQ.AWAY, NEAR, GRAB) are generous.
// rsq_debug 1 prints the off hand's position while a gun waits, to check them
// in the headset. Metres in the gun hand's frame: forward, left, up.
//
// Gun ids are the gate codes' last two digits:
//   1-13   BD22 (tool/weapon_patch.py GUN_IDS)
//   21-25  Vanilla VR Plus (tool/vplus/vplus_patch.py)
// Points were measured on each set's own models (tool/hands/gunview.py side
// views): where the off hand is when the magazine is home (its bottom), the
// shells go in, or the cell / rocket / grenade goes in.
class RSQ_Guns abstract
{
	static Vector3 Well(int gun)
	{
		switch (gun)
		{
		case 1:		return (0.12, 0, -0.20);	// rifle: magazine bottom
		case 2:		return (-0.08, 0, -0.17);	// pistol: under the grip
		case 3:		return (0.09, 0, -0.28);	// SMG: magazine bottom
		case 4:		return (0.30, 0, -0.22);	// MP40: magazine bottom
		case 5:		return (0.07, 0, -0.17);	// sniper: magazine bottom
		case 6:		return (0.15, 0, -0.12);	// assault shotgun: the drum
		case 7:		return (0.08, 0, -0.08);	// shotgun: loading port
		case 8:		return (0.03, 0.04, 0.01);	// revolver: the swung-out cylinder
		case 9:		return (0.03, 0, 0.03);		// SSG: the open breech
		case 10:	return (-0.22, 0.10, 0.10);	// rocket launcher: the drum
		case 11:	return (0.20, 0, -0.13);	// railgun: the cell
		case 12:	return (0.19, 0, -0.20);	// plasma rifle: the cell
		case 13:	return (0.06, 0, 0.03);		// grenade launcher: the open breech

		case 21:	return (0.13, 0, -0.15);	// VVR+ M16: magazine bottom
		case 22:
		case 23:	return (0.18, 0, 0.0);		// VVR+ revolvers: the open cylinder (gun tipped)
		case 24:	return (0.07, 0, -0.03);	// VVR+ pump: loading port
		case 25:	return (0.07, 0, 0.06);		// VVR+ SSG: the open breech
		}
		return (0.10, 0, -0.15);
	}

	// what a rack pulls back
	static Vector3 Handle(int gun)
	{
		switch (gun)
		{
		case 1:		return (-0.06, 0, 0.05);	// rifle: charging handle
		case 2:		return (-0.06, 0, 0.02);	// pistol: rear of the slide
		case 4:		return (0.14, 0.03, 0.01);	// MP40: cocking handle
		case 5:		return (-0.05, 0, 0.06);	// sniper: charging handle
		case 6:		return (0.10, 0.03, 0.02);	// assault shotgun: bolt
		case 7:		return (0.39, 0, -0.024);	// shotgun: the pump

		case 21:	return (0.15, -0.034, 0.052);	// VVR+ M16: charging handle (right side)
		case 24:	return (0.345, 0, 0.013);	// VVR+ pump
		}
		return (0, 0, 0.03);
	}

	static int Carry(int gun)
	{
		switch (gun)
		{
		case 2:		return RSQ.AMMO_PISTOL;
		case 1: case 3: case 4: case 5: case 6: case 21:
					return RSQ.AMMO_RIFLE;
		case 7: case 8: case 24:
					return RSQ.AMMO_SHELL;
		case 9: case 25:
					return RSQ.AMMO_SHELLS;
		case 10: case 13:
					return RSQ.AMMO_ROCKET;
		case 11: case 12:
					return RSQ.AMMO_CELL;
		}
		return RSQ.AMMO_FIST;		// VVR+ revolvers: rounds in a closed hand
	}
}
