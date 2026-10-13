import sys, json; sys.path.insert(0,'.')
from rig import *
from rend import *
from slabs import center_L
from scipy.optimize import minimize

def blade(g, Lc, box, w=1.0):
    V=np.concatenate([v for _,v in gun_tris(g)])
    f0,f1,u0,u1=box
    m=(np.abs(V[:,1]-Lc)<w)&(V[:,0]>=f0)&(V[:,0]<=f1)&(V[:,2]>=u0)&(V[:,2]<=u1)
    return V[m]

def contact(B, frac=0.45):
    top,bot=B[:,2].max(),B[:,2].min()
    u=top-frac*(top-bot)
    band=B[np.abs(B[:,2]-u)<max(0.3,(top-bot)*0.12)]
    if len(band)<2: band=B[np.argsort(np.abs(B[:,2]-u))[:3]]
    k=band[:,0].argmax()
    return np.array([band[k,0], B[:,1].mean(), u])

def solve(fg, target, back=(-1,0,0), x0=(30,40,25,0)):
    back=np.array(back,float)
    lim=[(-15,85),(0,100),(0,75),(-30,30)]
    def cost(x):
        P,N=fg.pose(x[:3],x[3])
        e=P[fg.pad_i]-target
        c=e@e + 0.4*(1-N[fg.pad_i]@back)
        c+=0.0004*(x[2]-0.65*x[1])**2 + 0.00005*(x[0]**2+x[1]**2+x[3]**2)
        for v,(lo,hi) in zip(x,lim): c+=0.05*(max(0,lo-v)**2+max(0,v-hi)**2)
        return c
    best=None
    for s in (x0,(10,60,40,10),(50,20,10,-10),(20,80,50,15)):
        r=minimize(cost,s,method='Nelder-Mead',options=dict(xatol=0.05,fatol=1e-6,maxiter=4000))
        if best is None or r.fun<best.fun: best=r
    x=best.x; P,N=fg.pose(x[:3],x[3])
    return x, np.linalg.norm(P[fg.pad_i]-target), P

def squeeze(x, amt=18):
    """a further curl of ~amt degrees, mostly at the PIP and DIP"""
    return np.concatenate([[x[0]+0.2*amt, x[1]+0.5*amt, x[2]+0.3*amt+2, x[3]], x[4:]])
import md3w, os
from rig import decode_normals
def full_frame(fg, P, N):
    """whole-hand md3 verts + normals with the finger replaced"""
    V=XYZ[fg.frame].copy(); Nm=decode_normals(fg.frame)
    V[INDEX]=fg.to_md3(P)
    Ninv=np.linalg.solve(fg.A, N.T).T            # directions back to md3 space
    Nm[INDEX]=Ninv/np.linalg.norm(Ninv,axis=1)[:,None]
    return V,Nm
def sheet(g, fg, poses, it, out, title, Lc, rng):
    """poses: list of (label, P, N). Rows: side slab+finger, bottom view, player view"""
    src=open(HAND,'rb').read()
    frames=[full_frame(fg,P,N) for _,P,N in poses]
    tmp='tmp_sheet.md3'; open(tmp,'wb').write(md3w.add_frames(src,frames,['x']*len(frames)))
    tiles=[]
    for k,(lab,P,N) in enumerate(poses):
        h=dict(it); h['path']=tmp; h['frame']=10+k
        a=slab(g,Lc,1.0,'zz.png',rng,px=24,pts=[(P,(255,140,80))],title='%s %s'%(title,lab))
        gunview.view([g,h],'zb.png','bottom',rng=(rng[0]-2,rng[1]+2,-8,6),px=24,title=lab)
        hudrender.render([g,h],'zc.png',eye=[-0.10,0.02,0.20],look=[0.0,-0.05,0.0],W=a.size[0],H=a.size[1],fov=40,title=lab+' (player-ish, from right)')
        b=Image.open('zb.png').copy(); c=Image.open('zc.png').copy()
        hudrender.render([g,h],'zd.png',eye=[0.12,-0.02,0.15],look=[0.0,-0.05,0.0],W=a.size[0],H=a.size[1],fov=40,title=lab+' (from left/below)')
        dd=Image.open('zd.png').copy()
        W=a.size[0]+b.size[0]; H=max(a.size[1],b.size[1])
        row=Image.new('RGB',(a.size[0]*2+b.size[0], max(a.size[1]*1,b.size[1])),(0,0,0))
        row.paste(a,(0,0)); row.paste(b,(a.size[0],0)); row.paste(c,(a.size[0]+b.size[0],0))
        tiles.append(row); tiles.append(dd)
    Wt=max(t.size[0] for t in tiles); Ht=sum(t.size[1] for t in tiles)
    sh=Image.new('RGB',(Wt,Ht)); y=0
    for t in tiles: sh.paste(t,(0,y)); y+=t.size[1]
    sh.save(out); return out

def pad_index(fg, lo=5.6, hi=6.5):
    F=fg.V[INDEX]; c=np.where((SP>lo)&(SP<hi))[0]
    return c[np.argmax(F[c]@fg.p)]

def solve2(fg, B, skin=0.2, fracs=(0.3,0.45,0.6,0.75)):
    """fingertip pad onto the front face of trigger blade B (gun verts, FLU)"""
    import itertools
    fg.pad_i=pad_index(fg)
    lo=B.min(0)-0.05; hi=B.max(0)+0.05
    targets=[]
    for fr in fracs:
        c=contact(B,fr); c[0]+=skin; targets.append(c)
    back=np.array([-1.0,0,0])
    lim=[(-15,85),(0,100),(0,75),(-30,30)]
    def cost(x,tg):
        P,N=fg.pose(x[:3],x[3])
        e=P[fg.pad_i]-tg
        c=e@e + 0.5*(1-N[fg.pad_i]@back)
        inside=np.all((P>lo)&(P<hi),axis=1)
        c+=2.0*inside.sum()
        c+=0.0004*(x[2]-0.65*x[1])**2 + 0.00003*(x[0]**2+x[1]**2+x[3]**2)
        for v,(l,h) in zip(x,lim): c+=0.05*(max(0,l-v)**2+max(0,v-h)**2)
        return c
    best=None
    for tg in targets:
        grid=sorted(((cost(np.array(s,float),tg),s) for s in itertools.product(range(-10,81,15),range(0,101,20),(0,30,60),range(-30,31,15))))[:4]
        for _,s in grid:
            r=minimize(cost,np.array(s,float),args=(tg,),method='Nelder-Mead',options=dict(xatol=0.05,fatol=1e-6,maxiter=3000))
            if best is None or r.fun<best[0].fun: best=(r,tg)
    r,tg=best; x=r.x; P,N=fg.pose(x[:3],x[3])
    inside=int(np.all((P>lo)&(P<hi),axis=1).sum())
    return x, float(np.linalg.norm(P[fg.pad_i]-tg)), float(N[fg.pad_i]@back), inside, tg

def solve3(fg, B, skin=0.2, fracs=(0.2,0.35,0.5,0.65,0.8), maxslide=0.9, x_init=None):
    """solve2 plus a slide of the finger at its root (<= maxslide cm, blended off at the knuckle)"""
    import itertools
    fg.pad_i=pad_index(fg)
    lo=B.min(0)-0.05; hi=B.max(0)+0.05
    targets=[]
    for fr in fracs:
        c=contact(B,fr); c[0]+=skin; targets.append(c)
    back=np.array([-1.0,0,0])
    lim=[(-15,85),(0,100),(0,75),(-30,30)]
    def unpack(x): return x[:3],x[3],x[4:7]
    def cost(x,tg):
        fl,ab,sl=unpack(x)
        P,N=fg.pose(fl,ab,sl)
        e=P[fg.pad_i]-tg
        c=e@e + 0.5*(1-N[fg.pad_i]@back)
        c+=2.0*np.all((P>lo)&(P<hi),axis=1).sum()
        c+=0.0004*(x[2]-0.65*x[1])**2 + 0.00003*(x[0]**2+x[1]**2+x[3]**2)
        sn=np.linalg.norm(sl); c+=0.02*sn*sn+5*max(0,sn-maxslide)**2
        for v,(l,h) in zip(x,lim): c+=0.05*(max(0,l-v)**2+max(0,v-h)**2)
        return c
    best=None
    for tg in targets:
        starts=[]
        for s in itertools.product(range(-10,81,15),range(0,101,20),(0,30,60),range(-30,31,15)):
            starts.append((cost(np.array(list(s)+[0,0,0],float),tg),s))
        starts.sort()
        for _,s in starts[:3]:
            r=minimize(cost,np.array(list(s)+[0,0,0],float),args=(tg,),method='Powell',options=dict(xtol=0.02,ftol=1e-6,maxiter=6000))
            if best is None or r.fun<best[0].fun: best=(r,tg)
    r,tg=best; x=r.x; P,N=fg.pose(x[:3],x[3],x[4:7])
    inside=int(np.all((P>lo)&(P<hi),axis=1).sum())
    return x, float(np.linalg.norm(P[fg.pad_i]-tg)), float(N[fg.pad_i]@back), inside, tg
