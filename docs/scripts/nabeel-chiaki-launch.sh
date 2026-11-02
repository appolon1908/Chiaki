#!/usr/bin/env bash
set -euo pipefail
BIN="${CHIAKI_BIN:-/usr/bin/chiaki}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
LOG_ROOT="${NABEEL_LOG_ROOT:-$HOME/.local/state/nabeel}"
mkdir -p "$LOG_ROOT"
[ -x "$BIN" ] || { echo "chiaki_binary_missing=$BIN" >&2; exit 2; }

case "${1:-status}" in
  status)
    echo "binary=$BIN"
    if command -v dpkg-query >/dev/null 2>&1; then dpkg-query -W -f='package=${Package} version=${Version}\n' chiaki 2>/dev/null || true; fi
    echo "config_home=$CONFIG_HOME"
    echo "credential_files_committed=NO"
    # Process arguments may contain pairing material; status exposes PIDs only.
    pgrep -f '(^|/)chiaki([ -]|$)' || true
    ;;
  launch)
    shift
    exec "$BIN" "$@"
    ;;
  *)
    echo "usage: $0 {status|launch [chiaki args...]}" >&2; exit 64;;
esac
