import sys; sys.path.insert(0,'.')
from rend import *
def center_L(g,tip):
    V=np.concatenate([v for _,v in gun_tris(g)])
    m=(V[:,0]>tip[0]-14)&(V[:,0]<tip[0]+6)&(V[:,2]>tip[2]-12)&(V[:,2]<tip[2]+4)
    V=V[m]; return 0.5*(np.percentile(V[:,1],5)+np.percentile(V[:,1],95))
def run(pack, skip, out, w=1.0):
    T=tab.parse(pack); tiles=[]; info={}
    for i in sorted(T['cls']):
        if i in skip: continue
        c=T['cls'][i]; g=gun_item(c); h=hand_fl(T,i)
        idx=h[INDEX]; tip=idx[idx[:,0].argmax()]
        Lc=center_L(g,tip); info[i]=(c,Lc,tip)
        print(i,c,'gun centre L %.2f'%Lc)
        tiles.append(slab(g,Lc,w,'z_%s%02d.png'%(pack,i),(tip[0]-14,tip[0]+6,tip[2]-12,tip[2]+4),px=18,pts=[(idx,(255,140,80))],title='%d %s Lc=%.1f'%(i,c,Lc)))
    W,H=tiles[0].size; cols=4
    sh=Image.new('RGB',(W*cols,H*((len(tiles)+cols-1)//cols)))
    for k,im in enumerate(tiles): sh.paste(im,((k%cols)*W,(k//cols)*H))
    sh.save(out); return info
if __name__=='__main__':
    run('bd',(22,24,25),'bd_slab.png')
