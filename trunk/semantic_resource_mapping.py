"""
    Classes to handle connecting to remote/local sparql endpoints
    and mapping the requested http resource to one that exists
    in the resource
    
"""

from rest_client import *
from string import join

class SparqlResult(object):
    "Encapsulates a SPARQL result"
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

    def reverse_predicate_resource_string(self, uri):
        return "select ?subject ?predicate {?subject ?predicate <%s>  .}" % uri

class SparqlEndPointConnection(SemanticServerConnection):
    """Handle connection to a sparql server"""
    
    def __init__(self,sparql_endpoint_address):
        self.sparql_endpoint_address = sparql_endpoint_address
    def query(self,response_type="application/json"):
        pass
        
class VirtuosoSparqlEndPointConnection(SparqlEndPointConnection):
    "Connect to a Virtuoso Sparql Endpoint"
    
    def query(self,query_string,default_graph):
        "Perform a SPARQL query"
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

    def find_resource_path(self,path_request):
        full_uri = self.full_uri_expansion(path_request)
        return self.find_resource(full_uri)

    def find_resource(self,path_request):
        if self.limit:
            limit_string = "limit %s" % self.limit
        else:
            limit_string = ""

        sparql_result = self.semantic_obj.query(self.semantic_obj.predicate_resource_string(path_request) + " "  + limit_string,self.default_graph)
        
        if len(sparql_result) == 0:
            return 0
        else:
            self.resource_map[path_request] = sparql_result
            return 1

    def full_uri_expansion(self,path_request):
        "Transform a path to a full"
        return self.uri_base_map + path_request

    def get_resource(self,path_request):
        full_uri = self.full_uri_expansion(path_request)
        if self.resource_map.has_key(full_uri):
            return self.resource_map[full_uri]
        else:
            return 0

    def get_reverse_resource(self, path_request):
        full_uri = self.full_uri_expansion(path_request)
        if self.limit:
            limit_string = "limit %s" % self.limit
        else:
            limit_string = ""
        sparql_result = self.semantic_obj.query(self.semantic_obj.reverse_predicate_resource_string(full_uri) + " "  + limit_string,self.default_graph)

        if len(sparql_result) == 0:
            return 0
        else:
            return sparql_result

class BlankSemanticResourceObject(object):
    def __init__(self):
        pass
    def __getitem__(self,item):
        return BlankSemanticResourceObject()
    def __repr__(self):
        return ""


class SemanticResourceObject(object):
    "Encapsulates a resource a uri in a triple store"
    def __init__(self,semantic_connection_obj, uri, semantic_resource_factory, graph_uri = None, namespaces = None, throw_error_missing_predicate=1, limit=1000):
        self.graph_uri = graph_uri
        self.semantic_connection_obj = semantic_connection_obj
        self.visited_properties = {}
        self.namespaces = namespaces
        self.semantic_resource_factory = semantic_resource_factory
        self.throw_error_missing_predicate = throw_error_missing_predicate
        self.limit = limit
        self.uri = uri

        self.links_cached = 0  #Indicates whether a call has been made to get the forward links
        self.links_to_cached = 0 #Indicates whether a call has been made to get the reverse links

        self.links = {} # Dictionary for holding forward links
        self.links_to = {} #Dictionary for hodling link_to the semantic resource

    def _get_resource_from_sparql_result(self,sparql_row,field_name="object"):
        resource_object = sparql_row[field_name]
        if resource_object["type"] == "uri":
            return self.semantic_resource_factory.create_resource(resource_object["value"])
        else:
            return resource_object["value"] # Right now we return the value we lose the language aspect of the tag

    def expand_uri(self,uri_to_expand):
        "Expands uri prefix when the namespace of the prefix is registered"
        if ":" in uri_to_expand:
            split_uri = uri_to_expand.split(":")
            if len(split_uri):
                prefix = split_uri[0]
                if self.namespaces.has_key(prefix):
                    return join([self.namespaces[prefix],split_uri[-1]],'')
                else:
                    return uri_to_expand
        else:
            return uri_to_expand
        
    def find_links(self):
        "Method gets data that this resource links to. In rdf this is where the resource is the subject of a triple."
        if self.limit:
            limit_string = "limit %s" % self.limit
        else:
            limit_string = ""

        self.resource_sparql_result = self.semantic_connection_obj.query(self.semantic_connection_obj.predicate_resource_string(self.uri) + " "  + limit_string, self.graph_uri)

        if len(self.resource_sparql_result) > 0:
            if self.resource_sparql_result:
                for row in self.resource_sparql_result:
                    predicate_uri = row["predicate"]["value"]
                    if self.links.has_key(predicate_uri): # Check if we have seen the predicate before
                        resource_object = self.links[predicate_uri]
                        if type(resource_object) != type([]): # if item has only occurred once
                            self.links[predicate_uri] = [self.links[predicate_uri]]
                        self.links[predicate_uri].append(self._get_resource_from_sparql_result(row))
                    else:
                        self.links[predicate_uri] = self._get_resource_from_sparql_result(row)

    def find_links_to(self):
        "Get data that links to this resource. In rdf this is where the resource is the object of the triple."
        if self.limit:
            limit_string = "limit %s" % self.limit
        else:
            limit_string = ""

        self.resource_sparql_result_link_to = self.semantic_connection_obj.query(self.semantic_connection_obj.reverse_predicate_resource_string(self.uri) + " "  + limit_string, self.graph_uri)

        if len(self.resource_sparql_result_link_to) > 0:
            for row in self.resource_sparql_result_link_to:
                predicate_uri = row["predicate"]["value"]
                if self.links_to.has_key(predicate_uri): # Check if we have seen the predicate before
                    resource_object = self.links_to[predicate_uri]
                    if type(resource_object) != type([]): # if item has only occurred once
                        self.links_to[predicate_uri] = [self.links_to[predicate_uri]]
                    self.links_to[predicate_uri].append(self._get_resource_from_sparql_result(row,"subject"))
                else:
                    self.links_to[predicate_uri] = self._get_resource_from_sparql_result(row,"subject")

    def get_link(self,uri):
        "For a resource given the predicate uri gets the object"
        uri = self.expand_uri(uri)
        if not(self.links_cached):
            self.find_links()
            self.links_cached = 1

        if self.throw_error_missing_predicate:
            return self.links[uri]
        else:
            if self.links.has_key(uri):
                return self.links[uri]
            else:
                return BlankSemanticResourceObject()

    def get_link_to(self,uri):
        "For a resource given the predicate uri that links to get the subject"
        uri = self.expand_uri(uri)
        if not(self.links_to_cached):
            self.find_links_to()
            self.links_to_cached = 1
        if self.throw_error_missing_predicate:
            return self.links_to[uri]
        else:
            if self.links_to.has_key(uri):
                return self.links_to[uri]
            else:
                return BlankSemanticResourceObject()
        
    def __getitem__(self,item):
        """
        -> ?
        <- ?
        -> foaf:givenName
        foaf:givenName
        <- foaf:Group
        http://link.informatics.stonybrook.edu/rxnorm/RXAUI/
        """

        if item.strip() == "-> ?":
            return self.predicates()
        elif item.strip() == "<- ?":
            return self.predicates_to()
        elif item.strip() == "-> ??":
            self.find_links()
            return self.links
        elif item.strip() == "<- ??":
            self.find_links_to()
            return self.links_to
        elif item[0:2] == "->":
            return self.get_link(item[2:].strip())
        elif item[0:2] == "<-":
            return self.get_link_to(item[2:].strip())
        else:
            return self.get_link(item)
        
    def predicates(self):
        "Returns a list of predicates"
        if not(self.links_cached):
            self.find_links()
            self.links_cached = 1
        return self.links.keys()
            
    def predicates_to(self):
        "Returns a list of predicates linking to this resource"
        if not(self.links_to_cached):
            self.find_links_to()
            self.links_to_cached = 1
        return self.links_to.keys()

    def __repr__(self):
        return "<%s>" % self.uri

class SemanticResourceObjectFactory(object):
    "Creates, caches, parameterizes, and returns a uri which is stored in a triple store"
    def __init__(self,semantic_connection_obj, default_graph=None,namespaces={},throw_error_missing_predicate=1):
        self.semantic_connection_obj = semantic_connection_obj
        self.default_graph = default_graph
        self.throw_error_missing_predicate = throw_error_missing_predicate
        self.semantic_resource_cache = {}
        self.namespaces =  {"foaf": "http://xmlns.com/foaf/0.1/", "rdfs" : "http://www.w3.org/2000/01/rdf-schema#", "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#" , "owl" : "http://www.w3.org/2002/07/owl#",  "dc":"http://purl.org/dc/terms/", "skos":"http://www.w3.org/2004/02/skos/core#"}

        for namespace in namespaces.items():
            self.namespaces[namespace[0]] = namespace[1]
        
    def create_resource(self,uri):
        "Create a semantic resource object"
        if self.semantic_resource_cache.has_key(uri):
            semantic_resource_object = self.semantic_resource_cache[uri]
        else:
            semantic_resource_object = SemanticResourceObject(self.semantic_connection_obj, uri, self,  self.default_graph, self.namespaces,self.throw_error_missing_predicate)
            self.semantic_resource_cache[uri] = semantic_resource_object
        return semantic_resource_object