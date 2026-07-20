# PyPI release

## One-time setup

1. Create `gfyupm` project on PyPI, or add a pending trusted publisher.
2. Add trusted publisher:
   - Owner: `umm-dev`
   - Repository: `gfyupm`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. In GitHub, create `pypi` environment. Require approval if wanted.

No PyPI API token needed. GitHub Actions exchanges its OpenID Connect identity for a short-lived PyPI publish token.

## Release

1. Set release version in `pyproject.toml`.
2. Run `python3 -m pytest -q`.
3. Merge release commit to `main`.
4. Create and publish GitHub release from that commit.
5. `Publish to PyPI` builds wheel and source distribution, then publishes them.
6. Verify:

```bash
python3 -m pip install --upgrade gfyupm
gfyupm --version
```

Do not run release workflow before trusted publisher setup. PyPI rejects untrusted publishes.
