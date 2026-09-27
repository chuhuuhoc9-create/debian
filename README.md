# Debian XRDP + XFCE + Wine

Debian 12 (Bookworm) container with:

- XFCE desktop
- XRDP on port `3389`
- Xorg/XRDP integration
- Wine 32/64-bit
- Firefox ESR
- D-Bus
- PulseAudio
- Docker Compose

## Build

```bash
docker compose build
```

## Start

```bash
docker compose up -d
```

## Connect

Connect using an RDP client:

```text
SERVER_IP:3389
```

Default credentials:

```text
Username: xrdpuser
Password: xrdp
```

## Stop

```bash
docker compose down
```

## Logs

```bash
docker compose logs -f
```

## Security

The default password is intended for testing only. Change it before exposing
the container to an untrusted network. The image also grants the desktop user
passwordless sudo for convenience; remove that configuration for production.
