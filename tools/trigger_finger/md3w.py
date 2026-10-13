import struct, numpy as np
def encode_normals(N):
    N=N/np.linalg.norm(N,axis=1)[:,None]
    lat=np.arccos(np.clip(N[:,2],-1,1)); lng=np.arctan2(N[:,1],N[:,0])
    a=np.round(lat*255/(2*np.pi)).astype(int)&255; b=np.round(lng*255/(2*np.pi)).astype(int)&255
    return a,b
def add_frames(src, frames, names):
    """src md3 bytes (one surface); frames: list of (V (nv,3) md3 units, N (nv,3)); returns new bytes"""
    d=bytearray(src)
    ident,ver,name,flags,nfr,ntag,nsurf,nskin,ofr,otag,osurf,oeof=struct.unpack_from('<4si64siiiiiiiii',d,0)
    assert nsurf==1 and ntag==0
    K=len(frames)
    head=d[:ofr]; frs=d[ofr:ofr+56*nfr]; surf=d[osurf:oeof]
    sid,sname,sflags,snfr,nsh,nv,nt,otri,osh,ost,oxyz,oend=struct.unpack_from('<4s64s10i',surf,0)
    assert oxyz>max(otri,osh,ost) and oend==oxyz+snfr*nv*8
    newfr=bytearray(); newxyz=bytearray()
    for (V,N),nm in zip(frames,names):
        mn=V.min(0); mx=V.max(0); r=float(np.linalg.norm(V,axis=1).max())
        newfr+=struct.pack('<3f3f3ff16s',*mn,*mx,0,0,0,r,nm.encode()[:15])
        q=np.round(V*64).astype(int); assert np.abs(q).max()<32767
        a,b=encode_normals(N)
        for k in range(nv):
            newxyz+=struct.pack('<3hBB',q[k,0],q[k,1],q[k,2],a[k],b[k])
    surf2=bytearray(surf)+newxyz
    struct.pack_into('<i',surf2,72,snfr+K)          # surface num_frames (after id + name)
    struct.pack_into('<i',surf2,68+4*9,oend+K*nv*8) # ofs_end
    out=bytearray(head)+frs+newfr
    osurf2=len(out); out+=surf2
    struct.pack_into('<i',out,76,nfr+K)
    struct.pack_into('<i',out,76+4*6,osurf2)
    struct.pack_into('<i',out,76+4*7,len(out))
    return bytes(out)
