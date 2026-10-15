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
    'climate': 'Weather and climate', 'soil': 'Soil properties',
    'flux-phenology': 'Flux observations and near-surface phenology',
    'remote-sensing': 'Satellite remote sensing and cloud platforms',
    'agricultural-statistics': 'Crop maps, yield and agricultural statistics',
    'water-resources': 'Water resources and water productivity',
    'biodiversity': 'Biodiversity and crop pests', 'china': 'China-focused datasets',
}
CATEGORIES_ZH = dict(zip(CATEGORIES, ['气象与气候', '土壤属性', '通量观测与近地面物候',
    '卫星遥感与云平台', '作物分布、产量与农业统计', '水资源与水分生产力', '生物多样性与病虫害', '中国数据专题']))
ACCESS = {'not-required': 'No registration', 'required': 'Account required', 'mixed': 'Function/product-specific', 'unknown': 'Not confirmed'}
ACCESS_ZH = {'not-required': '无需注册', 'required': '需要账户', 'mixed': '依功能/产品', 'unknown': '待核对'}
STATUS = {'documented': 'Documentation reviewed', 'partial': 'Partially reviewed', 'pending': 'Pending review'}
STATUS_ZH = {'documented': '文档已核对', 'partial': '部分核对', 'pending': '待核对'}
KINDS = {'platform': 'Platform', 'network': 'Observation network', 'dataset': 'Dataset'}
KINDS_ZH = {'platform': '平台', 'network': '观测网络', 'dataset': '数据集'}


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


def validate_translation(data, localized):
    """Translations may change wording, never identity, evidence, status or dates."""
    validate(localized)
    original = {r['id']: r for r in data['resources']}
    translated = {r['id']: r for r in localized['resources']}
    if original.keys() != translated.keys():
        raise ValueError('translation: resource IDs must match the English catalog')
    for rid, r in original.items():
        t = translated[rid]
        invariants = (
            all(r[k] == t[k] for k in ('id', 'name_en', 'kind', 'category', 'seed_refs')),
            r['access']['registration'] == t['access']['registration'],
            r['license']['url'] == t['license']['url'],
            all(r['verification'][k] == t['verification'][k] for k in ('status', 'checked_on')),
            [x['url'] for x in r['links']] == [x['url'] for x in t['links']],
            [x['url'] for x in r['verification']['sources']] == [x['url'] for x in t['verification']['sources']],
        )
        if not all(invariants):
            raise ValueError(f'translation: identity, evidence, licence, access, status or date mismatch for {rid}')


def render_locale(data, language='en', bilingual=True):
    zh = language == 'zh-CN'
    def tr(english, chinese):
        return chinese if zh else english
    categories = CATEGORIES_ZH if zh else CATEGORIES
    access = ACCESS_ZH if zh else ACCESS
    status = STATUS_ZH if zh else STATUS
    kinds = KINDS_ZH if zh else KINDS
    readme_name = 'README.zh-CN.md' if zh else 'README.md'
    catalog_name = 'catalog.zh-CN.md' if zh else 'catalog.md'
    json_name = 'resources.zh-CN.json' if zh else 'resources.json'
    source = f'data/{json_name}'
    resources = data['resources']
    counts = Counter(r['verification']['status'] for r in resources)
    latest = max(r['verification']['checked_on'] for r in resources)
    readme = [f'<!-- Generated by scripts/catalog.py; edit {source}. -->',
              '<p align="center"><img src="assets/open-agdata-logo.png" width="520" alt="Open AgData logo"></p>', '',
              tr('# Open AgData', '# Open AgData · 开放农业与环境数据资源'), '']
    if bilingual:
        readme += [tr('**English** | [简体中文](README.zh-CN.md)', '[English](README.md) | **简体中文**'), '']
    readme += [tr('**Public data resources for agriculture, remote sensing and the environment.**', '**收集、核实和汇总农业、遥感、资源环境领域的公开数据资源。**'), '',
        tr('A curated catalog with source references, explicit access conditions and machine-readable metadata. Browse by research need or category, then inspect the resource card before choosing a dataset.', '按研究需求或分类浏览，再查看资源卡片中的来源、访问条件与使用边界。目录同时提供机器可读元数据。'), '',
        tr(f'**{len(resources)} resources** across platforms, observation networks and datasets. Latest resource review: **{latest}**.', f'当前收录 **{len(resources)} 项**平台、观测网络和数据集；最近一次条目核对：**{latest}**。'), '',
        tr(f"Documentation reviewed: {counts['documented']} · Partially reviewed: {counts['partial']} · Pending: {counts['pending']}. These labels describe the evidence reviewed, not complete downloads or independent validation of data quality.", f"文档已核对 {counts['documented']} · 部分核对 {counts['partial']} · 待核对 {counts['pending']}。这反映资料核对程度，不表示已下载全部数据或独立验证数据精度。"), '',
        f"[{tr('Resource cards', '完整资源卡片')}](docs/{catalog_name}) · [JSON]({source}) · [{tr('CSV', 'CSV（英文）')}](data/resources.csv) · [{tr('Initial review', '首批核实说明（英文）')}](docs/initial-seed-audit.md) · [{tr('Contribute', '贡献指南（英文）')}](CONTRIBUTING.md)", '',
        tr('## Start with your research question', '## 从研究需求开始'), '',
        tr('| Research need | Starting points |', '| 需求 | 可从这些资源入手 |'), '| --- | --- |',
        tr('| Crop-model weather inputs | NASA POWER, Open-Meteo, CDMet, CMFD |', '| 作物模型气象驱动 | NASA POWER、Open-Meteo、CDMet、CMFD |'),
        tr('| Soil and drought context | SoilGrids, ChinaCropSM, SMCI |', '| 土壤与干旱背景 | SoilGrids、ChinaCropSM、SMCI |'),
        tr('| Field-scale imagery and sample extraction | Planetary Computer, Earth Engine, AppEEARS |', '| 田块遥感与样点提取 | Planetary Computer、Earth Engine、AppEEARS |'),
        tr('| Carbon, water fluxes and phenology | AmeriFlux, FLUXNET, PhenoCam, ChinaCropPhen |', '| 碳水通量与物候对照 | AmeriFlux、FLUXNET、PhenoCam、ChinaCropPhen |'),
        tr('| Crop distribution and yield | Quick Stats, CDL, FAOSTAT, China-focused crop and yield maps |', '| 作物分布与产量 | Quick Stats、CDL、FAOSTAT、中国作物图与单产产品 |'),
        tr('| Irrigation water use and productivity | FAO WaPOR |', '| 灌区耗水与生产力 | FAO WaPOR |'),
        tr('| Potential pest distributions | GBIF, with sampling-bias and coordinate-quality checks |', '| 病虫害潜在分布 | GBIF，结合采样偏倚与坐标质量控制 |'), '',
        tr('## Browse by category', '## 分类导航'), '']
    for cat, title in categories.items():
        n = sum(r['category'] == cat for r in resources)
        if n:
            readme.append(f'- [{title} ({n})](#category-{cat})')
    readme += ['', tr('## Read the access and evidence labels', '## 访问与核实说明'), '',
        tr('- Registration is listed separately from data licences, free-service limits and paid computing.', '- 注册要求、数据许可、免费服务限额与计算收费分别记录。'),
        tr('- Platforms describe discovery or computation services. Coverage, resolution and licences still depend on the individual product.', '- 平台描述检索与计算入口，覆盖、分辨率与许可仍须按具体产品确认。'),
        tr('- An ongoing product may have latency or incomplete current-year coverage. Check units, quality flags, spatial support and shared model inputs.', '- 持续更新不表示当年数据完整。使用时检查单位、质控、空间代表性及共享模型输入。'),
        tr('- Unknowns and conflicting versions are stated explicitly. A 403 response, timeout or JavaScript-only page is not proof that a dataset is permanently unavailable.', '- 未知与版本冲突明确记录；403、超时或 JavaScript 页面不等于数据永久失效。'), '']
    catalog = [f'<!-- Generated by scripts/catalog.py; edit {source}. -->', tr('# Resource cards', '# 完整资源卡片'), '',
        f"[{tr('Back to directory', '返回导航')}](../{readme_name}) · [{tr('Field definitions', '字段定义（英文）')}](data-dictionary.md)", '']
    if bilingual:
        catalog += [tr('**English** | [简体中文](catalog.zh-CN.md)', '[English](catalog.md) | **简体中文**'), '']
    catalog += [tr('Reviews use the cited official documentation, release records or DOI metadata. Complete downloads and independent accuracy assessment have not been performed.', '核对基于所列官方文档、发布记录或 DOI 元数据，未实测完整文件下载，也未独立验证精度。'), '']
    for cat, title in categories.items():
        group = [r for r in resources if r['category'] == cat]
        if not group:
            continue
        readme += [f'<a id="category-{cat}"></a>', '', f'## {title}', '',
            tr('| Resource | Contents and scope | Time / spatial scale | Access | Review |', '| 资源 | 内容与范围 | 时间 / 空间尺度 | 访问 | 核对 |'), '| --- | --- | --- | --- | --- |']
        catalog += [f'## {title}', '']
        for r in group:
            c, a, v = r['coverage'], r['access'], r['verification']
            readme.append(f"| [{md(r['name'])}](docs/{catalog_name}#{r['id']}) | {md(r['summary'])} | {md(c['temporal'])}; {md(c['spatial_resolution'])} | {access[a['registration']]} | {status[v['status']]} |")
            fields = [
                (tr('Provider', '提供者'), md(r['provider'])),
                (tr('Spatial coverage', '空间范围'), md(c['spatial'])),
                (tr('Temporal coverage', '时间覆盖'), md(c['temporal'])),
                (tr('Spatial resolution / depth', '空间尺度 / 深度'), md(c['spatial_resolution'])),
                (tr('Temporal resolution', '时间尺度'), md(c['temporal_resolution'])),
                (tr('Main variables', '主要变量'), md('; '.join(r['variables']))),
                (tr('Access methods', '获取方式'), md('; '.join(a['methods']))),
                (tr('Registration and access', '注册与访问'), f"**{access[a['registration']]}**; {md(a['note'])}"),
                (tr('Data licence', '数据许可'), f"[{md(r['license']['name'])}]({r['license']['url']}); {md(r['license']['note'])}"),
                (tr('Applications', '适用任务'), md('; '.join(r['applications']))),
                (tr('Review status', '核对状态'), f"**{status[v['status']]}** · {v['checked_on']}"),
                (tr('Review scope', '核对边界'), md(v['scope'])),
                (tr('Initial source groups', '首批来源分组'), ', '.join(r['seed_refs'])),
            ]
            catalog += [f'<a id="{r["id"]}"></a>', '', f"### {md(r['name'])}", '',
                f"`{r['id']}` · {kinds[r['kind']]}", '', md(r['summary']), '',
                tr('| Field | Description |', '| 字段 | 说明 |'), '| --- | --- |']
            catalog += [f'| {label} | {value} |' for label, value in fields]
            catalog += ['', f"**{tr('Links', '入口')}**: " + ' · '.join(f"[{md(x['label'])}]({x['url']})" for x in r['links']), '',
                        f"**{tr('Use notes', '使用提示')}**", '']
            catalog += ['- ' + md(x) for x in r['caveats']]
            catalog += ['', f"**{tr('Review sources', '核实来源')}**", '']
            catalog += [f"- [{md(x['note'])}]({x['url']})" for x in v['sources']]
            catalog += ['']
        readme += ['']
    readme += [tr('## Maintain and contribute', '## 持续维护与贡献'), '',
        tr('Suggest resources or corrections through Issues, or submit a pull request. Include an official entry point, a clear version, licence information and a reproducible access description.', '欢迎通过 Issue 或 PR 补充资源及修正。请提供官方入口、明确版本、许可和可重复的获取说明。'), '',
        tr('English metadata in `data/resources.json` is canonical. Keep `data/resources.zh-CN.json` in sync for Chinese readers, then regenerate both READMEs, both catalogs and the English CSV. Python 3.10+, standard library only.', '英文 `data/resources.json` 为主数据，中文内容保存在 `data/resources.zh-CN.json`。同步两份元数据后运行生成器，更新双语 README、详情与英文 CSV。Python 3.10+，仅使用标准库。'), '',
        '```bash', 'python3 scripts/catalog.py', 'python3 scripts/catalog.py --check', 'python3 -m unittest discover -s tests -v', '```', '',
        tr('Checks cover metadata structure, stable IDs, dates, URL syntax, evidence, translation invariants and generated-file consistency. They do not check live availability or scientific accuracy.', '检查覆盖字段、稳定 ID、日期、URL 格式、证据、翻译一致性和生成文件同步，不自动验证网站存活或科学精度。'), '',
        tr('See the [data dictionary](docs/data-dictionary.md) and [contribution guide](CONTRIBUTING.md). An optional [GitHub Actions template](docs/automation/README.md) is included; online workflows are not enabled.', '参见[字段字典](docs/data-dictionary.md)与[贡献指南](CONTRIBUTING.md)（英文）。仓库附[可启用的 Actions 模板](docs/automation/README.md)，线上工作流尚未启用。'), '',
        tr('## Licence and citation', '## 许可与引用'), '',
        tr('Original catalog text and curated metadata use [CC BY 4.0](LICENSE); scripts and tests use [MIT](LICENSE-CODE). External datasets, original release metadata and third-party marks retain their original rights and terms.', '原创目录文字与人工整理的元数据采用 [CC BY 4.0](LICENSE)，脚本和测试采用 [MIT](LICENSE-CODE)。外部数据、原始发布元数据及第三方标识保留原权利与条件。'), '',
        tr('Cite the actual dataset, version, DOI and authors in research. This repository provides links and descriptions; obtain complete data from the original provider.', '科研使用应引用具体数据集、版本、DOI 与原作者；完整数据从原提供方获取。'), '',
        tr('The [Open AgData logo](assets/README.md) is included as a transparent PNG, with its generation prompt and provenance.', '已提供[透明 PNG Logo 与生成说明](assets/README.md)。'), '']
    return '\n'.join(readme), '\n'.join(catalog)


def render(data, localized=None):
    readme, catalog = render_locale(data, bilingual=localized is not None)
    outputs = {'README.md': readme, 'docs/catalog.md': catalog}
    if localized is not None:
        zh_readme, zh_catalog = render_locale(localized, 'zh-CN')
        outputs.update({'README.zh-CN.md': zh_readme, 'docs/catalog.zh-CN.md': zh_catalog})
    resources = data['resources']
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
    outputs['data/resources.csv'] = '\ufeff' + out.getvalue()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1],
                        help='catalog project directory (default: repository root)')
    parser.add_argument('--check', action='store_true', help='read-only validation of metadata and generated outputs')
    args = parser.parse_args()
    try:
        data = json.loads((args.root / 'data/resources.json').read_text(encoding='utf-8'))
        validate(data)
        translation_path = args.root / 'data/resources.zh-CN.json'
        localized = None
        if translation_path.exists():
            localized = json.loads(translation_path.read_text(encoding='utf-8'))
            validate_translation(data, localized)
            lookup = {r['id']: r for r in localized['resources']}
            localized['resources'] = [lookup[r['id']] for r in data['resources']]
        outputs = render(data, localized)
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
