import unittest
from auditkit.contracts import parse_binary, validate_source_ids
from auditkit.analysis import paired_transitions, repeat_state

class ContractTests(unittest.TestCase):
    def test_json_type_id_and_completion_fail_closed(self):
        for text in ['{"id":1,"off_topic":"false"}', '{"id":true,"off_topic":false}',
                     '{"id":2,"off_topic":false}', '{"id":1,"off_topic":false,"off_topic":true}',
                     'Explanation: {"id":1,"off_topic":false}']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_binary(text,1,stop_reason='end_turn')
        with self.assertRaises(ValueError):
            parse_binary('{"id":1,"off_topic":false}',1,stop_reason='max_tokens')
        self.assertEqual(parse_binary('{"id":1,"off_topic":false}',1,stop_reason='end_turn'),'on_topic')

    def test_missing_calls_do_not_become_exclusions(self):
        result=paired_transitions({1:None,2:'off_topic'},{2:'on_topic',1:'off_topic'})
        self.assertEqual((result['complete_pairs'],result['unavailable_pairs'],result['changed']),(1,1,1))
        self.assertEqual(repeat_state([None,'off_topic']),'unavailable')
        self.assertEqual(repeat_state(['on_topic','off_topic']),'mixed')
        self.assertIsNone(paired_transitions({1:None},{1:None})['change_fraction'])
        with self.assertRaises(ValueError):paired_transitions({1:'on_topic'},{2:'on_topic'})

    def test_evidence_is_bound_to_supplied_source_ids(self):
        self.assertTrue(validate_source_ids('match',[2],{1,2}))
        for status,ids in [('match',[]),('match',[99]),('match',[True]),('match',[1,1]),('no_match',[1])]:
            with self.subTest(status=status,ids=ids), self.assertRaises(ValueError):
                validate_source_ids(status,ids,{1,2})

if __name__=='__main__':unittest.main()
