"""Patch a shipped pack in place: trigger-finger frames in models/rsq/hand.md3, MODELDEF.rsq
FrameIndex lines (RQGT = on the trigger, RQGU = squeezing), RSQ_HandTable.Trigger, hands.zs."""
import sys, zipfile, re, json; sys.path.insert(0,'.')
import build
from hm import HAND
pack, solfile, src, dst = sys.argv[1:5]
md3, letters, n0, nposes = build.make(pack, solfile, HAND)
z=zipfile.ZipFile(src)
assert z.read('models/rsq/hand.md3')==open(HAND,'rb').read(), 'pack hand.md3 is not the one the frames were made on'
LET=build.LET
# MODELDEF.rsq: new frames go in the RSQ_GunSide hand.md3 block
md=z.read('MODELDEF.rsq').decode('latin-1')
anchor=re.search(r'(\tFrameIndex RQGS H 0 \d+[^\n]*\n)', md)
lines=''.join('\tFrameIndex RQGT %s 0 %d\t// index finger on the trigger\n\tFrameIndex RQGU %s 0 %d\t// trigger squeezed\n'%(LET[k],n0+2*k,LET[k],n0+2*k+1) for k in range(nposes))
md=md[:anchor.end()]+lines+md[anchor.end():]
# handtable.zs: Trigger(i), a letter per gun ("" = no trigger frame)
ht=z.read('zscript/rsq/handtable.zs').decode('latin-1')
n=len(re.search(r'GunOne\(int i\)\s*\{\s*static const String v\[\] = \{([^}]*)\}',ht).group(1).split(','))
vals=['"%s"'%letters.get(i,'') for i in range(n)]; vals[0]='""'
fn='''
	// trigger-finger frames (RQGT on the trigger, RQGU squeezing): index finger bent onto
	// each gun's trigger (tf/ rig, fitted per gun); "" keeps the plain grip frame
	clearscope static String Trigger(int i)
	{
		static const String v[] = { %s };
		return i > 0 && i < v.Size() ? v[i] : "";
	}
''' % ', '.join(vals)
k=ht.rstrip().rfind('}')
ht=ht[:k].rstrip('\n')+'\n'+fn+'\n}\n'
# hands.zs: states and the pick
hz=z.read('zscript/rsq/hands.zs').decode('latin-1')
st=''.join('\tTrg%s: RQGT %s -1; Stop;\n\tSqz%s: RQGU %s -1; Stop;\n'%(L,L,L,L) for L in LET[:nposes])
hz=hz.replace('\tSupA: RQSP A -1; Stop;\n', '\t// the gun hand with its index finger on the trigger, and squeezing it (fire held)\n'+st+'\tSupA: RQSP A -1; Stop;\n',1)
old='''		invoker.SetLayer(p, RSQ_Layers.GUNHAND, gs, i > 0 && g != "" ? "Gun" .. g : "Hidden");'''
new='''		// the index finger rests on the trigger, and squeezes it while fire is held
		String tf = RSQ_HandTable.Trigger(i);
		String gl = tf != "" ? ((p.cmd.buttons & BT_ATTACK) ? "Sqz" .. tf : "Trg" .. tf) : "Gun" .. g;
		invoker.SetLayer(p, RSQ_Layers.GUNHAND, gs, i > 0 && g != "" ? gl : "Hidden");'''
assert hz.count(old)==1; hz=hz.replace(old,new)
rep={'models/rsq/hand.md3':md3,'MODELDEF.rsq':md.encode('latin-1'),'zscript/rsq/handtable.zs':ht.encode('latin-1'),'zscript/rsq/hands.zs':hz.encode('latin-1')}
zo=zipfile.ZipFile(dst,'w')
for info in z.infolist():
    data=rep.get(info.filename, None)
    if data is None: data=z.read(info.filename)
    ni=zipfile.ZipInfo(info.filename, info.date_time); ni.compress_type=info.compress_type; ni.external_attr=info.external_attr
    zo.writestr(ni, data)
zo.close()
print('letters',letters,'poses',nposes)
