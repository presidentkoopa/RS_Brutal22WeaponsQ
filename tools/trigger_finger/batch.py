import sys, json; sys.path.insert(0,'.')
from trig import *; import boxes
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pack=sys.argv[1]; out=sys.argv[2]; ids=[int(x) for x in sys.argv[3].split(',')]
BX=getattr(boxes,pack.upper()); LC=getattr(boxes,pack.upper()+'_LC')
T=tab.parse(pack); res={}
try: res=json.load(open(out))
except Exception: pass
for i in ids:
    for two in ((False,True) if T['one'][i]!=T['two'][i] else (False,)):
        key='%d%s'%(i,'b' if two else '')
        it=hand_item(T,i,two); g=gun_item(T['cls'][i]); fg=Finger(it['frame'],it)
        B=blade(g,LC.get(i,0.0),BX[i])
        x,e,o,ins,tg=(solve3 if '--slide' in sys.argv else solve2)(fg,B)
        res[key]=dict(cls=T['cls'][i],frame=it['frame'],x=[round(float(v),2) for v in x],err=round(e,2),orient=round(o,2),inside=ins,target=tg.round(2).tolist())
        print(key,res[key],flush=True)
        json.dump(res,open(out,'w'),indent=0)
