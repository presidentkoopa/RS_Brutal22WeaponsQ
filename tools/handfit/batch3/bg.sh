#!/bin/bash
export B22_IWAD=/home/claude/gamedata/doom2.wad B22_BD22=/home/claude/gamedata/brutal22test6.pk3 B22_VOX=/home/claude/gamedata/BD_VoxelPack.pk3 B22_BUILD=/home/claude/lane_b_b3run B22_PK3=/home/claude/lane_b_b3run/t.pk3
cd /home/claude/rsq_weapondepot/tools/rig
date +%T
flock -o -x /home/claude/rig.lock python3 mags.py 4 > /home/claude/lane_b_b3run/mags_b3.out 2>&1
git -C /home/claude/rsq_weapondepot checkout -q tools/rig/bin/config/qzdoom.ini
date +%T
for st in rest steady fire; do
  for pair in "eye|0.25 1.45 0.15 -25 0 0" "side|0.85 1.30 -0.50 0 90 0"; do
   B1_EYE="${pair#*|}" B1_GUNS=MP40 B1_STATES=$st B2_TAG="${pair%%|*}" flock -o -x /home/claude/rig.lock python3 /home/claude/lane_b_b3run/tools/sheet_b3.py /home/claude/lane_b_b3run/t.pk3
   git -C /home/claude/rsq_weapondepot checkout -q tools/rig/bin/config/qzdoom.ini
  done
done
date +%T
