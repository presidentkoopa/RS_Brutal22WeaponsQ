import sys, json
sys.path.insert(0,'melee')
import pk3model, hudrender
from PIL import Image
bl=pk3model.blocks(open('v7x/MODELDEF.bd.txt',encoding='latin-1').read())
H='/mnt/user-data/uploads/DOOMWork/RS_QuestHands/models/'
frame=int(sys.argv[1]); hook=json.loads(sys.argv[2]); rot=json.loads(sys.argv[3]); out=sys.argv[4]
guns=[('BrutalPistol','PIST'),('Rifle','RIFG'),('Shot_Gun','SHTN'),('Revolver','REVO')]
tiles=[]
for cls,spr in guns:
    it=pk3model.lookup(bl,cls,spr,'A','v7x'); it['color']=[150,155,170]
    hand=dict(path=H+'hand.md3',frame=frame,scale=[0.75,0.75,0.75],hook=hook,rot=rot,color=[225,170,135])
    for eye,tag in (([0.42,0.0,-0.03],'right'),([-0.42,0.0,-0.03],'left'),([0.15,0.25,0.30],'player')):
        o='melee/tmp_g.png'
        hudrender.render([it,hand],o,eye=eye,look=[0,-0.05,-0.04],W=300,H=230,fov=45,title='%s %s'%(cls,tag))
        tiles.append(Image.open(o).copy())
S=Image.new('RGB',(900,230*len(guns)))
for i,im in enumerate(tiles): S.paste(im,((i%3)*300,(i//3)*230))
S.save(out)
