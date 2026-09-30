#!/usr/bin/env python3
"""Restore an archived site with a new commit, preserving the current version.

Preview: python3 scripts/restore_site.py
Restore locally: python3 scripts/restore_site.py --apply
Restore and publish: python3 scripts/restore_site.py --apply --push
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args, capture=False):
    result = subprocess.run(['git', *args], cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag', nargs='?', default='ben-style-2026-09-30')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--push', action='store_true')
    args = parser.parse_args()
    if args.tag.startswith('-'):
        parser.error('Provide a tag name, not a Git option.')
    if args.push and not args.apply:
        parser.error('--push requires --apply.')
    target = git('rev-parse', '--verify', f'refs/tags/{args.tag}^{{commit}}', capture=True)
    print(f'Restore the complete site snapshot: {args.tag} ({target})', flush=True)
    print('This restores both design and content. The current version will be saved to GitHub first.', flush=True)
    if not args.apply:
        print('Preview only. Add --apply to create a restoration commit; add --push to publish it.')
        return
    if git('branch', '--show-current', capture=True) != 'main':
        parser.error('Run from the main branch.')
    if git('status', '--porcelain', capture=True):
        parser.error('The working tree must be clean. Commit or save pending work first.')
    git('fetch', 'origin')
    if git('rev-parse', 'HEAD', capture=True) != git('rev-parse', 'origin/main', capture=True):
        parser.error('Local main must match origin/main before restoring.')
    saved = 'before-restore-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    git('tag', '-a', saved, '-m', f'Automatic backup before restoring {args.tag}')
    git('push', 'origin', f'refs/tags/{saved}')
    git('restore', f'--source={target}', '--staged', '--worktree', '--', '.')
    restored_tree = git('write-tree', capture=True)
    expected_tree = git('rev-parse', f'{target}^{{tree}}', capture=True)
    if restored_tree != expected_tree:
        raise RuntimeError('Restored tree does not match the archived snapshot; nothing was published.')
    git('commit', '-m', f'Restore complete site from {args.tag}')
    if args.push:
        git('push', 'origin', 'main')
    print(f'Restored {args.tag}. Previous version remains on GitHub as {saved}.')


if __name__ == '__main__':
    main()
