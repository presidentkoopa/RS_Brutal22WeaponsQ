import sys, numpy as np, struct
S='/tmp/claude-0/-home-claude/54c8cc42-5034-5507-9493-fbebf01ce538/scratchpad'
sys.path.insert(0, S+'/melee')
import hudrender, gunview
HAND=S+'/cur/bd/models/rsq/hand.md3'
TRIS, XYZ = hudrender.load(HAND)[0]
PL=dict(scale=[-1.0,1.0,1.0], off=[0.0,-24.0,-10.0])
def fl(v, hook=(0,0,0), rot=(0,0,0)):
    return gunview.to_fl(hudrender.to_local(v, dict(hook=hook, rot=rot, **PL)))
def adjacency():
    n=XYZ.shape[1]; adj=[set() for _ in range(n)]
    for a,b,c in TRIS:
        adj[a]|={b,c}; adj[b]|={a,c}; adj[c]|={a,b}
    return adj
def components():
    adj=adjacency(); n=len(adj); comp=np.full(n,-1); c=0
    for s in range(n):
        if comp[s]>=0: continue
        st=[s]; comp[s]=c
        while st:
            u=st.pop()
            for w in adj[u]:
                if comp[w]<0: comp[w]=c; st.append(w)
        c+=1
    return comp
COMP=components()
INDEX=np.where(COMP==1)[0]; PALM=np.where(COMP==5)[0]
def rigid(A,B):
    """R,t with R@A+t ~ B (rows)"""
    ca,cb=A.mean(0),B.mean(0); H=(A-ca).T@(B-cb); U,s,Vt=np.linalg.svd(H)
    D=np.diag([1,1,np.sign(np.linalg.det(Vt.T@U.T))]); R=Vt.T@D@U.T
    return R, cb-R@ca
