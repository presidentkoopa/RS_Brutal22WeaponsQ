import sys; sys.path.insert(0,'.')
from slabs import *
pack=sys.argv[1]; ids=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
Lover={}
if len(sys.argv)>4:
    for kv in sys.argv[4].split(','): k,v=kv.split(':'); Lover[int(k)]=float(v)
w=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
T=tab.parse(pack); tiles=[]
for i in ids:
    c=T['cls'][i]; g=gun_item(c); h=hand_fl(T,i); idx=h[INDEX]; tip=idx[idx[:,0].argmax()]; base=idx[idx[:,0].argmin()]
    Lc=Lover.get(i,center_L(g,tip))
    tiles.append(slab(g,Lc,w,'/dev/null.png' if False else 'zz.png',(base[0]-3,tip[0]+5,tip[2]-8,tip[2]+3),px=32,pts=[(idx,(255,140,80))],title='%d %s Lc=%.1f'%(i,c,Lc)))
W=max(t.size[0] for t in tiles); H=max(t.size[1] for t in tiles); cols=int(__import__("os").environ.get("COLS","2"))
sh=Image.new('RGB',(W*cols,H*((len(tiles)+cols-1)//cols)))
for k,im in enumerate(tiles): sh.paste(im,((k%cols)*W,(k//cols)*H))
sh.save(out)
