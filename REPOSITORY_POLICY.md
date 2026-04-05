# Repository Policy

This project is operated with two different purposes:

- a private production repository for real automation
- a public repository for portfolio and demo use

The goal of this policy is to keep those two uses separate and safe.

## Repository Roles

### Private repository

The private repository is the production source of truth.

It may contain:

- real GitHub Actions automation
- real Notion, Telegram, and future Google Calendar integrations
- production-oriented README and operation notes

It must never contain:

- committed `.env` files
- API keys, bot tokens, refresh tokens, or any other live credentials
- exported personal data or logs from real services

### Public repository

The public repository is for explanation, review, and portfolio presentation.

It should contain:

- safe implementation code
- mock data
- portfolio-oriented README
- setup instructions that do not require real credentials

It should not contain:

- live secrets
- real workspace identifiers when they are sensitive
- production automation instructions that depend on private credentials

## Branch Rules

### `main`

`main` is the private working branch.

Use `main` for:

- production changes
- real integration work
- GitHub Actions automation for personal use

### `public-demo`

`public-demo` is the public presentation branch.

Use `public-demo` for:

- mock mode updates
- public-safe README changes
- sample data improvements
- code that is safe to mirror into the public repository

Do not use `public-demo` for:

- private operational notes
- production-only credentials or setup steps
- anything that assumes access to personal services

## Update Workflow

### When updating the private production system

1. Work on `main`
2. Test locally
3. Push to the private repository
4. Confirm GitHub Actions behavior if automation changed

### When updating the public demo repository

1. Start from `public-demo`
2. Keep the README portfolio-oriented
3. Use mock data only
4. Test locally with `USE_MOCK_DATA=true`
5. Push `public-demo` to the public repository's `main`

Recommended command pattern:

```bash
git checkout public-demo
git push public public-demo:main
git checkout main
```

## Secret Handling Rules

- Never commit `.env`
- Never paste tokens into tracked files
- Never print secrets in logs
- Keep production credentials only in local `.env` or GitHub Secrets

## README Rules

- The private repository README may explain real automation and GitHub Actions setup
- The public repository README should describe the architecture, motivation, and mock demo flow
- If the two READMEs need different messaging, update them on different branches rather than rewriting one back and forth

## Default Decision Rule

If a change improves real daily operation, it belongs on `main`.

If a change improves safe public explanation or demo quality, it belongs on `public-demo`.
