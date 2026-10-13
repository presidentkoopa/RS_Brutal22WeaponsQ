import sys, json; sys.path.insert(0,'.')
from trig import *
import md3w
LET='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def make(pack, solfile, src_md3):
    T=tab.parse(pack); sol=json.load(open(solfile))
    uniq=[]; idx_letter={}; frames=[]; names=[]
    for key in sorted(sol,key=lambda k:(int(k.rstrip('b')),k)):
        if key.endswith('b'): continue          # two-hand pistol frame == one-hand frame (checked)
        s=sol[key]; i=int(key); fr=s['frame']; x=np.array(s['x'])
        sig=(fr,tuple(np.round(x,1)))
        if sig not in uniq:
            uniq.append(sig)
            it=hand_item(T,i); fg=Finger(fr,it)
            for kind,xx in (('trg',x),('sqz',squeeze(x))):
                P,N=fg.pose(xx[:3],xx[3],xx[4:7] if len(xx)>4 else None)
                frames.append(full_frame(fg,P,N)); names.append('%s%d_%s'%(kind,fr,T['cls'][i][:6]))
        idx_letter[i]=LET[uniq.index(sig)]
    src=open(src_md3,'rb').read()
    nfr0=XYZ.shape[0]
    return md3w.add_frames(src,frames,names), idx_letter, nfr0, len(uniq)
if __name__=='__main__':
    b,m,n0,u=make(sys.argv[1],sys.argv[2],HAND)
    open(sys.argv[3],'wb').write(b); print(u,'poses',m,len(b))
