"""Zip src/ into BD22_Models_1.14.pk3 (load after brutal22test6.pk3)."""
import os, zipfile
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, 'src')
out = os.path.join(here, 'BD22_Models_1.14.pk3')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(src):
        for f in sorted(files):
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, src).replace(os.sep, '/'))
print(out)
