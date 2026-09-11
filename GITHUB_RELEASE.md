# GitHub release checklist

## Release

- Version: `1.0.0`
- Tag: `v1.0.0`
- Release title: `owfs2mqtt V3 1.0.0`
- Release notes source: `CHANGELOG.md`, section `1.0.0`

## Pre-publish checks

Run from the repository root:

```bash
python -m pytest -q
```

Expected result:

```text
15 passed
```

Also verify that:

- no local deployment file such as `owalias.txt` is committed;
- no `.env` or credentials are committed;
- no site-specific private IP addresses or host paths are present;
- generated Python/pytest cache files are absent;
- `docker-compose.yml` requires `MQTT_HOST` to be supplied by the deployment;
- the public alias template is `owalias.example.txt`.

## Git commands

```bash
git init
git add .
git commit -m "Release V3 1.0.0"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
git tag -a v1.0.0 -m "owfs2mqtt V3 1.0.0"
git push origin v1.0.0
```

Then create a GitHub Release for tag `v1.0.0` with title `owfs2mqtt V3 1.0.0` and use the `1.0.0` changelog section as the release notes.
