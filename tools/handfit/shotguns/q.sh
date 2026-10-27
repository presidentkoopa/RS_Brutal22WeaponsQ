#!/bin/bash
# shotguns lane check queue for one gun: boot dump, gun.sh (give/select/fire/alt/reload), reload test, sheet tiles. usage: q.sh <pk3> <Gun> <reload job: mags id | pump | brkN | none>
PK=$1; G=$2; J=$3; T=/home/claude/lane_b_sg/tools/handfit/shotguns
export B22_IWAD=/home/claude/gamedata/doom2.wad B22_BD22=/home/claude/gamedata/brutal22test6.pk3 B22_VOX=/home/claude/gamedata/BD_VoxelPack.pk3 B22_BUILD=/home/claude/lane_b_sgrun B22_PK3=$PK
cd /home/claude/lane_b_sgrun; ./run.sh boot $PK 300 "wait 100; quit"
$T/gun.sh $PK chk $G
cd /home/claude/rsq_weapondepot/tools/rig
case $J in none) ;; pump) flock -o -x /home/claude/rig.lock python3 $T/pump_sg.py ;; brk*) flock -o -x /home/claude/rig.lock python3 brk.py ${J#brk} ;; *) flock -o -x /home/claude/rig.lock python3 mags.py $J ;; esac
git -C /home/claude/rsq_weapondepot checkout -q tools/rig/bin/config/qzdoom.ini
for st in rest steady fire; do for pair in "eye|0.25 1.45 0.15 -25 0 0" "side|0.85 1.30 -0.50 0 90 0"; do
  B1_EYE="${pair#*|}" B1_GUNS=$G B1_STATES=$st B2_TAG="${pair%%|*}" flock -o -x /home/claude/rig.lock python3 $T/sheet_sg.py $PK
  git -C /home/claude/rsq_weapondepot checkout -q tools/rig/bin/config/qzdoom.ini
done; done
pkill -f "lane_b_sgrun.*Xvfb" 2>/dev/null; date +%T
