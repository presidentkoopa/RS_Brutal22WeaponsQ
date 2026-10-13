import sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad/melee')
import pk3model
S='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
READY = [('Rifle','RIFG','A'),('BrutalPistol','PIST','A'),('BrutalSMG','SMGS','A'),('MP40','MP40','A'),
 ('Sniper','X21G','A'),('AssaultShotgun','USAS','A'),('Shot_Gun','SHTN','A'),('Revolver','REVO','A'),
 ('SSG','SHTZ','A'),('Rocket_Launcher','MISG','A'),('RailGun','RAIL','A'),('Plasma_Gun','PRSG','F'),
 ('GrenadeLauncher','GRLN','A'),('Minigun','CHAG','A'),('BIG_FUCKING_GUN','BFGN','A'),('BFG10k','BG2G','A'),
 ('Unmaker','UNHG','A'),('FlameCannon','FLMG','A'),('Flamethrower2','FLMT','A'),('HellishMissileLauncher','RVCG','A'),
 ('IncendiaryLauncher','M202','A'),('MG42','HBUS','A'),('NukeLauncher','NKLG','A'),('Devastator','DEVA','A')]
_bl=None
def item(cls, spr=None, fr=None):
    global _bl
    if _bl is None:
        _bl=pk3model.blocks(open(S+'/v7x/MODELDEF.bd.txt',encoding='latin-1').read())
    if spr is None:
        for c,s,f in READY:
            if c==cls: spr,fr=s,f
    it=pk3model.lookup(_bl,cls,spr,fr,S+'/v7x')
    if it: it['key']=(spr,fr)
    if it and cls=='Sniper':
        # v8 placement (fill_tables.py): v4-v7 had the HK416 turned round
        it['scale']=[-1.35,1.35,1.35]; it['off']=[6.499,-3.835,10.913]
    return it
