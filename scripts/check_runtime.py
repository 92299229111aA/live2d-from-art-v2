#!/usr/bin/env python3
"""Validate local model3 references, not MOC binary correctness or visual quality."""
import argparse
import json
from pathlib import Path


def check(model_path):
    model_path = Path(model_path).resolve()
    errors, checked = [], []
    try:
        model = json.loads(model_path.read_text(encoding='utf-8'))
        refs = model['FileReferences']
        if not isinstance(refs, dict):
            raise ValueError('FileReferences must be an object')
    except (OSError, ValueError, KeyError) as exc:
        return {'ok': False, 'errors': [str(exc)], 'checked': []}
    targets = []
    for key in ('Moc', 'Textures'):
        value = refs.get(key)
        if key == 'Moc':
            if isinstance(value, str) and value:
                targets.append((key, value))
            else:
                errors.append('Missing valid Moc reference')
        elif isinstance(value, list) and value:
            targets.extend((key, item) for item in value)
        else:
            errors.append('Missing nonempty Textures list')
    for key in ('Physics', 'Pose', 'DisplayInfo', 'UserData'):
        if key in refs:
            targets.append((key, refs[key]))
    expressions = refs.get('Expressions', [])
    motions = refs.get('Motions', {})
    if not isinstance(expressions, list) or not isinstance(motions, dict):
        errors.append('Expressions must be a list; Motions must be an object')
    else:
        for entry in expressions:
            targets.append(('Expression', entry.get('File') if isinstance(entry, dict) else None))
        for group, entries in motions.items():
            if not isinstance(entries, list):
                errors.append(f'Motion group {group} must be a list')
                continue
            for entry in entries:
                targets.append(('Motion', entry.get('File') if isinstance(entry, dict) else None))
                if isinstance(entry, dict) and 'Sound' in entry:
                    targets.append(('Sound', entry['Sound']))
    for kind, value in targets:
        if not isinstance(value, str) or not value:
            errors.append(f'{kind}: invalid file reference')
            continue
        # This helper validates portable packages, not browser query-hashed manifests.
        path = (model_path.parent / value).resolve()
        if not path.is_relative_to(model_path.parent) or '?' in value or '#' in value:
            errors.append(f'{kind}: not a portable in-package path: {value}')
            continue
        try:
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError('missing or empty')
            if path.suffix == '.json':
                json.loads(path.read_text(encoding='utf-8'))
            checked.append(value)
        except (OSError, ValueError) as exc:
            errors.append(f'{kind}: {value}: {exc}')
    return {'ok': not errors, 'scope': 'Local references only; requires Core and visual validation',
            'checked': checked, 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    result = check(parser.parse_args().model)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['ok'] else 1)
