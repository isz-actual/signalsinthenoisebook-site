#!/usr/bin/env python3
"""Download any image referenced in build.py that is not yet in assets/img (one-time copy from Framer)."""
import os, re, urllib.request
ROOT = os.path.dirname(os.path.abspath(__file__))
names = sorted(set(re.findall(r'[A-Za-z0-9]{15,}\.(?:jpe?g|png)', open(os.path.join(ROOT, "build.py")).read())))
os.makedirs(os.path.join(ROOT, "assets/img"), exist_ok=True)
for n in names:
    p = os.path.join(ROOT, "assets/img", n)
    if not os.path.exists(p):
        urllib.request.urlretrieve("https://framerusercontent.com/images/" + n, p)
        print("downloaded", n)
