# SOPS + age (Repo‑level secret management)

This repo stores encrypted env files with [SOPS](https://github.com/getsops/sops) using **age** keys.

## Quickstart

1) **Generate keys (locally):**
```bash
age-keygen -o agekey.txt
# Public key
age-keygen -y agekey.txt > agekey.pub
cat agekey.pub   # looks like: age1....
```

2) **Update `.sops.yaml`:**
Replace `REPLACE_WITH_AGE_PUBLIC_KEY` with the value from `agekey.pub`.

3) **Create an encrypted env file:**
```bash
mkdir -p infra/secrets
cp infra/secrets/.env.template infra/secrets/.env
# edit values in infra/secrets/.env
sops --age $(cat agekey.pub) -e infra/secrets/.env > infra/secrets/.env.sops
git add infra/secrets/.env.sops .sops.yaml
git commit -m "chore(secrets): add encrypted env"
```

4) **GitHub → Settings → Secrets/Variables**
- Secrets → `AGE_SECRET_KEY` (private key content from `agekey.txt`)
- Secrets → `RAILWAY_TOKEN` (Railway project token)
- Variables → `RAILWAY_PROJECT_ID`, `RAILWAY_ENVIRONMENT`, `RAILWAY_SERVICE`

5) **Run the workflow** (manually or on push) to set variables in Railway and (optionally) trigger a redeploy.

## Notes
- Do **not** commit `agekey.txt`. Keep it private.
- The encrypted `.env.sops` is safe to commit.
- If you rotate keys, re‑encrypt files with the new public key.
