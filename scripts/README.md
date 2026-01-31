# Commands and scripts live here

## Env Guard CLI

Install editable and use the command:

```bash
pip install -e .
envguard validate --example .env.example --env .env --pretty
envguard validate --example .env.example --env .env --format summary
envguard docs --example .env.example --out docs/config.md
envguard diff --base .env --compare .env.staging --pretty
envguard diff --base .env --compare .env.staging --format summary
```

Fallback to the script:

```bash
python scripts/envguard_cli.py validate --example .env.example --env .env
python scripts/envguard_cli.py docs --example .env.example --out docs/config.md
python scripts/envguard_cli.py diff --base .env --compare .env.staging
```

Options:
- `--format` output format: `json`, `pretty`, `summary`
- `--pretty` pretty-print JSON output (default: compact)
- `--fail-on-warning` exit with code 1 on issues (default: 2)
