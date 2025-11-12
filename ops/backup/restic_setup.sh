# <!-- FILE: /ops/backup/restic_setup.sh -->
#!/usr/bin/env bash
set -euo pipefail

export RESTIC_REPOSITORY="s3:http://minio:9000/lucidia-backups"
export RESTIC_PASSWORD="restic_pass"

: "${AWS_ACCESS_KEY_ID:?Set AWS_ACCESS_KEY_ID (obtain from your secret manager or via an OIDC exchange).}"
: "${AWS_SECRET_ACCESS_KEY:?Set AWS_SECRET_ACCESS_KEY (obtain from your secret manager or via an OIDC exchange).}"
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY

restic init || true
