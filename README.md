# signalsinthenoisebook.com

Static site for *Signals in the Noise* by Timothy E. Reed, CPP.

- `build.py`: all page content and templates. Edit here, then push.
- `static/`: stylesheet and llms.txt, copied as-is.
- `assets/img/`: images (copied from the old Framer site by `fetch_images.py`).
- Every push to `main` builds and deploys through GitHub Actions.
- Repo variable `SITE_BASE` is `/signalsinthenoisebook-site` while previewing on github.io. Delete it when the custom domain goes live.
