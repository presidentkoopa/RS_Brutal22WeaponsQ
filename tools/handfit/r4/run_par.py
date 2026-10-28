"""Hands r4 farm runner: start several sup_r4.py jobs as detached processes (one core each) and return at once.
usage: python run_par.py <logdir> <job.json>    job.json = [[script, arg, ...], ...] (paths relative to this file's r4 root)"""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
logdir = os.path.join(ROOT, sys.argv[1]); os.makedirs(logdir, exist_ok=True); jobs = json.load(open(os.path.join(ROOT, sys.argv[2])))
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
flags = 0x00000008 | 0x00000200 if os.name == 'nt' else 0
for k, j in enumerate(jobs):
    argv = [sys.executable] + [os.path.join(ROOT, j[0])] + [os.path.join(ROOT, a) if a.startswith(('scen/', 'out/')) else a for a in j[1:]]
    name = j[-1] if len(j) > 1 else str(k); lf = open(os.path.join(logdir, 'job%02d.log' % k), 'w')
    p = subprocess.Popen(argv, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=ROOT, env=env, creationflags=flags, close_fds=True, start_new_session=(os.name != 'nt'))
    print('started', k, p.pid, ' '.join(j))
