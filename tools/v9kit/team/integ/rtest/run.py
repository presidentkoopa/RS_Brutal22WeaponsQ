"""TEST ONLY: headless runs of the v9 packs on the local QuestZDoom build.

    run.py <name> <set: bd|vp> <pack: v8|v9> <overlay: log|vr> <timeout s> [spec ...]

spec: "T:console cmds" runs them at about maptime T; "T:shot:LABEL" takes a screenshot
(shots/<name>_<LABEL>.png). Each run gets a fresh HOME (homes/<name>) from template.ini.
The overlay pk3 (test only, loaded after the pack): the driver / logger (driver.zs +
v9extra.zs or v8stub.zs); 'vr' also swaps in the reload release's fake VR hands
(rtest/vrhand_rsr.zs: gun hand in front of the player, scripted off hand, RSR_TestDriver).
"""
import os, sys, shutil, subprocess, glob, zipfile

S = '/tmp/claude-0/-home-claude/688b1996-39a0-5234-911a-a90085ab177b/scratchpad'
H = os.path.dirname(os.path.abspath(__file__))
BASE = {'bd': ['/mnt/user-data/uploads/DOOMWork/RS_VR_Weapons/bd22/brutal22test6.pk3'],
        'vp': ['/mnt/user-data/uploads/1.0b_Weapons_VanillaVRPlus_v1.2']}
PACK = {('bd', 'v8'): S + '/out/RS_BD22_Models_v8.pk3', ('vp', 'v8'): S + '/vplus/RS_VanillaVRPlus_VR.pk3',
        ('bd', 'v9'): S + '/team/out_v9/BD22_Models_v9.pk3', ('vp', 'v9'): S + '/team/out_v9/RS_VanillaVRPlus_VR_v9.pk3'}
VRHAND = os.environ.get('V9T_VRHAND', S + '/team/out_v9/_work/release/%s/rtest/vrhand_rsr.zs')   # the build's own snapshot

CVARS = '''user int v9t_mode = 0;
user int v9t_slot = 200;
user string v9t_guns = "";
user int v9t_empty = 0;
user string v9t_take = "";
user string v9t_give = "";
user int v9t_hl = 0;
user int v9t_reload_tmo = 700;
'''
EXTRA_ZS = []
CVARS_VR = '''user int rsrtest_script = 1;
user bool rsr_test_offdraw = true;
user float rsr_test_yaw = 0;
user int rsbtest_script = 0;
user int rsbtest_chambers = 0;
user bool rsp_test_steady = false;
user bool rsp_test_trigger = false;
user int rsptest_script = 0;
user float rsptest_speed = 1.0;
user int rsptest_holds = 0;
user int rsptest_every = 0;
user int rsptest_casings = 1;
'''


def overlay(pack, ov, kind):
    EXTRA_ZS.clear()
    out = os.path.join(H, 'ov_%s_%s_%s.pk3' % (kind, pack, ov))
    z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    extra = 'v9extra.zs' if pack == 'v9' else 'v8stub.zs'
    z.write(os.path.join(H, 'driver.zs'), 'zscript/v9t/driver.zs')
    z.write(os.path.join(H, extra), 'zscript/v9t/' + extra)
    hs = ['"V9T_Driver"'] + (['"V9T_HandsLog"'] if pack == 'v9' else []) + (['"RSR_TestDriver"'] if ov in ('vr', 'vrview') else [])
    z.writestr('CVARINFO.v9t', CVARS + (CVARS_VR if ov in ('vr', 'vrview') else ''))
    if ov in ('vr', 'vrview'):
        # the fake hands, and the merged reloads' own test drivers (break-open, pump) when the build
        # has them, in the one file the pack's ZSCRIPT includes (a later ZSCRIPT lump cannot be
        # seen from the pack's)
        vh = VRHAND % kind if '%s' in VRHAND else VRHAND
        body = open(vh).read()
        for f in ('rsb_testdriver.zs', 'pump_test.zs'):
            p = os.path.join(os.path.dirname(vh), f)
            if os.path.isfile(p):
                body += '\n// ---- ' + f + '\n' + open(p).read()
                EXTRA_ZS.append(f)
        z.writestr('zscript/rsvr/vrhand.zs', body)
    if ov == 'vrview':
        # TEST VIEW only (as the reload release's build_proto.py --test): keep the off-hand layers
        # with the gun when every layer is yawed for a side view (rsr_test_yaw)
        h = zipfile.ZipFile(PACK[(kind, pack)]).read('zscript/rsq/hands.zs').decode()
        a = '\toverride Vector3, Vector3 ModifyBobLayer3D(Vector3 translation, Vector3 rotation, int layer, double ticfrac)\n\t{\n'
        assert h.count(a) == 1
        z.writestr('zscript/rsq/hands.zs', h.replace(a, a + '\t\ttranslation += RSR_TestView.HandShift(layer);\t// TEST ONLY\n'))
    if 'rsb_testdriver.zs' in EXTRA_ZS:
        hs.append('"RSB_TestDriver"')
    if 'pump_test.zs' in EXTRA_ZS:
        hs.append('"RSP_TestDriver"')
    z.writestr('ZSCRIPT.v9t', 'version "4.10"\n#include "zscript/v9t/driver.zs"\n#include "zscript/v9t/%s"\n' % extra
               )
    z.writestr('MAPINFO.v9t', 'gameinfo { AddEventHandlers = %s }\n' % ', '.join(hs))
    z.close()
    return out


def run(name, kind, pack, ov, tmo, specs):
    home = os.path.join(H, 'homes', name)
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(home + '/.config/qzdoom')
    shutil.copy(os.path.join(H, 'template.ini'), home + '/.config/qzdoom/qzdoom.ini')
    tmp = os.path.join(H, 'shots', '_tmp_' + name)
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    items = []
    for a in specs:
        t, rest = a.split(':', 1)
        items.append((int(t), rest))
    items.sort(key=lambda x: x[0])
    cmds, now, shots = ['screenshot_dir ' + tmp], 0, []
    for t, c in items:
        if t > now:
            cmds.append('wait %d' % (t - now))
            now = t
        if c.startswith('shot:'):
            cmds.append('screenshot')
            shots.append(c[5:])
        else:
            cmds.append(c)
    cmds += ['wait 5', 'quit']
    files = BASE[kind] + [PACK[(kind, pack)]] + ([overlay(pack, ov, kind)] if ov != 'none' else [])
    env = dict(os.environ, LD_LIBRARY_PATH=S + '/build/zminst/lib', HOME=home)
    outp = os.path.join(H, 'out', name + '.out')
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, 'w') as f:
        r = subprocess.call(['timeout', str(tmo), 'xvfb-run', '-a', '-s', '-screen 0 1024x768x24', 'stdbuf', '-oL', '-eL',
                             './qzdoom', '-iwad', 'freedoom2.wad', '-file'] + files + ['-nosound', '+map', 'MAP01', '+' + '; '.join(cmds)],
                            cwd=S + '/build/qzd', env=env, stdout=f, stderr=subprocess.STDOUT)
    got = sorted(glob.glob(tmp + '/*.png'))
    for g, n in zip(got, shots):
        os.replace(g, os.path.join(H, 'shots', '%s_%s.png' % (name, n)))
    shutil.rmtree(tmp, ignore_errors=True)
    print('%s exit %d, shots %d of %d -> %s' % (name, r, len(got), len(shots), outp))
    return r


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6:])
