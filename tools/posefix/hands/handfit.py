import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/melee')
import align, ermac, guns, gunview, hudrender, support
import numpy as np
from PIL import Image
S='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
GRIPBOX=dict(f=(-22,6),l=(-5,5),u=(-24,1))
def hand_items(gun_set, gun_shift, sup_set, sup_shift, gunframe_override=None):
    out=[]
    if gun_set:
        g,gf,h1,h2,h1one=ermac.SETS[gun_set]
        fr = gunframe_override if gunframe_override is not None else h1
        out.append(dict(path=ermac.E+'hand/hand.md3',frame=fr,hook=align.hook_from_shift(gun_shift),color=[225,170,135],**ermac.PL))
    if sup_set:
        g,gf,h1,h2,_=ermac.SETS[sup_set]
        out.append(dict(path=ermac.E+'hand/hand2.md3',frame=h2,hook=align.hook_from_shift(sup_shift),color=[120,200,140],**ermac.PL))
    return out
def sheet(cls, items, out, title):
    it=guns.item(cls); it['color']=[150,155,170]
    a=S+'/hands/tmp_a.png'; b=S+'/hands/tmp_b.png'; c=S+'/hands/tmp_c.png'
    gunview.view([it]+items,a,'side',px=5,title=title)
    gunview.view([it]+items,b,'bottom',px=5,title=title)
    hudrender.render([it]+items,c,eye=[-0.22,0.20,0.32],look=[0,-0.04,-0.2],W=460,H=330,fov=60,title=title+' (player)')
    A,B,C=Image.open(a),Image.open(b),Image.open(c)
    W=max(A.width,B.width)+C.width+10; H=max(A.height+B.height,C.height)
    O=Image.new('RGB',(W,H)); O.paste(A,(0,0)); O.paste(B,(0,A.height)); O.paste(C,(max(A.width,B.width)+10,0)); O.save(out)
