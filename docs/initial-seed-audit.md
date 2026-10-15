# Initial resource review

Review date: 2026-10-15. The initial list contained 12 groups supplied by the maintainer. These became **27 separate resources**, preserving all supplied entry points and adding a companion precipitation DOI, current access routes and specific dataset records.

Descriptions were rewritten using official documentation, release metadata, registered DOI records and original data papers. Unverified site counts, promotional performance claims and blanket registration-free claims were omitted. Documented access conditions do not imply that every login and full download was tested.

## Original groups and current entries

| Initial group | Resource IDs | Main clarification |
| --- | --- | --- |
| 01 NASA POWER | `nasa-power` | Native meteorology: 0.5° × 0.625°; radiation: 1°; ICASA output and day boundaries documented separately |
| 02 Open-Meteo | `open-meteo-historical` | Separate ERA5, ERA5-Land and IFS start dates/resolutions; distinguish data licence from free-service limits |
| 03 SoilGrids | `soilgrids` | REST API pause and WCS/WebDAV alternatives noted; hydraulic variables need specific product checks |
| 04 AmeriFlux / FLUXNET | `ameriflux`, `fluxnet` | Separate Americas/global networks; AmeriFlux account and Legacy terms noted; add Shuttle |
| 05 Planetary Computer | `planetary-computer` | Distinguish STAC discovery, asset access and user computation; no arbitrary processing-speed guarantee |
| 06 Earth Engine | `google-earth-engine` | Account, Cloud project, eligibility verification and dataset licences described separately |
| 07 AppEEARS | `nasa-appeears` | Free Earthdata Login; coverage varies by product rather than sharing continuous coverage from 2000 |
| 08 PhenoCam | `phenocam` | Unverified site counts omitted; GCC transition dates are not direct crop-development measurements |
| 09 Quick Stats / CDL | `usda-quickstats`, `usda-cdl` | Separate administrative statistics and crop rasters; clarify early coverage and 10 m products from 2024 |
| 10 FAOSTAT / WaPOR | `faostat`, `fao-wapor` | Separate statistics and remote-sensing products; WaPOR 300/100/20 m coverage is level-specific |
| 11 GBIF | `gbif-occurrence` | Formal bulk requests need an account; occurrences are not pest-density measurements and do not all have reliable GPS |
| 12.01 CLCD | `clcd-china` | Registered metadata extends to 2025; retain version relations and the uninspected annual-file limitation |
| 12.02 Staple-crop yields | `china-staple-yield-2024` | 2024, kg/ha, remote-sensing/statistical estimates; no claim of field measurements or established peer review |
| 12.03 Northeast crops / wheat | `northeast-china-crops-10m`, `china-winter-wheat-30m` | Northeast crops are rice, maize and soybean; wheat coverage discrepancy remains explicit |
| 12.04 Crop phenology | `chinacropphen-1km`, `china-maize-phenology-30m` | ChinaCropPhen metadata through 2019; 30 m maize includes specific V3/maturity indicators for 1985–2020 |
| 12.05 ChinaCropSM | `chinacropsm-wheat-topsoil` | Supplied record is only dryland wheat at 0–10 cm |
| 12.06 China weather grids | `china-monthly-temperature-1km`, `china-monthly-precipitation-1km`, `cdmet-china` | Supplied DOI is temperature; add companion precipitation DOI; CDMet covers 2000–2020 |
| 12.07 TPDC | `cmfd-china`, `smci-china`, `tpdc` | Remove stray quotation mark; separate products from portal; retain version/licence limits |

## Unresolved information

- **Winter-wheat coverage and version:** the base DOI and `.v2` DataCite records describe 2016–2019, while the ecosystem data-center record describes 2001–2024. Actual files have not been inspected; full expanded coverage is not confirmed. [DOI metadata](https://api.datacite.org/dois/10.6084/m9.figshare.12003990.v2); [data-center record](https://www.nesdc.org.cn/sdo/detail?id=6189ecb57e2817667e3c7d98).
- **Peng group monthly temperature:** the original paper assigns `10.5281/zenodo.3185722` to temperature and `10.5281/zenodo.3114194` to precipitation. Direct retrieval of the temperature record failed; latest coverage and licence remain unchecked. Its description uses the original 1901–2017 paper coverage. [Original paper](https://essd.copernicus.org/articles/11/1931/2019/).
- **CMFD v2.0:** an official index confirms v1.6 was discontinued and links v2.0, but the v2.0 detail page returned a JavaScript shell. Confirmed v1.6 information has not been transferred to v2.0. [Official index](https://data.tpdc.ac.cn/allData?datasetType=isImportant).
- **Dynamic platforms and access workflows:** some Planetary Computer, PhenoCam and WaPOR routes were not tested end to end. See each resource card. Unverified changing network and record counts are not retained as catalog facts.

## Evidence and language

Every [resource card](catalog.md) links evidence and gives a review date and scope. [Metadata extracts](../data/provenance/) retain selected release and DOI fields plus retrieval failures. These are dated snapshots; fix actual versions when downloading.

English became the default repository language on 2026-10-15. Chinese metadata, [README](../README.zh-CN.md) and [resource cards](catalog.zh-CN.md) remain available. This language update preserved resource identity, URLs, review status and source-review dates; translation is not a new scientific review.
