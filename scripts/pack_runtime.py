#!/usr/bin/env python3
"""Copy validated manifest references into a NEW portable runtime directory."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from check_runtime import check


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def package(model, destination):
    model, destination = Path(model).resolve(), Path(destination).resolve()
    result = check(model)
    if not result['ok']:
        raise ValueError(result['errors'])
    if destination.exists():
        raise ValueError('Destination exists; choose a new build directory')
    if destination.is_relative_to(model.parent):
        raise ValueError('Destination must be outside source runtime')
    files = sorted(set([model.name] + result['checked']))
    destination.mkdir(parents=True)
    for name in files:
        source = (model.parent / name).resolve()
        target = destination / source.relative_to(model.parent)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return {'scope': 'references only, not Core or visual QA',
            'files': hashes(destination), 'model': model.name}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(package(args.model, args.destination), ensure_ascii=False, indent=2))
