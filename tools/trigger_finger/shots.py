import sys, json; sys.path.insert(0,'.')
from trig import *
import build
pack=sys.argv[1]; sol=json.load(open(sys.argv[2])); md3=sys.argv[3]; out=sys.argv[4]; n0=10
_,letters,_,_=build.make(pack,sys.argv[2],HAND)
T=tab.parse(pack); tiles=[]; W,H=230,170
eyeoff=np.array([float(v) for v in (sys.argv[5] if len(sys.argv)>5 else '3,-12,-2').split(',')])
for i in sorted(letters):
    L=letters[i]; k=build.LET.index(L)
    it=hand_item(T,i); g=gun_item(T['cls'][i]); tg=np.array(sol[str(i)]['target'])+(np.array([0,0,5.0]) if 'from_bd' in sol[str(i)] else 0)
    loc=lambda f: [-f[1]/100, f[2]/100, -f[0]/100]
    for kind,fr in (('on',n0+2*k),('sqz',n0+2*k+1)):
        h=dict(it); h['path']=md3; h['frame']=fr
        hudrender.render([g,h],'t.png',eye=loc(tg+eyeoff),look=loc(tg),W=W,H=H,fov=55,title='%d %s %s'%(i,T['cls'][i][:12],kind))
        tiles.append(Image.open('t.png').copy())
cols=8; sh=Image.new('RGB',(W*cols,H*((len(tiles)+cols-1)//cols)))
for j,t in enumerate(tiles): sh.paste(t,((j%cols)*W,(j//cols)*H))
sh.save(out)
