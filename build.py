"""Zip src/ into BD22_VR-Reloaded_<version>.pk3 (load after brutal22test6.pk3).

The version comes from the VERSION file next to this script. On main it is the public
number (1.9x); on dev it is the internal number (2.x). Pass a version on the command
line to override it for one build: python build.py 1.96c-test
"""
import os, sys, zipfile
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, 'src')
if len(sys.argv) > 1:
    version = sys.argv[1]
else:
    with open(os.path.join(here, 'VERSION')) as f:
        version = f.read().strip()
out = os.path.join(here, 'BD22_VR-Reloaded_%s.pk3' % version)
# .md3 models go in LZMA (zip method 14), as the 1.96b release did: about 30 MB instead of 50.
# QuestZDoom 17.3 reads it (file_zip.cpp). Everything else is deflated.
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(src):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, src).replace(os.sep, '/'),
                    compress_type=zipfile.ZIP_LZMA if f.lower().endswith('.md3') else zipfile.ZIP_DEFLATED)
print(out)
