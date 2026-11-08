import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import update_scholar_stats as stats

PROFILE = {'scholar': 'https://scholar.google.com/citations?user=bD5bbAgAAAAJ'}
CONFIG = {'api_base': 'https://google-scholar-badge.vercel.app'}


def badge(label, message):
    response = io.BytesIO(json.dumps({'schemaVersion': 1, 'label': label, 'message': message}).encode())
    response.status = 200
    return response


class ScholarStatisticsTests(unittest.TestCase):
    def test_rejects_error_badges_and_wrong_metrics(self):
        for message in ['Rate limit', 'Auth error', 'Not found', '1,,234', '-1', 'NaN']:
            with self.subTest(message=message), self.assertRaises(ValueError):
                stats.parse_badge({'schemaVersion': 1, 'label': 'Citations', 'message': message}, 'Citations')
        with self.assertRaises(ValueError):
            stats.parse_badge({'schemaVersion': 1, 'label': 'h-index', 'message': '9'}, 'Citations')
        self.assertEqual(stats.parse_badge({'schemaVersion': 1, 'label': 'Citations', 'message': '1,234'}, 'Citations'), 1234)

    def test_success_writes_one_coherent_snapshot(self):
        responses = [badge('Citations', '301'), badge('h-index', '9'), badge('i10-index', '9')]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'stats.json'
            with patch.object(stats, 'urlopen', side_effect=responses) as request:
                snapshot = stats.update_snapshot(PROFILE, CONFIG, output)
            self.assertEqual(snapshot['metrics'], {'citations': 301, 'h_index': 9, 'i10_index': 9})
            self.assertEqual(json.loads(output.read_text()), snapshot)
            self.assertTrue(all('user=bD5bbAgAAAAJ' in call.args[0].full_url for call in request.call_args_list))
            self.assertFalse(Path(str(output) + '.tmp').exists())

    def test_partial_failure_keeps_cached_bytes_and_date(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'stats.json'
            previous = b'{"fetched_at":"2026-01-01T00:00:00Z","cached":true}\n'
            output.write_bytes(previous)
            responses = [badge('Citations', '302'), badge('h-index', 'Rate limit')]
            with patch.object(stats, 'urlopen', side_effect=responses), self.assertRaises(ValueError):
                stats.update_snapshot(PROFILE, CONFIG, output)
            self.assertEqual(output.read_bytes(), previous)

    def test_network_failure_keeps_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'stats.json'
            output.write_text('last successful snapshot')
            with patch.object(stats, 'urlopen', side_effect=URLError('offline')), self.assertRaises(URLError):
                stats.update_snapshot(PROFILE, CONFIG, output)
            self.assertEqual(output.read_text(), 'last successful snapshot')

    def test_inconsistent_values_do_not_replace_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'stats.json'
            output.write_text('last successful snapshot')
            responses = [badge('Citations', '10'), badge('h-index', '9'), badge('i10-index', '9')]
            with patch.object(stats, 'urlopen', side_effect=responses), self.assertRaises(ValueError):
                stats.update_snapshot(PROFILE, CONFIG, output)
            self.assertEqual(output.read_text(), 'last successful snapshot')

    def test_snapshot_must_match_the_profile(self):
        data = {'schema_version': 1, 'scholar_id': 'someone-else', 'source': stats.SOURCE,
                'fetched_at': '2026-01-01T00:00:00Z', 'metrics': {'citations': 301, 'h_index': 9, 'i10_index': 9}}
        with self.assertRaises(ValueError):
            stats.validate_snapshot(data, 'bD5bbAgAAAAJ')


if __name__ == '__main__':
    unittest.main()
