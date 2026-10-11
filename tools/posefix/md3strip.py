"""Rewrite an MD3 keeping only some frames, in their original order.

Everything that is not per-frame (surface names, shaders, triangles, UVs) is
copied byte for byte. Per-frame data (frame headers, tags, vertex positions) is
copied for the kept frames only. Offsets are recomputed.
"""
import struct

HDR = struct.Struct('<4si64si8i')      # ident, version, name, flags, 8 ints
SURF = struct.Struct('<4s64s10i')      # ident, name, flags, numFrames, numShaders, numVerts,
                                       # numTris, ofsTris, ofsShaders, ofsST, ofsXYZ, ofsEnd


def parse(data):
    ident, ver, name, flags, nfr, ntag, nsurf, nskin, ofr, otag, osurf, oend = HDR.unpack_from(data, 0)
    if ident != b'IDP3':
        raise ValueError('not an MD3')
    frames = [data[ofr + i * 56: ofr + (i + 1) * 56] for i in range(nfr)]
    tags = [data[otag + i * ntag * 112: otag + (i + 1) * ntag * 112] for i in range(nfr)]
    surfs = []
    off = osurf
    for _ in range(nsurf):
        (sid, sname, sflags, snfr, nsh, nv, nt, otri, osh, ost, oxyz, send) = SURF.unpack_from(data, off)
        if snfr != nfr:
            raise ValueError('surface frame count %d != %d' % (snfr, nfr))
        surfs.append(dict(
            name=sname, flags=sflags, nsh=nsh, nv=nv, nt=nt,
            shaders=data[off + osh: off + osh + nsh * 68],
            tris=data[off + otri: off + otri + nt * 12],
            st=data[off + ost: off + ost + nv * 8],
            xyz=[data[off + oxyz + f * nv * 8: off + oxyz + (f + 1) * nv * 8] for f in range(nfr)],
        ))
        off += send
    return dict(ver=ver, name=name, flags=flags, nfr=nfr, ntag=ntag, nskin=nskin,
                frames=frames, tags=tags, surfs=surfs)


def build(m, keep):
    keep = list(keep)
    nfr = len(keep)
    body_frames = b''.join(m['frames'][k] for k in keep)
    body_tags = b''.join(m['tags'][k] for k in keep)
    surf_blobs = []
    for s in m['surfs']:
        ofs_sh = SURF.size
        ofs_tri = ofs_sh + len(s['shaders'])
        ofs_st = ofs_tri + len(s['tris'])
        ofs_xyz = ofs_st + len(s['st'])
        xyz = b''.join(s['xyz'][k] for k in keep)
        ofs_end = ofs_xyz + len(xyz)
        head = SURF.pack(b'IDP3', s['name'], s['flags'], nfr, s['nsh'], s['nv'], s['nt'],
                         ofs_tri, ofs_sh, ofs_st, ofs_xyz, ofs_end)
        surf_blobs.append(head + s['shaders'] + s['tris'] + s['st'] + xyz)
    ofr = HDR.size
    otag = ofr + len(body_frames)
    osurf = otag + len(body_tags)
    oend = osurf + sum(len(b) for b in surf_blobs)
    head = HDR.pack(b'IDP3', m['ver'], m['name'], m['flags'], nfr, m['ntag'], len(m['surfs']),
                    m['nskin'], ofr, otag, osurf, oend)
    return head + body_frames + body_tags + b''.join(surf_blobs)


def strip(data, keep):
    return build(parse(data), sorted(set(keep)))


def verify(orig, new, keep):
    """Every kept frame identical, everything static identical."""
    a, b = parse(orig), parse(new)
    keep = sorted(set(keep))
    assert b['nfr'] == len(keep)
    assert len(a['surfs']) == len(b['surfs'])
    for n, k in enumerate(keep):
        assert a['frames'][k] == b['frames'][n]
        assert a['tags'][k] == b['tags'][n]
        for sa, sb in zip(a['surfs'], b['surfs']):
            assert sa['xyz'][k] == sb['xyz'][n]
    for sa, sb in zip(a['surfs'], b['surfs']):
        for key in ('name', 'flags', 'nsh', 'nv', 'nt', 'shaders', 'tris', 'st'):
            assert sa[key] == sb[key], key
    return True
