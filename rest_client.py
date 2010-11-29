"""
    A simplified client for making rest calls
"""

import httplib2
import urllib2
import json

class RestClient(object):
    "A simplified client for making rest calls"
    def __init__(self, base_uri = "", default_headers={}):
        self.http_client = httplib2.Http()
        self.base_uri = base_uri
        self.default_headers = default_headers

    def request(self, resource, method, headers={},body=None):
        "Relatively low level method to make a call to a rest interface"
        method = method.upper()
        for key in self.default_headers:
            if not(headers.has_key(key)):
                headers[key] = self.default_headers[key]
       
        response, content = self.http_client.request(self.base_uri + resource, method, body, headers = headers)
        if response.has_key("content-type"): # Handles automatic conversion to json
            if "application/json" in response["content-type"]:
                content = json.loads(content)
        return response, content

    def get(self, resource, headers={}):
        "Makes a get call to a resource"
        return self.request(resource,"GET",headers)

    def post(self, resource, data, headers={}):
        "Makes a post call to a resource"
        return self.request(resource, "POST", headers, data)

    def put(self, resource, data, headers={}):
        "Makes a post call to a resource"
        return self.request(resource, "PUT", headers, data)

    def delete(self, resource, headers={}):
        "Makes a test call"
        return self.request(resource,"DELETE", headers)

    def encode_query_string(self, query_dictionary):
        "Encode a dictionary query string"
        query_string = "?"
        for key in query_dictionary:
            if len(query_string) > 1:
                query_string += "&"
            query_string += key + "="
            value_to_encode = query_dictionary[key]
            if type(value_to_encode)  == type([]):
                list_string = ""
                for value in value_to_encode:
                    if len(list_string) > 1:
                        list_string += "&"
                        list_string += key + '='
                    list_string += urllib2.quote(str(value))
                query_string += list_string
            else:
                query_string += urllib2.quote(str(value_to_encode))
        return query_string
