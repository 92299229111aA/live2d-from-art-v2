#!/usr/bin/env python3
"""Initialize a review with no inferred passes. Refuse to overwrite evidence."""
import argparse
import json
from pathlib import Path
from pack_runtime import hashes
from release_gate import ALL, BASE

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('review', type=Path)
    parser.add_argument('--target', choices=['vts', 'browser'], default='vts')
    args = parser.parse_args()
    if not args.package.is_dir() or not hashes(args.package):
        parser.error('package must be a nonempty directory')
    document = {'schema_version': 1, 'target': args.target,
                'required': sorted(BASE | ({'VTS_RUNTIME'} if args.target == 'vts' else set())),
                'package_sha256': hashes(args.package),
                'checks': {name: {'status': 'NOT_TESTED', 'scope': '', 'reviewer': '',
                                   'reviewed_at': '', 'evidence': [], 'notes': ''} for name in ALL}}
    args.review.parent.mkdir(parents=True, exist_ok=True)
    with args.review.open('x', encoding='utf-8') as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2)
