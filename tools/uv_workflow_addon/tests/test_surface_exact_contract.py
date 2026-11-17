"""Host-safe request boundary for explicit candidate reuse on final surfaces."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from uv_workflow_addon.surface_contract import normalize
from uv_workflow_addon.contract import WorkflowError


def request():
    return {'layers':{'Body':'UVW_final'},'frames':[1,10],
            'modes':['VIEWPORT','RENDER'],'triangle_limit':10000,'usage':'EXCLUSIVE'}


class SurfaceExactContractTests(unittest.TestCase):
    def rejected(self,value,code='INVALID_REQUEST'):
        with self.assertRaises(WorkflowError) as caught:normalize(value,['Body'])
        self.assertEqual(caught.exception.code,code)

    def test_legacy_exclusive_is_unchanged_and_copied(self):
        value=request();before=copy.deepcopy(value);normalized=normalize(value,['Body'])
        self.assertEqual(normalized,before)
        normalized['frames'].append(20)
        self.assertEqual(value,before)
        self.assertNotIn('candidate',value)

    def test_explicit_exact_candidate_accepts_ascii_boundary_ids(self):
        for candidate in ('A','Final_01-uv','A'+'0'*47):
            with self.subTest(candidate=candidate):
                value=request();value.update(usage='CANDIDATE_EXACT',candidate=candidate)
                self.assertEqual(normalize(value,['Body']),value)

    def test_exact_requires_candidate(self):
        value=request();value['usage']='CANDIDATE_EXACT';self.rejected(value)

    def test_candidate_id_is_not_coerced_or_truncated(self):
        for candidate in (None,1,True,{},[], '', '1abc','含中文','a.b','a/b','a b','a\n','a'*49):
            with self.subTest(candidate=candidate):
                value=request();value.update(usage='CANDIDATE_EXACT',candidate=candidate);self.rejected(value)

    def test_candidate_is_mutually_exclusive_with_legacy_usage(self):
        for candidate in ('Final',None):
            with self.subTest(candidate=candidate):
                value=request();value['candidate']=candidate;self.rejected(value)

    def test_missing_usage_and_unknown_usage_do_not_enable_reuse(self):
        value=request();del value['usage'];self.rejected(value)
        for usage in ('TILED','candidate_exact','AUTO',None,{},[]):
            with self.subTest(usage=usage):
                value=request();value.update(usage=usage,candidate='Final');self.rejected(value,'UNSUPPORTED')

    def test_modes_remain_explicit_and_distinct(self):
        value=request();del value['modes'];self.rejected(value)
        for modes in ([],['PREVIEW'],['RENDER','RENDER'],['VIEWPORT','RENDER','VIEWPORT']):
            with self.subTest(modes=modes):
                value=request();value.update(usage='CANDIDATE_EXACT',candidate='Final',modes=modes);self.rejected(value)

    def test_no_extra_reuse_or_approval_fields(self):
        for field in ('reuse_groups','settings','recipe','approved','tolerance'):
            with self.subTest(field=field):
                value=request();value.update(usage='CANDIDATE_EXACT',candidate='Final');value[field]=[];self.rejected(value)

    def test_exact_still_requires_complete_layer_map_and_resource_limit(self):
        value=request();value.update(usage='CANDIDATE_EXACT',candidate='Final')
        for layers in ({},{'Body':'UVW_final','Other':'UVW_final'},{'Body':''}):
            with self.subTest(layers=layers):
                bad=copy.deepcopy(value);bad['layers']=layers;self.rejected(bad)
        value['triangle_limit']=2000001;self.rejected(value,'RESOURCE_LIMIT')

    def test_exact_does_not_enable_inherited_configured_density(self):
        value=request();value.update(usage='CANDIDATE_EXACT',candidate='Final',policy={
            'name':'surface','purpose':'surface','reference':'caller',
            'density_basis':'CONFIGURED_TARGETS','stretch_p95_max':1,'stretch_max':1,
            'density_relative_max':.05,'border_px_min':0,'gap_px_min':0})
        self.rejected(value,'UNSUPPORTED')
        value['policy']['density_basis']='ISLAND_AREA_REFERENCE'
        self.assertEqual(normalize(value,['Body']),value)


if __name__=='__main__':unittest.main()
