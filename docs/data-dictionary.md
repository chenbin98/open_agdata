# Data dictionary and review conventions

`data/resources.json` holds the canonical English metadata. `data/resources.zh-CN.json` is its Chinese localization. Each contains `schema_version: 1`, a `language` code (`en` or `zh-CN`) and a `resources` array. The generator produces both READMEs, both resource catalogs and the English CSV.

## Fields

| Field | Type | Convention |
| --- | --- | --- |
| `id` | string | Unique, stable lowercase kebab-case ID; do not change when revising a display name |
| `name` / `name_en` | string | Localized display name and shared English name; both are English in the canonical file |
| `kind` | enum | `platform`, `network` or `dataset` |
| `category` | enum | `climate`, `soil`, `flux-phenology`, `remote-sensing`, `agricultural-statistics`, `water-resources`, `biodiversity` or `china` |
| `provider` | string | Original data institution or authors, distinguishing the provider from a hosting platform |
| `summary` | string | What the resource contains and how it is produced |
| `coverage.spatial` | string | Geographic extent and noncontinuous coverage |
| `coverage.temporal` | string | Data coverage rather than paper/publication date; distinguish historical and updated releases |
| `coverage.spatial_resolution` | string | Native resolution, output sampling, depth, point support or administrative scale |
| `coverage.temporal_resolution` | string | Hourly, daily, dekadal, annual, phenological dates or another interval |
| `variables` | string[] | Main variables, qualified when availability depends on product |
| `access.registration` | enum | `not-required`, `required`, `mixed` or `unknown` |
| `access.methods` | string[] | Web, REST API, STAC, GeoTIFF, WCS and other methods |
| `access.note` | string | Free-access limits, accounts, keys, quotas, signatures and application procedures |
| `license.name` / `url` / `note` | object | Actual data licence or official policy and its scope; explicitly flag an unconfirmed licence and link the relevant record |
| `links` | object[] | `label` and `url`; prefer official records, DOIs and version links over temporary signed URLs |
| `applications` | string[] | Suggested research uses, without guaranteeing suitability in every setting |
| `caveats` | string[] | Missingness, quality flags, spatial support, dependencies and training/evaluation overlap |
| `keywords` | string[] | Search terms, including crops, regions and variables |
| `verification.status` | enum | `documented`, `partial` or `pending`; defined below |
| `verification.checked_on` | string | Actual source-review date in `YYYY-MM-DD`; do not refresh on translation, export or HTTP success alone |
| `verification.scope` | string | What was read and what remains unchecked or contradictory |
| `verification.sources` | object[] | `url` and `note` explaining which claims the source supports; required evidence for reviewed records |
| `seed_refs` | string[] | Initial groups `01`–`11` and `12.01`–`12.07`; use `community` for later independent additions |

Each resource has one primary category. The China section is a regional entry point; use keywords for additional cross-topic associations. Add a category only by updating the generator and this dictionary together.

## Review status

- **Documentation reviewed (`documented`)**: official documentation, release records or provider-registered DOI metadata support the main description. This does not mean complete files were downloaded, every variable was tested or accuracy was independently assessed.
- **Partially reviewed (`partial`)**: identity and some information are supported, but version conflicts, access/licence uncertainty, dynamic pages or coverage gaps remain. Explain them in `scope` and `caveats`.
- **Pending review (`pending`)**: a candidate lead without enough primary-source evidence. Do not present a submitter’s unverified statement as confirmed.

HTTP 200 establishes a responding endpoint, not resource identity or correct parameters. HTTP 403, timeouts and SSL failures do not establish permanent unavailability. Preserve differences between documents, registered metadata and actual files until a specific release resolves them.

## Localization

English is canonical. Chinese wording can differ, but identity and evidence must agree. The generator checks matching resource sets, English names, kinds, categories, seed references, registration codes, licence URLs, entry URLs, evidence URLs, review statuses and dates before writing any outputs. Resource order follows the canonical English catalog.

Scientific facts expressed in prose, such as coverage and resolution, still need human comparison: automated structural alignment cannot establish that two translations mean the same thing. Preserve the review scope and limitations when translating. Source metadata snapshots retain their original wording.

## Generate and check

```bash
python3 scripts/catalog.py
python3 scripts/catalog.py --check
python3 -m unittest discover -s tests -v
```

Python 3.10+, standard library only. The repository containing the script is the default root; `--root /path/to/catalog` selects another directory. If a Chinese metadata file is present, it is validated and used to generate Chinese outputs. `--check` is read-only and compares expected exports with files on disk.

CSV uses UTF-8 with a BOM for spreadsheet compatibility. Most list fields use ` | ` separators; `links` and `sources` contain JSON strings to preserve labels and notes. Use JSON for lossless processing.

Checks cover structure, required values, unique IDs, enums, dates, URL syntax, evidence requirements, translation invariants and generated outputs. They do not run live endpoint, authenticated-download or scientific-quality checks.
