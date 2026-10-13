#!/bin/sh
# TEST ONLY: the v9 headless suite (team/integ/rtest). Runs one after another; outputs in out/,
# screenshots in shots/. Usage: suite.sh [load|fire|stock|vr|all]
cd "$(dirname "$0")"
R="python3 -I -B run.py"
BDG="Rifle BrutalPistol BrutalSMG MP40 Sniper AssaultShotgun Shot_Gun Revolver SSG Rocket_Launcher RailGun Plasma_Gun GrenadeLauncher"
VPG="VR_Rifle VR_Revolver VR_Revolver2 VR_Shotgun VR_SuperShotgun"
what=${1:-all}
if [ $what = load ] || [ $what = all ]; then
  for k in bd vp; do for p in v8 v9; do $R load_${k}_$p $k $p none 300 "60:echo LOADED"; done; done
fi
if [ $what = fire ] || [ $what = all ]; then
  ./fire_bd.sh fire_bd_v9 v9 vr
  specs="10:god; give all; show_messages 0; rsrtest_script 0; v9t_hl 1"
  $R fire_vp_v9 vp v9 vr 900 "$specs" "30:v9t_mode 1" $(k=0; while [ $k -lt 13 ]; do printf '%d:shot:g%02d ' $((40+k*200+100)) $k; k=$((k+1)); done) "2700:echo END"
fi
if [ $what = stock ] || [ $what = all ]; then
  # VR off (desktop: the real vrhand.zs says not in VR): every reloading gun, v8 and v9, same steps
  for p in v8 v9; do
    $R stock_bd_$p bd $p log 1200 "10:god; give all; give MP40; v9t_guns \"$BDG\"; v9t_mode 2" "2300:echo END"
    $R stock_vp_$p vp $p log 900 "10:god; give all; v9t_guns \"$VPG\"; v9t_mode 2" "1100:echo END"
    $R stockE_bd_$p bd $p log 600 "10:god; give all; v9t_guns Rifle; v9t_empty 1; v9t_take \"RifleAmmo DoubleRifleAmmo\"; v9t_mode 2" "400:echo END"
    $R stockE_vp_$p vp $p log 600 "10:god; give all; v9t_guns VR_Rifle; v9t_empty 1; v9t_take VR_RifleLoaded; v9t_mode 2" "400:echo END"
    $R stockP_bd_$p bd $p log 600 "10:god; give all; v9t_guns Rifle; v9t_mode 2" "400:echo END"
    $R stockP_vp_$p vp $p log 600 "10:god; give all; v9t_guns VR_Rifle; v9t_mode 2" "400:echo END"
  done
fi
if [ $what = vr ] || [ $what = all ]; then
  # fake VR hands (scripted off hand): the real VR reload on the Rifle and the M16, empty and partial;
  # and VR with Reloading = Stock
  $R vrE_bd_v9 bd v9 vr 900 "10:god; give all; rsr_debug 1; show_messages 0; v9t_guns Rifle; v9t_empty 1; v9t_take \"RifleAmmo DoubleRifleAmmo\"; v9t_mode 2" "1400:echo END"
  $R vrP_bd_v9 bd v9 vr 900 "10:god; give all; rsr_debug 1; show_messages 0; v9t_guns Rifle; v9t_mode 2" "1000:echo END"
  $R vrE_vp_v9 vp v9 vr 900 "10:god; give all; rsr_debug 1; show_messages 0; v9t_guns VR_Rifle; v9t_empty 1; v9t_take VR_RifleLoaded; v9t_mode 2" "1400:echo END"
  $R vrP_vp_v9 vp v9 vr 900 "10:god; give all; rsr_debug 1; show_messages 0; v9t_guns VR_Rifle; v9t_mode 2" "1000:echo END"
  for k in bd vp; do
    for y in 0 70; do
      shots=$(grep -o "HOLD [A-Z_]* t[0-9]*" out/vrE_${k}_v9.out | awk '{sub("t","",$3); printf "%d:shot:%s ", $3+8, $2}')
      $R vrshots_${k}_y$y $k v9 vrview 900 "10:god; give all; show_messages 0; rsr_test_yaw $y; v9t_guns $( [ $k = bd ] && echo Rifle || echo VR_Rifle ); v9t_empty 1; v9t_take $( [ $k = bd ] && echo RifleAmmo,DoubleRifleAmmo || echo VR_RifleLoaded ); v9t_mode 2" "55:shot:0_READY" $shots "420:shot:9_DONE" "430:echo END"
    done
  done
  $R vrS_bd_v9 bd v9 vr 600 "10:god; give all; rsr_reload 0; rsr_debug 1; v9t_guns Rifle; v9t_empty 1; v9t_take \"RifleAmmo DoubleRifleAmmo\"; v9t_mode 2" "400:echo END"
fi
