#!/usr/bin/env bash
echo "Legacy helper detected. Redirecting to run-pii-full-assessment.sh."
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-pii-full-assessment.sh" "$@"
