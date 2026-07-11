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

### Option A — Trusted publishing (recommended)

1. Create project at https://pypi.org/manage/projects/ (`agents-unite`)
2. **Publishing** → **Add a new pending publisher**
3. PyPI project name: `agents-unite`
4. Owner: `rahiakil`, repo: `agents-unite`, workflow: `release.yml`, environment: `pypi`
5. Create GitHub environment `pypi` under repo Settings → Environments (optional but matches workflow)

No API token needed when trusted publishing is configured.

### Option B — API token

1. Create PyPI API token (project-scoped)
2. Repo secret: `PYPI_API_TOKEN`
3. Workflow uses token as fallback with trusted publishing

## Verify

```bash
pip install "agents-unite[llm]"
agents-unite version
```
