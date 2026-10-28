// BD 2.0 (zscript/rsq/playerrounds.zs). Options: RSQ_Options in MENUDEF.rsq.

// "True Bullets: On / Off" (owner, 2026-10-28 18:24, r3 item 39: "If we are using True Bullet On/Off, then Off
// uses stock BD22 hitscan and tracers"). ONE switch for how the player's shots work and look:
//   On  = the player's hitscans fly as real rounds (zscript/rsq/playerrounds.zs) with the Dakka look: tracer
//         dots behind each round, the impact sparks and puff (zscript/rsq/shotfx.zs, Dakka by ijon).
//   Off = BD22 as it ships: hitscan, BD22's own tracers, puffs and the Ruger's rail trail, and no Dakka effect.
// Replaces sv_rsq_player_ballistics (Hitscan / Bullet) and rsq_shot_tracers (Off / Dakka): a separate tracer
// switch no longer exists. Default On (the owner liked the Dakka look, 2026-10-27 20:02-21:2x). A NEW NAME on
// purpose: an ini saved by 2.0.1 holds sv_rsq_player_ballistics=0, which would otherwise hide the new default.
// A server cvar: it decides where shots go, and the sparks are real actors using playsim random numbers.
server bool sv_rsq_true_bullets = true;

// "Pump Shotgun Spread: Stock / Enhanced" (owner's label, 2026-10-27 20:02). Stock = BD22's Shot_Gun spread;
// Enhanced = Dakka's shotgun pattern, 3 deg across x 2.5 deg up/down, same pellets and damage
// (actors/Weapons/Shotgun.dec). Server: it decides where shots go.
server int rsq_pump_spread = 0;

// "Hand Skin Tone" (owner, 2026-10-27 20:05): 0 = the FBX hands as drawn, 1..17 = tools/handtones.py's tones
// (zscript/rsq/handtone.zs). Local: your own hands.
user int rsq_hand_tone = 0;
