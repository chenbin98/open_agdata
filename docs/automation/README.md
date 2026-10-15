# Enable GitHub Actions

The [catalog.yml](catalog.yml) template runs metadata validation, generated-file checks and catalog tests on pushes and pull requests.

Copy it to `.github/workflows/catalog.yml` and commit with credentials authorized to write GitHub Actions workflows. OAuth/classic PAT credentials generally need the `workflow` scope; check the requirements for your credential type. Online workflows are not enabled in this repository’s initial setup.

```bash
mkdir -p .github/workflows
cp docs/automation/catalog.yml .github/workflows/catalog.yml
git add .github/workflows/catalog.yml
git commit -m "Enable catalog checks"
git push
```

The same checks can run locally:

```bash
python3 scripts/catalog.py --check
python3 -m unittest discover -s tests -v
```
