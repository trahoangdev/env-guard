# Configuration

Document every environment variable here.

| Name | Required | Default | Description | Constraints |
|------|----------|---------|-------------|-------------|
| APP_NAME | Yes | EnvGuard | Application name shown in logs |  |
| ENV | Yes | local | Environment name (local/dev/staging/prod) |  |
| LOG_LEVEL | No | info | Logging level |  |
| PORT | No | 8000 | Server port | type=int; min=1024; max=65535 |
| SECRET_TOKEN | Yes |  | Required secret token | pattern=^[A-Za-z0-9_\-]{12,}$; min_len=12 |
