# Commands and scripts live here

## Env Guard CLI

```bash
python scripts/envguard_cli.py validate --example .env.example --env .env
python scripts/envguard_cli.py docs --example .env.example --out docs/config.md
python scripts/envguard_cli.py diff --base .env --compare .env.staging
```
