#!/bin/sh
S=/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad
python3 - <<PY
import zipfile
S='$S'
src=zipfile.ZipFile(S+'/out/quick.pk3')
out=zipfile.ZipFile(S+'/rtest/rtest.pk3','w',zipfile.ZIP_STORED)
for i in src.infolist():
    if i.filename=='zscript/rsvr/vrhand.zs':
        out.writestr(i.filename, open(S+'/rtest/vrhand_fake.zs').read()); continue
    if i.filename=='MAPINFO.rsvr':
        out.writestr(i.filename, src.read(i.filename).decode().replace('"RSQ_Ballistics"','"RSQ_Ballistics", "RSQ_TestLog"')); continue
    out.writestr(i, src.read(i.filename))
out.writestr('CVARINFO.rtest', open(S+'/rtest/CVARINFO.txt').read())
out.close()
PY
