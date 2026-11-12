# signalsinthenoisebook.com

Static site for *Signals in the Noise* by Timothy E. Reed, CPP.

- `build.py`: all page content, metadata, and structured data. Edit here, then push.
- `static/`: stylesheet, self-hosted Inter font, favicons, llms.txt, security.txt. Copied as-is.
- `source-images/`: full-size originals (not deployed).
- `assets/img/`: web versions made by `optimize_images.py` (WebP at 1600 and 800px, plus a 1200px JPEG for social previews).
- Every push to `main` builds and deploys through GitHub Actions. New files in `source-images/` are optimized automatically.
