#!/bin/bash
# lane B shotguns lane: one engine run (QuestZDoom 17.3, tools/rig/bin) under the shared lock.
# usage: run.sh <name> <pk3> <secs> <script> [extra pk3...]   env passes through (QZ_RES, QZ_DUMP_*, B22_NOPROBE)
N=$1; P=$2; S=$3; C=$4; shift 4
export B22_IWAD=/home/claude/gamedata/doom2.wad B22_BD22=/home/claude/gamedata/brutal22test6.pk3 B22_VOX=/home/claude/gamedata/BD_VoxelPack.pk3 B22_BUILD=/home/claude/lane_b_sgrun
unset B22_RIG
EX=""; for e in "$@"; do EX="$EX,'$e'"; done
cd /home/claude/rsq_weapondepot/tools/rig
[ -n "$PCLASS" ] && sed -i "s/^playerclass=.*/playerclass=$PCLASS/" bin/config/qzdoom.ini
env B22_PK3=$P flock -o -x /home/claude/rig.lock python3 -c "
import sys; sys.path.insert(0,'.'); import rig
rc,t=rig.run('$N', sys.argv[1], $S, extra=[${EX#,}])
print('rc',rc)" "$C" > /home/claude/lane_b_sgrun/logs/$N.rc 2>&1
git -C /home/claude/rsq_weapondepot checkout -q tools/rig/bin/config/qzdoom.ini 2>/dev/null
true
