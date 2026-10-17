# TAN / PSD2

## TL;DR
- The bank needs a TAN (strong customer authentication) at login, roughly every 90 days.
- **Interactive run** (a TTY is attached) asks which TAN method to use, then waits for you to confirm in the app.
- **Unattended run** with a TAN due fails fast with `TanRequired`. It never hangs.
- Session state lives in `/data/fints.bin` (mode 600) and is reused by later runs.

## First run
```sh
podman run -it --rm --env-file .env -v consorssync-data:/data:U localhost/consorssync --dry-run
```
Choose the decoupled app method ("Consorsbank App"), approve the request in the app, then press Enter.

## When the timer fails with TanRequired
Run the same command again. One TAN refreshes the session.

## Known risk
Consorsbank has FinTS quirks: it puts the login SCA on the HKIDN segment. If login fails, check the
python-fints issues and PRs for Consorsbank fixes and pin a version that has them.
