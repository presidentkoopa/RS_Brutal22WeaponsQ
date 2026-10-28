#!/bin/bash
# TEST ONLY (2.0 final): every rig check on the final pk3, one engine at a time (rig.lock -x), the lane's fresh default ini
# (ini.f20: written by the engine itself on a boot with no ini, playerclass set to Rifle Start as the New Game menu would).
S=/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad; R=$S/int20_rig; T=$S/int20/tools; O=/home/claude/lane_b_out/final20
P=/home/claude/lane_b_out/BD22_VR-Reloaded_2.0.pk3; export INT20_INI=$R/ini.f20; mkdir -p $O $S/f20gate $S/f20scope
cd $R
for step in ${STEPS:-boot sweep held rsweep dual holds scope}; do case $step in
boot) echo "== boot"; ./run.sh f20_boot2 $P 120 'wait 200; quit' >/dev/null 2>&1
      grep -E "Script error|VM execution aborted|exception|Too many|cls " logs/f20_boot2.log | sort | uniq -c | head;;
sweep) echo "== sweep"; python3 sweep_f20.py $P f20 0;;
held) echo "== held"; python3 $T/int20_rig/f20held.py $P $O/held Melee_Attacks BrutalAxe Chain_saw DSweap BrutalPistol BrutalRevolver Revolver BrutalSMG MP40 Shot_Gun SSG AssaultShotgun Sniper Rifle Minigun MG42 Machinegun GrenadeLauncher IncendiaryLauncher Rocket_Launcher Devastator HellishMissileLauncher Plasma_Gun Railgun BFG10k BIG_FUCKING_GUN NukeLauncher Unmaker Flamethrower2 FlameCannon HandGrenades;;
rsweep) echo "== hand reloads"; python3 $T/int20_rig/rsweep.py $P all;;
dual) echo "== dual"; python3 $T/int20_rig/dualsweep.py $P f20d;;
holds) echo "== FBX reload holds"; RSQ_GATE=$S/f20gate python3 $T/int20_rig/f20wrap.py $R/ini.f20 $T/handfit/offhand/rig_holds.py $P f20 mag18 mag13 brkSSG:AmmoShell:0 brkGrenadeLauncher:AmmoRocket:0 brkRevolver:AmmoShell:0 brkBrutalRevolver:RevolverRounds:0 brkBrutalRevolver:RevolverRounds:1 pump m203 2>&1 | grep -vE '^\s*$' | cut -c1-220;;
scope) echo "== scope 3x + alt toggle"; for g in Sniper RailGun; do
      SCOPE_OUT=$S/f20scope EVERY=6 SECS=70 ALTSEQ='wait 30; +altattack; wait 40; -altattack; wait 70; +altattack; wait 40; -altattack; wait 70; ' python3 $T/int20_rig/f20wrap.py $R/ini.f20 $T/scope3x/drive.py s3_$g $P $g 30 0 0 1 '' 960 $S/int20 2>&1 | grep -E 'rc|RSQT|scope' | head -8
      python3 $T/scope3x/conv.py $S/f20scope/dump_s3_$g | tail -1; python3 $T/scope3x/blobs.py $S/f20scope/dump_s3_$g; done;;
esac; done
echo "== all done"
