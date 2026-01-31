# Commands and scripts live here

## Env Guard CLI

Install editable and use the command:

```bash
pip install -e .
envguard validate --example .env.example --env .env
envguard docs --example .env.example --out docs/config.md
envguard diff --base .env --compare .env.staging
```

Fallback to the script:

```bash
python scripts/envguard_cli.py validate --example .env.example --env .env
python scripts/envguard_cli.py docs --example .env.example --out docs/config.md
python scripts/envguard_cli.py diff --base .env --compare .env.staging
```
