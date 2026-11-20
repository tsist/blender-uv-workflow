"""Run under a timeout with Blender --background --factory-startup --python-exit-code 23 --python <this file>."""
from pathlib import Path
import sys
from unittest.mock import patch

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uv_workflow_addon import core


class Override:
    """Forward Blender access except for the selected native operator."""
    def __init__(self, wrapped, **overrides):
        self.wrapped = wrapped
        self.__dict__.update(overrides)

    def __getattr__(self, name):
        return getattr(self.wrapped, name)


bpy.ops.wm.read_factory_settings(use_empty=False)
obj = bpy.context.scene.objects['Cube']
source = obj.data.uv_layers.active
# An explicit shader consumer and a non-target UV layer must remain bound.
material = bpy.data.materials.new('SourceMaterial')
material.use_nodes = True
node = material.node_tree.nodes.new('ShaderNodeUVMap')
node.uv_map = source.name
obj.data.materials.append(material)
other = obj.data.uv_layers.new(name='OtherUV')
other.data[0].pin_uv = True
obj.data.uv_layers.active = source
before = core.protection([obj])
source_uv = core.coordinates(obj.data, source.name).copy()
other_uv = core.coordinates(obj.data, other.name).copy()
identity = (bpy.context.scene.name, bpy.context.view_layer.name, obj.name)
base = dict(version='1.0', scene=identity[0], view_layer=identity[1], objects=[identity[2]])


def run(name, method='SMART', native=None, **constraints):
    calls = []

    def pack(**kwargs):
        calls.append(kwargs)
        return bpy.ops.uv.pack_islands(**kwargs) if native is None else native

    ops = Override(bpy.ops, uv=Override(bpy.ops.uv, pack_islands=pack))
    with patch.object(core, 'bpy', Override(bpy, ops=ops)):
        result = core.execute(dict(base, operation='generate', methods=[method], candidate=name,
                                   constraints={obj.name: dict(constraints, source_uv=source.name)}))
    return result['candidates'][0], calls


affected = sys.platform == 'linux' and bpy.app.version[:2] == (5, 3)
expected_shape = 'AABB' if affected else 'CONCAVE'
row = None
if affected:
    row, calls = run('compat')
    assert len(calls) == 1 and calls[0]['shape_method'] == expected_shape, calls
    assert calls[0]['margin_method'] == 'FRACTION' and not calls[0]['pin'], calls
    assert row['status'] == 'needs_review' and row['metrics']['status'] == 'pass', row
    assert row['metrics']['gap']['min_px'] >= 16 and row['metrics']['boundary_margin_px'] >= 8, row['metrics']
    assert np.isfinite(core.coordinates(obj.data, row['layer'])).all()
    assert core.protection([obj], [row['layer']]) == before
    assert np.array_equal(core.coordinates(obj.data, source.name), source_uv)
    assert np.array_equal(core.coordinates(obj.data, other.name), other_uv)
    assert core._pins(obj.data, other.name) == [0]
    assert node.uv_map == source.name and material in list(obj.data.materials)
    assert obj.data.uv_layers.active.name == source.name and source.active_render
    assert not core.state(bpy.context.scene)['adopted']
    print('PASS native SMART', bpy.app.version_string, bpy.app.build_hash.decode(), calls[0], flush=True)
    print('PASS independent quality gap=%.6f border=%.6f' %
          (row['metrics']['gap']['min_px'], row['metrics']['boundary_margin_px']), flush=True)

# Existing fixed and seam constraints still reject SMART before it reaches pack.
for name, constraints in [('explicit_pin', {'pins': [0]}), ('locked_face', {'locked_faces': [0]}),
                          ('must_cut', {'must_cut': [0]}), ('must_not_cut', {'must_not_cut': [0]})]:
    rejected, calls = run(name, native={'CANCELLED'}, **constraints)
    assert not calls and rejected['status'] == 'rejected' and 'constraints' in rejected['reason'], rejected
source.data[0].pin_uv = True
rejected, calls = run('inherited_pin', native={'CANCELLED'})
assert not calls and rejected['status'] == 'rejected' and 'constraints' in rejected['reason'], rejected
source.data[0].pin_uv = False
print('PASS SMART constraints still rejected before pack', flush=True)

# Cancel at the native pack boundary: check exact arguments without risking a
# hang from a different pack branch, and verify scratch-created data is discarded.
for name, method, constraints, shape, pinned in [
    ('cancelled_smart', 'SMART', {}, expected_shape, False),
    ('cancelled_abf', 'ANGLE_BASED', {}, 'CONCAVE', False),
    ('cancelled_abf_pinned', 'ANGLE_BASED', {'pins': [0]}, 'CONCAVE', True),
    ('cancelled_smart_abf', 'SMART_ABF', {}, 'CONCAVE', False),
]:
    rejected, calls = run(name, method, native={'CANCELLED'}, **constraints)
    assert rejected['status'] == 'rejected' and 'Native packing did not finish' in rejected['reason'], rejected
    assert len(calls) == 1 and calls[0]['shape_method'] == shape and calls[0]['pin'] == pinned, calls
    assert calls[0]['margin_method'] == 'FRACTION' and calls[0]['pin_method'] == 'LOCKED', calls
assert list(core.state(bpy.context.scene)['candidates']) == (['compat_smart'] if affected else [])
assert len(bpy.data.scenes) == 1 and obj.mode == 'OBJECT'
new_layers = [row['layer']] if affected else []
assert [uv.name for uv in obj.data.uv_layers] == [source.name, other.name] + new_layers
assert core.protection([obj], new_layers) == before
print('PASS pack branches and cancelled-solve cleanup', flush=True)

if affected:
    rechecked = core.execute(dict(base, operation='validate', candidate='compat_smart'))['record']
    assert rechecked['status'] == 'needs_review' and rechecked['metrics']['status'] == 'pass'
    assert rechecked['uv_hash'] == row['uv_hash']
    print('PASS candidate revalidation and source protection', flush=True)
