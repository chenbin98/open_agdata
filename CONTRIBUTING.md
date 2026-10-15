# Contributing

Help improve public data discovery for agriculture, remote sensing and the environment. Suggest datasets, observation networks or platforms, report access changes, or correct coverage and licence information. The Issue templates are available if you prefer not to edit JSON.

## Scope

Prefer traceable resources with useful metadata, documented access conditions and an identifiable licence. Public datasets hosted by commercial platforms are welcome when their free-access limits are clear. Marketing-only pages and unidentified or unauthorized mirrors are not recommended as reviewed resources.

## Submit a pull request

1. Add or update the English canonical record in `data/resources.json`, following the [data dictionary](docs/data-dictionary.md). Use a stable ID and an existing category. For new community resources, set `seed_refs` to `["community"]`.
2. Update the corresponding record in `data/resources.zh-CN.json`. Translations must keep the same IDs, classifications, evidence and entry URLs, licence URLs, registration codes, review statuses and review dates. Missing or conflicting translations fail validation.
3. Read official release metadata, methods and licence information. Record the actual version/DOI, coverage, resolution and account/key requirements. Use `partial` or `pending` and explain anything not confirmed.
4. In `verification.sources`, link evidence and state which fields it supports. Keep the date of the source review; regenerating or translating files does not refresh that date.
5. Generate and check all outputs:

   ```bash
   python3 scripts/catalog.py
   python3 scripts/catalog.py --check
   python3 -m unittest discover -s tests -v
   ```

6. Commit both metadata files and generated READMEs, resource cards and CSV. In the PR description, list the resource IDs, evidence, changes and remaining limitations.

## Editing conventions

- English is the repository default. Use `README.zh-CN.md` and `docs/catalog.zh-CN.md` for Chinese navigation and resource cards; both versions link to each other.
- Distinguish datasets, networks and platforms. Put alternate entry points for one product in `links`; describe meaningful crop, depth and version differences explicitly.
- Avoid unverified claims such as universal registration-free access, guaranteed processing speed or highest accuracy.
- Describe free access, data licences and service terms separately. An unknown licence does not imply public-domain or CC BY status.
- State whether a product uses observations, statistics, assimilation, interpolation or remote-sensing/machine-learning estimates. Note shared training and evaluation inputs where relevant.
- Keep large raw datasets, credentials and temporary signed URLs out of the repository. Link official sources and durable metadata instead.
- Record the method and date of a failed request. Confirm an official migration before replacing URLs; a single 403 or timeout is not enough to delete a resource.

Original text and curated metadata are contributed under CC BY 4.0; scripts and tests under MIT. External datasets and original release metadata retain their own rights and licences.
