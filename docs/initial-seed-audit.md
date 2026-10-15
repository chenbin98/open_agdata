# 首批资源整理与核实说明

整理日期：2026-10-15。首批线索来自维护者提供的 12 组资源介绍。按实际平台、网络与数据产品拆分为 **27 个条目**，保留全部给定入口；另补充配套降水 DOI、新版下载入口及具体数据集记录。

本目录重写了资源介绍，优先使用官方说明、数据发布元数据、DOI 注册信息与原始数据论文。未照录宣传性效果、未证实的网络数量或统一的“免注册直下”结论。目录中的访问条件描述不代表已实际登录或下载全部产品。

## 原始分组与目录对应

| 初始分组 | 当前条目 ID | 处理说明 |
| --- | --- | --- |
| 01 NASA POWER | `nasa-power` | 气象原生网格 0.5° × 0.625°，辐射 1°；ICASA 格式和日界单列说明 |
| 02 Open-Meteo | `open-meteo-historical` | ERA5、ERA5-Land、IFS 的分辨率与起点分别记录；区分数据许可与免费服务限制 |
| 03 SoilGrids | `soilgrids` | 记录 REST API 暂停公告与 WCS/WebDAV 替代；水力变量需另核具体产品 |
| 04 AmeriFlux & FLUXNET | `ameriflux`、`fluxnet` | 美洲与全球网络拆分；AmeriFlux 需账户，保留 Legacy 政策；FLUXNET 新增 Shuttle 入口 |
| 05 Planetary Computer | `planetary-computer` | 区分 STAC 发现、资产读取与用户计算；不承诺秒级完成任意田块分析 |
| 06 Earth Engine | `google-earth-engine` | Google 账户、Cloud project、非商业资格验证与数据集许可分开说明 |
| 07 AppEEARS | `nasa-appeears` | 免费 Earthdata Login；时间/范围依产品，不统一承诺 2000 年起连续覆盖 |
| 08 PhenoCam | `phenocam` | 不采用未核实的总站数和农田数；GCC 转换日期不等同于作物发育阶段真值 |
| 09 Quick Stats & CDL | `usda-quickstats`、`usda-cdl` | 行政统计与分类栅格拆分；CDL 早期范围与 2024 起 10 m 变化补充 |
| 10 FAOSTAT & WaPOR | `faostat`、`fao-wapor` | 统计与遥感产品拆分；WaPOR 300/100/20 m 分层覆盖，20 m 不是全球 |
| 11 GBIF | `gbif-occurrence` | 正式批量下载需账户；物种出现不等于虫口密度，不假定所有记录都有可靠 GPS |
| 12.01 CLCD | `clcd-china` | 登记元数据到 2025；概念 DOI 的多版本关系与未核文件清单说明保留 |
| 12.02 中国主粮单产 | `china-staple-yield-2024` | 明确 2024 年、kg/ha、遥感与省级统计融合估计；不声称田间实测或已确认同行评议 |
| 12.03 东北作物与冬小麦 | `northeast-china-crops-10m`、`china-winter-wheat-30m` | 东北为稻/玉米/大豆；冬小麦 DOI 与数据中心扩展年份存在差异，明确标为部分核对 |
| 12.04 作物物候 | `chinacropphen-1km`、`china-maize-phenology-30m` | ChinaCropPhen 登记到 2019；玉米 30 m 为 1985–2020、V3/成熟等特定指标 |
| 12.05 ChinaCropSM | `chinacropsm-wheat-topsoil` | 给定记录仅小麦旱地 0–10 cm，不等于完整系列 |
| 12.06 中国气象网格 | `china-monthly-temperature-1km`、`china-monthly-precipitation-1km`、`cdmet-china` | 原链接为气温；补配套降水 DOI；CDMet 确认 2000–2020 年 |
| 12.07 TPDC | `cmfd-china`、`smci-china`、`tpdc` | 修复 URL 尾部弯引号；将 CMFD/SMCI 从门户单列，记录版本与非商业许可限制 |

## 尚未完全解决的信息

- **冬小麦年份与版本**：DataCite 中基础 DOI 和 `.v2` 仍称 2016–2019；国家生态科学数据中心对应记录称 2001–2024。尚未读取实际文件清单，不能宣称哪个入口已经提供全部年份。[DOI 登记](https://api.datacite.org/dois/10.6084/m9.figshare.12003990.v2)；[数据中心记录](https://www.nesdc.org.cn/sdo/detail?id=6189ecb57e2817667e3c7d98)。
- **彭守璋团队月气温**：原始论文明确气温 DOI 为 `10.5281/zenodo.3185722`、降水为 `10.5281/zenodo.3114194`。气温记录本次直接获取失败，最新覆盖与许可待确认，暂以原始论文的 1901–2017 说明。[原始数据论文](https://essd.copernicus.org/articles/11/1931/2019/)。
- **CMFD 2.0**：官方索引确认 1.6 停更及 2.0 入口，2.0 详情本次仅返回 JavaScript 外壳。保留 1.6 的已确认信息，不迁移为 2.0 的参数或许可。[官方索引](https://data.tpdc.ac.cn/allData?datasetType=isImportant)。
- **动态平台与访问流程**：Planetary Computer、PhenoCam、WaPOR 等部分页面或下载路径未完成端到端验证；具体范围见资源卡片。未核实的动态站点数、记录数未保留为目录事实。

## 证据记录

每张[资源卡片](catalog.md)给出来源链接、核对日期和核对边界。[首批发布元数据摘录](../data/provenance/)保留部分 Zenodo、Figshare/DataCite 的标题、DOI、版本、许可和文件元数据，以及失败读取结果。这些是当日快照，不能代替后续下载时固定版本。
