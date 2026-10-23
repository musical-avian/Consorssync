# consorssync

Pulls Consorsbank transactions (FinTS) into [Actual Budget](https://actualbudget.org). Reruns create no duplicates, and transfers between your own accounts are linked.

```sh
podman build -t consorssync .
podman run -it --rm --env-file .env -v consorssync-data:/data:U consorssync --dry-run
```

Docs: [setup](docs/setup.md) · [TAN](docs/tan.md) · [podman](docs/podman.md) · [hosted Actual](docs/hosted.md) · [risks & limits](docs/risks.md)
