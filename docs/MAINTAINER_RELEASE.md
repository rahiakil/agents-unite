# Maintainer release guide

## Cut a release

1. Bump version in `pyproject.toml` and `src/agents_unite/__init__.py`
2. Update `.github/RELEASE_BODY.md` with release-specific notes (keep marketing intro)
3. Commit, push, tag:

```bash
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

4. GitHub Actions runs [release.yml](../.github/workflows/release.yml):
   - Builds sdist + wheel
   - Creates GitHub Release with `.github/RELEASE_BODY.md`
   - Publishes to PyPI via `pypa/gh-action-pypi-publish`

## PyPI one-time setup

### Option A — Trusted publishing (recommended, no token)

1. Create project at https://pypi.org/manage/projects/ (`agents-unite`)
2. **Publishing** → **Add a new pending publisher**
3. Fill in:
   - PyPI project: `agents-unite`
   - Owner: `rahiakil`
   - Repository: `agents-unite`
   - Workflow: `release.yml`
   - **Environment name:** leave **blank** (repo-level publisher)
4. Re-run the failed `pypi-publish` job on the release workflow, or tag `v0.1.1`

### Option B — API token

1. Create PyPI API token (project-scoped for `agents-unite`)
2. GitHub repo → Settings → Secrets → `PYPI_API_TOKEN`
3. Re-run `pypi-publish` on the latest release workflow

### Re-run after setup

```bash
gh run rerun <run-id> --job pypi-publish
# or push a patch tag:
git tag v0.1.1 && git push origin v0.1.1
```

## Verify

```bash
pip install "agents-unite[llm]"
agents-unite version
```
