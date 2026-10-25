![BD22 VR Weapons](renders/hero.gif)

# BD22 VR Weapons

![BD22 VR Weapons options menu](renders/options_menu.png)

Coordinated, directed and tested by PresidentKoopa, coded by Claude.

VR weapon pack for **Brutal Doom v22** (`brutal22test6.pk3`) on **QuestZDoom 17.x**. Stock
engine, no engine changes. Fire each gun independently in dual-wield mode.

Download from the Releases page. Load it after `brutal22test6.pk3` and the Voxel pack.

## Models for
Pistol, Revolver, SMG, MP40\*\*, Rifle, Shotgun, Super shotgun, Assault shotgun, Minigun,
MG42 buzzsaw\*\*, Grenade launcher, Incendiary launcher, Rocket launcher, Nuke launcher,
Devastator\*\*, Hellish missile launcher\*\*, Plasma gun, Railgun, BFG, BFG10k, Unmaker,
Flamethrower, Flame cannon\*\*, Axe, Chainsaw, Fists, Grenades

\*\* = hidden from the player's roster. Turn on "Allow extra weapons with cheats" in the
options menu to get them through cheats (give all, idkfa).

## Features
- Posed VR hands on every weapon: hand on the grip, finger on the trigger, support hand.
- Manual, immersive reloading (when enabled):
  - magazines out and in;
  - slides, charging handles and pumps racked by hand;
  - the pistol slide and the rifle, SMG and assault shotgun bolts lock back when fired dry;
  - shotgun shells through the real loading port, topped off any time.
- Kitbash M4 + M203: the rifle's secondary fire launches the underbarrel grenade. In VR, hold the
  off trigger on the tube to unlatch, slide it forward, grab a 40 mm round and push it in, then
  slide it shut. Spent cases drop out when the tube opens. Flick-reloading loads it too.
- Secondary fire: the SMG toggles 3-round burst / full auto. Slug shots for the shotgun and the
  shotvolver (options menu, off by default).
- Pistol Semi Auto option: one shot per trigger pull (options menu, off by default, any time).
- Brass ejects from each gun's real ejection port (pistol, rifle, SMG, assault shotgun).
- Dual Wield support. Flick guns down arcade style to reload when akimbo.
- Grenade: pull the pin with the off hand. Hold the trigger, swing and release to throw; release
  while still to cook it. The axe throws the same way.
- A fist in each hand. The off-hand fist can be selected back after moving a gun there.
- VR punching (physical jabs and hooks), VR throwing and VR reloading can each be turned on/off.
- Left-handed support.
- A gun in each hand uses stock reload so the action isn't interrupted.
- VR reloading works on the main-hand weapon when the off hand is the fist.
- Purist mode: models and hands, no reloading (as Brutal Doom intends).

Built and tested on PCVR QuestZDoom 17.x.

## Versions

Public releases are numbered 1.9x and are the only tags on this repo; `main` is always
the latest public release plus any fixes on their way to the next one. Work in progress lives
on the `dev` branch under internal 2.x numbers. There is no public 2.0 until that work is
finished and played, so a 2.x number in a commit message is not a release.


## What's new in 1.96b

Replaces 1.95 and includes everything in it.

### The Ruger Mini-14 Ranch

- **It drew as a flat sprite the moment you fired.** The firing pose used a sprite no model was
  keyed to, and because every state after it inherits that sprite, the whole shot and recoil
  played in 2D. Keyed, so it stays a model.
- **It fired continuously.** It had no semi-automatic flag, so a held trigger fired again on
  the very next tic. It is semi-auto now, one shot per pull, as a Mini-14 should be.
- Its woodgrain and metal are darker.

### Melee

- **Chainsaw has a trigger finger.** The index finger sits on the saw's trigger and squeezes
  when you fire, like every other weapon.
- **Two-handed axe.** Bring the off hand onto the haft and the grip shifts up toward the head;
  a blow landing with the cutting edge leading does extra damage at shorter range. Two hands on
  the haft alone is not enough -- the edge has to lead.
- **Axe lock-on and throw.** In one hand, hold the throw and the axe paints the monster you are
  looking at; release during the swing to throw at it. A two-handed axe is not thrown -- let go
  with the off hand first.
- **Melee poses fixed.** The sword is held like a baseball bat, the axe with the hands spread
  and the weapon hand at the head, and the chainsaw's support hand no longer splays away.

### Punching

- **Punches open doors and work switches**, at the fist's own reach, with either hand.
- The off hand can punch while the main hand holds a gun.

### Reloading

- **Free charge** (on by default). Take the charging handle or slide with no reload running, to
  crack the action and look in the chamber. It is a look, not a rack: no ammo moves and nothing
  is given to the weapon.
- **The Use key works with a gun in hand**, not only with the fist.

### Fixes

- **Dual wield could strand a reload for good.** Run the main-hand gun dry, go dual, come back
  to one gun, pick up ammo -- and no magazine could ever be seated again. The off-hand slot had
  kept a stale copy of a weapon that was no longer there.
- **The pistol and SMG racked when they should not.** A charge token left over from an earlier
  reload survived into the next, so a gun that still had rounds asked to be charged. The rule is
  the real one now: rack only after reloading a completely empty gun.
- **The SMG racked twice** -- a phantom rack after the magazine was already home.
- **Punch detection read its own history wrong**, comparing the oldest sample instead of the
  newest, so a twitch could register as a blow.
- **Flick reload did nothing with a single rifle.**
- **Thrown grenades dribbled** -- the throw speed was computed in the wrong units.
- **A new map starts clean.** Hand, reload and grenade-fuse state were keyed on a level time
  that restarts at zero.

## Credits
Weapon models: **br_vr** by ajantaju (Brutal Doom VR Weapons, BD v21), made from:
- Grenade by Gomuz; MP40 by Krystian; Shotgun by serg-654; Beretta M9 by damkung13
- Axe by martn00; M4A1 by seandxyz; Minigun by overlordchaos; DBS-2 by ironcladmax501
- SemiAuto Shotgun by Derak Derantick; Grenade Launcher 2 by watercat; RPS-6 by David Short
- KRISS Vector by Bandit; Chainsaw by 3DHaupt; M16A3/M203 by rubenve; M249 by Buce
- M79 by omgitstallin; Rorsch Mk-1 by CrazyRusEnginer; M13-Gaus (plasma) by DigitalTales
- RD-100 (BFGs) by Cameron Chung Art; Flamethrower (TF2) by arminalcapon
- Mancubus flame cannon by Arthur Manhaes; Dragonslayer by Jakob Pihl; MG42 by TastyTony
- Taurus Judge by Tori-nyan; Boot by Nicolas.KoiSculpt; Fingerless Glove by 3DMaesen
- Revenant missile launcher and Reaper by id Software (Doom 2016)

(All from Sketchfab; textures edited.)

- VR hands: Ermac (Force Unleashed / Rusted Legacy, MIT)
- Brutal Doom: Sergeant Mark IV
- QuestZDoom: Team Beef

## Screenshots

![Kitbash M4 + M203](renders/m4_m203.png)

![Hands on the guns](renders/hands_on_guns_1.png)
![Hands on the guns](renders/hands_on_guns_2.png)
![Hands on the guns](renders/hands_on_guns_3.png)
