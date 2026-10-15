# 数据字典与核实约定

`data/resources.json` 是资源信息的唯一编辑源。`schema_version: 1`，`resources` 是资源数组。README、`docs/catalog.md`、`data/resources.csv` 由脚本生成，避免分别维护导致参数不一致。

## 字段

| 字段 | 类型 | 约定 |
| --- | --- | --- |
| `id` | string | 唯一、稳定的小写短横线 ID；修订名称不改 ID |
| `name` / `name_en` | string | 中文显示名和英文名，不必照录宣传标题 |
| `kind` | enum | `platform` 平台、`network` 网络、`dataset` 具体数据集 |
| `category` | enum | `climate`、`soil`、`flux-phenology`、`remote-sensing`、`agricultural-statistics`、`water-resources`、`biodiversity`、`china` |
| `provider` | string | 实际数据提供机构或作者，区分托管平台和原始提供者 |
| `summary` | string | 数据是什么、如何产生，以及主要用途 |
| `coverage.spatial` | string | 空间范围及不连续覆盖边界 |
| `coverage.temporal` | string | 数据覆盖时间，不是论文/网页发表日期；历史版与更新版分别说明 |
| `coverage.spatial_resolution` | string | 原生空间尺度、输出采样、深度或点/行政尺度，不能混淆 |
| `coverage.temporal_resolution` | string | 小时、日、旬、年、关键日期等 |
| `variables` | string[] | 主要变量；按产品不同的变量加以限定 |
| `access.registration` | enum | `not-required`、`required`、`mixed`、`unknown` |
| `access.methods` | string[] | 如 Web、REST API、STAC、GeoTIFF、WCS |
| `access.note` | string | 免费范围、账户、密钥、配额、签名及申请流程，按已核对内容填写 |
| `license.name` / `url` / `note` | object | 具体数据许可、官方政策链接及适用范围；未知时写“待核对具体记录”，链接到待核对记录 |
| `links` | object[] | `label` 和 `url`；优先官方入口、DOI 和版本链接，不保存过期签名链接 |
| `applications` | string[] | 适用任务，作为选择提示，不保证在任何地区有效 |
| `caveats` | string[] | 缺测、质量标记、尺度、依赖、训练/验证重叠等实际使用边界 |
| `keywords` | string[] | 便于全文检索的关键词，可继续增加作物/地区/变量 |
| `verification.status` | enum | `documented`、`partial`、`pending`，定义见下 |
| `verification.checked_on` | string | 本次核对日期 `YYYY-MM-DD`，不能因导出或 HTTP 成功而自动刷新 |
| `verification.scope` | string | 本次读了什么、还有哪些未核对或相互矛盾；不以空值掩盖未知 |
| `verification.sources` | object[] | `url` 和 `note`，说明该来源支撑哪些字段；非待核对条目必须有证据 |
| `seed_refs` | string[] | 首批来源分组 `01`–`11`、`12.01`–`12.07`；之后独立新增用 `community` |

类别保持一个主分类；中国专题是地区入口，其他地区或跨主题关联可用 `keywords` 补充。新类别需要同步修改生成器及本字典。

## 核对状态

- **文档已核对（documented）**：已读取官方说明、发布记录或发布方登记的 DOI 元数据，主要描述有来源。仍不代表逐文件下载、精度验证或所有变量都可用。
- **部分核对（partial）**：已确认资源及部分信息，但存在版本冲突、许可/访问流程未确认、动态页面不可读，或具体覆盖未核实。必须在 `scope` 和 `caveats` 写清楚。
- **待核对（pending）**：仅收录候选线索，尚无足够的一手证据。不在描述中将提交者的说法包装为已确认事实。

HTTP 200 只能说明某个端点可响应，不能证明资源身份或参数正确；HTTP 403、超时、SSL 错误也不直接证明数据失效。文档、注册元数据、实际文件发生冲突时保留差异，找到正式版本证据后再修改。

## 导出与检查

```bash
python3 scripts/catalog.py
python3 scripts/catalog.py --check
python3 -m unittest discover -s tests -v
```

Python 3.10+，无第三方依赖。默认使用脚本所在仓库；`--root /path/to/catalog` 可对另一目录中的 `data/resources.json` 生成/检查输出。`--check` 不写文件，检查元数据约定与三个输出文件是否一致。

CSV 采用 UTF-8 BOM 以便表格软件识别中文；列表字段多数用 ` | ` 拼接，`links` 和 `sources` 使用 JSON 字符串以保留标签/说明。需要无损处理时优先读取 JSON。

自动检查覆盖字段类型与必填项、ID 唯一性、分类枚举、日期和 URL 格式、来源要求、生成文件一致性。它不替代人工核实，也不运行外部链接存活、认证下载或科学质量检查。
