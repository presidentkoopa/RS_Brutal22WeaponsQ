#!/bin/bash
# 2.0 integration lane: one engine run, exclusive shared lock, pristine ini. usage: run.sh <name> <pk3> <secs> <script> [extra pk3...]
S=/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad
N=$1; P=$2; T=$3; C=$4; shift 4
export B22_IWAD=/home/claude/gamedata/doom2.wad B22_BD22=/home/claude/gamedata/brutal22test6.pk3 B22_VOX=/home/claude/gamedata/BD_VoxelPack.pk3
export B22_BUILD=$S/int20_rig B22_RIG=$S/int20_rig/bin B22_PK3=$P
cd /home/claude/rsq_weapondepot/tools/rig
# yield: a lane already blocked on the lock (support-hand fix has priority) is woken first while we pause
sleep 4
flock -o -x /home/claude/rig.lock bash -c "cp $S/int20_rig/ini.pristine $S/int20_rig/bin/config/qzdoom.ini; exec python3 -c 'import sys,rig; rc,t=rig.run(sys.argv[1],sys.argv[2],int(sys.argv[3]),tuple(sys.argv[4:])); print(\"rc\",rc)' \"\$@\"" _ "$N" "$C" "$T" "$@"
