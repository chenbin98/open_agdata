## Change

List resource IDs and any coverage, access or licence changes.

## Evidence

Link official documentation, release records or DOIs. State unresolved or conflicting information.

## Checks

- [ ] Updated English canonical metadata and the Chinese localization
- [ ] Regenerated both READMEs, both resource catalogs and the English CSV
- [ ] `python3 scripts/catalog.py --check`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] No large raw files, credentials or temporary signed URLs
