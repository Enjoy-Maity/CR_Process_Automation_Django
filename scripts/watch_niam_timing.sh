#!/usr/bin/env bash
#
# Watch the NIAM timing checkpoints together with the normal app error log
# (and, on the VM, the systemd journal) in one live stream.
#
# Every line is prefixed with its source and also saved to a timestamped
# capture file under cr_process_automation/logs/.
#
# Usage:
#   chmod +x scripts/watch_niam_timing.sh
#   ./scripts/watch_niam_timing.sh                 # tail timing + errors + journal
#   ./scripts/watch_niam_timing.sh --no-journal    # files only
#   ./scripts/watch_niam_timing.sh --reset         # clear the timing log first
#   SERVICE=cr-app ./scripts/watch_niam_timing.sh  # choose the systemd unit
#
# Press Ctrl+C to stop.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/cr_process_automation/logs"
TIMING_LOG="$LOG_DIR/notice_timing.log"
ERROR_LOG="$LOG_DIR/errors.log"
SERVICE="${SERVICE:-cr-app}"
CAPTURE="$LOG_DIR/niam_timing_capture_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"
touch "$TIMING_LOG" "$ERROR_LOG"

for arg in "$@"; do
  case "$arg" in
    --reset)
      : > "$TIMING_LOG"
      echo "[watch] cleared $TIMING_LOG"
      ;;
    --no-journal)
      NO_JOURNAL=1
      ;;
    *)
      echo "[watch] unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

prefix_stream() {
  local label="$1"
  while IFS= read -r line; do
    printf '[%s] %s\n' "$label" "$line"
  done
}

cleanup() {
  trap - EXIT INT TERM
  pkill -P "$$" 2>/dev/null || true
  echo
  echo "[watch] stopped. Capture saved to: $CAPTURE"
}
trap cleanup EXIT INT TERM

echo "[watch] capture: $CAPTURE"
echo "[watch] timing:  $TIMING_LOG"
echo "[watch] errors:  $ERROR_LOG"

tail -n 200 -F "$TIMING_LOG" | prefix_stream TIMING | tee -a "$CAPTURE" &
tail -n 200 -F "$ERROR_LOG" | prefix_stream ERROR  | tee -a "$CAPTURE" &

if command -v journalctl >/dev/null 2>&1 && [ "${NO_JOURNAL:-0}" != "1" ]; then
  echo "[watch] journal: unit $SERVICE"
  journalctl -u "$SERVICE" -f --no-pager -o cat | prefix_stream JOURNAL | tee -a "$CAPTURE" &
else
  echo "[watch] journal: skipped"
fi

wait
