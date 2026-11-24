"""Package the standalone extension and complete UV skill; never overwrite output."""
from pathlib import Path
import argparse
import hashlib
import json
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / 'tools/uv_workflow_addon'


def write_zip(path, entries):
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for name, source in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compresslevel=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New output directory; existing paths are rejected')
    args = parser.parse_args()
    manifest = tomllib.loads((ADDON / 'blender_manifest.toml').read_text('utf-8'))
    version = manifest['version']
    extension = [(p.name, p) for p in ADDON.iterdir()
                 if p.is_file() and (p.suffix == '.py' or p.name in
                    {'blender_manifest.toml', 'LICENSE', 'NOTICE.md'})]
    assert len(extension) == 34, 'Review changed production member set before publishing'
    assert {'LICENSE', 'NOTICE.md', '__init__.py', 'blender_manifest.toml'} <= {
        name for name, _ in extension}
    skill = [(p.relative_to(ROOT).as_posix(), p)
             for p in (ROOT / 'skills/blender-uv').rglob('*')
             if p.is_file() and (p.suffix == '.md' or p.name == 'LICENSE')]
    # The frozen skill ZIP uses a root license rather than a duplicate nested copy.
    skill = [(name, p) for name, p in skill if name != 'skills/blender-uv/LICENSE']
    skill += [('docs/cli/UV工作流.md', ROOT / 'docs/cli/UV工作流.md'),
              ('LICENSE', ROOT / 'LICENSE'), ('NOTICE.md', ROOT / 'NOTICE.md')]
    for _, source in extension + skill:
        assert source.is_file(), source
    args.output.mkdir(parents=True, exist_ok=False)
    outputs = [(f'uv-workflow-{version}.zip', extension),
               ('blender-uv-skill-20261117.zip', skill)]
    checksums = []
    for filename, entries in outputs:
        path = args.output / filename
        write_zip(path, entries)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksums.append(f'{digest}  {filename}')
    (args.output / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'pass', 'version': version,
                      'output': str(args.output.resolve()), 'checksums': checksums}))


if __name__ == '__main__':
    main()
