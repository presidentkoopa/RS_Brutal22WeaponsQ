#!/bin/sh
# quick test pack: v8 build output with tool/vrmelee files replaced from disk (no full rebuild)
S=/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad
python3 - <<PY
import zipfile, os
S='$S'
src=zipfile.ZipFile(S+'/out/RS_BD22_Models_v8.pk3')
V=S+'/tool/vrmelee'
mine={}
for root,_,fs in os.walk(V):
    for f in fs:
        full=os.path.join(root,f); mine[os.path.relpath(full,V)]=open(full,'rb').read()
out=zipfile.ZipFile(S+'/out/quick.pk3','w',zipfile.ZIP_STORED)
for i in src.infolist():
    if i.filename in mine: continue
    out.writestr(i, src.read(i.filename))
for n,b in mine.items(): out.writestr(n,b)
out.close()
PY
