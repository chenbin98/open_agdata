#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Open AgData and deterministically render Markdown and CSV (stdlib only)."""
import argparse
from collections import Counter
import csv
from datetime import date
import html
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

CATEGORIES = {
    'climate': '气象与气候',
    'soil': '土壤属性',
    'flux-phenology': '通量观测与近地面物候',
    'remote-sensing': '卫星遥感与云平台',
    'agricultural-statistics': '作物分布、产量与农业统计',
    'water-resources': '水资源与水分生产力',
    'biodiversity': '生物多样性与病虫害',
    'china': '中国数据专题',
}
ACCESS = {'not-required': '无需注册', 'required': '需要账户', 'mixed': '依功能/产品', 'unknown': '待核对'}
STATUS = {'documented': '文档已核对', 'partial': '部分核对', 'pending': '待核对'}
KINDS = {'platform': '平台', 'network': '观测网络', 'dataset': '数据集'}


def validate(data):
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def text(value, field):
        require(isinstance(value, str) and bool(value.strip()), f'{field}: non-empty string required')

    def url(value, field):
        text(value, field)
        p = urlsplit(value)
        require(p.scheme in ('http', 'https') and bool(p.hostname)
                and not p.username and not p.password
                and not any(c.isspace() or c in '\"\'<>“”‘’' for c in value), f'{field}: invalid url')

    def strings(value, field):
        require(isinstance(value, list) and bool(value), f'{field}: non-empty list required')
        for item in value:
            text(item, field)

    def fields(obj, names, prefix):
        require(isinstance(obj, dict), f'{prefix}: object required')
        for name in names:
            require(name in obj, f'{prefix}.{name}: required')

    fields(data, ['schema_version', 'resources'], 'catalog')
    require(type(data['schema_version']) is int and data['schema_version'] == 1, 'unsupported schema_version')
    require(isinstance(data['resources'], list) and bool(data['resources']), 'resources: non-empty list required')
    seen = set()
    for r in data['resources']:
        fields(r, ['id', 'name', 'name_en', 'kind', 'category', 'provider', 'summary', 'coverage',
                   'variables', 'access', 'license', 'links', 'applications', 'caveats',
                   'verification', 'keywords', 'seed_refs'], 'resource')
        for field in ('id', 'name', 'name_en', 'provider', 'summary'):
            text(r[field], field)
        require(bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', r['id'])), 'id: use lowercase kebab-case')
        require(r['id'] not in seen, f"duplicate id: {r['id']}")
        seen.add(r['id'])
        require(r['kind'] in KINDS, f"{r['id']}: invalid kind")
        require(r['category'] in CATEGORIES, f"{r['id']}: invalid category")
        for field in ('variables', 'applications', 'caveats', 'keywords', 'seed_refs'):
            strings(r[field], f"{r['id']}.{field}")
        fields(r['coverage'], ['spatial', 'temporal', 'spatial_resolution', 'temporal_resolution'], 'coverage')
        for k, v in r['coverage'].items():
            text(v, 'coverage.' + k)
        fields(r['access'], ['registration', 'methods', 'note'], 'access')
        require(r['access']['registration'] in ACCESS, 'access.registration: invalid enum')
        strings(r['access']['methods'], 'access.methods')
        text(r['access']['note'], 'access.note')
        fields(r['license'], ['name', 'url', 'note'], 'license')
        text(r['license']['name'], 'license.name')
        url(r['license']['url'], 'license.url')
        text(r['license']['note'], 'license.note')
        fields(r['verification'], ['status', 'checked_on', 'scope', 'sources'], 'verification')
        v = r['verification']
        require(v['status'] in STATUS, 'verification.status: invalid enum')
        text(v['scope'], 'verification.scope')
        try:
            require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', v['checked_on'])), 'checked_on: expected YYYY-MM-DD')
            date.fromisoformat(v['checked_on'])
        except (TypeError, ValueError) as exc:
            raise ValueError('checked_on: invalid ISO date') from exc
        require(isinstance(v['sources'], list), 'verification.sources: list required')
        require(v['status'] == 'pending' or bool(v['sources']), 'verification.sources: evidence required')
        require(isinstance(r['links'], list) and bool(r['links']), 'links: non-empty list required')
        for entry in r['links']:
            fields(entry, ['label', 'url'], 'links')
            text(entry['label'], 'links.label')
            url(entry['url'], 'links.url')
        for entry in v['sources']:
            fields(entry, ['url', 'note'], 'verification.sources')
            url(entry['url'], 'verification.sources.url')
            text(entry['note'], 'verification.sources.note')


def md(value):
    return html.escape(str(value), quote=False).replace('|', '\\|').replace('\n', ' ')


def render(data):
    resources = data['resources']
    counts = Counter(r['verification']['status'] for r in resources)
    latest = max(r['verification']['checked_on'] for r in resources)
    readme = [
        '<!-- Generated by scripts/catalog.py; edit data/resources.json for resource changes. -->',
        '# Open AgData · 开放农业与环境数据资源', '',
        '**收集、核实和汇总农业、遥感、资源环境领域的公开数据资源。**', '',
        'A curated, source-backed catalog of public data resources for agriculture, remote sensing, and the environment. Chinese first, with stable IDs and machine-readable metadata.', '',
        f'当前收录 **{len(resources)} 项**平台、观测网络和数据集；最近一次条目核对：**{latest}**。', '',
        f"核对状态：文档已核对 {counts['documented']} · 部分核对 {counts['partial']} · 待核对 {counts['pending']}。这反映说明与元数据的核对程度，不表示已下载验证全部数据。", '',
        '[完整资源卡片](docs/catalog.md) · [JSON](data/resources.json) · [CSV](data/resources.csv) · [首批资源核实说明](docs/initial-seed-audit.md) · [贡献指南](CONTRIBUTING.md)', '',
        '## 从研究需求开始', '',
        '| 需求 | 可从这些资源入手 |', '| --- | --- |',
        '| 作物模型气象驱动 | NASA POWER、Open-Meteo、CDMet、CMFD |',
        '| 土壤与干旱背景 | SoilGrids、ChinaCropSM、SMCI |',
        '| 田块遥感与样点提取 | Planetary Computer、Earth Engine、AppEEARS |',
        '| 碳水通量与物候对照 | AmeriFlux、FLUXNET、PhenoCam、ChinaCropPhen |',
        '| 作物分布与产量 | Quick Stats、CDL、FAOSTAT、中国作物图与单产产品 |',
        '| 灌区耗水与生产力 | FAO WaPOR |',
        '| 病虫害潜在分布 | GBIF，配合采样偏倚和坐标质量控制 |', '',
        '## 分类导航', '',
    ]
    for cat, title in CATEGORIES.items():
        n = sum(r['category'] == cat for r in resources)
        if n:
            readme.append(f'- [{title}（{n}）](#category-{cat})')
    readme += ['', '## 如何读这份目录', '',
        '- 访问条件分为无需注册、需要账户、依功能/产品、待核对；免费访问、开放许可和计算服务收费分别记录。',
        '- 平台条目描述检索与计算入口；数据集条目描述具体产品，不能把平台的时间范围、分辨率或许可套给全部产品。',
        '- “至今”表示源持续更新，不能理解为当年所有日期均已有数据。空间尺度、单位、质量标记和模型推导依赖应在研究中另行检查。',
        '- 未读到的内容写明待核对；403、超时或 JavaScript 页面不等于数据永久失效。', '',
    ]
    catalog = ['<!-- Generated by scripts/catalog.py; edit data/resources.json. -->',
               '# 完整资源卡片', '', '[返回导航](../README.md) · [字段定义](data-dictionary.md)', '',
               '核对基于所列官方文档、发布记录或 DOI 注册元数据。未实测完整文件下载，也未独立验证产品精度。', '']
    for cat, title in CATEGORIES.items():
        group = [r for r in resources if r['category'] == cat]
        if not group:
            continue
        readme += [f'<a id="category-{cat}"></a>', f'## {title}', '',
                   '| 资源 | 内容与范围 | 时间 / 空间尺度 | 访问 | 核对 |', '| --- | --- | --- | --- | --- |']
        catalog += [f'## {title}', '']
        for r in group:
            c, a, v = r['coverage'], r['access'], r['verification']
            readme.append(f"| [{md(r['name'])}](docs/catalog.md#{r['id']}) | {md(r['summary'])} | {md(c['temporal'])}；{md(c['spatial_resolution'])} | {ACCESS[a['registration']]} | {STATUS[v['status']]} |")
            catalog += [f'<a id="{r["id"]}"></a>', f"### {md(r['name'])}", '',
                        f"{md(r['name_en'])} · `{r['id']}` · {KINDS[r['kind']]}", '', md(r['summary']), '',
                        '| 字段 | 说明 |', '| --- | --- |',
                        f"| 提供者 | {md(r['provider'])} |",
                        f"| 空间范围 | {md(c['spatial'])} |", f"| 时间覆盖 | {md(c['temporal'])} |",
                        f"| 空间尺度 / 深度 | {md(c['spatial_resolution'])} |", f"| 时间尺度 | {md(c['temporal_resolution'])} |",
                        f"| 主要变量 | {md('、'.join(r['variables']))} |",
                        f"| 获取方式 | {md('、'.join(a['methods']))} |",
                        f"| 注册与访问 | **{ACCESS[a['registration']]}**；{md(a['note'])} |",
                        f"| 数据许可 | [{md(r['license']['name'])}]({r['license']['url']})；{md(r['license']['note'])} |",
                        f"| 适用任务 | {md('、'.join(r['applications']))} |",
                        f"| 核对状态 | **{STATUS[v['status']]}** · {v['checked_on']} |",
                        f"| 核对边界 | {md(v['scope'])} |",
                        f"| 首批来源分组 | {md('、'.join(r['seed_refs']))} |", '',
                        '**入口**：' + ' · '.join(f"[{md(x['label'])}]({x['url']})" for x in r['links']), '', '**使用提示**', '']
            catalog += ['- ' + md(x) for x in r['caveats']]
            catalog += ['', '**核实来源**', '']
            catalog += [f"- [{md(x['note'])}]({x['url']})" for x in v['sources']]
            catalog += ['']
        readme += ['']
    readme += ['## 持续维护与贡献', '',
        '欢迎通过 Issue 提交新资源或报告失效链接，也可以直接提交 Pull Request。优先提供官方入口、明确版本、许可和可重复的获取说明。', '',
        '只编辑 `data/resources.json` 中的资源信息，随后运行以下命令；Python 3.10+，仅使用标准库，无需安装依赖。', '',
        '```bash', 'python3 scripts/catalog.py', 'python3 scripts/catalog.py --check', 'python3 -m unittest discover -s tests -v', '```', '',
        '脚本检查字段、稳定 ID、日期、URL 格式、核实来源和导出一致性；另附[可启用的 GitHub Actions 模板](docs/automation/README.md)，首版尚未启用线上工作流。校验不自动验证外部网站存活或数据质量。', '',
        '字段约定见 [数据字典](docs/data-dictionary.md)。新增数据优先补充版本、DOI、单位、质量标记和使用边界；下载范例、网站与更多专题可在后续按需求增加。', '',
        '## 许可与引用', '',
        '本仓库原创目录文字与人工整理的元数据采用 [CC BY 4.0](LICENSE)，脚本与测试采用 [MIT](LICENSE-CODE)。外部数据、原始发布元数据、机构商标和引用作品保留原权利及许可；收录不改变它们的使用条件。', '',
        '科研使用应引用具体数据集、版本、DOI 与原始作者；本目录只帮助发现和判断资源。仓库保存链接与说明，完整数据从原提供方获取。', '',
    ]
    out = io.StringIO(newline='')
    columns = ['id', 'name', 'name_en', 'kind', 'category', 'provider', 'summary', 'spatial', 'temporal',
               'spatial_resolution', 'temporal_resolution', 'variables', 'registration', 'access_methods',
               'access_note', 'license', 'license_url', 'license_note', 'links', 'applications', 'caveats',
               'keywords', 'verification_status', 'checked_on', 'verification_scope', 'sources', 'seed_refs']
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    for r in resources:
        writer.writerow({
            **{k: r[k] for k in ('id', 'name', 'name_en', 'kind', 'category', 'provider', 'summary')},
            **r['coverage'], 'variables': ' | '.join(r['variables']), 'registration': r['access']['registration'],
            'access_methods': ' | '.join(r['access']['methods']), 'access_note': r['access']['note'],
            'license': r['license']['name'], 'license_url': r['license']['url'], 'license_note': r['license']['note'],
            'links': json.dumps(r['links'], ensure_ascii=False), 'applications': ' | '.join(r['applications']),
            'caveats': ' | '.join(r['caveats']), 'keywords': ' | '.join(r['keywords']),
            'verification_status': r['verification']['status'], 'checked_on': r['verification']['checked_on'],
            'verification_scope': r['verification']['scope'],
            'sources': json.dumps(r['verification']['sources'], ensure_ascii=False), 'seed_refs': ' | '.join(r['seed_refs'])})
    # UTF-8 BOM helps spreadsheet software recognize Chinese text.
    return {'README.md': '\n'.join(readme), 'docs/catalog.md': '\n'.join(catalog),
            'data/resources.csv': '\ufeff' + out.getvalue()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1],
                        help='catalog project directory (default: repository root)')
    parser.add_argument('--check', action='store_true', help='read-only validation of metadata and generated outputs')
    args = parser.parse_args()
    try:
        data = json.loads((args.root / 'data/resources.json').read_text(encoding='utf-8'))
        validate(data)
        outputs = render(data)
        if args.check:
            drift = [name for name, value in outputs.items()
                     if not (args.root / name).exists() or (args.root / name).read_bytes() != value.encode('utf-8')]
            if drift:
                raise ValueError('stale or missing exports: ' + ', '.join(drift) + '; run python3 scripts/catalog.py')
        else:
            for name, value in outputs.items():
                target = args.root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(value.encode('utf-8'))
        print(f"OK: {len(data['resources'])} resources; {'checked' if args.check else 'generated'} {len(outputs)} exports")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
