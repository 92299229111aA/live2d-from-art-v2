"""Offline invariant tests; fixtures are NOT real Core/visual validation."""
import json
import tempfile
import unittest
from pathlib import Path
from pack_runtime import package, hashes
from release_gate import evaluate, ALL, BASE


class PipelineTests(unittest.TestCase):
    def test_package_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            (source / 'test.moc3').write_bytes(b'fixture only')
            (source / 'texture.png').write_bytes(b'fixture only')
            (source / 'private.txt').write_text('must not ship')
            model = source / 'test.model3.json'
            model.write_text(json.dumps({'FileReferences': {'Moc': 'test.moc3', 'Textures': ['texture.png']}}))
            dest = root / 'runtime'
            package(model, dest)
            self.assertFalse((dest / 'private.txt').exists())
            with self.assertRaises(ValueError):
                package(model, dest)
            evidence = root / 'evidence.txt'
            evidence.write_text('synthetic test evidence, not a real model review')
            review = {'target': 'vts', 'required': sorted(BASE), 'package_sha256': hashes(dest),
                      'checks': {n: {'status': 'PASS', 'scope': 'fixture', 'reviewer': 'test',
                                     'reviewed_at': '2026-09-21', 'notes': 'fixture',
                                     'evidence': ['evidence.txt']} for n in ALL}}
            path = root / 'review.json'
            def result():
                path.write_text(json.dumps(review))
                return evaluate(path, dest)['project_status']
            self.assertEqual(result(), 'PRODUCTION_READY')
            review['checks']['VTS_RUNTIME']['status'] = 'NOT_TESTED'
            self.assertEqual(result(), 'BROWSER_VALIDATED_VTS_UNVERIFIED')
            review['checks']['HEAD']['evidence'] = ['missing.png']
            self.assertEqual(result(), 'NEEDS_FIXES')
            review['checks']['HEAD']['evidence'] = ['evidence.txt']
            (dest / 'texture.png').write_bytes(b'changed')
            self.assertEqual(result(), 'NEEDS_FIXES')
            document = json.loads(model.read_text())
            document['FileReferences']['Moc'] = '../evidence.txt'
            model.write_text(json.dumps(document))
            with self.assertRaises(ValueError):
                package(model, root / 'invalid')


if __name__ == '__main__':
    unittest.main()
