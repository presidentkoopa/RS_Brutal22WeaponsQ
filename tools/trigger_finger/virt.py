import sys, json; sys.path.insert(0,'.')
from trig import *
pack=sys.argv[1]; out=sys.argv[2]; ids=[int(x) for x in sys.argv[3].split(',')]; ref=sys.argv[4].split(',')
T=tab.parse(pack); sol=json.load(open(out))
# mean trigger offset from the MCP pivot, in the finger's own frame (a, p, l), over the reference guns
offs=[]
for k in ref:
    i=int(k.rstrip('b')); it=hand_item(T,i,k.endswith('b')); fg=Finger(it['frame'],it)
    d=np.array(sol[k]['target'])-fg.piv[0]; offs.append([d@fg.a,d@fg.p,d@fg.l])
off=np.mean(offs,0); print('mean offset (a,p,l)',off.round(2), 'spread',np.std(offs,0).round(2))
for i in ids:
    it=hand_item(T,i); fg=Finger(it['frame'],it)
    tg=fg.piv[0]+off[0]*fg.a+off[1]*fg.p+off[2]*fg.l
    tg[0]-=0.2   # the blade face; solve3 puts the pad 0.2 in front
    B=np.array([[tg[0]-0.3*s, tg[1]+0.15*q, tg[2]+u] for u in np.linspace(-1.2,1.2,9) for s in (0,1) for q in (-1,1)])
    x,e,o,ins,t2=solve3(fg,B)
    sol[str(i)]=dict(cls=T['cls'][i],frame=it['frame'],x=[round(float(v),2) for v in x],err=round(e,2),orient=round(o,2),inside=ins,target=t2.round(2).tolist(),virtual=True)
    print(i,sol[str(i)],flush=True)
    json.dump(sol,open(out,'w'),indent=0)
