#!/bin/sh
# run.sh <name> <console script>
S=/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad
cd $S/build/qzd
export LD_LIBRARY_PATH=$S/build/zminst/lib HOME=$S/build/home
timeout 400 xvfb-run -a -s "-screen 0 1024x768x24" stdbuf -oL -eL ./qzdoom -iwad freedoom2.wad -file /mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2 $S/vplus/rtest/rtest.pk3 -nosound +map MAP01 +"$2" ${3:-} > $S/vplus/rtest/$1.out 2>&1
echo "$1 exit $?"
