import unittest
from auditkit.masking import build_school_pattern


class SchoolMaskingTests(unittest.TestCase):
    def test_ordinary_word_preserved_real_school_still_masked(self):
        p=build_school_pattern(['ALL','Oak Elementary','All Saints School'])
        self.assertEqual(p.sub('[SCHOOL]','All students at Oak Elementary and ALL SAINTS SCHOOL.'),
                         'All students at [SCHOOL] and [SCHOOL].')
    def test_boundaries_and_case(self):
        p=build_school_pattern(['all','Pine'])
        self.assertEqual(p.sub('[SCHOOL]','All tall students at PINE, not Pineapple.'),
                         'All tall students at [SCHOOL], not Pineapple.')
    def test_empty_dictionary_cannot_match_every_position(self):
        self.assertEqual(build_school_pattern(['ALL']).sub('[SCHOOL]','All students.'),'All students.')
    def test_generator_keeps_real_schools(self):
        p=build_school_pattern(v for v in ['ALL','Oak'])
        self.assertEqual(p.sub('[SCHOOL]','All students at Oak.'),'All students at [SCHOOL].')


if __name__=='__main__':unittest.main()
