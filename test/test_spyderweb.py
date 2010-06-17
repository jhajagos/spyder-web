# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
import sys
sys.path.append("../")
import json
from pprint import pprint

from semantic_resource_mapping import *

class TestSparqlResult(unittest.TestCase):
    def setUp(self):
        raw_sparql_result_string = """{ "head": { "link": [], "vars": ["predicate", "object"] },
  "results": { "distinct": false, "ordered": true, "bindings": [
    { "predicate": { "type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI" }},
    { "predicate": { "type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#label" }	, "object": { "type": "literal", "value": "aspirin" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/REL#ingredient_of" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/2601469" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/REL#ingredient_of" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/2601471" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/REL#ingredient_of" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/2601468" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/REL#ingredient_of" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/2601472" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/REL#ingredient_of" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/2601467" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/REL#ingredient_of" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/2601470" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/hasRXCUI" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXCUI/1191" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/hasSAB" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/SAB/MTHSPL" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/hasTermType" }	, "object": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/TTY/SU" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/RXAUI" }	, "object": { "type": "literal", "value": "2601466" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/RXAUI/CODE" }	, "object": { "type": "literal", "value": "NOCODE" }},
    { "predicate": { "type": "uri", "value": "http://link.informatics.stonybrook.edu/rxnorm/ATN#SPL_SET_ID" }	, "object": { "type": "literal", "value": "b512c6ce-5b32-4b4f-a93e-293a68eda6b5" }} ] } }"""

        raw_sparql_result = json.loads(raw_sparql_result_string)
        self.sparql_result = SparqlResult(raw_sparql_result)

        
    def testEmptyQuery(self):
        raw_empty_sparql_result_string = """{ "head": { "link": [], "vars": ["predicate", "object"] },
  "results": { "distinct": false, "ordered": true, "bindings": [ ] } }"""
        raw_empty_sparql_result = json.loads(raw_empty_sparql_result_string)
        empty_sparql_result = SparqlResult(raw_empty_sparql_result)
        self.assertEqual(0,len(empty_sparql_result))
        

class  TestSpyderWebTestCase(unittest.TestCase):
    def setUp(self):
        semantic_connection =  VirtuosoSparqlEndPointConnection("http://dbpedia.org/sparql")
        self.semantic_resource_map = SemanticResourceMapping(semantic_connection,"http://dbpedia.org")

    def test_resource_mapping(self):
        found = self.semantic_resource_map.find_resource_path("/resource/Aspirin")
        self.assertEquals(1,found,"Resource exists in dpedia")
        not_found = self.semantic_resource_map.find_resource_path("/resource/MythicalMedicineForThe1950s")
        self.assertEquals(0,not_found,"This resource should not exist on dbPedia!")

class TestSemanticResourceFactory(unittest.TestCase):
    def setUp(self):
        self.semantic_connection =  VirtuosoSparqlEndPointConnection("http://dbpedia.org/sparql")
        
    def test_resource_factory(self):
        semantic_resource_factory = SemanticResourceObjectFactory(self.semantic_connection)
        aspirin_resource = semantic_resource_factory.create_resource("http://dbpedia.org/resource/Aspirin")
#        print(aspirin_resource.predicates())
#        print(aspirin_resource.links)

        aspirin_subject = aspirin_resource.get_link("skos:subject")
        pprint(aspirin_subject[0].predicates())
        pprint(aspirin_subject[0]["-> rdf:type"])

#        pprint(aspirin_subject)
#        pprint(aspirin_subject[0].predicates())
#        pprint(aspirin_subject[0].links)
#        pprint(aspirin_subject[0].predicates_to())
#        pprint(aspirin_subject[0].links_to)
#

        
if __name__ == '__main__':
    unittest.main()

