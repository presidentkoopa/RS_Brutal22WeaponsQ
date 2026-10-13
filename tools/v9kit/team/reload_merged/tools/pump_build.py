"""RSR-PUMP: what build_proto.py adds for the pump shotguns (hand-loaded shells, a hand-worked pump).

  prepare(R, kind, test)  runs gen_pump.py and rsr_pump_patch.py into R/src, and returns the
                          lumps to replace / add, the ZSCRIPT includes and the event handlers
  hook_hands(path)        pump_hands_hook.py on the (already RSR-hooked) hands.zs, in place
  menudef(text)           the shotgun lines for the RS options help text
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

WEAPON = {'bd': ('actors/Weapons/Shotgun.dec', 'actors/Weapons/Shotgun.dec'),
          'vp': ('Decorate/shotty.txt', 'Decorate/shotty.txt')}
CLEAR = {'bd': 'models/bd/ShotGun/rsr_clear.png'}     # V+: the shotgun shares the M16's folder (the RSR clear skin is there)
TEST_CVARS = (b'user bool rsp_test_steady = false;\t// TEST ONLY: stands in for the engine\'s two-hand steadying\n'
              b'user bool rsp_test_trigger = false;\t// TEST ONLY: stands in for the off-hand trigger\n'
              b'user int rsptest_script = 0;\t\t// TEST ONLY: the scripted off hand (rtest/pump_test.zs)\n'
              b'user float rsptest_speed = 1.0;\t// TEST ONLY: its stroke speed\n'
              b'user int rsptest_holds = 1;\t\t// TEST ONLY: it holds still at moments worth a screenshot\n'
              b'user int rsptest_every = 0;\t\t// TEST ONLY: log every tic\n'
              b'user int rsptest_casings = 1;\t\t// TEST ONLY: count the set\'s spent casings\n')


def prepare(R, kind, test):
    src = R + '/src'
    subprocess.check_call([sys.executable, HERE + '/gen_pump.py', src], stdout=subprocess.DEVNULL)
    subprocess.check_call([sys.executable, HERE + '/rsr_pump_patch.py', src], stdout=subprocess.DEVNULL)
    lump, path = WEAPON[kind]
    out = dict(repl={lump: open(src + '/' + path, 'rb').read()},
               add={'zscript/rsr/rsr_pump.zs': open(src + '/zscript/rsr/rsr_pump.zs', 'rb').read(),
                    'zscript/rsr/rsr_pump_guns.zs': open(src + '/zscript/rsr/rsr_pump_guns.zs', 'rb').read(),
                    'MODELDEF.rsrpump': open(src + '/MODELDEF.rsrpump.' + kind, 'rb').read() + open(src + '/MODELDEF.rsrpump.hands', 'rb').read()},
               zs='#include "zscript/rsr/rsr_pump.zs"\n#include "zscript/rsr/rsr_pump_guns.zs"\n',
               handlers=', "RSP_Handler"' + (', "RSP_TestDriver"' if test else ''),
               test_cvars=TEST_CVARS if test else b'')
    if kind in CLEAR:
        out['add'][CLEAR[kind]] = open(src + '/rsr_clear.png', 'rb').read()
    if test:
        out['add']['zscript/rsr/pump_test.zs'] = open(R + '/rtest/pump_test.zs', 'rb').read()
        out['zs'] += '#include "zscript/rsr/pump_test.zs"\n'
    return out


def hook_hands(path):
    subprocess.check_call([sys.executable, HERE + '/pump_hands_hook.py', path, path], stdout=subprocess.DEVNULL)


def menudef(t):
    a = '\tStaticText "all the way back and let go.", 1\n'
    if t.count(a) != 1:
        return t
    return t.replace(a, a + '\tStaticText " "\n'
                     '\tStaticText "Pump shotguns, VR: reload, then take a shell", 1\n'
                     '\tStaticText "away from the gun (off trigger, or grip away", 1\n'
                     '\tStaticText "from the gun), put it under the loading port", 1\n'
                     '\tStaticText "and push it in. With your hand on the pump", 1\n'
                     '\tStaticText "(steadied, or the off trigger held on it), pull", 1\n'
                     '\tStaticText "it back and push it forward after each shot.", 1\n')
