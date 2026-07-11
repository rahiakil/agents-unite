# Maintainer release guide

## Cut a release

1. Bump version in `pyproject.toml` and `src/agents_unite/__init__.py`
2. Update `.github/RELEASE_BODY.md` with release-specific notes (keep marketing intro)
3. Commit, push, tag:

```bash
git tag v0.1.3
git push origin main
git push origin v0.1.3
```

4. GitHub Actions runs:
   - [publish-pypi.yml](../.github/workflows/publish-pypi.yml) — PyPI.org + GitHub Packages
   - [release.yml](../.github/workflows/release.yml) — GitHub Release + wheel assets

## PyPI trusted publisher — exact form values

On https://pypi.org → your project → **Publishing** → **Add a new pending publisher**:

| PyPI field | Enter this | Do NOT enter |
|------------|------------|--------------|
| **PyPI project name** | `agents-unite` | — |
| **Owner** | `rahiakil` | `https://github.com/rahiakil` |
| **Repository name** | `agents-unite` | `rahiakil/agents-unite` or full URL |
| **Workflow name** | `publish-pypi.yml` | `Publish PyPI` (display name) or `release.yml` |
| **Environment name** | *(leave blank)* | `pypi` unless you configured GitHub Environment |

The **repository name** field is only the repo slug — the part after the slash in `rahiakil/agents-unite`. Putting the full URL or `owner/repo` in that box causes **invalid repository name**.

The **workflow name** field is the **filename** under `.github/workflows/`, not the workflow's `name:` label in YAML.

### Option B — API token

1. Create PyPI API token (project-scoped for `agents-unite`)
2. GitHub repo → Settings → Secrets → `PYPI_API_TOKEN`
3. Re-run **Publish PyPI** workflow or push a new tag

### Test without tagging

```bash
gh workflow run publish-pypi.yml --repo rahiakil/agents-unite
```

*(Only works after a tag exists with a built package, or use workflow_dispatch after merging publish-pypi.yml.)*

## Verify

```bash
# PyPI
pip install "agents-unite[llm]"

# GitHub Packages
pip install "agents-unite[llm]" --extra-index-url https://pypi.pkg.github.com/rahiakil/simple/

agents-unite configure
agents-unite version
```

PyPI: https://pypi.org/project/agents-unite/  
GitHub Packages: https://github.com/rahiakil/agents-unite/packages
