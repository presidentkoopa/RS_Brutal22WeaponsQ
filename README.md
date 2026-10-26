![BD22 VR Weapons](renders/hero.gif)

# BD22 VR Weapons 1.99

Brutal Doom v22 in VR, with your hands.

Coordinated, directed and tested by PresidentKoopa, coded by Claude.

A VR weapon pack for **Brutal Doom v22** (`brutal22test6.pk3`) on **QuestZDoom 17.3**, built for
**standalone Quest**. It runs on the stock engine with no engine changes. It's an add-on: Brutal
Doom stays Brutal Doom. It replaces none of its guns, every gun fires at Brutal Doom's own rate
and does its own damage, and with the options off it plays exactly as Brutal Doom shipped.

## Install

Download the pk3 from the Releases page and load, in this order:

```
doom2.wad  ->  brutal22test6.pk3  ->  BD_VoxelPack.pk3  ->  BD22_VR-Reloaded_1.99.pk3
```

Use Doom 2, not Freedoom: the voxel pack names Doom 2's own sprites.

To build it yourself: `python build.py` zips `src/` into `BD22_VR-Reloaded_<VERSION>.pk3`.

## What's new in 1.99

### Every gun reloads by hand
Every gun that isn't a melee weapon reloads with your hands: **23 guns**. The BFG and BFG10k stay
as Brutal Doom made them.

| How it reloads | Guns |
|---|---|
| Magazine | Rifle, Pistol, SMG, MP40, Assault Shotgun, Railgun, Plasma Gun, Ruger, Rocket Launcher, Machinegun (100-round box) |
| Drum, canister or box | MG42 belt drum, Flamethrower canister, Unmaker skull, Minigun ammo box, Hellish launcher's rear drum |
| Cylinder | Incendiary Launcher (six shots) |
| Bay or block | Devastator loading bay, Nuker warhead block |
| Pump | Shotgun |
| Break-open | Super Shotgun, Grenade Launcher, Shotvolver, slug revolver, and the 40 mm under the Rifle and the Machinegun |

Pull the part out with your off hand, reach to your belt for a fresh one, and push it home.

Brutal Doom never reloads most of the heavy guns at all. On those, the part you swap was cut out
of the gun's own model, and it counts down Brutal Doom's own ammo. The ammo you carry and the
damage you do are still exactly Brutal Doom's.

### Throwing the axe
- Hold the throw and a **lock-on ring** goes on the monster your hand points at. It's the same
  mark as the ShieldSaw and the QuestSaber.
- If you let go without throwing, the ring **stays on for a second**. Pick the hold back up and
  you're still locked.
- The throw **blends your arm's swing with where your hand points**, as the ShieldSaw does.

### New guns from Brutal Doom 21
- **BD21 Machinegun** (M249 with an underbarrel 40 mm). Off by default:
  "Machinegun replaces MG42".
- **Slug revolver**. Off by default: "Slug revolver replaces Shotvolver".

### Melee
- **Gun bash**: your kick key bashes with the gun you're holding. It uses Brutal Doom's own kick
  damage.
- **Pistol whip**: swing a pistol or revolver into something.
- **Butt strike**: drive the stock forward with both hands. Works on all eight guns with a stock.
  Off by default.
- **Real punching** with either fist. Punching a switch or a door works it. Off by default.

### Every gun shoots like itself
These are behind the **Ballistics** switch. Stock is Brutal Doom's own.
- **Recoil** for 22 guns, each worked out from its own cartridge and weight. In VR it moves the
  gun in your hands, never your view.
- **Muzzle flash** light for 18 guns, and an echo for 14 that sounds different indoors and
  outdoors.
- **Visible rounds in flight** for 11 guns, at their real speed.
- **Impact sounds** per surface, **ricochets** off shallow angles, and **brass** from each gun's
  real ejection port, as 3D casings.

### Fixes
- **Guns no longer spin round your shoulder.** Recoil kept adding to itself during reloads and
  turned the gun. It now kicks and settles.
- **No muzzle flash or gunshot echo without a shot.** Footsteps, kicks and the reload buzz were being
  taken for gunshots.
- **Brutal Doom's own ricochet, glass, sparks and magazine-drop sounds are back.** Some of the
  pack's sound files had the same short names and were playing in their place.
- **Fire rates:** QuestZDoom 17.3 lets a held trigger re-fire some guns faster than Brutal Doom
  does on PC: the pistol, the pump shotgun, the Incendiary Launcher and the dual pistols. They're
  held to PC's rate now. The Ruger is one shot per pull.
- **Rounds you pull out stay yours:** pull a part-full magazine with no reserve left, and its
  rounds go back in when you seat it again.
- **Incendiary Launcher:** pressing reload did nothing. Fixed.
- **Flamethrower:** it returned to the wrong frame after firing. Fixed.
- **Dot scope:** it could stop the game's scripts running, on the Railgun and the Ruger. Fixed.
- **Ruger:** it drew 2D sprites while firing. Fixed.
- **Purist Rifle:** it fired the M203. Fixed.
- **Grip-mode charging handle:** a racked handle could not be grabbed. Fixed.
- **Axe alt-fire hold:** it did nothing for players upgrading from older builds. Fixed.
- The pk3 is about **30 MB**: models are LZMA-compressed, as 1.96b's were.

## Everything else
- Posed VR hands on every weapon: hand on the grip, finger on the trigger, support hand.
- Slides, charging handles, bolts and pumps racked by hand. Pistol slides and rifle, SMG and
  assault shotgun bolts lock back when fired dry.
- Shotgun shells go in through the real loading port, and you can top off any time.
- Kitbash M4 + M203. In VR: unlatch the tube, slide it forward, push a round in, slide it shut.
- SMG alt fire toggles 3-round burst or full auto. Slug shots for the shotgun and the Shotvolver
  are menu options, off by default.
- Pistol Semi Auto option: one shot per trigger pull.
- Dual wield, with each gun fired independently. Flick a gun down to reload when you're using two.
- Grenades: pull the pin with your off hand, swing and release to throw, or release while still
  to cook it.
- Left-handed support. Purist mode gives you models and hands, without reloading.

## Options
**Options → BD22 VR Weapons.** Here you'll find reloading (VR or Brutal Doom's stock reload), what
grabs the ammo, where a new magazine comes from, checking the chamber by hand, the scopes,
ballistics and recoil, real casings, throwing, punching, gun bash and butt strike, the dual-wield
and voxel pages, and a tuning and debug page for reloading.

Every option defaults to how Brutal Doom behaves, or to the gentler setting, except the VR hands
and reloading themselves. Set Reloading to "Stock (BD22)" and every gun reloads the way it always
did.

## Known gaps
- The Minigun's ammo box in your hand is the small box off the gun. A bigger one is planned.
- The Minigun throws its brass from the body: its model has no ejection port.
- QuestZDoom 17.3 can't do recoil roll or the backward shove. Those need engine support this pack
  doesn't have.

## Versions
Public releases are numbered 1.9x and are the only tags on this repo. `main` is always the latest
public release plus any fixes on their way to the next one. Work in progress lives on the `dev`
branch under internal 2.x numbers.

This build is generated by the RSQ Weapon Depot. Every number in it is measured off a model or
parsed out of Brutal Doom's own code, and `src/README.txt` (shipped inside the pk3) has the long
version.

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
