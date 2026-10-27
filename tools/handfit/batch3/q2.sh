#!/bin/bash
while pgrep -f "lane_b_b3run/bg.sh|sweep3.sh" >/dev/null; do sleep 5; done
cd /home/claude/lane_b_b3run
./run.sh boot /home/claude/lane_b_b3run/t.pk3 300 "wait 250; quit"
export B22_IWAD=/home/claude/gamedata/doom2.wad B22_BD22=/home/claude/gamedata/brutal22test6.pk3 B22_VOX=/home/claude/gamedata/BD_VoxelPack.pk3 B22_BUILD=/home/claude/lane_b_b3run B22_PK3=/home/claude/lane_b_b3run/t.pk3
cd /home/claude/rsq_weapondepot/tools/rig
flock -o -x /home/claude/rig.lock python3 mags.py 4 3 > /home/claude/lane_b_b3run/mags_b3.out 2>&1
git -C /home/claude/rsq_weapondepot checkout -q tools/rig/bin/config/qzdoom.ini
date +%T >> /home/claude/lane_b_b3run/mags_b3.out
