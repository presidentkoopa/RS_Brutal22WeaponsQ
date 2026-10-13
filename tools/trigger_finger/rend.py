import sys
sys.path.insert(0,'.')
from hm import *
import tab, guns, gunview, hudrender
from PIL import Image
HANDP=S+'/cur/bd/models/rsq/hand.md3'
def hand_item(T,i,two=False,path=HANDP,frame=None):
    L=(T['two'] if two else T['one'])[i]
    return dict(path=path,frame=T['letfr'][L] if frame is None else frame,hook=T['hook'][i],rot=T['rot'][i],color=[225,170,135],**PL)
def gun_item(cls):
    it=guns.item(cls); it['color']=[150,155,170]; return it
def gun_tris(g):
    out=[]
    for tris,raw in gunview.item_mesh(g):
        v=gunview.to_fl(hudrender.to_local(raw,g)); out.append((tris,v))
    return out
def hand_fl(T,i,V=None,two=False):
    it=hand_item(T,i,two)
    if V is None: V=XYZ[it['frame']]
    return gunview.to_fl(hudrender.to_local(V,it))
def slab(g, Lc, w, out, rng, px=20, pts=(), title='', marks=()):
    from PIL import ImageDraw
    import math
    h0,h1,v0,v1=rng; W,H=int((h1-h0)*px),int((v1-v0)*px)
    img=Image.new('RGB',(W,H),(60,62,78)); dr=ImageDraw.Draw(img)
    P=lambda f,u:((f-h0)*px,H-(u-v0)*px)
    for gx in range(math.ceil(h0),int(h1)+1):
        dr.line([P(gx,v0),P(gx,v1)],fill=(80,82,100) if gx%5 else (130,130,160))
    for gy in range(math.ceil(v0),int(v1)+1):
        dr.line([P(h0,gy),P(h1,gy)],fill=(80,82,100) if gy%5 else (130,130,160))
    polys=[]
    for tris,v in gun_tris(g):
        a,b,c=v[tris[:,0]],v[tris[:,1]],v[tris[:,2]]; cen=(a+b+c)/3
        n=np.cross(b-a,c-a); n/=np.linalg.norm(n,axis=1)[:,None]+1e-12
        sel=np.abs(cen[:,1]-Lc)<w
        for k in np.where(sel)[0]:
            sh=abs(n[k,1])*0.5+0.4
            polys.append((-cen[k,1],[P(p[0],p[2]) for p in (a[k],b[k],c[k])],tuple(int(150*sh+40*(abs(cen[k,1]-Lc)<w/3)) for _ in range(3))))
    polys.sort(key=lambda t:t[0])
    for _,pp,c in polys: dr.polygon(pp,fill=c,outline=(40,40,50))
    for P3,col in pts:
        for p in P3: x,y=P(p[0],p[2]); dr.ellipse((x-2,y-2,x+2,y+2),fill=col)
    for f,u,lab,col in marks:
        x,y=P(f,u); dr.ellipse((x-6,y-6,x+6,y+6),outline=col,width=2); dr.text((x+7,y-7),lab,fill=col)
    for gx in range(math.ceil(h0),int(h1)+1):
        if gx%2==0: dr.text((P(gx,v0)[0]+2,H-14),str(gx),fill=(255,255,255))
    for gy in range(math.ceil(v0),int(v1)+1):
        if gy%2==0: dr.text((2,P(h0,gy)[1]-12),str(gy),fill=(255,255,255))
    dr.text((3,3),title+'  grid 1cm, F right U up',fill=(255,255,0))
    img.save(out); return img.copy()
VPG='/mnt/user-data/uploads/DOOMWork/VR_WeaponSetRebuild/WeaponSets/questvanillavrplusforclaude/models/weapons/hud/'
VPITEMS={'VR_Rifle':'guns/m16.md3','VR_Revolver':'gats/rev.md3','VR_Revolver2':'gats/rev.md3','VR_Shotgun':'guns/shotgun.md3','VR_SuperShotgun':'guns/ssg.md3'}
_gi=gun_item
def gun_item(cls):
    if cls in VPITEMS:
        return dict(path=VPG+VPITEMS[cls],frame=0,scale=[1.35,1.35,1.35],off=[0,0,0],color=[150,155,170])
    return _gi(cls)
VPSHARED={'Vanilla_Chaingun':('Minigun',None),'Vanilla_RocketLauncher':('Rocket_Launcher',None),'Vanilla_PlasmaRifle':('Plasma_Gun',None),'Vanilla_BFG9000':('BIG_FUCKING_GUN',6)}
_gi2=gun_item
def gun_item(cls):
    if cls in VPSHARED:
        bd,fr=VPSHARED[cls]; it=_gi2(bd); it['off']=[0.0,0.0,0.0]
        if fr is not None: it['frame']=fr
        return it
    return _gi2(cls)
