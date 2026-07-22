#!/usr/bin/env bash
echo "Legacy helper detected. Redirecting to run-pii-detailed-report-only.sh."
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-pii-detailed-report-only.sh" "$@"
