#!/bin/bash
# every weapon class: give, select, fire, alt-fire, reload (real button), fire; rsr_reload 1, ballistics 2. ONE engine at a time.
W="BrutalSMG BIG_FUCKING_GUN HellishMissileLauncher Unmaker FlameCannon Flamethrower2 HandGrenades BrutalRevolver"
PK=$1; TAG=$2
for w in $W; do /home/claude/lane_b_b3run/run.sh sw_b3_$w $PK 600 "wait 120; god; rsq_extra_weapons 1; rsq_ballistics 2; rsr_reload 1; give ammo; give RevolverRounds; give $w; wait 2; use $w; wait 170; +attack; wait 20; -attack; wait 40; +altattack; wait 20; -altattack; wait 60; +reload; wait 6; -reload; wait 80; +attack; wait 10; -attack; wait 40; quit"; echo "$w done"; done
