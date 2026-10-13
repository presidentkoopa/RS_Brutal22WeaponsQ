import re, sys
S='/tmp/claude-0/-home-claude/54c8cc42-5034-5507-9493-fbebf01ce538/scratchpad'
def parse(pack):
    t=open(S+'/cur/%s/zscript/rsq/handtable.zs'%pack).read()
    cls={int(n):c for c,n in re.findall(r"if \(w is '(\w+)'\)\s*return (\d+);",t)}
    def strs(fn):
        b=re.search(r'%s\(int i\)\s*\{\s*static const String v\[\] = \{([^}]*)\}'%fn,t).group(1)
        return re.findall(r'"([^"]*)"',b)
    def vec(fn):
        b=re.search(r'%s\(int i\)\s*\{(.*?)if \(i'%fn,t,re.S).group(1)
        xs=[[float(x) for x in re.search(r'%s\[\] = \{([^}]*)\}'%a,b).group(1).split(',')] for a in 'xyz']
        return [list(r) for r in zip(*xs)]
    m=open(S+'/cur/%s/MODELDEF.rsq'%pack).read()
    blk=m.split('Model RSQ_GunSide')[1]
    letfr={L:int(f) for L,f in re.findall(r'FrameIndex RQGS (\w) 0 (\d+)',blk)}
    return dict(cls=cls,one=strs('GunOne'),two=strs('GunTwo'),hook=vec('GunHook'),rot=vec('GunRot'),letfr=letfr)
