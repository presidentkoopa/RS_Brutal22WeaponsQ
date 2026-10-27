// BD 2.0 Player Ballistics (zscript/rsq/playerrounds.zs): the player's round in flight, in Bullet
// mode. The same eight btracer.obj calibres as RSQ_Bullet (MODELDEF.rsbullet), same frames, so a
// gun's round looks the same whichever way it is fired. RSBM is the 1x1 clear mount sprite.

Model RSQ_PlayerRound	// pistol -- a 9mm, .45 or .38 in flight: a short thin dart
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.2500 0.2286 0.2286
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM A 0 0
}

Model RSQ_PlayerRound	// smg -- the same round out of a submachine gun
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.3250 0.2714 0.2714
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM B 0 0
}

Model RSQ_PlayerRound	// intermediate -- 5.56, 7.92 Kurz: the assault-rifle streak
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.4250 0.2857 0.2857
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM C 0 0
}

Model RSQ_PlayerRound	// rifle -- full-power: 7.62, .30-06, 7.62x54R
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.5750 0.3286 0.3286
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM D 0 0
}

Model RSQ_PlayerRound	// heavy -- 9.3x74R and the extreme machine-gun look
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.7250 0.4143 0.4143
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM E 0 0
}

Model RSQ_PlayerRound	// pellet -- one pellet of buckshot: a stub
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.1250 0.1714 0.1714
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM F 0 0
}

Model RSQ_PlayerRound	// tracer -- long and bright, the round you are meant to read
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 0.8000 0.4571 0.4571
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM G 0 0
}

Model RSQ_PlayerRound	// tracerheavy -- the mesh at its full authored size
{
	Path "models/rsb"
	Model 0 "btracer.obj"
	SurfaceSkin 0 0 "btracer.png"
	Scale 1.0000 0.5571 0.5571
	DontCullBackfaces
	USEACTORPITCH
	USEACTORROLL
	FrameIndex RSBM H 0 0
}

