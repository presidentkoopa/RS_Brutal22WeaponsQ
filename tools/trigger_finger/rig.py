"""Index-finger rig on Ermac's hand.md3 (the cut copy in the v9 packs).
The index finger is its own mesh piece (component 1, 79 verts). Three hinge joints
(MCP at its root, PIP, DIP at the two vertex-ring gaps), flexion about the finger's
lateral axis plus MCP abduction. All maths in the controller frame (F, L, U cm) for
a given placement; md3 coords come back through the inverse of the (affine) placement."""
import numpy as np, sys
sys.path.insert(0,'.')
from hm import *

def affine(it):
    """FLU = A @ md3 + b for a hand placement item"""
    o=gunview.to_fl(hudrender.to_local(np.zeros((1,3)),it))[0]
    A=np.stack([gunview.to_fl(hudrender.to_local(np.eye(3)[k:k+1],it))[0]-o for k in range(3)],1)
    return A,o

def rodrigues(axis, ang):
    a=axis/np.linalg.norm(axis); t=np.radians(ang)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+np.sin(t)*K+(1-np.cos(t))*K@K

# rest segmentation from the straight pistol pose (frame 2): position along the finger
_P2=XYZ[2][INDEX]; _c=_P2.mean(0); _u,_s,_vt=np.linalg.svd(_P2-_c); _ax=_vt[0]
if (XYZ[2][PALM].mean(0)-_c)@_ax>0: _ax=-_ax
SP=(_P2-_c)@_ax; SP=SP-SP.min()          # 0 at the root .. ~7.1 at the tip (md3 units)
J_S=(0.0, 2.09, 4.39)                    # MCP, PIP, DIP along the finger
BLEND=(0.9, 0.35, 0.35)                  # half-width of each joint's blend
def weights(j):
    s=J_S[j]; h=BLEND[j]
    if j==0:
        x=np.clip(SP/h,0,1)            # root ring stays on the knuckle, full turn by 0.9
    else:
        x=np.clip((SP-(s-h))/(2*h),0,1)
    return x*x*(3-2*x)

class Finger:
    def __init__(self, frame, it):
        self.frame=frame; self.it=it
        self.A,self.b=affine(it)
        V=XYZ[frame]
        self.V=(self.A@V.T).T+self.b                # whole hand, FLU
        F=self.V[INDEX]
        # finger axis from root to tip in this pose (first segment)
        seg0=F[SP<1.8]; seg2=F[SP>4.7]
        c0=seg0.mean(0)
        u,s,vt=np.linalg.svd(F[SP<4.2]-F[SP<4.2].mean(0)); a=vt[0]
        if (seg2.mean(0)-c0)@a<0: a=-a
        self.a=a
        # palmar side: toward the middle finger (curled under the index on every grip)
        mid=self.V[COMP==2].mean(0)
        p=mid-F.mean(0); p-=a*(p@a); self.p=p/np.linalg.norm(p)
        self.l=np.cross(self.a,self.p)                     # flexion axis: +angle curls toward p
        # check sign: rotating the tip about l by +30 deg moves it toward p
        R=rodrigues(self.l,30); tip=F[SP.argmax()]; root=F[SP<0.3].mean(0)
        if ((R@(tip-root))-(tip-root))@self.p<0: self.l=-self.l
        # joint pivots: ring centres, nudged to the palmar half (skin creases there)
        self.piv=[]
        for j,sj in enumerate(J_S):
            ring=F[np.abs(SP-sj)<0.45] if j else F[SP<0.45]
            c=ring.mean(0)
            if j==0: c=c-self.a*0.5             # MCP sits a little inside the knuckle
            self.piv.append(c+self.p*0.15)
        self.N=decode_normals(frame)
        self.Nf=(self.A@self.N.T).T; self.Nf/=np.linalg.norm(self.Nf,axis=1)[:,None]
        # pad: palmar surface of the distal segment, a third of the way from the DIP
        dist=np.where((SP>5.0)&(SP<6.1))[0]
        self.pad_i=dist[np.argmax(F[dist]@self.p)]
    def pose(self, flex, abd=0.0, slide=None):
        """flex=(MCP, PIP, DIP) degrees of extra curl; abd: MCP turn about the palmar axis.
        returns finger FLU verts, finger normals (FLU) and the frames used"""
        P=self.V[INDEX].copy(); N=self.Nf[INDEX].copy()
        for j in (2,1,0):
            w=weights(j)
            for k in range(len(P)):
                if w[k]<=0: continue
                R=rodrigues(self.l,flex[j]*w[k])
                if j==0 and abd: R=rodrigues(self.p,abd*w[k])@R
                P[k]=R@(P[k]-self.piv[j])+self.piv[j]; N[k]=R@N[k]
        if slide is not None:
            P=P+weights(0)[:,None]*np.asarray(slide)[None,:]
        return P,N
    def to_md3(self, P):
        return np.linalg.solve(self.A,(P-self.b).T).T

def decode_normals(frame):
    import struct
    d=open(HAND,'rb').read()
    o=struct.unpack_from('<8i',d,76)[6]
    nv=struct.unpack_from('<10i',d,o+68)[3]; oxyz=struct.unpack_from('<10i',d,o+68)[8]
    raw=np.frombuffer(d,dtype='<u1',count=frame*0+nv*8,offset=o+oxyz+frame*nv*8).reshape(nv,8)
    lat=raw[:,6]*(2*np.pi/255); lng=raw[:,7]*(2*np.pi/255)
    return np.stack([np.cos(lng)*np.sin(lat),np.sin(lng)*np.sin(lat),np.cos(lat)],1)
