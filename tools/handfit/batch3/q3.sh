#!/bin/bash
while pgrep -f "bg.sh" >/dev/null; do sleep 5; done
cd /home/claude/lane_b_b3run
for W in MP40 BrutalSMG; do
./run.sh fin_b3_$W /home/claude/lane_b_out/BD22_VR-Reloaded_1.99x-lb-r6-hands3.pk3 600 "wait 120; god; rsq_extra_weapons 1; rsq_ballistics 2; rsr_reload 1; give ammo; give $W; wait 2; use $W; wait 170; +attack; wait 20; -attack; wait 40; +altattack; wait 20; -altattack; wait 60; +reload; wait 6; -reload; wait 80; +attack; wait 10; -attack; wait 40; quit"
done
date +%T
