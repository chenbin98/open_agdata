"""Contract checks: prevent lost resources, false evidence and stale exports."""
import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'catalog.py'
FIXTURE = {
    'schema_version': 1,
    'resources': [{
        'id': 'sample-data', 'name': '测试气象', 'name_en': 'Sample climate',
        'kind': 'dataset', 'category': 'climate', 'provider': 'Sample institute',
        'summary': '多源气象, soil | 边界',
        'coverage': {'spatial': '中国', 'temporal': '2000–2020',
                     'spatial_resolution': '1 km', 'temporal_resolution': '日'},
        'variables': ['温度', '降水'], 'applications': ['模型驱动'],
        'keywords': ['climate'], 'seed_refs': ['01'],
        'access': {'registration': 'not-required', 'methods': ['HTTP'], 'note': '无需账户'},
        'license': {'name': 'CC BY 4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/', 'note': '引用作者'},
        'links': [{'label': '数据入口', 'url': 'https://example.org/data'}],
        'caveats': ['勿把格点值当站点观测'],
        'verification': {'status': 'documented', 'checked_on': '2026-10-15',
                         'scope': '已阅读官方元数据，未下载',
                         'sources': [{'url': 'https://example.org/docs', 'note': '范围与许可'}]}
    }]
}

class CatalogContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()

    def run_catalog(self, data=None, *flags):
        if data is not None:
            (self.root / 'data/resources.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), *flags],
                              capture_output=True, text=True)

    def test_exports_preserve_chinese_and_csv_columns(self):
        result = self.run_catalog(FIXTURE)
        self.assertEqual(result.returncode, 0, result.stderr)
        with (self.root / 'data/resources.csv').open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]['summary'], '多源气象, soil | 边界')
        self.assertEqual(rows[0]['license'], 'CC BY 4.0')
        self.assertIn('测试气象', (self.root / 'docs/catalog.md').read_text(encoding='utf-8'))

    def test_duplicate_ids_rejected_before_writing(self):
        data = copy.deepcopy(FIXTURE)
        data['resources'].append(copy.deepcopy(data['resources'][0]))
        result = self.run_catalog(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate id', result.stderr)
        self.assertFalse((self.root / 'README.md').exists())

    def test_documented_resource_requires_evidence(self):
        data = copy.deepcopy(FIXTURE)
        data['resources'][0]['verification']['sources'] = []
        result = self.run_catalog(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('verification.sources', result.stderr)

    def test_check_detects_drift_without_overwriting(self):
        result = self.run_catalog(FIXTURE)
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.root / 'README.md'
        target.write_text('stale export\n', encoding='utf-8')
        result = self.run_catalog(None, '--check')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('README.md', result.stderr)
        self.assertEqual(target.read_text(encoding='utf-8'), 'stale export\n')

    def test_malformed_source_url_and_date_rejected(self):
        for field, value in [('url', 'https://example.org/”'), ('checked_on', 'tomorrow')]:
            with self.subTest(field=field):
                data = copy.deepcopy(FIXTURE)
                if field == 'url': data['resources'][0]['verification']['sources'][0]['url'] = value
                else: data['resources'][0]['verification'][field] = value
                result = self.run_catalog(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field, result.stderr)

if __name__ == '__main__':
    unittest.main()
