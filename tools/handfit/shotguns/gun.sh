#!/bin/bash
# one class: give, select, fire, alt-fire, reload (real button), fire (sweep3.sh's script). usage: gun.sh <pk3> <tag> <class...>
PK=$1; TAG=$2; shift 2
for w in "$@"; do /home/claude/lane_b_sgrun/run.sh ${TAG}_$w $PK 600 "wait 120; god; rsq_extra_weapons 1; rsq_ballistics 2; rsr_reload 1; give ammo; give RevolverRounds; give $w; wait 2; use $w; wait 170; +attack; wait 20; -attack; wait 40; +altattack; wait 20; -altattack; wait 60; +reload; wait 6; -reload; wait 80; +attack; wait 10; -attack; wait 40; quit"; echo "$w done"; done
