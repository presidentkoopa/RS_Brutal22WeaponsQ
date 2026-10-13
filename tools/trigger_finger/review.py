import sys, json; sys.path.insert(0,'.')
from trig import *; import boxes
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pack=sys.argv[1]; sol=json.load(open(sys.argv[2])); out=sys.argv[3]
keys=sys.argv[4].split(',') if len(sys.argv)>4 else list(sol)
BX=getattr(boxes,pack.upper()); LC=getattr(boxes,pack.upper()+'_LC')
T=tab.parse(pack)
n=len(keys); fig,axs=plt.subplots(n,2,figsize=(9,2.6*n))
if n==1: axs=[axs]
for r,key in enumerate(keys):
    s=sol[key]; i=int(key.rstrip('b')); two=key.endswith('b')
    it=hand_item(T,i,two); g=gun_item(T['cls'][i]); fg=Finger(it['frame'],it)
    V=np.concatenate([v for _,v in gun_tris(g)]); x=np.array(s['x'])
    Lc=LC.get(i,0.0); bx=BX.get(i)
    P,_=fg.pose(x[:3],x[3]); xs=squeeze(x); Q,_=fg.pose(xs[:3],xs[3]); H=fg.V
    tg=np.array(s['target'])
    a=axs[r][0]; m=np.abs(V[:,1]-Lc)<1.0
    a.scatter(V[m,0],V[m,2],s=1,c='grey'); a.scatter(H[PALM,0],H[PALM,2],s=1,c='tan')
    a.scatter(Q[:,0],Q[:,2],s=3,c='red'); a.scatter(P[:,0],P[:,2],s=3,c='orange'); a.scatter(*tg[[0,2]],marker='x',c='blue')
    a.set_xlim(tg[0]-8,tg[0]+5); a.set_ylim(tg[2]-5,tg[2]+4); a.set_aspect('equal'); a.set_title('%s %s side  x=%s e=%.2f o=%.2f'%(key,s['cls'],s['x'],s['err'],s['orient']),fontsize=7)
    a=axs[r][1]; m=(V[:,0]>tg[0]-1.5)&(V[:,0]<tg[0]+1.5)
    a.scatter(-V[m,1],V[m,2],s=1,c='grey'); a.scatter(-Q[:,1],Q[:,2],s=3,c='red'); a.scatter(-P[:,1],P[:,2],s=3,c='orange'); a.scatter(-tg[1],tg[2],marker='x',c='blue')
    a.set_xlim(-tg[1]-4,-tg[1]+7); a.set_ylim(tg[2]-5,tg[2]+4); a.set_aspect('equal'); a.set_title('front slab (player right = right)',fontsize=7)
plt.tight_layout(); plt.savefig(out,dpi=55)
