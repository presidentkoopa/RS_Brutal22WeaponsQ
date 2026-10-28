"""TEST ONLY (2.0 final): run a rig tool with the lane's fresh default ini copied in before EVERY engine run (inside the
tool's own rig.lock hold), on the lane's rig binary copy, with the shared lock /home/claude/rig.lock.
f20wrap.py <ini> <script.py> [args...]"""
import os, sys, shutil, runpy
S = '/tmp/claude-0/-home-claude/ec7c6d07-987d-5b8f-a444-5e0b8eae01fd/scratchpad'; GD = '/home/claude/gamedata'
INI = os.path.abspath(sys.argv[1])
os.environ.update(B22_RIG=S + '/int20_rig/bin', B22_IWAD=GD + '/doom2.wad', B22_BD22=GD + '/brutal22test6.pk3', B22_VOX=GD + '/BD_VoxelPack.pk3',
                  RSQ_RIGLOCK='/home/claude/rig.lock', RSQ_GAMEDATA=GD, RSQ_DEPOT='/home/claude/rsq_weapondepot')
if os.environ.get('SCOPE_OUT'): os.environ['B22_BUILD'] = os.environ['SCOPE_OUT']
sys.path.insert(0, '/home/claude/rsq_weapondepot/tools/rig'); import rig
_run = rig.run
def run(*a, **k):
    rig.PK3 = os.environ.get('B22_PK3', rig.PK3)	# drive.py sets the env after rig is imported
    shutil.copy(INI, rig.RIG + '/config/qzdoom.ini'); return _run(*a, **k)
rig.run = run
sys.argv = sys.argv[2:]; sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
runpy.run_path(sys.argv[0], run_name='__main__')
