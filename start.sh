#!/bin/bash
set -e

echo "========================================="
echo " Starting XRDP Docker Container"
echo "========================================="

echo "[1/5] Preparing runtime directories..."
mkdir -p /run/dbus /run/xrdp /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
rm -f /run/dbus/pid /run/xrdp/xrdp.pid /run/xrdp/xrdp-sesman.pid

echo "[2/5] Starting D-Bus daemon..."
if ! pgrep -x dbus-daemon >/dev/null 2>&1; then
    dbus-daemon --system --fork
fi
echo "D-Bus started."

echo "[3/5] Starting PulseAudio..."
pulseaudio \
    --system \
    --disallow-exit \
    --disable-shm \
    --exit-idle-time=-1 \
    2>/tmp/pulseaudio.log || true
echo "PulseAudio started (or already running)."

echo "[4/5] Starting xrdp-sesman..."
/usr/sbin/xrdp-sesman
sleep 1

if ! pgrep -x xrdp-sesman >/dev/null 2>&1; then
    echo "ERROR: xrdp-sesman failed to start."
    cat /var/log/xrdp-sesman.log 2>/dev/null || true
    exit 1
fi

echo "[5/5] Starting xrdp on port 3389..."
exec /usr/sbin/xrdp --nodaemon
