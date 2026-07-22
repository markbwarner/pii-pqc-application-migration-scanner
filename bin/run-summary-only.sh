#!/usr/bin/env bash
echo "Legacy helper detected. Redirecting to run-pii-summary-only.sh."
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-pii-summary-only.sh" "$@"
