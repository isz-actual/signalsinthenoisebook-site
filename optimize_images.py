#!/usr/bin/env python3
"""Make web-sized images from source-images/ into assets/img/.
For each source: NAME.webp (max 1600px wide), NAME-800.webp (cards), NAME-og.jpg (1200px, social previews).
Writes assets/img/dims.json with the size of NAME.webp. Run after adding images: python optimize_images.py
"""
import os, json
from PIL import Image
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(ROOT, "source-images"), os.path.join(ROOT, "assets", "img")
os.makedirs(OUT, exist_ok=True)
dims = {}
def fit(im, w):
    return im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
for f in sorted(os.listdir(SRC)):
    stem, ext = os.path.splitext(f)
    if ext.lower() not in (".jpg", ".jpeg", ".png"):
        continue
    im = Image.open(os.path.join(SRC, f)).convert("RGB")
    big = fit(im, 1600); big.save(os.path.join(OUT, stem + ".webp"), "WEBP", quality=80, method=6)
    fit(im, 800).save(os.path.join(OUT, stem + "-800.webp"), "WEBP", quality=78, method=6)
    fit(im, 1200).save(os.path.join(OUT, stem + "-og.jpg"), "JPEG", quality=82, optimize=True, progressive=True)
    dims[stem] = [big.width, big.height]
json.dump(dims, open(os.path.join(OUT, "dims.json"), "w"), indent=0)
print("optimized", len(dims), "images")
