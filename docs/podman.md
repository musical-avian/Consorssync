# Podman

## TL;DR
Build the image, run it once by hand (TAN), then a Quadlet unit plus a systemd timer runs it daily. Rootless.

## Build
```sh
podman build -t consorssync .
```

## Run once
```sh
podman run -it --rm --env-file .env -v consorssync-data:/data:U consorssync --dry-run
podman run -it --rm --env-file .env -v consorssync-data:/data:U consorssync
```
`:U` chowns the volume to the container user. Rootless podman needs this.
If Actual runs in another container, put both on one network (`--network`) and set `ACTUAL_URL` to match.

## Schedule (Quadlet)
```sh
cp .env ~/.config/consorssync.env && chmod 600 ~/.config/consorssync.env
mkdir -p ~/.config/containers/systemd ~/.config/systemd/user
cp deploy/consorssync.container ~/.config/containers/systemd/
cp deploy/consorssync.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now consorssync.timer
loginctl enable-linger "$USER"   # run while you're logged out
```

## Ops
- Run now: `systemctl --user start consorssync`
- Logs: `journalctl --user -u consorssync`
- Next run: `systemctl --user list-timers`
