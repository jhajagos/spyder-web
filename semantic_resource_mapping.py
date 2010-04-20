"""
    Classes to handle connecting to remote/local sparql endpoints
    and mapping the requested http resource to one that exists
    in the resource
"""

from rest_client import *

class SparqlResult(object):
    def __init__(self,raw_sparql_result,type="json"):
        self.raw_sparql_result = raw_sparql_result

        self.variables = self.raw_sparql_result["head"]["vars"]
        self.raw_result = self.raw_sparql_result["results"]["bindings"]
        
    def __len__(self):
        return len(self.raw_result)

    def __getitem__(self,ind):
        return self.raw_result[ind]

class SemanticServerConnection(object):
    """Abstract class to connect to a semantic server"""
    def get_predicates(self):
        pass
    def get_classes(self):
        return ""
    def predicate_resource_string(self,uri):
        return "select ?predicate ?object {<%s> ?predicate ?object}" % uri

class SparqlEndPointConnection(SemanticServerConnection):
    """Handle connection to a sparql server"""
    
    def __init__(self,sparql_endpoint_address):
        self.sparql_endpoint_address = sparql_endpoint_address
    def query(self,response_type="application/json"):
        pass
        
class VirtuosoSparqlEndPointConnection(SparqlEndPointConnection):
    "Connect to a Virtuoso Sparql Endpoint"
    
    def query(self,query_string,default_graph):

        query_hash = {"query":query_string}
        if default_graph is not None:
            query_hash["default-graph-uri"] = default_graph

        rest_client = RestClient(self.sparql_endpoint_address,{"accept":"application/json"})
        (response,result) = rest_client.get(rest_client.encode_query_string(query_hash))
        if response["status"] == "200":
            return SparqlResult(result)
        else:
            raise IOError

class SemanticResourceMapping(object):
    "Handles mapping of a reasource from a HTTP request to the uri in the web server"
    def __init__(self, semantic_connection_obj, uri_base_map, default_graph=None,limit=1000):
        self.semantic_obj = semantic_connection_obj
        self.uri_base_map = uri_base_map
        self.default_graph = default_graph
        self.limit = limit
        self.resource_map = {} #Resource caches
        
    def find_resource(self,path_request):
        full_uri = self.full_uri(path_request)
        if self.limit:
            limit_string = "limit %s" % self.limit
        else:
            limit_string = ""

        sparql_result = self.semantic_obj.query(self.semantic_obj.predicate_resource_string(full_uri) + " "  + limit_string,self.default_graph)
        
        if len(sparql_result) == 0:
            return 0
        else:
            self.resource_map[full_uri] = sparql_result
            return 1

    def full_uri(self,path_request):
        "Transform a path to a full"
        return self.uri_base_map + path_request

    def get_resource(self,path_request):
        full_uri = self.full_uri(path_request)
        if self.resource_map.has_key(full_uri):
            return self.resource_map[full_uri]
        else:
            return 0
    