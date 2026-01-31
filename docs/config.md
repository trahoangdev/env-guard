# Configuration

Document every environment variable here.

| Name | Required | Default | Description | Constraints |
|------|----------|---------|-------------|-------------|
| APP_NAME | Yes | EnvGuard | Application name shown in logs |  |
| ENV | Yes | local | Environment name (local/dev/staging/prod) |  |
| LOG_LEVEL | No | info | Logging level | allowed=debug,info,warning,error; allowed_ci=true; aliases=warn,err |
| PORT | No | 8000 | Server port | type=int; min=1024; max=65535 |
| SECRET_TOKEN | Yes |  | Required secret token | pattern=^[A-Za-z0-9_\-]{12,}$; min_len=12; message=Token must be 12+ safe chars |
