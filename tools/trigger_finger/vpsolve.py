import sys, json; sys.path.insert(0,'.')
from trig import *
T=tab.parse('vp'); out='sol_vp.json'
try: sol=json.load(open(out))
except Exception: sol={}
# V+'s low-poly guns: trigger = a point inside the guard opening (no blade in the meshes), L 0
TG={1:(3.2,0,-5.4),3:(2.8,0,-3.2),4:(1.8,0,-4.2),5:(1.6,0,-3.4)}
for i in [int(x) for x in sys.argv[1].split(',')]:
    it=hand_item(T,i); fg=Finger(it['frame'],it); tg=np.array(TG[i],float)
    B=np.array([[tg[0]-0.3*s, tg[1]+0.15*q, tg[2]+u] for u in np.linspace(-0.9,0.9,7) for s in (0,1) for q in (-1,1)])
    x,e,o,ins,t2=solve3(fg,B)
    sol[str(i)]=dict(cls=T['cls'][i],frame=it['frame'],x=[round(float(v),2) for v in x],err=round(e,2),orient=round(o,2),inside=ins,target=t2.round(2).tolist(),virtual=True)
    print(i,sol[str(i)],flush=True); json.dump(sol,open(out,'w'),indent=0)
