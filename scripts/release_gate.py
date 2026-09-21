#!/usr/bin/env python3
"""Validate recorded evidence and package freshness; never judge image quality."""
import argparse
import json
from pathlib import Path
from pack_runtime import hashes

ALL = 'STATIC_FIDELITY CORE_LOAD PARAMETER_BINDING BLINK EYE_TRACKING MOUTH HEAD BODY HAIR RABBIT_EARS TWIN_TAILS SLEEVES ACCESSORIES PHYSICS BROWSER_RUNTIME VTS_RUNTIME'.split()
BASE = set('STATIC_FIDELITY CORE_LOAD PARAMETER_BINDING BLINK EYE_TRACKING MOUTH HEAD BODY PHYSICS BROWSER_RUNTIME'.split())
STATUSES = {'PASS', 'WARN', 'FAIL', 'NOT_TESTED', 'NOT_IMPLEMENTED'}


def evaluate(review_path, package):
    review_path, package = Path(review_path).resolve(), Path(package).resolve()
    review = json.loads(review_path.read_text(encoding='utf-8-sig'))
    errors = []
    checks = review.get('checks', {})
    if not isinstance(checks, dict):
        raise ValueError('checks must be an object')
    target = review.get('target')
    if target not in ('vts', 'browser'):
        errors.append('target must be vts or browser')
    required = set(review.get('required', [])) | BASE
    if target == 'vts':
        required.add('VTS_RUNTIME')
    if required - set(ALL):
        errors.append('unknown required checks')
    if not package.is_dir() or not review.get('package_sha256') or hashes(package) != review['package_sha256']:
        errors.append('package absent or changed since review')
    for name in ALL:
        item = checks.get(name, {})
        if not isinstance(item, dict) or item.get('status') not in STATUSES:
            errors.append(f'{name}: missing or invalid status')
            continue
        if item['status'] == 'PASS':
            for field in ('scope', 'reviewer', 'reviewed_at', 'notes', 'evidence'):
                if not item.get(field):
                    errors.append(f'{name}: missing {field}')
            evidence = item.get('evidence', [])
            if not isinstance(evidence, list):
                errors.append(f'{name}: evidence must be a list')
                continue
            for value in evidence:
                if not isinstance(value, str):
                    errors.append(f'{name}: invalid evidence path')
                    continue
                path = (review_path.parent / value).resolve()
                if not path.is_relative_to(review_path.parent) or not path.is_file() or path.stat().st_size == 0:
                    errors.append(f'{name}: absent or outside QA evidence {value}')
    passed = lambda key: checks.get(key, {}).get('status') == 'PASS'
    if errors or any(c.get('status') == 'FAIL' for c in checks.values() if isinstance(c, dict)):
        status = 'NEEDS_FIXES'
    elif all(passed(k) for k in required):
        status = 'PRODUCTION_READY' if target == 'vts' else 'BROWSER_VALIDATED'
    elif passed('BROWSER_RUNTIME') and not passed('VTS_RUNTIME'):
        status = 'BROWSER_VALIDATED_VTS_UNVERIFIED'
    else:
        status = 'IN_PROGRESS'
    return {'project_status': status, 'errors': errors,
            'pending_required': sorted(k for k in required if not passed(k)),
            'scope': 'Declared reviews and evidence freshness only; no automated visual judgment'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    result = evaluate(args.review, args.package)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['project_status'] in ('PRODUCTION_READY', 'BROWSER_VALIDATED') else 1)
