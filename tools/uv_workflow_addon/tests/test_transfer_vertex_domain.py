"""Regression for explicit UV transfer across preserved, unreferenced vertices."""
import copy
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uv_workflow_addon import transfer_math, transfer_contract
from uv_workflow_addon.contract import WorkflowError


def meshes():
    source = {'name': 'source', 'positions': [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
              'faces': [[0, 1, 2], [0, 2, 3]], 'face_loops': [[0, 1, 2], [3, 4, 5]]}
    target = {'name': 'target', 'positions': [[0, 0, 0], [1, 0, 0], [5, 6, 7], [1, 1, 0], [0, 1, 0]],
              'faces': [[0, 1, 3], [0, 3, 4]], 'face_loops': [[0, 1, 2], [3, 4, 5]]}
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 0], [1, 1], [0, 1]], dtype=np.float32)
    return source, target, uv


class VertexDomainTests(unittest.TestCase):
    def test_default_still_requires_all_vertices(self):
        source, target, uv = meshes()
        with self.assertRaises(transfer_math.TransferError) as caught:
            transfer_math.topology(source, target, uv, list(range(6)))
        self.assertEqual(caught.exception.code, 'CONFLICT')
        copied, report = transfer_math.topology(source, copy.deepcopy(source), uv, list(range(6)))
        np.testing.assert_array_equal(copied, uv)
        self.assertTrue(report['checks']['vertex_bijection'])
        self.assertNotIn('vertex_domain', report)

    def test_explicit_referenced_domain_preserves_inputs_and_reports_exclusion(self):
        source, target, uv = meshes()
        before = copy.deepcopy((source, target)); uv_before = uv.copy()
        copied, report = transfer_math.topology(source, target, uv, list(range(6)),
                                               vertex_domain='FACE_REFERENCED')
        np.testing.assert_array_equal(copied, uv_before)
        np.testing.assert_array_equal(uv, uv_before)
        self.assertEqual((source, target), before)
        self.assertEqual(report['target']['excluded_vertex_indices'], [2])
        self.assertEqual(report['mapping_summary']['mapped_vertex_count'], 4)
        self.assertFalse(report['checks']['vertex_bijection'])
        self.assertFalse(report['checks']['full_vertex_bijection_required'])
        self.assertTrue(report['checks']['face_referenced_vertex_bijection'])

    def test_bad_corner_and_vertex_correspondence_remains_rejected(self):
        source, target, uv = meshes()
        for mapping in ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4, 4], [0, 2, 1, 3, 4, 5]):
            with self.subTest(mapping=mapping):
                with self.assertRaises(transfer_math.TransferError) as caught:
                    transfer_math.topology(source, target, uv, mapping, vertex_domain='FACE_REFERENCED')
                self.assertEqual(caught.exception.code, 'CONFLICT')

    def test_contract_option_only_belongs_to_explicit_rows(self):
        row = {'source_object': 'source', 'source_uv': 'UVMap',
               'source_binding': {'geometry': 'a'*64, 'mesh': 'source', 'uv_hash': 'b'*64},
               'target_binding': {'geometry': 'c'*64, 'mesh': 'target', 'protection': 'd'*64, 'active_uv': 'UVMap'},
               'mode': 'EXPLICIT', 'corner_map': list(range(6)), 'winding': 'PRESERVE'}
        request = {'transfer_unit_scale': 1, 'transfer': {'target': row}}
        transfer_contract.normalize(request, ['target'])
        self.assertNotIn('vertex_domain', row)
        row['vertex_domain'] = 'FACE_REFERENCED'
        transfer_contract.normalize(request, ['target'])
        row['vertex_domain'] = 'unknown'
        with self.assertRaises(WorkflowError):
            transfer_contract.normalize(request, ['target'])
        row['vertex_domain'] = 'FACE_REFERENCED'; row['mode'] = 'INDEXED'
        del row['corner_map']; del row['winding']
        with self.assertRaises(WorkflowError):
            transfer_contract.normalize(request, ['target'])


if __name__ == '__main__':
    unittest.main()
