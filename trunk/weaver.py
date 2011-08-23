"""
    weaver.py allows building simple web-services around a SPARQL query
    and a sparql endpoint.

    Queries and input parameters are specified in a json file format.
    The file is read by the webservice.
"""

__author__ = 'Janos G. Hajagos'

import semantic_resource_mapping
import json
import re
import urllib
import urlparse


def serve(environ, start_response):
    if environ.has_key("WEAVER_SERVICE_DEFINITIONS"):
        service_definitions = json.loads(environ["WEAVER_SERVICE_DEFINITIONS"])
        query_dictionary = urlparse.parse_qs(environ["QUERY_STRING"])
        requested_path = environ["PATH_INFO"]
        requested_path = requested_path.split("/")[-1]

        eval_parameters = []
        for qd in query_dictionary.keys():
            eval_parameters.append([qd,query_dictionary[qd][0]])
        weaving_obj = Weaving(service_definitions)
        try:
            headers = [("Content-type", "application/json")]
            response = weaving_obj.evaluate(requested_path,eval_parameters)
            status = '200 Ok'
        except RuntimeError, message:
            headers = [("Content-type", "text/plain")]
            response = message
            status = '500 Internal Server Error'
        print(status,headers)
        start_response(status, headers)
        print(response)
        return [response]
    return "hi"

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


def test_server(environ, start_response):
    import sbu_mi_services
    environ["WEAVER_SERVICE_DEFINITIONS"] = json.dumps(sbu_mi_services.service_definitions)
    return serve(environ, start_response)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 9001, test_server)
    server.serve_forever()
