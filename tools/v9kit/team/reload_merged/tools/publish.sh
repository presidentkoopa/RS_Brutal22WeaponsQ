#!/bin/sh
# Publishes team/reload to team/reload_release (what the integrator builds v9 from):
# copies the sources, tools, tests, docs, screenshots and the four packs into
# reload_release.tmp, then swaps it in. The packs must already be built.
#   tools/publish.sh
set -e
S=/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad
R=$S/team/reload
T=$S/team/reload_release.tmp
rm -rf "$T"
mkdir -p "$T"
cd "$R"
for f in DESIGN.md PROGRESS.md proto_bd22.pk3 proto_bd22_test.pk3 proto_vplus.pk3 proto_vplus_test.pk3 _hands_in.zs _hands_test.zs; do
	cp -p "$f" "$T/"
done
cp -rp src tools "$T/"
mkdir -p "$T/rtest" "$T/shots"
cp -p rtest/*.py rtest/*.sh rtest/*.zs "$T/rtest/"
cp -rp rtest/home rtest/out "$T/rtest/"
cp -p shots/*.png "$T/shots/" 2>/dev/null || true
rm -rf "$T/tools/__pycache__" "$T/rtest/home/.cache"
rm -rf "$S/team/reload_release"
mv "$T" "$S/team/reload_release"
echo "published: $(du -sh $S/team/reload_release | cut -f1)"
