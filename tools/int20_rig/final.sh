#!/bin/bash
# 2.0 int r2 final checks on the final pk3 (each engine run through run.sh: shared lock -x, 4 s yield, pristine ini)
S=/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad; R=$S/int20_rig; T=$S/int20r2/tools/int20_rig
P=/home/claude/lane_b_out/int20/BD22_VR-Reloaded_2.0-int-r2.pk3; OLD=/home/claude/lane_b_out/int20/BD22_VR-Reloaded_2.0-int.pk3
cd $R
echo "== boot"; ./run.sh boot $P 120 'wait 200; quit' >/dev/null 2>&1
grep -E "Script error|VM execution aborted|exception" logs/boot.log | sort | uniq -c
echo "== purist before (2.0-int)"; python3 $T/puristcap.py $OLD before PuristRifle
echo "== purist after"; python3 $T/puristcap.py $P final PuristRifle
echo "== sweep"; python3 $T/sweep.py $P r2 0
echo "== done"
