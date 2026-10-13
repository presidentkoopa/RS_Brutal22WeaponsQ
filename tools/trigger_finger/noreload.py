"""Switch immersive (VR) reloading off in a v9 pack: the gate always says no, the menu row is
greyed out (and reads Stock), the reload debug row and the long help text are gone."""
import sys, zipfile, re
src, dst = sys.argv[1:3]
z=zipfile.ZipFile(src); rep={}
v=z.read('zscript/rsr/vreload.zs').decode('latin-1')
a="""		if (!mo || !mo.player || RSR.PlayerInt(mo.player, 'rsr_reload', 0) != 1 || !RSVR_VRHand.InVR(mo))
			return false;"""
b="""		// VR reloading is switched off (2026-10-12): every gun reloads stock, whatever rsr_reload says
		return false;
		if (!mo || !mo.player || RSR.PlayerInt(mo.player, 'rsr_reload', 0) != 1 || !RSVR_VRHand.InVR(mo))
			return false;"""
assert v.count(a)==1; v=v.replace(a,b)
a2="""		return mo && mo.player && RSR.PlayerInt(mo.player, 'rsr_reload', 0) == 1 && RSVR_VRHand.InVR(mo);"""
assert v.count(a2)==1; v=v.replace(a2,"""		return false;	// VR reloading is switched off""")
rep['zscript/rsr/vreload.zs']=v
c=z.read('CVARINFO.rsq').decode('latin-1')
c2=re.sub(r'user int rsr_reload = 1;[^\n]*','user int rsr_reload = 0;\t\t\t// VR reloading is switched off; the menu row is greyed out\nuser noarchive bool rsr_reload_available = false;\t// greys out the Reloading row',c)
assert c2!=c; rep['CVARINFO.rsq']=c2
m=z.read('MENUDEF.rsq').decode('latin-1')
body=re.search(r'OptionMenu "RSQ_Options"\s*\{(.*?)\n\}',m,re.S)
new='''
	Title "RS VR HANDS, RELOAD, BALLISTICS"
	Option "VR hands", "rsq_hands", "OnOff"
	Option "Reloading (VR reloading is off)", "rsr_reload", "RSR_ReloadMode", "rsr_reload_available"
	Option "Ballistics", "rsq_ballistics", "RSQ_Ballistics"'''
m=m[:body.start(1)]+new+m[body.end(1):]
rep['MENUDEF.rsq']=m
zo=zipfile.ZipFile(dst,'w')
for info in z.infolist():
    data=rep.get(info.filename); data=z.read(info.filename) if data is None else data.encode('latin-1')
    ni=zipfile.ZipInfo(info.filename,info.date_time); ni.compress_type=info.compress_type; ni.external_attr=info.external_attr
    zo.writestr(ni,data)
zo.close(); print(m[m.find('OptionMenu'):])
