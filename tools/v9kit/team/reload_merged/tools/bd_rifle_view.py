import numpy as np
from rgeo import *
from rview import view
S='/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
O=S+'/team/reload/tools/'
m = load_md3(S+'/team/reload_survey/_v8x/models/bd/Rifle/Rifle.md3')
sc, off = (-1, 1, 1), (0, 0, -5)
cols=[(255,120,60),(255,220,60),(120,200,255),(90,230,120),(190,190,180),(200,120,255)]
for fr in (3, 19):
    parts=[(surf_flu(m, i, fr, sc, off), s['tris'], cols[i]) for i, s in enumerate(m)]
    view(parts, O+'bd_rifle_side_f%d.png'%fr, 'side', rng=(-35,70,-30,15), px=8, title='BD rifle f%d: liikkuvat orange, ejectport yellow, trigger blue, Lipas green'%fr)
parts=[(surf_flu(m, i, 3, sc, off), s['tris'], cols[i]) for i, s in enumerate(m)]
view(parts, O+'bd_rifle_bottom.png', 'bottom', rng=(-35,70,-10,10), px=8, title='BD rifle bottom')
view(parts, O+'bd_rifle_top.png', 'top', rng=(-35,70,-10,10), px=8, title='BD rifle top')
