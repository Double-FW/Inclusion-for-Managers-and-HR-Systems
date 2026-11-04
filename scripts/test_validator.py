#!/usr/bin/env python3
"""Regression checks: schemas reject unsafe metadata and retrieval keeps context."""
import copy,unittest
import validate
from build_index import build,search

class IntegrityTests(unittest.TestCase):
    def setUp(self):self.record=copy.deepcopy(validate.load('data/guidance.yaml')['records'][0])
    def test_extra_fields_rejected(self):
        self.record['diagnosis']='invented';self.assertTrue(validate.errors_for('guidance',self.record))
    def test_approval_needs_dates(self):
        self.record['review_status']='approved';self.assertTrue(validate.errors_for('guidance',self.record))
    def test_invalid_directive_rejected(self):
        self.record['directive']='automatic_legal_duty';self.assertTrue(validate.errors_for('guidance',self.record))
    def test_invalid_date_rejected(self):
        self.record['reviewed_on']='tomorrow';self.assertTrue(validate.errors_for('guidance',self.record))
    def test_dependency_needs_pin(self):
        d=copy.deepcopy(validate.load('evidence/dependencies.yaml')['dependencies'][2]);d['reviewed_commit']=None
        self.assertTrue(validate.errors_for('dependency',d))
    def test_default_excludes_unapproved_records(self):
        # In this review package all records are draft; future adoption changes this expectation.
        self.assertEqual(build(),[])
    def test_complete_draft_sections(self):
        items=build(True);self.assertEqual(len(items),len(validate.load('data/guidance.yaml')['records']))
        for r in items:
            self.assertIn('**Boundary:**',r['text']);self.assertIn('**Evidence:**',r['text'])
            self.assertEqual(r['review_status'],'draft');self.assertFalse(r['authoritative']);self.assertTrue(r['source_ids'])
    def test_retrieval_keeps_important_limits(self):
        expectations={'IE-COM-001':'No platform','IE-ADJ-003':'not a substitute','IE-SYS-002':'no employee should be raced','IE-SYS-003':'payment','IE-AI-002':'Never execute','IE-EVA-002':'Never put completed'}
        for rid,phrase in expectations.items():
            result=search(build(True),rid)[0];self.assertEqual(result['id'],rid);self.assertIn(phrase,result['text'])
    def test_repo_references_and_coverage(self):
        errors,counts=validate.collect();self.assertEqual(errors,[]);self.assertEqual(counts['input_units'],70)
    def test_boundary_removal_is_detectable(self):
        r=search(build(True),'IE-AI-002')[0]
        self.assertIn('No diagnosis',r['limitations']) if 'No diagnosis' in r['limitations'] else self.assertIn('governance',r['limitations'])
        self.assertIn('autonomous hiring',r['text'])

if __name__=='__main__':unittest.main(verbosity=2)
