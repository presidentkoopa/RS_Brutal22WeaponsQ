#!/bin/bash
# 2.0 int r2, after the r12 + lane-scope merges and the butt-point move: butt hits, boot, sweep, scope 3x (final pk3)
S=/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad; R=$S/int20_rig; T=$S/int20r2/tools/int20_rig
P=/home/claude/lane_b_out/int20/BD22_VR-Reloaded_2.0-int-r2.pk3
cd $R
echo "== butt strike hits"; MODE=orbit BR=0.25 TH0=60 TH1=120 NST=2 python3 $T/butt.py $P final Rifle,Shot_Gun,MG42
echo "== boot"; ./run.sh boot $P 120 'wait 200; quit' >/dev/null 2>&1
grep -E "Script error|VM execution aborted|exception|Too many" logs/boot.log | sort | uniq -c
echo "== sweep"; python3 $T/sweep.py $P r2 0
echo "== scope 3x"; for g in Sniper RailGun; do SCOPE_OUT=$R/scope3x python3 $S/int20r2/tools/scope3x/drive.py s3_$g $P $g 0 0 0 1 '' 960 $S/int20r2 2>&1 | tail -4; python3 $S/int20r2/tools/scope3x/conv.py $R/scope3x/dump_s3_$g | tail -1; python3 $S/int20r2/tools/scope3x/blobs.py $R/scope3x/dump_s3_$g | tail -3; done
echo "== done"
