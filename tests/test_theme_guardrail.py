from copy import deepcopy
import unittest
from auditkit import theme_guardrail as gate


class ThemeRoutingTests(unittest.TestCase):
    def setUp(self):
        self.comment='There is too little planning time. Fixed desks prevent group work.'
        self.pred={'status':1,'themes':{'2':[0],'6':[1]},'evidence':[
            {'theme_id':2,'quote':'There is too little planning time.'},
            {'theme_id':6,'quote':'Fixed desks prevent group work.'}]}
        self.verdicts={2:{'verdict':'explicit','quote':'There is too little planning time.'},
                       6:{'verdict':'not_explicit','quote':'Fixed desks prevent group work.'}}

    def test_one_claim_survives_without_clearing_other(self):
        r=gate.route(self.comment,self.pred,self.verdicts)
        self.assertEqual((r['action'],r['label']),('partial_accept',1))
        self.assertEqual(set(r['accepted_themes']),{2});self.assertEqual(set(r['held_themes']),{6})
        self.assertTrue(r['requires_review'])

    def test_all_rejected_stays_unknown_not_negative(self):
        self.verdicts[2]['verdict']='unclear'
        r=gate.route(self.comment,self.pred,self.verdicts)
        self.assertEqual(r['action'],'hold');self.assertIsNone(r['label']);self.assertFalse(r['accepted_themes'])

    def test_all_supported_completes_without_review(self):
        self.verdicts[6]['verdict']='explicit'
        r=gate.route(self.comment,self.pred,self.verdicts)
        self.assertEqual(r['action'],'auto_accept');self.assertFalse(r['requires_review'])

    def test_bad_quote_only_holds_its_own_theme(self):
        self.verdicts[6]={'verdict':'explicit','quote':'Invented evidence'}
        r=gate.route(self.comment,self.pred,self.verdicts)
        self.assertEqual(set(r['accepted_themes']),{2});self.assertEqual(r['held_themes'][6]['reason'],'verifier_quote_missing')

    def test_missing_theme_verdict_preserves_valid_one(self):
        r=gate.route(self.comment,self.pred,{2:self.verdicts[2]})
        self.assertEqual(set(r['accepted_themes']),{2});self.assertIn(6,r['held_themes'])

    def test_unknown_ids_cannot_cross_input_boundary(self):
        self.verdicts[24]={'verdict':'explicit','quote':'There is too little planning time.'}
        r=gate.route(self.comment,self.pred,self.verdicts)
        self.assertEqual(r['action'],'hold');self.assertFalse(r['accepted_themes'])

    def test_duplicate_canonical_ids_fail_closed(self):
        self.verdicts['2']=self.verdicts[2]
        self.assertEqual(gate.route(self.comment,self.pred,self.verdicts)['action'],'hold')

    def test_proposal_quote_failure_is_local(self):
        self.pred['evidence'][1]['quote']='Invented original quote'
        r=gate.route(self.comment,self.pred,self.verdicts)
        self.assertEqual(set(r['accepted_themes']),{2});self.assertIn(6,r['held_themes'])

    def test_negative_pass_through_and_uncertainty(self):
        self.assertEqual(gate.route(self.comment,{'status':0,'themes':{}})['label'],0)
        for pred in [None,{'status':2,'themes':{}},{'status':True,'themes':{}}]:
            r=gate.route(self.comment,pred);self.assertIsNone(r['label']);self.assertTrue(r['requires_review'])

    def test_no_source_mutation(self):
        before=deepcopy((self.pred,self.verdicts));r=gate.route(self.comment,self.pred,self.verdicts)
        r['accepted_themes'][2]['source_spans'].append(7)
        self.assertEqual((self.pred,self.verdicts),before)





if __name__=='__main__':unittest.main()
