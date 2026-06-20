# Branch scripts

Creates `feature/` or `hotfix/` branches from `main` synced with `origin`.

## Usage

After cloning, configure aliases once per repository:

```bash
./scripts/setup-git-aliases.sh
```

Then:

```bash
git feature login-oauth
git hotfix fix-login-crash
```

The prefix is added automatically (`feature/login-oauth`, `hotfix/fix-login-crash`).

Direct alternative (without aliases):

```bash
chmod +x scripts/*.sh   # first time only (Git Bash/WSL)
./scripts/create-feature-branch.sh login-oauth
```

## Flow

1. Validates the branch name
2. Updates `main` (`fetch` + `pull --ff-only`)
3. Creates and checks out the new branch

## After creating

```bash
git push -u origin feature/branch-name
```

Use short lowercase names separated by hyphens (e.g. `login-oauth`, `JIRA-123-filters`).
