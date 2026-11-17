"""Real Blender disk-report operator regression for explicit boolean complete.

Uses immutable real public uv.inspect receipts. No source asset is saved.
"""
import argparse
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--inputs', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--phase', choices=('before', 'after'), required=True)
parser.add_argument('--module', default='uv_workflow_addon')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
addon = importlib.import_module(args.module)
registered_here = not hasattr(bpy.types, 'UVW_OT_surface_report')
if registered_here:
    addon.register()
ui = importlib.import_module(args.module + '.surface_ui')
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
assert not (out / 'RESULT.json').exists(), 'Preserve existing evidence'
inputs = json.loads(Path(args.inputs).read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
base = json.loads(Path(inputs['small_exact']).read_text(encoding='utf-8-sig'))
source = Path(base['source']['file'])
assert sha(source) == base['source']['sha256']
protected = {str(source): sha(source)}
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)

def invoke(path):
    try:
        result = bpy.ops.uvw.surface_report(filepath=str(path))
        error = None
    except RuntimeError as exc:
        result, error = {'CANCELLED'}, str(exc)
    return sorted(result), error

def write_report(name, report):
    report['inspection']['surface'] = copy.deepcopy(report['surface'])
    path = out / (name + '.json')
    assert not path.exists()
    path.write_text(json.dumps(report, ensure_ascii=False), encoding='utf-8')
    return path

rows = []
invalid = [('int_one', 1), ('float_one', 1.0), ('string_true', 'true'),
           ('nonempty_list', [True]), ('nonempty_dict', {'value': True})]
if args.phase == 'after':
    # A valid first sample must not hide an invalid later sample.
    ok, _ = invoke(inputs['small_exact'])
    assert ok == ['FINISHED'] and ui._REPORT is not None
    bad = copy.deepcopy(base)
    assert len(bad['surface']['samples']) > 1
    bad['surface']['samples'][-1]['complete'] = 'true'
    path = write_report('last_sample_string_true', bad)
    actual, error = invoke(path)
    assert actual == ['CANCELLED'] and ui._REPORT is None
    rows.append({'case': 'last_sample_string_true', 'operator': actual, 'cache_cleared': True})

    invalid += [('int_zero', 0), ('float_zero', 0.0), ('null', None),
                ('empty_string', ''), ('empty_list', []), ('empty_dict', {}),
                ('missing', None)]
for usage in ('CANDIDATE_EXACT', 'EXCLUSIVE'):
    for name, value in invalid:
        ok, _ = invoke(inputs['small_exact'])
        assert ok == ['FINISHED'] and ui._REPORT is not None
        bad = copy.deepcopy(base)
        bad['surface']['request']['usage'] = usage
        bad['surface']['usage'] = usage
        sample = bad['surface']['samples'][0]
        if name == 'missing':
            sample.pop('complete')
        else:
            sample['complete'] = value
        path = write_report(usage.lower() + '_' + name, bad)
        actual, error = invoke(path)
        expected = ['FINISHED'] if args.phase == 'before' else ['CANCELLED']
        assert actual == expected, (usage, name, actual, error)
        if args.phase == 'after':
            assert ui._REPORT is None, 'Rejected report must clear cached success'
        rows.append({'usage': usage, 'value_case': name, 'operator': actual,
                     'cache_cleared': ui._REPORT is None, 'error': error})

if args.phase == 'after':
    # Non-pass samples cannot use a non-bool to bypass the type gate either.
    for status in ('fail', 'unknown'):
        bad = copy.deepcopy(base)
        bad['surface']['status'] = status
        bad['surface']['samples'][0].update(status=status, complete=1)
        path = write_report('nonpass_' + status + '_int_one', bad)
        actual, error = invoke(path)
        assert actual == ['CANCELLED'] and ui._REPORT is None
        rows.append({'status': status, 'complete': 1, 'operator': actual, 'cache_cleared': True})

    # Explicit boolean False is valid evidence for an incomplete sample.
    partial = copy.deepcopy(base)
    partial['surface']['status'] = 'unknown'
    partial['surface']['samples'][0]['complete'] = False
    path = write_report('explicit_bool_false_unknown', partial)
    actual, error = invoke(path)
    assert actual == ['FINISHED'] and ui._REPORT['surface']['status'] == 'unknown'
    rows.append({'case': 'explicit_bool_false_unknown', 'operator': actual, 'surface_status': 'unknown'})

    for complete in (True, False):
        failed = copy.deepcopy(base)
        failed['surface']['status'] = 'fail'
        failed['surface']['samples'][0].update(status='fail', complete=complete)
        failed['surface']['samples'][0]['metrics']['status'] = 'fail'
        path = write_report('explicit_bool_' + str(complete).lower() + '_fail', failed)
        actual, error = invoke(path)
        assert actual == ['FINISHED'] and ui._REPORT['surface']['status'] == 'fail'
        rows.append({'case': 'explicit_bool_fail', 'complete': complete,
                     'operator': actual, 'surface_status': 'fail'})

    for name, expected in [('small_exact', 'pass'), ('exclusive', 'pass'), ('bevel_unknown', 'unknown')]:
        doc = json.loads(Path(inputs[name]).read_text(encoding='utf-8-sig'))
        path = Path(doc['source']['file'])
        assert sha(path) == doc['source']['sha256']
        protected[str(path)] = sha(path)
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
        actual, error = invoke(inputs[name])
        assert actual == ['FINISHED'] and ui._REPORT['surface']['status'] == expected
        rows.append({'actual_public_report': name, 'operator': actual, 'surface_status': expected})

assert all(sha(p) == digest for p, digest in protected.items())
result = {'status': 'known_truthy_bug_reproduced' if args.phase == 'before' else 'pass',
          'phase': args.phase, 'module': str(addon.__file__), 'surface_ui_sha256': sha(ui.__file__),
          'blender': bpy.app.version_string, 'cases': rows,
          'protected_source_files': protected, 'source_bytes_unchanged': True,
          'scope': 'Actual bpy.ops.uvw.surface_report invocation; no visible GUI claim'}
(out / 'RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
if registered_here:
    addon.unregister()
print(json.dumps({'status': result['status'], 'cases': len(rows), 'out': str(out)}))
