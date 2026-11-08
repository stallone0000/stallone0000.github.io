#!/usr/bin/env python3
"""Cache all three dexhunter/google-scholar-badge metrics as one valid snapshot."""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://github.com/dexhunter/google-scholar-badge'
METRICS = [('citations', 'citations', 'Citations'),
           ('h_index', 'h-index', 'h-index'),
           ('i10_index', 'i10-index', 'i10-index')]


def get_scholar_id(profile):
    url = urlsplit(profile['scholar'])
    scholar_id = parse_qs(url.query).get('user', [''])[0]
    if url.hostname != 'scholar.google.com' or not re.fullmatch(r'[\w-]{12}', scholar_id, re.ASCII):
        raise ValueError('Invalid Google Scholar profile URL')
    return scholar_id


def validate_snapshot(data, scholar_id):
    if data.get('schema_version') != 1 or data.get('scholar_id') != scholar_id:
        raise ValueError('Scholar snapshot does not match this profile')
    if data.get('source') != SOURCE:
        raise ValueError('Unexpected Scholar data source')
    checked = datetime.fromisoformat(data['fetched_at'].replace('Z', '+00:00'))
    if checked.tzinfo is None:
        raise ValueError('Snapshot timestamp must include a timezone')
    metrics = data['metrics']
    for key, _, _ in METRICS:
        value = metrics[key]
        if type(value) is not int or not 0 <= value <= 9007199254740991:
            raise ValueError(f'Invalid {key} value')
    if metrics['h_index'] ** 2 > metrics['citations'] or metrics['i10_index'] * 10 > metrics['citations']:
        raise ValueError('Inconsistent Scholar metrics')
    return data


def parse_badge(data, label):
    if not isinstance(data, dict) or data.get('schemaVersion') != 1 or data.get('isError'):
        raise ValueError(f'{label} endpoint returned an invalid badge')
    if data.get('label') != label:
        raise ValueError(f'{label} endpoint returned the wrong metric')
    message = data.get('message')
    if not isinstance(message, str) or not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)', message, re.ASCII):
        raise ValueError(f'{label} endpoint did not return a numeric value')
    return int(message.replace(',', ''))


def fetch_snapshot(profile, config):
    scholar_id = get_scholar_id(profile)
    base = config['api_base'].rstrip('/')
    if base != 'https://google-scholar-badge.vercel.app':
        raise ValueError('Use the configured dexhunter badge service')
    metrics = {}
    # Sequential requests reuse the upstream's per-author metrics cache.
    for key, endpoint, label in METRICS:
        request = Request(f'{base}/{endpoint}?{urlencode({"user": scholar_id})}',
                          headers={'Accept': 'application/json', 'User-Agent': 'QilongShiHomepage/1.0'})
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise ValueError(f'{label} endpoint returned HTTP {response.status}')
            metrics[key] = parse_badge(json.loads(response.read(65536)), label)
    snapshot = {
        'schema_version': 1, 'scholar_id': scholar_id, 'source': SOURCE,
        'fetched_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'metrics': metrics,
    }
    return validate_snapshot(snapshot, scholar_id)


def update_snapshot(profile, config, output):
    # Do not touch the existing file until every endpoint has passed validation.
    snapshot = fetch_snapshot(profile, config)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + '.tmp')
    try:
        temporary.write_text(json.dumps(snapshot, indent=2) + '\n')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return snapshot


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/scholar-stats.json')
    args = parser.parse_args()
    try:
        profile = json.loads((ROOT / 'data/profile.json').read_text())
        config = json.loads((ROOT / 'data/scholar.json').read_text())
        snapshot = update_snapshot(profile, config, args.output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Scholar update failed; previous snapshot kept: {error}', file=sys.stderr)
        sys.exit(1)
    print('Scholar statistics checked:', json.dumps(snapshot['metrics']))
