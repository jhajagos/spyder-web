"""
    Weaver.py is to build simple web-services around a SPARQL query to a semantic web
    resource.

    Queries and input parameters are specified in a json file format.
    The file is read by the webservice.
"""

__author__ = 'Janos G. Hajagos'

import semantic_resource_mapping
import json
import re
import urllib

sample_service_definitions = {"pubmed2cuis" : {"parameters": {"pmid": {"regex" : r'[0-9]{0,10}'}},
                              "sparql_endpoint" : "http://link.informatics.stonybrook.edu/sparqltoo/",
"sparql_query" : """select distinct ?cui ?cuilabel where {
{
?pmid  <http://purl.org/ontology/bibo/pmid> "%(pmid)s" .
?pmid <http://link.informatics.stonybrook.edu/pubmed/#MeshHeadingList> ?mh .
?mh ?seq ?pmidmh .
?pmidmh <http://link.informatics.stonybrook.edu/pubmed/#MeshMinorDescriptor> ?cui .
?pmidmh rdfs:label ?cuilabel . }
union
{
?pmid  <http://purl.org/ontology/bibo/pmid> "%(pmid)s" .
?pmid <http://link.informatics.stonybrook.edu/pubmed/#MeshHeadingList> ?mh .
?mh ?seq ?pmidmh .
?pmidmh <http://link.informatics.stonybrook.edu/pubmed/#MeshMajorDescriptor> ?cui .
?pmidmh rdfs:label ?cuilabel . }
}""", "default_graph" : "http://link.informatics.stonybrook.edu/pubmed"
}}

class Weaving(object):
    def __init__(self,service_definitions):
        self.service_definitions = service_definitions

    def validate_service_definition(self):
        pass

    def evaluate(self,service,eval_parameters = []): # [[name,value]]
        if self.service_definitions.has_key(service):
            service_definition = self.service_definitions[service]
            if len(eval_parameters) > 0:
                evaluation_dictionary = {}
                for eval_parameter in eval_parameters:
                    parameter = urllib.unquote(eval_parameter[0])
                    eval_value = urllib.unquote(eval_parameter[1])
                    if service_definition["parameters"].has_key(parameter):
                        regular_expression_value = re.compile(service_definition["parameters"][parameter]["regex"])
                        if regular_expression_value.match(eval_value):
                            evaluation_dictionary[parameter] = eval_value
                        else:
                            raise RuntimeError, "Value of parameter '%s' is not valid" % parameter
                    else:
                        raise RuntimeError, "Parameter '%s' is not valid for service '%s'" % (parameter, service)
                sparql_query = service_definition["sparql_query"] % evaluation_dictionary
                srm = semantic_resource_mapping.VirtuosoSparqlEndPointConnection(service_definition["sparql_endpoint"])
                default_graph = service_definition["default_graph"]
                query_result = srm.query(sparql_query,default_graph)
                return json.dumps(query_result.to_list_dict())
            else:
                pass
        else:
            raise RuntimeError, "Service '%s' is not defined" % service

if __name__ == "__main__":
    w_obj = Weaving(sample_service_definitions)
    print(w_obj.evaluate("pubmed2cuis", [["pmid","20828096"]]))