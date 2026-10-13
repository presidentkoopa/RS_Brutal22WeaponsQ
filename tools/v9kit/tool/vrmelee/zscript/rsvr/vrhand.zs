// RS VR melee -- where the weapon hand is (QuestZDoom 17.3 fields, read only).
//
// QZD sets these on the player every frame (hw_openxrdevice.cpp / gl_openvr.cpp):
//   AttackPos            the weapon controller, world position
//   AttackDir(mo, a, p)  a direction in the controller's own frame, returned as
//                        (angle, pitch, 0); relative yaw 0 / pitch 0 = forward,
//                        yaw +90 = left, pitch +90 = up (MapWeaponDir)
//   OffhandPos           the other controller, world position
//   OverrideAttackPosDir true while playing in VR
// The held model hangs off the same transform (models.cpp RenderHUDModel), so a
// point of the model can be placed in the world exactly where it is drawn.
// This is the only file that touches QZD's own fields.

class RSVR_VRHand play
{
	// playing in VR with the weapon following the controller
	static bool InVR(PlayerPawn mo)
	{
		return mo && mo.player && mo.player.PlayInVR && mo.OverrideAttackPosDir;
	}

	// the weapon controller, world position
	static Vector3 HandPos(PlayerPawn mo)
	{
		return mo.AttackPos;
	}

	// the other controller, world position (rsq/reload.zs, rsq/hands.zs)
	static Vector3 OffPos(PlayerPawn mo)
	{
		return mo.OffhandPos;
	}

	// unit vector of a direction in the controller's frame (yaw 0 pitch 0 =
	// forward, yaw 90 = left, pitch 90 = up), with the hand transform's vertical
	// squash (1 / pixelstretch) taken back out
	static Vector3 HandDir(PlayerPawn mo, double yaw, double pitch, double ps)
	{
		Vector3 ap = mo.AttackDir(mo, mo.angle + yaw, mo.pitch + pitch);
		double cp = cos(ap.y);
		Vector3 v = (cp * cos(ap.x), cp * sin(ap.x), -sin(ap.y) * ps);
		double l = v.Length();
		if (l <= 0)
			return (1, 0, 0);
		return v / l;
	}
}
