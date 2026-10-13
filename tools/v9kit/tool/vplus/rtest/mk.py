import zipfile, sys
S='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
src=zipfile.ZipFile(S+'/vplus/RS_VanillaVRPlus_VR.pk3')
out=zipfile.ZipFile(S+'/vplus/rtest/rtest.pk3','w',zipfile.ZIP_STORED)
for i in src.infolist():
    d=src.read(i.filename)
    if i.filename=='zscript/rsvr/vrhand.zs':
        d=open(S+'/vplus/rtest/vrhand_fake.zs','rb').read()
    if i.filename=='MAPINFO.rsq':
        d=d.decode().replace('"RSQ_Ballistics"','"RSQ_Ballistics", "RSQ_TestLog"').encode()
    if i.filename=='ZSCRIPT.rsq':
        d=d.decode().replace('#include "zscript/rsq/ballistics.zs"','#include "zscript/rsq/ballistics.zs"\n#include "zscript/rtest/testlog.zs"').encode()
    out.writestr(i.filename,d)
out.writestr('zscript/rtest/testlog.zs',open(S+'/vplus/rtest/testlog.zs').read())
out.writestr('CVARINFO.rtest',open(S+'/rtest/CVARINFO.txt').read())
out.close()
